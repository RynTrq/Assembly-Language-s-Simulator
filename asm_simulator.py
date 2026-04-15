"""Assembler and simulator for the teaching 16-bit assembly ISA.

The module is intentionally importable and side-effect free.  The legacy
scripts in this repository delegate to the CLI helpers at the bottom.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


MEMORY_SIZE = 128
WORD_BITS = 16
REGISTER_COUNT = 8
ADDRESS_BITS = 7
IMMEDIATE_BITS = 7
MAX_UNSIGNED_VALUE = 2 ** WORD_BITS - 1

REGISTERS: Dict[str, int] = {
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "FLAGS": 7,
}

FLAG_OVERFLOW = 1 << 3
FLAG_LESS = 1 << 2
FLAG_GREATER = 1 << 1
FLAG_EQUAL = 1


@dataclass(frozen=True)
class InstructionSpec:
    mnemonic: str
    opcode: str
    kind: str


INSTRUCTIONS: Dict[str, InstructionSpec] = {
    "add": InstructionSpec("add", "00000", "A"),
    "sub": InstructionSpec("sub", "00001", "A"),
    "mov": InstructionSpec("mov", "00010", "B_OR_C"),
    "ld": InstructionSpec("ld", "00100", "D"),
    "st": InstructionSpec("st", "00101", "D"),
    "mul": InstructionSpec("mul", "00110", "A"),
    "div": InstructionSpec("div", "00111", "C"),
    "rs": InstructionSpec("rs", "01000", "B"),
    "ls": InstructionSpec("ls", "01001", "B"),
    "xor": InstructionSpec("xor", "01010", "A"),
    "or": InstructionSpec("or", "01011", "A"),
    "and": InstructionSpec("and", "01100", "A"),
    "not": InstructionSpec("not", "01101", "C"),
    "cmp": InstructionSpec("cmp", "01110", "C"),
    "jmp": InstructionSpec("jmp", "01111", "E"),
    "addf": InstructionSpec("addf", "10000", "A"),
    "subf": InstructionSpec("subf", "10001", "A"),
    "movf": InstructionSpec("movf", "10010", "B_FLOAT"),
    "addi": InstructionSpec("addi", "10011", "B"),
    "subi": InstructionSpec("subi", "10100", "B"),
    "muli": InstructionSpec("muli", "10101", "B"),
    "remi": InstructionSpec("remi", "10110", "B"),
    "quoi": InstructionSpec("quoi", "10111", "B"),
    "hlt": InstructionSpec("hlt", "11010", "F"),
    "jlt": InstructionSpec("jlt", "11100", "E"),
    "jgt": InstructionSpec("jgt", "11101", "E"),
    "je": InstructionSpec("je", "11111", "E"),
}

OPCODES = {spec.opcode: spec for spec in INSTRUCTIONS.values() if spec.kind != "B_OR_C"}
OPCODES["00010"] = InstructionSpec("mov", "00010", "B")
OPCODES["00011"] = InstructionSpec("mov", "00011", "C")


class AssemblyError(Exception):
    """Raised when assembly source cannot be converted to machine code."""

    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("\n".join(self.errors))


class SimulationError(Exception):
    """Raised when a machine-code program cannot be simulated safely."""


@dataclass(frozen=True)
class ParsedLine:
    number: int
    tokens: Tuple[str, ...]


@dataclass(frozen=True)
class Program:
    machine_code: List[str]
    symbols: Dict[str, int]
    variables: Dict[str, int]


def binary(value: int, bits: int) -> str:
    if value < 0 or value >= 2 ** bits:
        raise ValueError(f"{value} does not fit in {bits} bits")
    return format(value, f"0{bits}b")


def parse_register(token: str, line_number: int, *, allow_flags: bool = False) -> int:
    if token not in REGISTERS:
        raise AssemblyError([f"Line {line_number}: invalid register '{token}'"])
    if token == "FLAGS" and not allow_flags:
        raise AssemblyError([f"Line {line_number}: FLAGS cannot be used here"])
    return REGISTERS[token]


def strip_immediate_prefix(token: str) -> str:
    return token[1:] if token.startswith(("$", "&")) else token


def parse_int(token: str, line_number: int, *, bits: int, name: str) -> int:
    raw = strip_immediate_prefix(token)
    try:
        value = int(raw, 10)
    except ValueError as exc:
        raise AssemblyError([f"Line {line_number}: invalid {name} '{token}'"]) from exc
    if str(value) != raw and not (raw.startswith("+") and raw[1:] == str(value)):
        raise AssemblyError([f"Line {line_number}: {name} must be a whole decimal number"])
    if value < 0 or value >= 2 ** bits:
        raise AssemblyError([f"Line {line_number}: {name} {value} is outside 0..{2 ** bits - 1}"])
    return value


def parse_float_fraction(token: str, line_number: int) -> Fraction:
    raw = strip_immediate_prefix(token)
    try:
        value = Fraction(raw)
    except ValueError as exc:
        raise AssemblyError([f"Line {line_number}: invalid floating immediate '{token}'"]) from exc
    if value < 0:
        raise AssemblyError([f"Line {line_number}: floating immediate cannot be negative"])
    return value


def encode_float8(value: Fraction, line_number: int = 0) -> str:
    if value == 0:
        return "00000000"
    for exponent in range(8):
        scaled = value / (2 ** exponent)
        if Fraction(1, 1) <= scaled < Fraction(2, 1):
            mantissa = (scaled - 1) * 32
            if mantissa.denominator == 1 and 0 <= mantissa.numerator < 32:
                return binary(exponent, 3) + binary(mantissa.numerator, 5)
    location = f"Line {line_number}: " if line_number else ""
    raise AssemblyError([f"{location}floating immediate {float(value):g} is not representable in 8 bits"])


def decode_float8(bits: str) -> Fraction:
    exponent = int(bits[:3], 2)
    mantissa = int(bits[3:], 2)
    if exponent == 0 and mantissa == 0:
        return Fraction(0, 1)
    return (Fraction(1, 1) + Fraction(mantissa, 32)) * (2 ** exponent)


def encode_float_register(value: Fraction) -> int:
    return int(encode_float8(value), 2)


def decode_float_register(value: int) -> Fraction:
    return decode_float8(binary(value & 0xFF, 8))


def remove_comment(line: str) -> str:
    return line.split("#", 1)[0].strip()


def parse_source(lines: Iterable[str]) -> List[ParsedLine]:
    parsed: List[ParsedLine] = []
    for number, raw_line in enumerate(lines, 1):
        line = remove_comment(raw_line)
        if not line:
            continue
        if line in {"hogya", "donee"}:
            break
        parsed.append(ParsedLine(number, tuple(line.replace(",", " ").split())))
    return parsed


def instruction_kind(tokens: Sequence[str], line_number: int) -> str:
    mnemonic = tokens[0]
    if mnemonic not in INSTRUCTIONS:
        raise AssemblyError([f"Line {line_number}: unknown instruction '{mnemonic}'"])
    kind = INSTRUCTIONS[mnemonic].kind
    if kind == "B_OR_C":
        if len(tokens) != 3:
            raise AssemblyError([f"Line {line_number}: mov expects 2 operands"])
        return "C" if tokens[2] in REGISTERS else "B"
    return kind


def validate_symbols(parsed: Sequence[ParsedLine]) -> Tuple[List[ParsedLine], Dict[str, int], Dict[str, int], List[str]]:
    errors: List[str] = []
    labels: Dict[str, int] = {}
    variables: Dict[str, int] = {}
    instructions: List[ParsedLine] = []
    seen_non_var = False
    hlt_count = 0

    for line in parsed:
        tokens = list(line.tokens)
        if not tokens:
            continue

        if tokens[0] == "var":
            if seen_non_var:
                errors.append(f"Line {line.number}: variables must be declared before instructions")
            if len(tokens) != 2:
                errors.append(f"Line {line.number}: var expects exactly one name")
            elif tokens[1] in variables or tokens[1] in labels or tokens[1] in INSTRUCTIONS:
                errors.append(f"Line {line.number}: duplicate or reserved symbol '{tokens[1]}'")
            else:
                variables[tokens[1]] = -1
            continue

        seen_non_var = True
        if tokens[0].endswith(":"):
            label = tokens[0][:-1]
            if not label:
                errors.append(f"Line {line.number}: empty label")
                continue
            if label in labels or label in variables or label in INSTRUCTIONS:
                errors.append(f"Line {line.number}: duplicate or reserved label '{label}'")
                continue
            labels[label] = len(instructions)
            tokens = tokens[1:]
            if not tokens:
                errors.append(f"Line {line.number}: label must be followed by an instruction")
                continue

        if tokens[0] == "hlt":
            hlt_count += 1
        elif hlt_count:
            errors.append(f"Line {line.number}: instruction appears after hlt")

        instructions.append(ParsedLine(line.number, tuple(tokens)))

    if hlt_count == 0:
        errors.append("Program is missing hlt")
    elif hlt_count > 1:
        errors.append("Program contains multiple hlt instructions")

    instruction_count = len(instructions)
    for index, name in enumerate(variables):
        variables[name] = instruction_count + index

    if instruction_count + len(variables) > MEMORY_SIZE:
        errors.append(f"Program uses {instruction_count + len(variables)} memory slots; maximum is {MEMORY_SIZE}")

    return instructions, labels, variables, errors


def assemble_instruction(line: ParsedLine, labels: Dict[str, int], variables: Dict[str, int]) -> str:
    tokens = line.tokens
    mnemonic = tokens[0]
    kind = instruction_kind(tokens, line.number)

    if kind == "A":
        if len(tokens) != 4:
            raise AssemblyError([f"Line {line.number}: {mnemonic} expects 3 registers"])
        rd = parse_register(tokens[1], line.number)
        rs1 = parse_register(tokens[2], line.number)
        rs2 = parse_register(tokens[3], line.number)
        return INSTRUCTIONS[mnemonic].opcode + "00" + binary(rd, 3) + binary(rs1, 3) + binary(rs2, 3)

    if kind == "B":
        if len(tokens) != 3:
            raise AssemblyError([f"Line {line.number}: {mnemonic} expects a register and immediate"])
        register = parse_register(tokens[1], line.number)
        immediate = parse_int(tokens[2], line.number, bits=IMMEDIATE_BITS, name="immediate")
        opcode = "00010" if mnemonic == "mov" else INSTRUCTIONS[mnemonic].opcode
        return opcode + "0" + binary(register, 3) + binary(immediate, 7)

    if kind == "B_FLOAT":
        if len(tokens) != 3:
            raise AssemblyError([f"Line {line.number}: movf expects a register and floating immediate"])
        register = parse_register(tokens[1], line.number)
        immediate = encode_float8(parse_float_fraction(tokens[2], line.number), line.number)
        return INSTRUCTIONS[mnemonic].opcode + binary(register, 3) + immediate

    if kind == "C":
        if len(tokens) != 3:
            raise AssemblyError([f"Line {line.number}: {mnemonic} expects 2 registers"])
        rd = parse_register(tokens[1], line.number)
        rs = parse_register(tokens[2], line.number, allow_flags=mnemonic == "mov")
        opcode = "00011" if mnemonic == "mov" else INSTRUCTIONS[mnemonic].opcode
        return opcode + "00000" + binary(rd, 3) + binary(rs, 3)

    if kind == "D":
        if len(tokens) != 3:
            raise AssemblyError([f"Line {line.number}: {mnemonic} expects a register and variable"])
        register = parse_register(tokens[1], line.number)
        symbol = tokens[2]
        if symbol in labels:
            raise AssemblyError([f"Line {line.number}: label '{symbol}' used where variable was expected"])
        if symbol not in variables:
            raise AssemblyError([f"Line {line.number}: undefined variable '{symbol}'"])
        return INSTRUCTIONS[mnemonic].opcode + "0" + binary(register, 3) + binary(variables[symbol], ADDRESS_BITS)

    if kind == "E":
        if len(tokens) != 2:
            raise AssemblyError([f"Line {line.number}: {mnemonic} expects a label"])
        label = tokens[1]
        if label in variables:
            raise AssemblyError([f"Line {line.number}: variable '{label}' used where label was expected"])
        if label not in labels:
            raise AssemblyError([f"Line {line.number}: undefined label '{label}'"])
        return INSTRUCTIONS[mnemonic].opcode + "0000" + binary(labels[label], ADDRESS_BITS)

    if kind == "F":
        if len(tokens) != 1:
            raise AssemblyError([f"Line {line.number}: hlt does not take operands"])
        return INSTRUCTIONS[mnemonic].opcode + "0" * 11

    raise AssertionError(f"Unhandled instruction kind {kind}")


def assemble(source: str) -> Program:
    parsed = parse_source(source.splitlines())
    instructions, labels, variables, errors = validate_symbols(parsed)
    machine_code: List[str] = []
    for line in instructions:
        try:
            machine_code.append(assemble_instruction(line, labels, variables))
        except AssemblyError as exc:
            errors.extend(exc.errors)
    if errors:
        raise AssemblyError(errors)
    return Program(machine_code, labels, variables)


def validate_machine_line(line: str, number: int) -> str:
    word = line.strip()
    if not word:
        return ""
    if len(word) != WORD_BITS or any(ch not in "01" for ch in word):
        raise SimulationError(f"Line {number}: machine code must be exactly 16 binary digits")
    if word[:5] not in OPCODES:
        raise SimulationError(f"Line {number}: unknown opcode {word[:5]}")
    return word


def parse_machine_code(text: str) -> List[str]:
    code = [word for number, line in enumerate(text.splitlines(), 1) if (word := validate_machine_line(line, number))]
    if not code:
        raise SimulationError("No machine code supplied")
    if len(code) > MEMORY_SIZE:
        raise SimulationError(f"Program has {len(code)} instructions; maximum is {MEMORY_SIZE}")
    if not any(word.startswith(INSTRUCTIONS["hlt"].opcode) for word in code):
        raise SimulationError("Program is missing hlt")
    return code


@dataclass
class CPU:
    memory: List[int]
    registers: List[int]
    pc: int = 0
    halted: bool = False

    @classmethod
    def from_machine_code(cls, code: Sequence[str]) -> "CPU":
        memory = [0] * MEMORY_SIZE
        for index, word in enumerate(code):
            memory[index] = int(word, 2)
        return cls(memory=memory, registers=[0] * REGISTER_COUNT)

    @property
    def flags(self) -> int:
        return self.registers[REGISTERS["FLAGS"]]

    @flags.setter
    def flags(self, value: int) -> None:
        self.registers[REGISTERS["FLAGS"]] = value & 0xF

    def clear_flags(self) -> None:
        self.flags = 0

    def set_overflow(self) -> None:
        self.flags = FLAG_OVERFLOW

    def checked_store(self, register: int, value: int) -> None:
        if value < 0 or value > MAX_UNSIGNED_VALUE:
            self.registers[register] = 0
            self.set_overflow()
        else:
            self.clear_flags()
            self.registers[register] = value

    def current_trace(self, pc: Optional[int] = None) -> str:
        parts = [binary(self.pc if pc is None else pc, ADDRESS_BITS)]
        parts.extend(binary(value, WORD_BITS) for value in self.registers)
        return " ".join(parts)

    def dump_memory(self) -> List[str]:
        return [binary(value, WORD_BITS) for value in self.memory]

    def step(self) -> str:
        if self.halted:
            raise SimulationError("CPU is already halted")
        if self.pc < 0 or self.pc >= MEMORY_SIZE:
            raise SimulationError(f"Program counter out of bounds: {self.pc}")

        trace_pc = self.pc
        word = binary(self.memory[self.pc], WORD_BITS)
        opcode = word[:5]
        spec = OPCODES.get(opcode)
        if spec is None:
            raise SimulationError(f"PC {self.pc}: unknown opcode {opcode}")

        next_pc = self.pc + 1
        if spec.kind == "A":
            rd = int(word[7:10], 2)
            rs1 = int(word[10:13], 2)
            rs2 = int(word[13:16], 2)
            self.execute_a(spec.mnemonic, rd, rs1, rs2)
        elif spec.kind == "B":
            register = int(word[6:9], 2)
            immediate = int(word[9:16], 2)
            self.execute_b(spec.mnemonic, register, immediate)
        elif spec.kind == "B_FLOAT":
            register = int(word[5:8], 2)
            immediate = word[8:16]
            self.clear_flags()
            self.registers[register] = int(immediate, 2)
        elif spec.kind == "C":
            left = int(word[10:13], 2)
            right = int(word[13:16], 2)
            self.execute_c(spec.mnemonic, left, right)
        elif spec.kind == "D":
            register = int(word[6:9], 2)
            address = int(word[9:16], 2)
            self.execute_d(spec.mnemonic, register, address)
        elif spec.kind == "E":
            address = int(word[9:16], 2)
            next_pc = self.execute_e(spec.mnemonic, address, next_pc)
        elif spec.kind == "F":
            self.halted = True
        else:
            raise SimulationError(f"PC {self.pc}: unsupported instruction type {spec.kind}")

        self.pc = next_pc if not self.halted else trace_pc
        return self.current_trace(trace_pc)

    def execute_a(self, mnemonic: str, rd: int, rs1: int, rs2: int) -> None:
        left = self.registers[rs1]
        right = self.registers[rs2]
        if mnemonic == "add":
            self.checked_store(rd, left + right)
        elif mnemonic == "sub":
            self.checked_store(rd, left - right)
        elif mnemonic == "mul":
            self.checked_store(rd, left * right)
        elif mnemonic == "xor":
            self.clear_flags()
            self.registers[rd] = left ^ right
        elif mnemonic == "or":
            self.clear_flags()
            self.registers[rd] = left | right
        elif mnemonic == "and":
            self.clear_flags()
            self.registers[rd] = left & right
        elif mnemonic in {"addf", "subf"}:
            result = decode_float_register(left) + decode_float_register(right)
            if mnemonic == "subf":
                result = decode_float_register(left) - decode_float_register(right)
            try:
                self.registers[rd] = encode_float_register(result)
                self.clear_flags()
            except AssemblyError:
                self.registers[rd] = 0
                self.set_overflow()
        else:
            raise SimulationError(f"Unsupported A instruction {mnemonic}")

    def execute_b(self, mnemonic: str, register: int, immediate: int) -> None:
        value = self.registers[register]
        if mnemonic == "mov":
            self.clear_flags()
            self.registers[register] = immediate
        elif mnemonic == "rs":
            self.clear_flags()
            self.registers[register] = value >> immediate
        elif mnemonic == "ls":
            self.clear_flags()
            self.registers[register] = (value << immediate) & MAX_UNSIGNED_VALUE
        elif mnemonic == "addi":
            self.checked_store(register, value + immediate)
        elif mnemonic == "subi":
            self.checked_store(register, value - immediate)
        elif mnemonic == "muli":
            self.checked_store(register, value * immediate)
        elif mnemonic == "remi":
            if immediate == 0:
                self.registers[register] = 0
                self.set_overflow()
            else:
                self.clear_flags()
                self.registers[register] = value % immediate
        elif mnemonic == "quoi":
            if immediate == 0:
                self.registers[register] = 0
                self.set_overflow()
            else:
                self.clear_flags()
                self.registers[register] = value // immediate
        else:
            raise SimulationError(f"Unsupported B instruction {mnemonic}")

    def execute_c(self, mnemonic: str, left: int, right: int) -> None:
        if mnemonic == "mov":
            self.registers[left] = self.registers[right]
            self.clear_flags()
        elif mnemonic == "div":
            divisor = self.registers[right]
            if divisor == 0:
                self.registers[0] = 0
                self.registers[1] = 0
                self.set_overflow()
            else:
                dividend = self.registers[left]
                self.registers[0] = dividend // divisor
                self.registers[1] = dividend % divisor
                self.clear_flags()
        elif mnemonic == "not":
            self.registers[left] = (~self.registers[right]) & MAX_UNSIGNED_VALUE
            self.clear_flags()
        elif mnemonic == "cmp":
            a = self.registers[left]
            b = self.registers[right]
            if a < b:
                self.flags = FLAG_LESS
            elif a > b:
                self.flags = FLAG_GREATER
            else:
                self.flags = FLAG_EQUAL
        else:
            raise SimulationError(f"Unsupported C instruction {mnemonic}")

    def execute_d(self, mnemonic: str, register: int, address: int) -> None:
        if address < 0 or address >= MEMORY_SIZE:
            raise SimulationError(f"Memory address out of bounds: {address}")
        if mnemonic == "ld":
            self.registers[register] = self.memory[address]
        elif mnemonic == "st":
            self.memory[address] = self.registers[register]
        else:
            raise SimulationError(f"Unsupported D instruction {mnemonic}")
        self.clear_flags()

    def execute_e(self, mnemonic: str, address: int, fallthrough_pc: int) -> int:
        if address < 0 or address >= MEMORY_SIZE:
            raise SimulationError(f"Jump target out of bounds: {address}")
        flags = self.flags
        should_jump = (
            mnemonic == "jmp"
            or (mnemonic == "jlt" and bool(flags & FLAG_LESS))
            or (mnemonic == "jgt" and bool(flags & FLAG_GREATER))
            or (mnemonic == "je" and bool(flags & FLAG_EQUAL))
        )
        self.clear_flags()
        return address if should_jump else fallthrough_pc


def simulate(machine_code: Sequence[str], *, max_steps: int = 10_000) -> Tuple[List[str], List[str]]:
    cpu = CPU.from_machine_code(machine_code)
    traces: List[str] = []
    for _ in range(max_steps):
        trace = cpu.step()
        traces.append(trace)
        if cpu.halted:
            return traces, cpu.dump_memory()
    raise SimulationError(f"Program did not halt within {max_steps} steps")


def assemble_text(source: str) -> str:
    return "\n".join(assemble(source).machine_code)


def simulate_text(machine_text: str, *, max_steps: int = 10_000) -> str:
    code = parse_machine_code(machine_text)
    traces, memory = simulate(code, max_steps=max_steps)
    return "\n".join(traces + memory)


def run_assembler(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble source code from stdin into 16-bit machine code.")
    parser.add_argument("path", nargs="?", help="Assembly source file. Reads stdin when omitted.")
    args = parser.parse_args(argv)
    try:
        source = Path(args.path).read_text(encoding="utf-8") if args.path else sys.stdin.read()
        print(assemble_text(source))
        return 0
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except AssemblyError as exc:
        for error in exc.errors:
            print(f"Error: {error}", file=sys.stderr)
        return 1


def run_simulator(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Simulate 16-bit machine code from stdin.")
    parser.add_argument("path", nargs="?", help="Machine-code file. Reads stdin when omitted.")
    parser.add_argument("--max-steps", type=int, default=10_000, help="Stop non-halting programs after this many steps.")
    args = parser.parse_args(argv)
    try:
        text = Path(args.path).read_text(encoding="utf-8") if args.path else sys.stdin.read()
        print(simulate_text(text, max_steps=args.max_steps))
        return 0
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except SimulationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run_assembler())
