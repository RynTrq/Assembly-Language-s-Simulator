# Assembly Language Simulator

A small, dependency-free Python assembler and simulator for a teaching 16-bit instruction set.  The project accepts assembly source, emits 16-bit machine code, and can execute that machine code while printing the register trace and final memory image.

The repository used to contain three large scripts with duplicated logic and interactive prompts.  It now has one tested core module plus compatibility wrappers, so the old commands still work while the implementation is maintainable.

## Quick Start

| Task | Command |
| --- | --- |
| Assemble from a file | `python3 Assembler.py program.asm > program.mc` |
| Assemble from stdin | `python3 Assembler.py < program.asm` |
| Simulate from a file | `python3 Final_Simulator.py program.mc` |
| Run tests | `python3 -m unittest discover -s tests -v` |

Example assembly program:

```asm
var result
mov R1 $5
mov R2 $7
add R3 R1 R2
st R3 result
hlt
```

Assemble it:

```bash
python3 Assembler.py program.asm > program.mc
```

The machine code will look like this:

```text
0001000010000101
0001000100000111
0000000011001010
0010100110000101
1101000000000000
```

Simulate it:

```bash
python3 Final_Simulator.py program.mc
```

The simulator prints one trace line per executed instruction followed by the complete 128-word memory dump.  Each trace line is:

```text
PC R0 R1 R2 R3 R4 R5 R6 FLAGS
```

## Project Layout

| Path | Purpose |
| --- | --- |
| `asm_simulator.py` | Production implementation of parsing, assembling, CPU execution, and CLI helpers. |
| `Assembler.py` | Compatibility wrapper for the assembler CLI. |
| `Final_Simulator.py` | Compatibility wrapper for the simulator CLI. |
| `Pre_Simulator.py` | Compatibility wrapper for the simulator CLI. |
| `tests/test_asm_simulator.py` | Unit tests for critical assembler and simulator behavior. |
| `*.png`, `x86_assembler_simulator_readme.pdf` | Original project reference artifacts. |

## Architecture

```mermaid
flowchart LR
  A["Assembly source"] --> B["parse_source"]
  B --> C["validate_symbols"]
  C --> D["assemble_instruction"]
  D --> E["16-bit machine code"]
  E --> F["parse_machine_code"]
  F --> G["CPU.from_machine_code"]
  G --> H["CPU.step loop"]
  H --> I["Trace + memory dump"]
```

The core module is intentionally side-effect free when imported.  `assemble()` returns a `Program` object, and `simulate()` returns trace and memory lists.  The command-line wrappers only handle file/stdin IO and error reporting.

## Instruction Set

The machine has 128 memory words, 7 general-purpose registers (`R0` through `R6`), and one `FLAGS` register.  Each word and register is 16 bits.

| Type | Format | Instructions |
| --- | --- | --- |
| A | `opcode(5) 00 rd rs1 rs2` | `add`, `sub`, `mul`, `xor`, `or`, `and`, `addf`, `subf` |
| B | `opcode(5) 0 reg imm7` | `mov`, `rs`, `ls`, `addi`, `subi`, `muli`, `remi`, `quoi` |
| B float | `opcode(5) reg imm8` | `movf` |
| C | `opcode(5) 00000 reg1 reg2` | `mov`, `div`, `not`, `cmp` |
| D | `opcode(5) 0 reg addr7` | `ld`, `st` |
| E | `opcode(5) 0000 addr7` | `jmp`, `jlt`, `jgt`, `je` |
| F | `opcode(5) 00000000000` | `hlt` |

### Opcode Table

