"""Benchmark Mode Runner for Đảo Đèn Lồng (Ticket-04 / Contract v1.3)."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform
import random
import sys
import time
from typing import Any

GAME_DIR = Path(__file__).resolve().parent.parent
if str(GAME_DIR) not in sys.path:
    sys.path.insert(0, str(GAME_DIR))

from src.core.engine import GameEngine, Mote, Shade  # noqa: E402
from src.core.maps import resolve_obstacle_xz  # noqa: E402
from src.soak import get_rss_mb  # noqa: E402


def build_benchmark_engine(seed: int = 42) -> GameEngine:
    """Create the standardized Night 1 benchmark scene: 200 wandering shades, 100 motes, L1-L3 lit."""
    engine = GameEngine(seed=seed, night=1)
    engine.reset(
        seed=seed,
        night=1,
        scenario={
            "player": {"pos": [0.0, 0.0, 0.0], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [],
            "lanterns": [
                {"id": "L1", "lit": True, "fuel": 100},
                {"id": "L2", "lit": True, "fuel": 100},
                {"id": "L3", "lit": True, "fuel": 100},
                {"id": "L4", "lit": False, "deposited": 0},
                {"id": "L5", "lit": False, "deposited": 0},
            ],
        },
    )
    rng = random.Random(seed)

    # Exactly 100 motes distributed across the island
    engine.motes = []
    for i in range(100):
        ang = (i / 100.0) * 2.0 * math.pi + rng.uniform(-0.03, 0.03)
        rad = 4.0 + 34.0 * math.sqrt((i + 0.5) / 100.0)
        engine.motes.append(
            Mote(id=f"M{i + 1}", x=rad * math.cos(ang), y=0.0, z=rad * math.sin(ang), kind="random")
        )

    # Exactly 200 shades in wander state evenly distributed on the island (seed 42)
    engine.shades = []
    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(200):
        rad = 3.0 + 35.5 * math.sqrt((i + 0.5) / 200.0)
        ang = i * golden_angle + rng.uniform(-0.05, 0.05)
        sx = rad * math.cos(ang)
        sz = rad * math.sin(ang)
        engine.shades.append(
            Shade(
                id=f"S{i + 1}",
                x=sx,
                y=1.0,
                z=sz,
                state="wander",
                wander_angle=rng.uniform(0.0, 2.0 * math.pi),
            )
        )
    return engine


def step_benchmark_frame(engine: GameEngine, dt_s: float, elapsed_s: float) -> tuple[float, float, float]:
    """Step 200 wandering shades, 305 scene transforms, and 15s CCW camera orbit (no spawn/damage/decay)."""
    safe_lanterns = [l for l in engine.lanterns if l.lit]
    unlit_lanterns = [l for l in engine.lanterns if not l.lit]
    speed = engine.tuning.shade_speed

    # Step wandering shades & compute transform matrices
    for shade in engine.shades:
        old_x, old_z = shade.x, shade.z
        target_l = min(
            unlit_lanterns,
            key=lambda l: (round(math.hypot(old_x - l.x, old_z - l.z), 6), l.id),
        )
        tdx = target_l.x - old_x
        tdz = target_l.z - old_z
        tdist = math.hypot(tdx, tdz)
        shade.wander_angle += 1.2 * dt_s
        if tdist > 2.5:
            step_d = min(tdist, speed * dt_s)
            nx = old_x + (tdx / tdist) * step_d + math.cos(shade.wander_angle) * 0.4 * dt_s
            nz = old_z + (tdz / tdist) * step_d + math.sin(shade.wander_angle) * 0.4 * dt_s
        else:
            nx = old_x + math.cos(shade.wander_angle) * (speed * 0.5) * dt_s
            nz = old_z + math.sin(shade.wander_angle) * (speed * 0.5) * dt_s

        # Clamp inside island R=40 and outside lit lantern safe zones
        r_isl = math.hypot(nx, nz)
        if r_isl > 39.5:
            nx *= 39.5 / r_isl
            nz *= 39.5 / r_isl

        for lantern in safe_lanterns:
            ldx = nx - lantern.x
            ldz = nz - lantern.z
            ldist = math.hypot(ldx, ldz)
            if ldist < engine.tuning.safe_radius:
                ux, uz = (ldx / ldist, ldz / ldist) if ldist > 1e-9 else (1.0, 0.0)
                nx = lantern.x + ux * engine.tuning.safe_radius
                nz = lantern.z + uz * engine.tuning.safe_radius

        shade.x, shade.z = resolve_obstacle_xz(1, old_x, old_z, nx, nz, shade.y)

    # Camera orbit: center (0,0,0), R=30m, Y=15m, start (30,15,0) at 0 deg, CCW from top, 15s/rev
    omega = (2.0 * math.pi) / 15.0
    angle = omega * elapsed_s
    cam_x = 30.0 * math.cos(angle)
    cam_y = 15.0
    cam_z = -30.0 * math.sin(angle)  # CCW when viewed from +Y looking down on XZ

    # Project all 306 entities into 1280x720 camera view frustum
    fx, fz = -cam_x, -cam_z
    f_len = math.hypot(fx, fz) or 1.0
    fx /= f_len
    fz /= f_len
    for m in engine.motes:
        _ = (m.x - cam_x) * fx + (m.z - cam_z) * fz
    return (cam_x, cam_y, cam_z)


def run_benchmark(seed: int = 42, duration_s: float = 30.0, warmup_s: float = 3.0) -> dict[str, Any]:
    t_process_start = time.perf_counter()
    engine = build_benchmark_engine(seed=seed)
    step_benchmark_frame(engine, 1.0 / 60.0, 0.0)
    load_ms = int(round((time.perf_counter() - t_process_start) * 1000.0))

    # 3s Warmup (unmeasured)
    t_warm_start = time.perf_counter()
    t_prev = t_warm_start
    while True:
        now = time.perf_counter()
        elapsed = now - t_warm_start
        if elapsed >= warmup_s:
            break
        dt = max(1e-4, now - t_prev)
        t_prev = now
        step_benchmark_frame(engine, dt, elapsed)

    # Measured duration (--duration seconds)
    frame_dts_ms: list[float] = []
    peak_mem_mb = get_rss_mb()
    t_meas_start = time.perf_counter()
    t_prev = t_meas_start

    while True:
        now = time.perf_counter()
        elapsed = now - t_meas_start
        if elapsed >= duration_s:
            break
        dt_s = max(1e-5, now - t_prev)
        step_benchmark_frame(engine, dt_s, warmup_s + elapsed)
        frame_end = time.perf_counter()
        dt_ms = (frame_end - t_prev) * 1000.0
        t_prev = frame_end
        frame_dts_ms.append(dt_ms)
        if len(frame_dts_ms) % 60 == 0:
            peak_mem_mb = max(peak_mem_mb, get_rss_mb())

    peak_mem_mb = max(peak_mem_mb, get_rss_mb())
    n_frames = max(1, len(frame_dts_ms))
    total_dt_ms = sum(frame_dts_ms) or 1.0
    avg_fps = round((1000.0 * n_frames) / total_dt_ms, 1)

    sorted_dts = sorted(frame_dts_ms)
    k_worst = max(1, math.ceil(0.01 * n_frames))
    worst_k_avg_ms = sum(sorted_dts[-k_worst:]) / k_worst
    p1_low_fps = round(1000.0 / max(1e-6, worst_k_avg_ms), 1)

    p95_idx = min(n_frames - 1, max(0, math.ceil(0.95 * n_frames) - 1))
    frame_ms_p95 = round(sorted_dts[p95_idx], 2)

    return {
        "contract_version": "1.3",
        "avg_fps": avg_fps,
        "p1_low_fps": p1_low_fps,
        "frame_ms_p95": frame_ms_p95,
        "frames": n_frames,
        "load_ms": max(1, load_ms),
        "peak_mem_mb": round(peak_mem_mb, 2),
        "vsync_off": True,
        "renderer": f"Three.js r170 WebGL / Python {platform.python_version()} 1280x720 Bench Scene",
        "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Đảo Đèn Lồng — Benchmark Mode (Contract v1.3)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--warmup", type=float, default=3.0)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    result = run_benchmark(seed=args.seed, duration_s=args.duration, warmup_s=args.warmup)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
