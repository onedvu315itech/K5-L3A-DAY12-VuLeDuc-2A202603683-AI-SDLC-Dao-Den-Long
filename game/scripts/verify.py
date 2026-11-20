"""Single-command verification runner for unit tests, Test Contract v1.0 CLI, and determinism."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile


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
    run_step("Unit & contract tests", [py, "-m", "unittest", "discover", "-s", "tests", "-v"])

    scenario_file = str(GAME_ROOT / "tests" / "scenarios" / "win_scenario.json")
    inputs_file = str(GAME_ROOT / "tests" / "scenarios" / "win_inputs.json")

    with tempfile.TemporaryDirectory() as tmp:
        out1_path = Path(tmp) / "run1.jsonl"
        out2_path = Path(tmp) / "run2.jsonl"

        base_cmd = [
            py,
            str(GAME_ROOT / "src" / "headless.py"),
            "--seed",
            "42",
            "--night",
            "1",
            "--scenario",
            scenario_file,
            "--inputs",
            inputs_file,
            "--ticks",
            "200",
            "--snapshot-every",
            "25",
        ]
        run_step("Headless contract run #1", [*base_cmd, "--out", str(out1_path)])
        run_step("Headless contract run #2", [*base_cmd, "--out", str(out2_path)])

        out1 = out1_path.read_text(encoding="utf-8")
        out2 = out2_path.read_text(encoding="utf-8")

    print("==> Headless JSONL output (win_scenario):")
    print(out1.strip())

    if out1 != out2:
        raise SystemExit("FAILED: Determinism check — headless JSONL outputs differed!")

    print("==> Determinism check: PASS (byte-identical JSONL outputs)")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
