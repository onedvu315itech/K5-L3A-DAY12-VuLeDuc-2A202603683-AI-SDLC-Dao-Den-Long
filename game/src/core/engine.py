"""Pure deterministic 3D simulation core (CP0 Hello starter)."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any


FIXED_DT = 1.0 / 60.0
PLAYER_SPEED = 4.0
ISLAND_RADIUS = 14.0
LANTERN_TRIGGER_RADIUS = 1.6


@dataclass(frozen=True)
class StepInput:
    """Normalized movement input for a single simulation tick."""

    move_x: float = 0.0
    move_z: float = 0.0


@dataclass
class Lantern:
    id: str
    x: float
    y: float
    z: float
    lit: bool = False


@dataclass
class Player:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0


@dataclass
class GameEngine:
    """Deterministic simulation engine shared by headless CLI and 3D renderer."""

    seed: int = 42
    dt: float = FIXED_DT
    tick: int = 0
    player: Player = field(default_factory=Player)
    lanterns: list[Lantern] = field(
        default_factory=lambda: [Lantern(id="lantern-hello", x=0.0, y=0.0, z=-6.0)]
    )

    def reset(self, seed: int | None = None) -> dict[str, Any]:
        """Reset simulation state deterministically."""
        if seed is not None:
            self.seed = seed
        self.tick = 0
        self.player = Player()
        self.lanterns = [Lantern(id="lantern-hello", x=0.0, y=0.0, z=-6.0)]
        return self.snapshot()

    def step(self, action: StepInput) -> dict[str, Any]:
        """Advance simulation by one fixed timestep."""
        dx = float(action.move_x)
        dz = float(action.move_z)
        mag = math.hypot(dx, dz)
        if mag > 1.0:
            dx /= mag
            dz /= mag

        if mag > 1e-6:
            self.player.x += dx * PLAYER_SPEED * self.dt
            self.player.z += dz * PLAYER_SPEED * self.dt
            self.player.yaw = math.atan2(dx, dz)

        dist_origin = math.hypot(self.player.x, self.player.z)
        if dist_origin > ISLAND_RADIUS:
            scale = ISLAND_RADIUS / dist_origin
            self.player.x *= scale
            self.player.z *= scale

        for lantern in self.lanterns:
            if not lantern.lit:
                dist = math.hypot(self.player.x - lantern.x, self.player.z - lantern.z)
                if dist <= LANTERN_TRIGGER_RADIUS:
                    lantern.lit = True

        self.tick += 1
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        """Return rounded JSON-safe snapshot for deterministic verification and rendering."""
        return {
            "seed": self.seed,
            "tick": self.tick,
            "time": round(self.tick * self.dt, 4),
            "player": {
                "x": round(self.player.x, 4),
                "y": round(self.player.y, 4),
                "z": round(self.player.z, 4),
                "yaw": round(self.player.yaw, 4),
            },
            "lanterns": [
                {
                    "id": l.id,
                    "x": round(l.x, 4),
                    "y": round(l.y, 4),
                    "z": round(l.z, 4),
                    "lit": l.lit,
                }
                for l in self.lanterns
            ],
        }
