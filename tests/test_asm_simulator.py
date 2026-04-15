import unittest

from asm_simulator import AssemblyError, assemble, assemble_text, parse_machine_code, simulate, simulate_text


class AssemblerTests(unittest.TestCase):
    def test_encodes_basic_program(self):
        source = """
        mov R1 $5
        mov R2 $7
        add R3 R1 R2
        hlt
        """

        self.assertEqual(
            assemble(source).machine_code,
            [
                "0001000010000101",
                "0001000100000111",
                "0000000011001010",
                "1101000000000000",
            ],
        )

    def test_places_variables_after_instructions(self):
        program = assemble(
            """
            var answer
            mov R1 $42
            st R1 answer
            hlt
            """
        )

        self.assertEqual(program.variables["answer"], 3)
        self.assertEqual(program.machine_code[1], "0010100010000011")

    def test_reports_multiple_source_errors(self):
        with self.assertRaises(AssemblyError) as raised:
            assemble(
                """
                mov R8 $1
                ld R1 missing
                add R1 R2
                """
            )

        message = "\n".join(raised.exception.errors)
        self.assertIn("Program is missing hlt", message)
        self.assertIn("invalid register 'R8'", message)
        self.assertIn("undefined variable 'missing'", message)
        self.assertIn("add expects 3 registers", message)

    def test_rejects_instruction_after_hlt(self):
        with self.assertRaises(AssemblyError) as raised:
            assemble(
                """
                hlt
                mov R1 $1
                """
            )

        self.assertIn("instruction appears after hlt", "\n".join(raised.exception.errors))

    def test_rejects_variable_after_instruction(self):
        with self.assertRaises(AssemblyError) as raised:
            assemble(
                """
                mov R1 $1
                var late
                hlt
                """
            )

        self.assertIn("variables must be declared before instructions", "\n".join(raised.exception.errors))

    def test_encodes_float_immediate(self):
        self.assertEqual(assemble_text("movf R1 $1.5\nhlt\n").splitlines()[0], "1001000100010000")


class SimulatorTests(unittest.TestCase):
    def test_runs_integer_arithmetic(self):
        machine = assemble(
            """
            mov R1 $5
            mov R2 $7
            add R3 R1 R2
            hlt
            """
        ).machine_code

        traces, memory = simulate(machine)

        self.assertEqual([line.split()[0] for line in traces], ["0000000", "0000001", "0000010", "0000011"])
        self.assertEqual(traces[-1].split()[4], "0000000000001100")
        self.assertEqual(memory[:4], machine)

    def test_branching_uses_compare_flags(self):
        machine = assemble(
            """
            mov R1 $3
            mov R2 $9
            cmp R1 R2
            jlt smaller
            mov R3 $99
            smaller: mov R3 $7
            hlt
            """
        ).machine_code

        traces, _ = simulate(machine)

        self.assertEqual(traces[-1].split()[4], "0000000000000111")

    def test_load_and_store_round_trip(self):
        output = simulate_text(
            assemble_text(
                """
                var slot
                mov R1 $42
                st R1 slot
                ld R2 slot
                hlt
                """
            )
        ).splitlines()

        final_trace = output[3]
        memory_dump = output[4:]
        self.assertEqual(final_trace.split()[3], "0000000000101010")
        self.assertEqual(memory_dump[4], "0000000000101010")

    def test_detects_non_halting_program(self):
        machine = assemble(
            """
            loop: jmp loop
            hlt
            """
        ).machine_code

        with self.assertRaisesRegex(Exception, "did not halt"):
            simulate(machine, max_steps=3)

    def test_validates_machine_input(self):
        with self.assertRaisesRegex(Exception, "16 binary digits"):
            parse_machine_code("101\n")


if __name__ == "__main__":
    unittest.main()