| Instruction | Opcode | Notes |
| --- | --- | --- |
| `add` | `00000` | Integer addition. |
| `sub` | `00001` | Integer subtraction. |
| `mov reg imm` | `00010` | Immediate move. |
| `mov reg reg` | `00011` | Register move. |
| `ld` | `00100` | Load from memory. |
| `st` | `00101` | Store to memory. |
| `mul` | `00110` | Integer multiplication. |
| `div` | `00111` | Quotient in `R0`, remainder in `R1`. |
| `rs` | `01000` | Logical right shift. |
| `ls` | `01001` | Logical left shift. |
| `xor` | `01010` | Bitwise XOR. |
| `or` | `01011` | Bitwise OR. |
| `and` | `01100` | Bitwise AND. |
| `not` | `01101` | Bitwise NOT. |
| `cmp` | `01110` | Sets comparison flags. |
| `jmp` | `01111` | Unconditional jump. |
| `addf` | `10000` | 8-bit teaching-float addition. |
| `subf` | `10001` | 8-bit teaching-float subtraction. |
| `movf` | `10010` | Move 8-bit teaching-float immediate. |
| `addi` | `10011` | Add immediate. |
| `subi` | `10100` | Subtract immediate. |
| `muli` | `10101` | Multiply immediate. |
| `remi` | `10110` | Remainder by immediate. |
| `quoi` | `10111` | Quotient by immediate. |
| `hlt` | `11010` | Halt. |
| `jlt` | `11100` | Jump when less-than flag is set. |
| `jgt` | `11101` | Jump when greater-than flag is set. |
| `je` | `11111` | Jump when equal flag is set. |

## Assembly Syntax

Comments start with `#`.  Commas are optional because the parser treats them as whitespace.

```asm
# Variables must be declared before executable instructions.
var counter

start: mov R1 $10
subi R1 $1
st R1 counter
cmp R1 R0
jgt start
hlt
```

Rules enforced by the assembler:

| Rule | Why |
| --- | --- |
| Program must contain exactly one `hlt`. | Prevents ambiguous or non-terminating source. |
| No instructions may appear after `hlt`. | Keeps emitted programs deterministic. |
| Variables must appear before instructions. | Makes memory layout predictable. |
| Labels must be unique and followed by an instruction. | Avoids unresolved jump targets. |
| Integer immediates must fit in 7 bits (`0..127`). | Matches the ISA format. |
| Machine code must fit in 128 memory words. | Matches simulator memory size. |

## Floating Values

`movf`, `addf`, and `subf` use an 8-bit teaching float:

```text
exponent(3 bits) mantissa(5 bits)
value = (1 + mantissa / 32) * 2^exponent
```

Zero is encoded as `00000000`.  Values must be non-negative and exactly representable in this format.

## Error Handling

Assembler errors are printed to stderr and return exit code `1`:

```bash
$ python3 Assembler.py bad.asm
Error: Line 2: invalid register 'R8'
Error: Program is missing hlt
```

Simulator errors are also printed to stderr and return exit code `1`, including malformed machine code, missing `hlt`, unknown opcodes, and non-halting execution when `--max-steps` is reached.

## Developer Workflow

No third-party packages are required.

```bash
python3 --version
python3 -m unittest discover -s tests -v
python3 Assembler.py --help
python3 Final_Simulator.py --help
```

For a quick end-to-end check:

```bash
cat > /tmp/example.asm <<'ASM'
var result
mov R1 $5
mov R2 $7
add R3 R1 R2
st R3 result
hlt
ASM

python3 Assembler.py /tmp/example.asm > /tmp/example.mc
python3 Final_Simulator.py /tmp/example.mc
```

## Implementation Notes

The central `CPU.step()` method decodes the current 16-bit word, executes exactly one instruction, updates flags, and returns the trace line for that cycle.  `simulate()` repeatedly calls `step()` until `hlt` or until the configurable step limit is reached.

The assembler is split into clear phases:

| Phase | Function | Responsibility |
| --- | --- | --- |
| Lexing | `parse_source()` | Remove comments, normalize commas, keep source line numbers. |
| Symbol pass | `validate_symbols()` | Resolve labels and variables, enforce global program rules. |
| Encoding | `assemble_instruction()` | Validate operands and emit one 16-bit instruction. |
| CLI | `run_assembler()` | Read files/stdin and print machine code or errors. |

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `Program is missing hlt` | Add one `hlt` as the final instruction. |
| `variables must be declared before instructions` | Move all `var` declarations to the top of the file. |
| `undefined label` | Check spelling and make sure the label ends with `:` where defined. |
| `machine code must be exactly 16 binary digits` | Feed the simulator assembled machine code, not assembly source. |
| Program stops with `did not halt within ... steps` | The code likely has an infinite loop; raise `--max-steps` only if the loop is intentional and eventually halts. |

## Compatibility

The old filenames are preserved:

```bash
python3 Assembler.py
python3 Final_Simulator.py
python3 Pre_Simulator.py
```

Unlike the original scripts, these commands do not print interactive prompts.  They read from a file argument or stdin, which makes them usable in tests, scripts, and shell pipelines.
