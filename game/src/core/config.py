"""Standardized Ticket-02 / Test Contract v1.1 tuning constants."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


FIXED_DT: float = 1.0 / 60.0
JUMP_VELOCITY: float = 7.0
GRAVITY: float = 20.0

DASH_DURATION_TICKS: int = 12       # 0.2s * 60
DASH_COOLDOWN_TICKS: int = 90       # 1.5s * 60
PULSE_COOLDOWN_TICKS: int = 180     # 3.0s * 60
PULSE_STUN_TICKS: int = 120         # 2.0s * 60
PULSE_PUSH_TICKS: int = 15
INVULN_TICKS: int = 90              # 1.5s * 60
RESPAWN_WAIT_TICKS: int = 60        # 1.0s * 60
SAFE_PUSH_TICKS: int = 30
RECOIL_TICKS: int = 60
RECOIL_DIST_M: float = 2.0

INITIAL_RANDOM_MOTES: int = 20
MAX_ACTIVE_MOTES: int = 30
MOTE_SPAWN_INTERVAL_TICKS: int = 240
DROPPED_MOTE_TTL_TICKS: int = 480

CHARM_DURATION_TICKS: int = 600
CHARM_RESPAWN_TICKS: int = 2700
CHARM_SPEED: float = 7.2

DRIFTER_IDLE_SPEED: float = 2.0
DRIFTER_FAST_SPEED: float = 7.0
DRIFTER_DETECT_RADIUS: float = 15.0
DRIFTER_STEAL_RADIUS: float = 1.2
DRIFTER_STEAL_CAP: int = 3
DRIFTER_MIN_CARRIED: int = 5
DRIFTER_FLEE_TICKS: int = 240
DRIFTER_STUN_FLEE_TICKS: int = 120
DRIFTER_SPAWN_INTERVAL_TICKS: int = 1200
MAX_DRIFTERS: int = 2

SHADE_DETECT_RADIUS: float = 12.0
SHADE_LOSE_RADIUS: float = 18.0
SHADE_FIRST_SPAWN_TICK: int = 300
SHADE_NIGHT3_SPEED: float = 4.5

WIND_INTERVAL_TICKS: int = 1800     # 30s
WIND_DURATION_TICKS: int = 300      # 5s
WIND_WARN_TICKS: int = 120          # 2s
WIND_PUSH_SPEED: float = 2.0


@dataclass(frozen=True)
class ScoreConfig:
    per_mote: int = 0
    per_lantern: int = 100
    per_stun: int = 5
    per_second_left: int = 2
    per_flame_left: int = 50
    per_mote_deposit: int = 10

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
    player_speed: float = 6.0
    dash_speed: float = 14.0
    dash_duration_s: float = 0.2
    dash_cooldown_s: float = 1.5
    carry_capacity: int = 10
    lantern_cost: int = 10
    lantern_count_night1: int = 5
    pickup_radius: float = 1.0
    interact_radius: float = 2.0
    pulse_cost: int = 3
    pulse_radius: float = 5.0
    night1_duration_s: float = 300.0
    night2_duration_s: float = 330.0
    night3_duration_s: float = 360.0
    flames: int = 3
    invuln_s: float = 1.5
    hit_drop_ratio: float = 0.5
    pulse_stun_s: float = 2.0
    pulse_push_m: float = 4.0
    pulse_cooldown_s: float = 3.0
    safe_radius: float = 6.0
    shade_speed: float = 4.0
    shade_hit_radius: float = 1.0
    fall_enabled: bool = True
    score: ScoreConfig = field(default_factory=ScoreConfig)

    def duration_for_night(self, night: int) -> float:
        if night == 1:
            return self.night1_duration_s
        if night == 2:
            return self.night2_duration_s
        return self.night3_duration_s

    def to_dict(self) -> dict[str, Any]:
        return {
            "player_speed": self.player_speed,
            "dash_speed": self.dash_speed,
            "dash_duration_s": self.dash_duration_s,
            "dash_cooldown_s": self.dash_cooldown_s,
            "carry_capacity": self.carry_capacity,
            "lantern_cost": self.lantern_cost,
            "lantern_count_night1": self.lantern_count_night1,
            "pickup_radius": self.pickup_radius,
            "interact_radius": self.interact_radius,
            "pulse_cost": self.pulse_cost,
            "pulse_radius": self.pulse_radius,
            "night1_duration_s": self.night1_duration_s,
            "night2_duration_s": self.night2_duration_s,
            "night3_duration_s": self.night3_duration_s,
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
