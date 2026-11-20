"""Single-command verification runner for unit tests and headless determinism."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


GAME_ROOT = Path(__file__).resolve().parent.parent


def run_step(label: str, cmd: list[str]) -> str:
    print(f"==> {label}: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=GAME_ROOT, capture_output=True, text=True, check=False)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)
    if proc.returncode != 0:
        raise SystemExit(f"FAILED: {label} (exit {proc.returncode})")
    return proc.stdout


def main() -> None:
    py = sys.executable
    run_step("Unit tests", [py, "-m", "unittest", "discover", "-s", "tests", "-v"])

    out1 = run_step("Headless run #1", [py, "-m", "src.headless", "--steps", "90", "--seed", "42"])
    out2 = run_step("Headless run #2", [py, "-m", "src.headless", "--steps", "90", "--seed", "42"])

    if out1 != out2:
        raise SystemExit("FAILED: Determinism check — headless outputs differed!")

    print("==> Determinism check: PASS (byte-identical outputs)")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
