"""Standardized 3-Night map layouts, terrain collision, ramps, and jump pads."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class JumpPad:
    x: float
    y: float
    z: float
    radius: float
    vy: float
    vh: float
    dir_x: float
    dir_z: float


def _ring_points(
    count: int,
    radius: float,
    start_deg: float,
    step_deg: float,
    center_x: float = 0.0,
    center_z: float = 0.0,
    y: float = 0.0,
) -> list[tuple[float, float, float]]:
    pts: list[tuple[float, float, float]] = []
    for i in range(count):
        ang = math.radians(start_deg + i * step_deg)
        pts.append((center_x + radius * math.cos(ang), y, center_z + radius * math.sin(ang)))
    return pts


def night_lantern_specs(night: int) -> list[tuple[str, float, float, float]]:
    if night == 1:
        return [
            ("L1", 0.0, 0.0, 25.0),
            ("L2", 23.8, 0.0, 7.7),
            ("L3", 14.7, 0.0, -20.2),
            ("L4", -14.7, 0.0, -20.2),
            ("L5", -23.8, 0.0, 7.7),
        ]
    if night == 2:
        return [
            ("L1", 0.0, 0.0, 20.0),
            ("L2", 17.0, 0.0, -10.0),
            ("L3", -17.0, 0.0, -10.0),
            ("L4", 70.0, 0.0, 20.0),
            ("L5", 87.0, 0.0, -10.0),
            ("L6", 53.0, 0.0, -10.0),
        ]
    return [
        ("L1", 0.0, 6.0, 6.0),
        ("L2", 18.0, 3.0, 10.0),
        ("L3", -18.0, 3.0, 10.0),
        ("L4", 35.0, 0.0, -10.0),
        ("L5", -35.0, 0.0, -10.0),
        ("L6", 20.0, 0.0, -35.0),
        ("L7", -20.0, 0.0, -35.0),
    ]


def night_mote_spawn_points(night: int) -> list[tuple[float, float, float]]:
    if night == 1:
        return _ring_points(8, 12.0, 0.0, 45.0) + _ring_points(16, 33.0, 0.0, 22.5)
    if night == 2:
        pts: list[tuple[float, float, float]] = []
        for cx in (0.0, 70.0):
            pts.extend(_ring_points(4, 10.0, 0.0, 90.0, center_x=cx))
            pts.extend(_ring_points(8, 22.0, 0.0, 45.0, center_x=cx))
        return pts
    pts3: list[tuple[float, float, float]] = []
    pts3.extend(_ring_points(18, 34.0, 0.0, 20.0, y=0.0))
    pts3.extend(_ring_points(8, 18.0, 20.0, 20.0, y=3.0))
    pts3.extend(_ring_points(4, 5.0, 45.0, 90.0, y=6.0))
    return pts3


def night_shade_spawn_points(night: int) -> list[tuple[float, float, float]]:
    if night == 1:
        return _ring_points(12, 37.0, 15.0, 30.0)
    if night == 2:
        pts: list[tuple[float, float, float]] = []
        for cx in (0.0, 70.0):
            pts.extend(_ring_points(8, 26.0, 22.5, 45.0, center_x=cx))
        return pts
    return _ring_points(16, 43.0, 0.0, 22.5, y=0.0)


def night_charm_specs(night: int) -> list[tuple[str, float, float, float]]:
    if night == 2:
        return [("C1", 35.0, 0.0, 0.0)]
    if night == 3:
        return [("C1", 30.0, 0.0, 25.0), ("C2", -30.0, 0.0, 25.0)]
    return []


def night_jump_pads(night: int) -> list[JumpPad]:
    if night == 2:
        # Pad A (20,0,18) -> target (70,0,0)
        dx1, dz1 = 70.0 - 20.0, 0.0 - 18.0
        d1 = math.hypot(dx1, dz1)
        # Pad B (50,0,-18) -> target (0,0,0)
        dx2, dz2 = 0.0 - 50.0, 0.0 - (-18.0)
        d2 = math.hypot(dx2, dz2)
        return [
            JumpPad(20.0, 0.0, 18.0, 1.0, 14.0, 24.0, dx1 / d1, dz1 / d1),
            JumpPad(50.0, 0.0, -18.0, 1.0, 14.0, 24.0, dx2 / d2, dz2 / d2),
        ]
    if night == 3:
        return [JumpPad(0.0, 3.0, 13.0, 1.0, 12.0, 8.0, 0.0, -1.0)]
    return []


def night_shade_schedule(night: int) -> tuple[int, int]:
    """Return (spawn_interval_ticks, max_shades)."""
    if night == 1:
        return (480, 6)
    if night == 2:
        return (420, 8)
    return (360, 10)


def _night3_ramp_height(x: float, z: float) -> float | None:
    for deg in (30.0, 150.0):
        ang = math.radians(deg)
        ux, uz = math.cos(ang), math.sin(ang)
        proj = x * ux + z * uz
        perp = abs(-x * uz + z * ux)
        if 24.0 <= proj <= 30.0 and perp <= 1.5:
            t = (30.0 - proj) / 6.0
            return max(0.0, min(3.0, 3.0 * t))
    return None


def ground_height_at(night: int, x: float, z: float, current_y: float = 0.0) -> float | None:
    """Return walkable ground Y at (x, z) or None if over the cloud sea."""
    if night == 1:
        return 0.0 if math.hypot(x, z) <= 40.0 else None

    if night == 2:
        if math.hypot(x, z) <= 28.0:
            return 0.0
        if math.hypot(x - 70.0, z) <= 28.0:
            return 0.0
        if 26.0 <= x <= 44.0 and -2.0 <= z <= 2.0:
            return 0.0
        return None

    # Night 3 — Đảo Chuông
    r = math.hypot(x, z)
    if r > 45.0:
        return None

    candidates = [0.0]
    if 12.0 <= r <= 24.0 and z > 0.0:
        candidates.append(3.0)
    if r <= 8.0:
        candidates.append(6.0)
    ramp_h = _night3_ramp_height(x, z)
    if ramp_h is not None:
        candidates.append(ramp_h)

    reachable = [h for h in candidates if h <= current_y + 0.45]
    return max(reachable) if reachable else 0.0


def resolve_obstacle_xz(
    night: int, old_x: float, old_z: float, new_x: float, new_z: float, y: float
) -> tuple[float, float]:
    """Clamp horizontal move against Night 3 bell tower and vertical cliff walls."""
    if night != 3:
        return new_x, new_z

    # Bell tower at (0, 6, 0) with radius 2.0m, height 8.0m
    if 5.5 <= y <= 14.5:
        r_tower = math.hypot(new_x, new_z)
        if r_tower < 2.0:
            if r_tower > 1e-9:
                new_x = (new_x / r_tower) * 2.0
                new_z = (new_z / r_tower) * 2.0
            else:
                new_x, new_z = 2.0, 0.0

    # Vertical tier ledges block walking UP without ramp/jump-pad
    r_new = math.hypot(new_x, new_z)
    ramp_h = _night3_ramp_height(new_x, new_z)
    if y < 2.65 and 12.0 <= r_new <= 24.0 and new_z > 0.0 and ramp_h is None:
        # Check if we were already outside Tier 1 or at Tier 0
        r_old = math.hypot(old_x, old_z)
        if not (12.0 <= r_old <= 24.0 and old_z > 0.0):
            return old_x, old_z
    if y < 5.65 and r_new <= 8.0:
        r_old = math.hypot(old_x, old_z)
        if r_old > 8.0:
            return old_x, old_z

    return new_x, new_z
