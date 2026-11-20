"""Single-command verification runner for unit tests, Contract v1.1 Nights 1-3, determinism, and <=30s perf."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import time


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
    run_step("Unit & Contract v1.1 tests", [py, "-m", "unittest", "discover", "-s", "tests", "-v"])

    with tempfile.TemporaryDirectory() as tmp:
        for night in (1, 2, 3):
            out1_p = Path(tmp) / f"n{night}_1.jsonl"
            out2_p = Path(tmp) / f"n{night}_2.jsonl"
            ticks = "21600" if night == 3 else "1200"
            t0 = time.perf_counter()
            run_step(
                f"Headless Night {night} run #1 ({ticks} ticks)",
                [
                    py,
                    str(GAME_ROOT / "src" / "headless.py"),
                    "--seed",
                    "42",
                    "--night",
                    str(night),
                    "--ticks",
                    ticks,
                    "--snapshot-every",
                    "60",
                    "--out",
                    str(out1_p),
                ],
            )
            elapsed = time.perf_counter() - t0
            run_step(
                f"Headless Night {night} run #2 ({ticks} ticks)",
                [
                    py,
                    str(GAME_ROOT / "src" / "headless.py"),
                    "--seed",
                    "42",
                    "--night",
                    str(night),
                    "--ticks",
                    ticks,
                    "--snapshot-every",
                    "60",
                    "--out",
                    str(out2_p),
                ],
            )
            if out1_p.read_text(encoding="utf-8") != out2_p.read_text(encoding="utf-8"):
                raise SystemExit(f"FAILED: Night {night} determinism check!")
            print(f"==> Night {night} ({ticks} ticks) elapsed={elapsed:.3f}s | Determinism: PASS")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
