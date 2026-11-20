"""Deterministic 60Hz simulation engine for Đảo Đèn Lồng (Phase 1 / Test Contract v1.0)."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Any

from src.core.config import (
    DEFAULT_INITIAL_MOTES,
    DEFAULT_INITIAL_SHADES,
    DEFAULT_ISLAND_RADIUS,
    FIXED_DT,
    GRAVITY,
    JUMP_VELOCITY,
    MAX_RANDOM_SHADES,
    MOTE_RESPAWN_INTERVAL_TICKS,
    SHADE_SPAWN_INTERVAL_TICKS,
    TUNING,
    TuningConfig,
)


class ContractValidationError(ValueError):
    """Raised when scenario or inputs JSON violates Test Contract v1.0 (exit code 2)."""


def _is_num(val: Any) -> bool:
    return not isinstance(val, bool) and isinstance(val, (int, float)) and math.isfinite(float(val))


def _is_int(val: Any) -> bool:
    return not isinstance(val, bool) and isinstance(val, int)


def _validate_pos3(val: Any, label: str) -> tuple[float, float, float]:
    if not isinstance(val, (list, tuple)) or len(val) != 3 or not all(_is_num(v) for v in val):
        raise ContractValidationError(f"Invalid 3D position for {label}: {val!r}")
    return (float(val[0]), float(val[1]), float(val[2]))


def _round3(val: float) -> float:
    r = round(float(val), 3)
    return 0.0 if r == 0.0 else r


@dataclass
class StepInput:
    """Raw input state for a single simulation step."""

    move_x: float = 0.0
    move_z: float = 0.0
    cam_yaw_deg: float = 0.0
    jump: bool = False
    interact: bool = False
    pulse: bool = False
    dash: bool = False


@dataclass
class Player:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    vy: float = 0.0
    yaw: float = 0.0
    flames: int = TUNING.flames
    carried: int = 0
    invuln_left: float = 0.0
    pulse_cooldown_left: float = 0.0

    @property
    def pos(self) -> list[float]:
        return [_round3(self.x), _round3(self.y), _round3(self.z)]


@dataclass
class Lantern:
    id: str
    x: float
    y: float
    z: float
    deposited: int = 0
    lit: bool = False

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "pos": [_round3(self.x), _round3(self.y), _round3(self.z)],
            "lit": self.lit,
            "deposited": self.deposited,
        }


@dataclass
class Mote:
    id: str
    x: float
    y: float
    z: float

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "pos": [_round3(self.x), _round3(self.y), _round3(self.z)],
        }


@dataclass
class Shade:
    id: str
    x: float
    y: float
    z: float
    state: str = "chase"
    stun_left: float = 0.0

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "pos": [_round3(self.x), _round3(self.y), _round3(self.z)],
            "state": self.state,
        }


def default_night1_lanterns() -> list[Lantern]:
    """Create 5 Great Lanterns (L1..L5) arranged symmetrically on a 24m ring."""
    radius = 24.0
    lanterns: list[Lantern] = []
    for idx in range(TUNING.lantern_count_night1):
        angle = math.radians(idx * (360.0 / TUNING.lantern_count_night1))
        lx = radius * math.sin(angle)
        lz = radius * math.cos(angle)
        lanterns.append(Lantern(id=f"L{idx + 1}", x=lx, y=0.0, z=lz, deposited=0, lit=False))
    return lanterns


def parse_inputs_frames(payload: Any) -> dict[int, dict[str, Any]]:
    """Validate and index an inputs JSON object by strictly increasing tick."""
    if not isinstance(payload, dict) or "frames" not in payload:
        raise ContractValidationError("Inputs file must be a JSON object with a 'frames' list.")
    frames = payload["frames"]
    if not isinstance(frames, list):
        raise ContractValidationError("'frames' in inputs must be a list.")

    allowed_keys = {"tick", "move", "cam_yaw_deg", "jump", "interact", "pulse", "dash"}
    by_tick: dict[int, dict[str, Any]] = {}
    last_tick = -1

    for idx, frame in enumerate(frames):
        if not isinstance(frame, dict) or "tick" not in frame:
            raise ContractValidationError(f"Frame #{idx} must be an object with 'tick'.")
        unknown = set(frame.keys()) - allowed_keys
        if unknown:
            raise ContractValidationError(f"Frame #{idx} has unknown keys: {sorted(unknown)}")
        tick = frame["tick"]
        if not _is_int(tick) or tick < 0:
            raise ContractValidationError(f"Frame #{idx} has invalid tick: {tick!r}")
        if tick <= last_tick:
            raise ContractValidationError(
                f"Frame ticks must be strictly increasing (got {tick} after {last_tick})."
            )
        last_tick = tick

        if "move" in frame:
            mv = frame["move"]
            if (
                not isinstance(mv, (list, tuple))
                or len(mv) != 2
                or not _is_num(mv[0])
                or not _is_num(mv[1])
            ):
                raise ContractValidationError(f"Frame at tick {tick} has invalid move: {mv!r}")
            mx, mz = float(mv[0]), float(mv[1])
            if mx < -1.0 or mx > 1.0 or mz < -1.0 or mz > 1.0:
                raise ContractValidationError(
                    f"Frame at tick {tick} move components must be in [-1, 1]: {mv!r}"
                )

        if "cam_yaw_deg" in frame and not _is_num(frame["cam_yaw_deg"]):
            raise ContractValidationError(
                f"Frame at tick {tick} has invalid cam_yaw_deg: {frame['cam_yaw_deg']!r}"
            )

        for bkey in ("jump", "interact", "pulse", "dash"):
            if bkey in frame and not isinstance(frame[bkey], bool):
                raise ContractValidationError(
                    f"Frame at tick {tick} field '{bkey}' must be boolean."
                )

        by_tick[tick] = frame

    return by_tick


@dataclass
class GameEngine:
    """Deterministic simulation engine for Night 1 (Đảo Bến)."""

    seed: int = 42
    night: int = 1
    tuning: TuningConfig = TUNING
    dt: float = FIXED_DT
    tick: int = 0
    sim_tick: int = 0
    state: str = "playing"
    score: int = 0
    initial_time_left_s: float = TUNING.night1_duration_s
    time_left_s: float = TUNING.night1_duration_s
    island_radius: float = DEFAULT_ISLAND_RADIUS
    random_motes: bool = True
    random_shades: bool = True
    player: Player = field(default_factory=Player)
    lanterns: list[Lantern] = field(default_factory=default_night1_lanterns)
    motes: list[Mote] = field(default_factory=list)
    shades: list[Shade] = field(default_factory=list)
    last_pulse_tick: int = -1000
    game_over_reason: str | None = None

    _rng: random.Random = field(default_factory=lambda: random.Random(42), repr=False)
    _next_mote_seq: int = field(default=1, repr=False)
    _next_shade_seq: int = field(default=1, repr=False)
    _prev_jump: bool = field(default=False, repr=False)
    _prev_interact: bool = field(default=False, repr=False)
    _prev_pulse: bool = field(default=False, repr=False)
    _prev_dash: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        self.reset(seed=self.seed)

    def reset(self, seed: int | None = None, scenario: dict[str, Any] | None = None) -> dict[str, Any]:
        """Reset simulation to initial Night 1 state and optionally apply a test scenario."""
        if seed is not None:
            self.seed = int(seed)
        if self.night != 1:
            raise ContractValidationError(f"Unsupported night: {self.night} (Phase 1 only supports night 1).")

        self._rng = random.Random(self.seed)
        self.tick = 0
        self.sim_tick = 0
        self.state = "playing"
        self.score = 0
        self.game_over_reason = None
        self.last_pulse_tick = -1000
        self.initial_time_left_s = float(self.tuning.night1_duration_s)
        self.time_left_s = self.initial_time_left_s
        self.island_radius = DEFAULT_ISLAND_RADIUS
        self.random_motes = True
        self.random_shades = True
        self.player = Player(flames=self.tuning.flames)
        self.lanterns = default_night1_lanterns()
        self.motes = []
        self.shades = []
        self._next_mote_seq = 1
        self._next_shade_seq = 1
        self._prev_jump = False
        self._prev_interact = False
        self._prev_pulse = False
        self._prev_dash = False

        if scenario is not None:
            self._apply_scenario(scenario)
        else:
            self._spawn_initial_random_entities()

        self._expand_island_radius_for_entities()
        return self.snapshot()

    def _spawn_initial_random_entities(self) -> None:
        if self.random_motes:
            for _ in range(DEFAULT_INITIAL_MOTES):
                self._spawn_random_mote()
        if self.random_shades:
            for _ in range(DEFAULT_INITIAL_SHADES):
                self._spawn_random_shade()

    def _spawn_random_mote(self) -> Mote:
        angle = self._rng.uniform(0.0, 2.0 * math.pi)
        radius = self._rng.uniform(4.5, DEFAULT_ISLAND_RADIUS - 4.0)
        mx = radius * math.cos(angle)
        mz = radius * math.sin(angle)
        mote = Mote(id=f"M{self._next_mote_seq}", x=mx, y=0.0, z=mz)
        self._next_mote_seq += 1
        self.motes.append(mote)
        return mote

    def _spawn_random_shade(self) -> Shade:
        for _ in range(16):
            angle = self._rng.uniform(0.0, 2.0 * math.pi)
            radius = self._rng.uniform(28.0, DEFAULT_ISLAND_RADIUS - 4.0)
            sx = radius * math.cos(angle)
            sz = radius * math.sin(angle)
            if math.hypot(sx - self.player.x, sz - self.player.z) < 10.0:
                continue
            if any(
                l.lit and math.hypot(sx - l.x, sz - l.z) <= self.tuning.safe_radius + 0.5
                for l in self.lanterns
            ):
                continue
            break
        shade = Shade(id=f"S{self._next_shade_seq}", x=sx, y=1.0, z=sz, state="chase")
        self._next_shade_seq += 1
        self.shades.append(shade)
        return shade

    def _apply_scenario(self, scenario: Any) -> None:
        if not isinstance(scenario, dict):
            raise ContractValidationError("Scenario root must be a JSON object.")

        if "random_motes" in scenario:
            if not isinstance(scenario["random_motes"], bool):
                raise ContractValidationError("'random_motes' must be a boolean.")
            self.random_motes = scenario["random_motes"]

        if "random_shades" in scenario:
            if not isinstance(scenario["random_shades"], bool):
                raise ContractValidationError("'random_shades' must be a boolean.")
            self.random_shades = scenario["random_shades"]

        if "time_left_s" in scenario:
            t_val = scenario["time_left_s"]
            if not _is_num(t_val) or float(t_val) <= 0.0:
                raise ContractValidationError(f"Invalid 'time_left_s': {t_val!r}")
            self.initial_time_left_s = float(t_val)
            self.time_left_s = self.initial_time_left_s

        if "player" in scenario:
            p_obj = scenario["player"]
            if not isinstance(p_obj, dict):
                raise ContractValidationError("'player' in scenario must be an object.")
            if "pos" in p_obj:
                px, py, pz = _validate_pos3(p_obj["pos"], "player.pos")
                self.player.x, self.player.y, self.player.z = px, py, pz
            if "carried" in p_obj:
                if not _is_int(p_obj["carried"]) or p_obj["carried"] < 0:
                    raise ContractValidationError(f"Invalid player.carried: {p_obj['carried']!r}")
                self.player.carried = int(p_obj["carried"])
            if "flames" in p_obj:
                if not _is_int(p_obj["flames"]) or p_obj["flames"] < 0:
                    raise ContractValidationError(f"Invalid player.flames: {p_obj['flames']!r}")
                self.player.flames = int(p_obj["flames"])

        if "lanterns" in scenario:
            l_list = scenario["lanterns"]
            if not isinstance(l_list, list):
                raise ContractValidationError("'lanterns' in scenario must be a list.")
            by_id = {l.id: l for l in self.lanterns}
            for idx, item in enumerate(l_list):
                if not isinstance(item, dict) or "id" not in item or not isinstance(item["id"], str):
                    raise ContractValidationError(f"Invalid lantern entry #{idx}: {item!r}")
                lid = item["id"]
                target = by_id.get(lid)
                if target is None:
                    raise ContractValidationError(f"Unknown lantern id in scenario: {lid!r}")
                if "pos" in item:
                    lx, ly, lz = _validate_pos3(item["pos"], f"lantern[{lid}].pos")
                    target.x, target.y, target.z = lx, ly, lz
                if "deposited" in item:
                    dep = item["deposited"]
                    if not _is_int(dep) or dep < 0:
                        raise ContractValidationError(f"Invalid lantern[{lid}].deposited: {dep!r}")
                    target.deposited = int(dep)
                if "lit" in item:
                    if not isinstance(item["lit"], bool):
                        raise ContractValidationError(f"Invalid lantern[{lid}].lit: {item['lit']!r}")
                    target.lit = item["lit"]
                    if target.lit and "deposited" not in item and target.deposited < self.tuning.lantern_cost:
                        target.deposited = self.tuning.lantern_cost
                elif "deposited" in item:
                    target.lit = target.deposited >= self.tuning.lantern_cost

        if "motes" in scenario:
            m_list = scenario["motes"]
            if not isinstance(m_list, list):
                raise ContractValidationError("'motes' in scenario must be a list.")
            self.motes = []
            for idx, item in enumerate(m_list):
                if isinstance(item, (list, tuple)):
                    mx, my, mz = _validate_pos3(item, f"motes[{idx}]")
                    mid = f"M{self._next_mote_seq}"
                elif isinstance(item, dict) and "pos" in item:
                    mx, my, mz = _validate_pos3(item["pos"], f"motes[{idx}].pos")
                    mid = str(item.get("id", f"M{self._next_mote_seq}"))
                else:
                    raise ContractValidationError(f"Invalid mote entry #{idx}: {item!r}")
                self._next_mote_seq += 1
                self.motes.append(Mote(id=mid, x=mx, y=my, z=mz))
        elif self.random_motes:
            for _ in range(DEFAULT_INITIAL_MOTES):
                self._spawn_random_mote()

        if "shades" in scenario:
            s_list = scenario["shades"]
            if not isinstance(s_list, list):
                raise ContractValidationError("'shades' in scenario must be a list.")
            self.shades = []
            used_ids: set[str] = set()
            for idx, item in enumerate(s_list):
                if isinstance(item, (list, tuple)):
                    sx, sy, sz = _validate_pos3(item, f"shades[{idx}]")
                    sid = f"S{self._next_shade_seq}"
                    s_state = "chase"
                elif isinstance(item, dict) and "pos" in item:
                    sx, sy, sz = _validate_pos3(item["pos"], f"shades[{idx}].pos")
                    sid = str(item.get("id", f"S{self._next_shade_seq}"))
                    s_state = str(item.get("state", "chase"))
                else:
                    raise ContractValidationError(f"Invalid shade entry #{idx}: {item!r}")
                if not sid or sid in used_ids:
                    raise ContractValidationError(f"Duplicate or empty shade id: {sid!r}")
                used_ids.add(sid)
                if sid.startswith("S") and sid[1:].isdigit():
                    self._next_shade_seq = max(self._next_shade_seq, int(sid[1:]) + 1)
                else:
                    self._next_shade_seq += 1
                stun_left = self.tuning.pulse_stun_s if s_state == "stunned" else 0.0
                self.shades.append(Shade(id=sid, x=sx, y=sy, z=sz, state=s_state, stun_left=stun_left))
        elif self.random_shades:
            for _ in range(DEFAULT_INITIAL_SHADES):
                self._spawn_random_shade()

    def _expand_island_radius_for_entities(self) -> None:
        max_r = DEFAULT_ISLAND_RADIUS
        pts = [(self.player.x, self.player.z)]
        pts.extend((l.x, l.z) for l in self.lanterns)
        pts.extend((m.x, m.z) for m in self.motes)
        pts.extend((s.x, s.z) for s in self.shades)
        for px, pz in pts:
            d = math.hypot(px, pz)
            if d + 15.0 > max_r:
                max_r = d + 15.0
        self.island_radius = max_r

    def step(self, action: StepInput) -> list[dict[str, Any]]:
        """Execute one 1/60s simulation step (k -> k+1) and return events emitted at tick k+1."""
        if self.state != "playing":
            return []

        events: list[dict[str, Any]] = []
        next_tick = self.tick + 1

        # Edge-trigger detection (false -> true)
        jump_edge = (not self._prev_jump) and bool(action.jump)
        interact_edge = (not self._prev_interact) and bool(action.interact)
        pulse_edge = (not self._prev_pulse) and bool(action.pulse)
        self._prev_jump = bool(action.jump)
        self._prev_interact = bool(action.interact)
        self._prev_pulse = bool(action.pulse)
        self._prev_dash = bool(action.dash)

        # 1. Advance timers & cooldowns
        self.player.invuln_left = max(0.0, self.player.invuln_left - self.dt)
        self.player.pulse_cooldown_left = max(0.0, self.player.pulse_cooldown_left - self.dt)
        for shade in self.shades:
            if shade.stun_left > 0.0:
                shade.stun_left = max(0.0, shade.stun_left - self.dt)
                if shade.stun_left <= 1e-9:
                    shade.stun_left = 0.0
                    shade.state = "chase"
            elif shade.state == "stunned":
                shade.state = "chase"

        # 2. Player movement (camera-rotated XZ) and jump
        mx = float(action.move_x)
        mz = float(action.move_z)
        mag = math.hypot(mx, mz)
        if mag > 1.0:
            mx /= mag
            mz /= mag

        if mag > 1e-9:
            theta = math.radians(float(action.cam_yaw_deg))
            wx = mx * math.cos(theta) + mz * math.sin(theta)
            wz = -mx * math.sin(theta) + mz * math.cos(theta)
            self.player.x += wx * self.tuning.player_speed * self.dt
            self.player.z += wz * self.tuning.player_speed * self.dt
            self.player.yaw = math.atan2(wx, wz)

            dist_origin = math.hypot(self.player.x, self.player.z)
            if dist_origin > self.island_radius:
                scale = self.island_radius / dist_origin
                self.player.x *= scale
                self.player.z *= scale

        if jump_edge and self.player.y <= 1e-6:
            self.player.vy = JUMP_VELOCITY

        if self.player.y > 0.0 or self.player.vy > 0.0:
            self.player.y += self.player.vy * self.dt
            self.player.vy -= GRAVITY * self.dt
            if self.player.y <= 0.0:
                self.player.y = 0.0
                self.player.vy = 0.0

        # 3. Mote pickup (XZ distance <= pickup_radius)
        if self.player.carried < self.tuning.carry_capacity and self.motes:
            remaining_motes: list[Mote] = []
            for mote in self.motes:
                if self.player.carried < self.tuning.carry_capacity:
                    dist = math.hypot(self.player.x - mote.x, self.player.z - mote.z)
                    if dist <= self.tuning.pickup_radius + 1e-9:
                        self.player.carried += 1
                        self.score += self.tuning.score.per_mote
                        events.append(
                            {
                                "type": "event",
                                "tick": next_tick,
                                "name": "mote_picked",
                                "data": {"carried": self.player.carried},
                            }
                        )
                        continue
                remaining_motes.append(mote)
            self.motes = remaining_motes

        # 4. Lantern deposit (interact false -> true within interact_radius)
        if interact_edge and self.player.carried > 0:
            candidate: Lantern | None = None
            best_dist = float("inf")
            for lantern in self.lanterns:
                if lantern.lit:
                    continue
                dist = math.hypot(self.player.x - lantern.x, self.player.z - lantern.z)
                if dist <= self.tuning.interact_radius + 1e-9 and dist < best_dist:
                    best_dist = dist
                    candidate = lantern

            if candidate is not None:
                needed = max(0, self.tuning.lantern_cost - candidate.deposited)
                amount = min(self.player.carried, needed)
                if amount > 0:
                    self.player.carried -= amount
                    candidate.deposited += amount
                    events.append(
                        {
                            "type": "event",
                            "tick": next_tick,
                            "name": "deposit",
                            "data": {
                                "lantern_id": candidate.id,
                                "amount": amount,
                                "deposited": candidate.deposited,
                            },
                        }
                    )
                    if candidate.deposited >= self.tuning.lantern_cost and not candidate.lit:
                        candidate.lit = True
                        self.score += self.tuning.score.per_lantern
                        events.append(
                            {
                                "type": "event",
                                "tick": next_tick,
                                "name": "lantern_lit",
                                "data": {"lantern_id": candidate.id},
                            }
                        )

        # 5. Pulse (pulse false -> true)
        if (
            pulse_edge
            and self.player.pulse_cooldown_left <= 1e-9
            and self.player.carried >= self.tuning.pulse_cost
        ):
            self.player.carried -= self.tuning.pulse_cost
            self.player.pulse_cooldown_left = self.tuning.pulse_cooldown_s
            self.last_pulse_tick = next_tick
            stunned_ids: list[str] = []

            for shade in self.shades:
                dx = shade.x - self.player.x
                dz = shade.z - self.player.z
                dist = math.hypot(dx, dz)
                if dist <= self.tuning.pulse_radius + 1e-9:
                    stunned_ids.append(shade.id)
                    shade.state = "stunned"
                    shade.stun_left = self.tuning.pulse_stun_s
                    if dist > 1e-9:
                        ux = dx / dist
                        uz = dz / dist
                    else:
                        ux, uz = 1.0, 0.0
                    shade.x += ux * self.tuning.pulse_push_m
                    shade.z += uz * self.tuning.pulse_push_m

            self.score += self.tuning.score.per_stun * len(stunned_ids)
            events.append(
                {
                    "type": "event",
                    "tick": next_tick,
                    "name": "pulse",
                    "data": {"stunned_ids": stunned_ids},
                }
            )

        # 6. Shade chase & lit lantern safe_radius enforcement
        lit_lanterns = [l for l in self.lanterns if l.lit]
        for shade in self.shades:
            if shade.state == "stunned":
                continue
            dx = self.player.x - shade.x
            dz = self.player.z - shade.z
            dist = math.hypot(dx, dz)
            step_dist = min(dist, self.tuning.shade_speed * self.dt)
            if dist > 1e-9:
                nx = shade.x + (dx / dist) * step_dist
                nz = shade.z + (dz / dist) * step_dist
            else:
                nx, nz = shade.x, shade.z

            for lantern in lit_lanterns:
                ldx = nx - lantern.x
                ldz = nz - lantern.z
                ldist = math.hypot(ldx, ldz)
                if ldist < self.tuning.safe_radius:
                    if ldist > 1e-9:
                        nx = lantern.x + (ldx / ldist) * self.tuning.safe_radius
                        nz = lantern.z + (ldz / ldist) * self.tuning.safe_radius
                    else:
                        nx = lantern.x + self.tuning.safe_radius
                        nz = lantern.z

            shade.x, shade.z = nx, nz

        # 7. Shade hit detection
        if self.player.invuln_left <= 1e-9:
            for shade in self.shades:
                if shade.state == "stunned":
                    continue
                dist = math.hypot(shade.x - self.player.x, shade.z - self.player.z)
                if dist <= self.tuning.shade_hit_radius + 1e-9:
                    self.player.flames = max(0, self.player.flames - 1)
                    dropped = int(math.floor(self.player.carried * self.tuning.hit_drop_ratio))
                    self.player.carried = max(0, self.player.carried - dropped)
                    self.player.invuln_left = self.tuning.invuln_s
                    events.append(
                        {
                            "type": "event",
                            "tick": next_tick,
                            "name": "player_hit",
                            "data": {
                                "by": "shade",
                                "flames": self.player.flames,
                                "dropped": dropped,
                            },
                        }
                    )
                    break

        # 8. Advance tick & periodic random spawns
        self.tick = next_tick
        self.sim_tick = next_tick
        self.time_left_s = max(0.0, self.initial_time_left_s - (self.tick / 60.0))

        if (
            self.random_motes
            and self.tick % MOTE_RESPAWN_INTERVAL_TICKS == 0
            and len(self.motes) < DEFAULT_INITIAL_MOTES
        ):
            self._spawn_random_mote()

        if (
            self.random_shades
            and self.tick % SHADE_SPAWN_INTERVAL_TICKS == 0
            and len(self.shades) < MAX_RANDOM_SHADES
        ):
            new_shade = self._spawn_random_shade()
            events.append(
                {
                    "type": "event",
                    "tick": self.tick,
                    "name": "shade_spawned",
                    "data": {"id": new_shade.id},
                }
            )

        # 9. End-of-game checks (won / lost)
        if self.lanterns and all(l.lit for l in self.lanterns):
            self.state = "won"
            self.game_over_reason = "all_lit"
            time_bonus = int(round(self.time_left_s * self.tuning.score.per_second_left))
            flame_bonus = self.player.flames * self.tuning.score.per_flame_left
            self.score += time_bonus + flame_bonus
            events.append(
                {
                    "type": "event",
                    "tick": self.tick,
                    "name": "game_over",
                    "data": {"result": "won", "reason": "all_lit"},
                }
            )
        elif self.player.flames <= 0:
            self.state = "lost"
            self.game_over_reason = "no_flames"
            events.append(
                {
                    "type": "event",
                    "tick": self.tick,
                    "name": "game_over",
                    "data": {"result": "lost", "reason": "no_flames"},
                }
            )
        elif self.time_left_s <= 1e-9:
            self.state = "lost"
            self.game_over_reason = "dawn"
            events.append(
                {
                    "type": "event",
                    "tick": self.tick,
                    "name": "game_over",
                    "data": {"result": "lost", "reason": "dawn"},
                }
            )

        return events

    def snapshot(self) -> dict[str, Any]:
        """Return Test Contract v1.0 snapshot dictionary with 3-decimal rounded coordinates."""
        return {
            "type": "snapshot",
            "tick": self.tick,
            "sim_tick": self.sim_tick,
            "state": self.state,
            "time_left_s": _round3(self.time_left_s),
            "score": self.score,
            "player": {
                "pos": self.player.pos,
                "flames": self.player.flames,
                "carried": self.player.carried,
            },
            "lanterns": [l.to_snapshot() for l in self.lanterns],
            "shades": [s.to_snapshot() for s in self.shades],
            "motes": [m.to_snapshot() for m in self.motes],
            "motes_active": len(self.motes),
        }

    def ui_snapshot(self) -> dict[str, Any]:
        """Extended snapshot for 3D WebGL client & HUD (adds camera/cooldown/tuning metadata)."""
        snap = self.snapshot()
        snap["player_yaw"] = _round3(self.player.yaw)
        snap["player_invuln_s"] = _round3(self.player.invuln_left)
        snap["pulse_cooldown_s"] = _round3(self.player.pulse_cooldown_left)
        snap["last_pulse_tick"] = self.last_pulse_tick
        snap["game_over_reason"] = self.game_over_reason
        snap["tuning"] = self.tuning.to_dict()
        return snap
