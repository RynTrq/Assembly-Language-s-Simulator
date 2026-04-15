"""Compatibility entry point for the simulator CLI.

Historically this file contained an intermediate simulator draft.  It now
delegates to the maintained simulator implementation so both legacy commands
behave consistently.
"""

from asm_simulator import run_simulator


if __name__ == "__main__":
    raise SystemExit(run_simulator())
