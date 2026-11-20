"""Central tuning and configuration constants synced with root game.contract.json."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


FIXED_DT: float = 1.0 / 60.0
DEFAULT_ISLAND_RADIUS: float = 42.0
JUMP_VELOCITY: float = 7.5
GRAVITY: float = 20.0

DEFAULT_INITIAL_MOTES: int = 15
MOTE_RESPAWN_INTERVAL_TICKS: int = 360  # 6s at 60Hz
DEFAULT_INITIAL_SHADES: int = 2
MAX_RANDOM_SHADES: int = 5
SHADE_SPAWN_INTERVAL_TICKS: int = 1800  # 30s at 60Hz


@dataclass(frozen=True)
class ScoreConfig:
    per_mote: int = 10
    per_lantern: int = 100
    per_stun: int = 25
    per_second_left: int = 5
    per_flame_left: int = 50

    def to_dict(self) -> dict[str, int]:
        return {
            "per_mote": self.per_mote,
            "per_lantern": self.per_lantern,
            "per_stun": self.per_stun,
            "per_second_left": self.per_second_left,
            "per_flame_left": self.per_flame_left,
        }


@dataclass(frozen=True)
class TuningConfig:
    player_speed: float = 7.0
    carry_capacity: int = 5
    lantern_cost: int = 3
    lantern_count_night1: int = 5
    pickup_radius: float = 1.8
    interact_radius: float = 2.5
    pulse_cost: int = 1
    pulse_radius: float = 6.0
    night1_duration_s: float = 240.0
    flames: int = 3
    invuln_s: float = 1.5
    hit_drop_ratio: float = 0.5
    pulse_stun_s: float = 3.0
    pulse_push_m: float = 5.0
    pulse_cooldown_s: float = 3.0
    safe_radius: float = 5.0
    shade_speed: float = 4.2
    shade_hit_radius: float = 1.2
    fall_enabled: bool = False
    score: ScoreConfig = field(default_factory=ScoreConfig)

    def to_dict(self) -> dict[str, Any]:
        return {
            "player_speed": self.player_speed,
            "carry_capacity": self.carry_capacity,
            "lantern_cost": self.lantern_cost,
            "lantern_count_night1": self.lantern_count_night1,
            "pickup_radius": self.pickup_radius,
            "interact_radius": self.interact_radius,
            "pulse_cost": self.pulse_cost,
            "pulse_radius": self.pulse_radius,
            "night1_duration_s": self.night1_duration_s,
            "flames": self.flames,
            "invuln_s": self.invuln_s,
            "hit_drop_ratio": self.hit_drop_ratio,
            "pulse_stun_s": self.pulse_stun_s,
            "pulse_push_m": self.pulse_push_m,
            "pulse_cooldown_s": self.pulse_cooldown_s,
            "safe_radius": self.safe_radius,
            "shade_speed": self.shade_speed,
            "shade_hit_radius": self.shade_hit_radius,
            "fall_enabled": self.fall_enabled,
            "score": self.score.to_dict(),
        }


TUNING = TuningConfig()
