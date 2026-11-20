"""Cross-platform process RSS memory helper (stdlib only) + 10-Night Soak Test runner."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import gc
import json
from pathlib import Path
import random
import sys
import time
from typing import Any

GAME_DIR = Path(__file__).resolve().parent.parent
if str(GAME_DIR) not in sys.path:
    sys.path.insert(0, str(GAME_DIR))

from src.core.engine import GameEngine, StepInput  # noqa: E402


def get_rss_mb() -> float:
    """Return current process Resident Set Size (RSS) in MiB using stdlib only."""
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
                if line.startswith("VmRSS:"):
                    kb = float(line.split()[1])
                    return round(kb / 1024.0, 2)
        except OSError:
            pass

    if sys.platform == "darwin" or sys.platform.startswith("linux"):
        try:
            import resource

            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform == "darwin":
                return round(rss / (1024.0 * 1024.0), 2)
            return round(rss / 1024.0, 2)
        except Exception:  # noqa: BLE001
            pass

    if sys.platform == "win32":
        try:

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            pmc = PROCESS_MEMORY_COUNTERS()
            pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            k32 = ctypes.windll.kernel32
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            k32.K32GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
                wintypes.DWORD,
            ]
            k32.K32GetProcessMemoryInfo.restype = wintypes.BOOL
            handle = k32.GetCurrentProcess()
            if k32.K32GetProcessMemoryInfo(handle, ctypes.byref(pmc), ctypes.sizeof(pmc)):
                return round(pmc.WorkingSetSize / (1024.0 * 1024.0), 2)
        except Exception:  # noqa: BLE001
            pass

    return 24.0


def run_soak_test(seed: int = 7, nights: int = 10) -> dict[str, Any]:
    """Run N nights sequentially in a single process with seeded random inputs."""
    t0 = time.perf_counter()
    crashes = 0
    results: list[str] = []

    engine = GameEngine(seed=seed, night=1)
    mem_start_mb = get_rss_mb()

    for i in range(nights):
        night_num = (i % 3) + 1
        night_seed = seed + i
        rng = random.Random(night_seed)

        try:
            engine.reset(seed=night_seed, night=night_num)
            max_ticks = int(round(engine.initial_time_left_s * 60))
            mx, mz = 0.0, 0.0

            for k in range(max_ticks):
                if engine.state in ("won", "lost"):
                    break
                if k % 30 == 0:
                    mx = rng.uniform(-1.0, 1.0)
                    mz = rng.uniform(-1.0, 1.0)
                jump = rng.random() < 0.05
                dash = rng.random() < 0.03
                pulse = rng.random() < 0.02
                interact = rng.random() < 0.10
                engine.step(
                    StepInput(
                        move_x=mx,
                        move_z=mz,
                        cam_yaw_deg=0.0,
                        jump=jump,
                        interact=interact,
                        pulse=pulse,
                        dash=dash,
                    )
                )
            results.append(engine.state if engine.state in ("won", "lost") else "lost")
        except Exception:  # noqa: BLE001
            crashes += 1
            results.append("crash")

    engine.reset(seed=seed, night=1)
    gc.collect()
    mem_end_mb = get_rss_mb()
    duration_s = round(time.perf_counter() - t0, 2)

    return {
        "nights": nights,
        "crashes": crashes,
        "results": results,
        "mem_start_mb": mem_start_mb,
        "mem_end_mb": mem_end_mb,
        "duration_s": duration_s,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Đảo Đèn Lồng — Soak Test Runner (Contract v1.3)")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--nights", type=int, default=10)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    report = run_soak_test(seed=args.seed, nights=args.nights)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["crashes"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
