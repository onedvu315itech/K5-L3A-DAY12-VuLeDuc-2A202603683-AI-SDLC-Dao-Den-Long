"""Deterministic 60Hz simulation engine for Đảo Đèn Lồng (Phase 2 / Ticket-02 / Contract v1.1)."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Any

from src.core.config import (
    CHARM_DURATION_TICKS,
    CHARM_RESPAWN_TICKS,
    CHARM_SPEED,
    DASH_COOLDOWN_TICKS,
    DASH_DURATION_TICKS,
    DRIFTER_DETECT_RADIUS,
    DRIFTER_FAST_SPEED,
    DRIFTER_FLEE_TICKS,
    DRIFTER_IDLE_SPEED,
    DRIFTER_MIN_CARRIED,
    DRIFTER_SPAWN_INTERVAL_TICKS,
    DRIFTER_STEAL_CAP,
    DRIFTER_STEAL_RADIUS,
    DRIFTER_STUN_FLEE_TICKS,
    DROPPED_MOTE_TTL_TICKS,
    FIXED_DT,
    GRAVITY,
    INITIAL_RANDOM_MOTES,
    INVULN_TICKS,
    JUMP_VELOCITY,
    MAX_ACTIVE_MOTES,
    MAX_DRIFTERS,
    MOTE_SPAWN_INTERVAL_TICKS,
    PULSE_COOLDOWN_TICKS,
    PULSE_PUSH_TICKS,
    PULSE_STUN_TICKS,
    RECOIL_DIST_M,
    RECOIL_TICKS,
    RESPAWN_WAIT_TICKS,
    SAFE_PUSH_TICKS,
    SHADE_DETECT_RADIUS,
    SHADE_FIRST_SPAWN_TICK,
    SHADE_LOSE_RADIUS,
    SHADE_NIGHT3_SPEED,
    TUNING,
    TuningConfig,
    WIND_DURATION_TICKS,
    WIND_INTERVAL_TICKS,
    WIND_PUSH_SPEED,
    WIND_WARN_TICKS,
)
from src.core.maps import (
    ground_height_at,
    night_charm_specs,
    night_jump_pads,
    night_lantern_specs,
    night_mote_spawn_points,
    night_shade_schedule,
    night_shade_spawn_points,
    resolve_obstacle_xz,
)


class ContractValidationError(ValueError):
    """Raised when scenario or inputs JSON violates Test Contract v1.1 (exit code 2)."""


VALID_SHADE_STATES = {"spawning", "wander", "chase", "recoil", "stunned"}
VALID_DRIFTER_STATES = {"idle", "chase", "flee", "removed"}


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
    """Raw input state for a single simulation tick."""

    move_x: float = 0.0
    move_z: float = 0.0
    cam_yaw_deg: float = 0.0
    jump: bool = False
    interact: bool = False
    pulse: bool = False
    dash: bool = False
    pause: bool = False


@dataclass
class Player:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    yaw: float = 0.0
    grounded: bool = True
    flames: int = TUNING.flames
    carried: int = 0
    invuln_ticks: int = 0
    dash_ticks_left: int = 0
    dash_cd_ticks: int = 0
    dash_dir_x: float = 0.0
    dash_dir_z: float = 1.0
    pulse_cd_ticks: int = 0
    charm_ticks: int = 0
    respawn_ticks_left: int = 0
    launch_vx: float = 0.0
    launch_vz: float = 0.0
    launched: bool = False

    @property
    def pos(self) -> list[float]:
        return [_round3(self.x), _round3(self.y), _round3(self.z)]

    @property
    def vel(self) -> list[float]:
        return [_round3(self.vx), _round3(self.vy), _round3(self.vz)]


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
    kind: str = "random"  # "random" | "dropped"
    ttl_ticks: int | None = None
    spawn_tick: int = 0

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "pos": [_round3(self.x), _round3(self.y), _round3(self.z)],
            "kind": self.kind,
            "ttl_s": None if self.ttl_ticks is None else _round3(self.ttl_ticks * FIXED_DT),
        }


@dataclass
class Shade:
    id: str
    x: float
    y: float
    z: float
    state: str = "chase"
    state_ticks_left: int = 0
    push_ticks_left: int = 0
    push_vx: float = 0.0
    push_vz: float = 0.0
    recoil_vx: float = 0.0
    recoil_vz: float = 0.0
    safe_push_ticks_left: int = 0
    safe_push_vx: float = 0.0
    safe_push_vz: float = 0.0
    wander_angle: float = 0.0
    spawn_tick: int = 0

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "pos": [_round3(self.x), _round3(self.y), _round3(self.z)],
            "state": self.state,
        }


@dataclass
class Drifter:
    id: str
    x: float
    y: float
    z: float
    state: str = "idle"
    stolen: int = 0
    has_stolen: bool = False
    flee_ticks_left: int = 0
    idle_angle: float = 0.0
    spawn_tick: int = 0

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "pos": [_round3(self.x), _round3(self.y), _round3(self.z)],
            "state": self.state,
            "stolen": self.stolen,
        }


@dataclass
class Charm:
    id: str
    x: float
    y: float
    z: float
    available: bool = True
    respawn_ticks: int = 0
    spawn_tick: int = 0

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "available": self.available,
            "respawn_s": _round3(self.respawn_ticks * FIXED_DT),
        }


def parse_inputs_frames(payload: Any) -> dict[int, dict[str, Any]]:
    """Validate and index an inputs JSON object by strictly increasing tick."""
    if not isinstance(payload, dict) or "frames" not in payload:
        raise ContractValidationError("Inputs file must be a JSON object with a 'frames' list.")
    frames = payload["frames"]
    if not isinstance(frames, list):
        raise ContractValidationError("'frames' in inputs must be a list.")

    allowed_keys = {"tick", "move", "cam_yaw_deg", "jump", "interact", "pulse", "dash", "pause"}
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

        for bkey in ("jump", "interact", "pulse", "dash", "pause"):
            if bkey in frame and not isinstance(frame[bkey], bool):
                raise ContractValidationError(
                    f"Frame at tick {tick} field '{bkey}' must be boolean."
                )

        by_tick[tick] = frame

    return by_tick


@dataclass
class GameEngine:
    """Deterministic simulation engine for Nights 1-3 (Contract v1.1)."""

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
    random_motes: bool = True
    random_shades: bool = True
    random_drifters: bool = True
    wind_enabled: bool = False
    wind_active: bool = False
    wind_warning: bool = False
    wind_dir_deg: float = 0.0
    wind_ticks_left: int = 0

    player: Player = field(default_factory=Player)
    lanterns: list[Lantern] = field(default_factory=list)
    motes: list[Mote] = field(default_factory=list)
    shades: list[Shade] = field(default_factory=list)
    drifters: list[Drifter] = field(default_factory=list)
    charms: list[Charm] = field(default_factory=list)
    last_pulse_tick: int = -1000
    game_over_reason: str | None = None

    _rng: random.Random = field(default_factory=lambda: random.Random(42), repr=False)
    _next_mote_seq: int = field(default=1, repr=False)
    _next_shade_seq: int = field(default=1, repr=False)
    _next_drifter_seq: int = field(default=1, repr=False)
    _prev_jump: bool = field(default=False, repr=False)
    _prev_interact: bool = field(default=False, repr=False)
    _prev_pulse: bool = field(default=False, repr=False)
    _prev_dash: bool = field(default=False, repr=False)
    _prev_pause: bool = field(default=False, repr=False)
    _night_started_emitted: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        self.reset(seed=self.seed, night=self.night)

    def reset(
        self,
        seed: int | None = None,
        night: int | None = None,
        scenario: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if seed is not None:
            self.seed = int(seed)
        if night is not None:
            self.night = int(night)
        if self.night not in (1, 2, 3):
            raise ContractValidationError(f"Unsupported --night {self.night} (must be 1, 2, or 3).")

        self._rng = random.Random(self.seed + self.night * 1009)
        self.tick = 0
        self.sim_tick = 0
        self.state = "playing"
        self.score = 0
        self.game_over_reason = None
        self.last_pulse_tick = -1000
        self.initial_time_left_s = float(self.tuning.duration_for_night(self.night))
        self.time_left_s = self.initial_time_left_s

        self.random_motes = True
        self.random_shades = True
        self.random_drifters = self.night in (2, 3)
        self.wind_enabled = self.night == 3
        self.wind_active = False
        self.wind_warning = False
        self.wind_dir_deg = 0.0
        self.wind_ticks_left = 0

        self.player = Player(flames=self.tuning.flames)
        self.lanterns = [
            Lantern(id=lid, x=lx, y=ly, z=lz)
            for lid, lx, ly, lz in night_lantern_specs(self.night)
        ]
        self.motes = []
        self.shades = []
        self.drifters = []
        self.charms = [
            Charm(id=cid, x=cx, y=cy, z=cz)
            for cid, cx, cy, cz in night_charm_specs(self.night)
        ]

        self._next_mote_seq = 1
        self._next_shade_seq = 1
        self._next_drifter_seq = 1
        self._prev_jump = False
        self._prev_interact = False
        self._prev_pulse = False
        self._prev_dash = False
        self._prev_pause = False
        self._night_started_emitted = False

        if scenario is not None:
            self._apply_scenario(scenario)
        else:
            self._spawn_initial_random_motes()

        return self.snapshot()

    def _free_mote_spawn_points(self) -> list[tuple[float, float, float]]:
        candidates = night_mote_spawn_points(self.night)
        free: list[tuple[float, float, float]] = []
        for cx, cy, cz in candidates:
            occupied = any(
                math.hypot(m.x - cx, m.z - cz) < 0.8 and abs(m.y - cy) < 0.8
                for m in self.motes
            )
            if not occupied:
                free.append((cx, cy, cz))
        return free

    def _spawn_initial_random_motes(self) -> None:
        if not self.random_motes:
            return
        pts = list(night_mote_spawn_points(self.night))
        self._rng.shuffle(pts)
        for mx, my, mz in pts[:INITIAL_RANDOM_MOTES]:
            self.motes.append(Mote(id=f"M{self._next_mote_seq}", x=mx, y=my, z=mz, kind="random"))
            self._next_mote_seq += 1

    def _spawn_one_random_mote(self, current_sim_tick: int) -> Mote | None:
        if len(self.motes) >= MAX_ACTIVE_MOTES:
            return None
        free = self._free_mote_spawn_points()
        if not free:
            return None
        mx, my, mz = self._rng.choice(free)
        mote = Mote(
            id=f"M{self._next_mote_seq}",
            x=mx,
            y=my,
            z=mz,
            kind="random",
            spawn_tick=current_sim_tick,
        )
        self._next_mote_seq += 1
        self.motes.append(mote)
        return mote

    def _spawn_one_shade(self, current_sim_tick: int) -> Shade | None:
        _, max_shades = night_shade_schedule(self.night)
        if len(self.shades) >= max_shades:
            return None
        lit_lanterns = [l for l in self.lanterns if l.lit]
        valid: list[tuple[float, float, float]] = []
        for sx, sy, sz in night_shade_spawn_points(self.night):
            if math.hypot(sx - self.player.x, sz - self.player.z) < 15.0:
                continue
            if any(math.hypot(sx - l.x, sz - l.z) <= self.tuning.safe_radius for l in lit_lanterns):
                continue
            valid.append((sx, sy, sz))
        if not valid:
            return None
        sx, sy, sz = self._rng.choice(valid)
        dist = math.hypot(sx - self.player.x, sz - self.player.z)
        init_state = "chase" if dist <= SHADE_DETECT_RADIUS else "wander"
        shade = Shade(
            id=f"S{self._next_shade_seq}",
            x=sx,
            y=sy + 1.0,
            z=sz,
            state=init_state,
            wander_angle=self._rng.uniform(0.0, 2.0 * math.pi),
            spawn_tick=current_sim_tick,
        )
        self._next_shade_seq += 1
        self.shades.append(shade)
        return shade

    def _spawn_one_drifter(self, current_sim_tick: int) -> Drifter | None:
        active = [d for d in self.drifters if d.state != "removed"]
        if len(active) >= MAX_DRIFTERS:
            return None
        pts = night_shade_spawn_points(self.night)
        if not pts:
            return None
        dx, dy, dz = self._rng.choice(pts)
        drifter = Drifter(
            id=f"D{self._next_drifter_seq}",
            x=dx,
            y=dy + 1.2,
            z=dz,
            state="idle",
            idle_angle=self._rng.uniform(0.0, 2.0 * math.pi),
            spawn_tick=current_sim_tick,
        )
        self._next_drifter_seq += 1
        self.drifters.append(drifter)
        return drifter

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

        if "random_drifters" in scenario:
            if not isinstance(scenario["random_drifters"], bool):
                raise ContractValidationError("'random_drifters' must be a boolean.")
            self.random_drifters = scenario["random_drifters"]

        if "wind_enabled" in scenario:
            if not isinstance(scenario["wind_enabled"], bool):
                raise ContractValidationError("'wind_enabled' must be a boolean.")
            self.wind_enabled = scenario["wind_enabled"]

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
                gh = ground_height_at(self.night, px, pz, py)
                self.player.grounded = gh is not None and abs(py - gh) <= 0.05
            if "carried" in p_obj:
                if not _is_int(p_obj["carried"]) or p_obj["carried"] < 0:
                    raise ContractValidationError(f"Invalid player.carried: {p_obj['carried']!r}")
                self.player.carried = int(p_obj["carried"])
            if "flames" in p_obj:
                if not _is_int(p_obj["flames"]) or p_obj["flames"] < 0:
                    raise ContractValidationError(f"Invalid player.flames: {p_obj['flames']!r}")
                self.player.flames = int(p_obj["flames"])
            for tick_key, attr in (
                ("invuln_ticks", "invuln_ticks"),
                ("dash_cd_ticks", "dash_cd_ticks"),
                ("pulse_cd_ticks", "pulse_cd_ticks"),
                ("charm_ticks", "charm_ticks"),
            ):
                if tick_key in p_obj:
                    val = p_obj[tick_key]
                    if not _is_int(val) or val < 0:
                        raise ContractValidationError(f"Invalid player.{tick_key}: {val!r}")
                    setattr(self.player, attr, int(val))

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
                    kind = "random"
                    ttl_ticks = None
                elif isinstance(item, dict) and "pos" in item:
                    mx, my, mz = _validate_pos3(item["pos"], f"motes[{idx}].pos")
                    mid = str(item.get("id", f"M{self._next_mote_seq}"))
                    kind = str(item.get("kind", "random"))
                    ttl_ticks = int(round(float(item["ttl_s"]) * 60)) if item.get("ttl_s") is not None else None
                else:
                    raise ContractValidationError(f"Invalid mote entry #{idx}: {item!r}")
                self._next_mote_seq += 1
                self.motes.append(Mote(id=mid, x=mx, y=my, z=mz, kind=kind, ttl_ticks=ttl_ticks))
        elif self.random_motes:
            self._spawn_initial_random_motes()

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
                    state_ticks = 0
                elif isinstance(item, dict) and "pos" in item:
                    sx, sy, sz = _validate_pos3(item["pos"], f"shades[{idx}].pos")
                    sid = str(item.get("id", f"S{self._next_shade_seq}"))
                    s_state = str(item.get("state", "chase"))
                    if s_state not in VALID_SHADE_STATES:
                        raise ContractValidationError(f"Invalid shade state: {s_state!r}")
                    state_ticks = int(item.get("state_ticks_left", PULSE_STUN_TICKS if s_state == "stunned" else 0))
                else:
                    raise ContractValidationError(f"Invalid shade entry #{idx}: {item!r}")
                if not sid or sid in used_ids:
                    raise ContractValidationError(f"Duplicate or empty shade id: {sid!r}")
                used_ids.add(sid)
                if sid.startswith("S") and sid[1:].isdigit():
                    self._next_shade_seq = max(self._next_shade_seq, int(sid[1:]) + 1)
                else:
                    self._next_shade_seq += 1
                self.shades.append(
                    Shade(id=sid, x=sx, y=sy, z=sz, state=s_state, state_ticks_left=state_ticks)
                )

        if "drifters" in scenario:
            d_list = scenario["drifters"]
            if not isinstance(d_list, list):
                raise ContractValidationError("'drifters' in scenario must be a list.")
            self.drifters = []
            for idx, item in enumerate(d_list):
                if not isinstance(item, dict) or "pos" not in item:
                    raise ContractValidationError(f"Invalid drifter entry #{idx}: {item!r}")
                dx, dy, dz = _validate_pos3(item["pos"], f"drifters[{idx}].pos")
                did = str(item.get("id", f"D{self._next_drifter_seq}"))
                d_state = str(item.get("state", "idle"))
                if d_state not in VALID_DRIFTER_STATES:
                    raise ContractValidationError(f"Invalid drifter state: {d_state!r}")
                stolen = int(item.get("stolen", 0))
                self._next_drifter_seq += 1
                self.drifters.append(
                    Drifter(
                        id=did,
                        x=dx,
                        y=dy,
                        z=dz,
                        state=d_state,
                        stolen=stolen,
                        has_stolen=stolen > 0,
                        flee_ticks_left=DRIFTER_FLEE_TICKS if d_state == "flee" else 0,
                    )
                )

        if "charms" in scenario:
            c_list = scenario["charms"]
            if not isinstance(c_list, list):
                raise ContractValidationError("'charms' in scenario must be a list.")
            self.charms = []
            for idx, item in enumerate(c_list):
                if not isinstance(item, dict):
                    raise ContractValidationError(f"Invalid charm entry #{idx}: {item!r}")
                cid = str(item.get("id", f"C{idx + 1}"))
                cx, cy, cz = _validate_pos3(item.get("pos", [0.0, 0.0, 0.0]), f"charms[{idx}].pos")
                avail = bool(item.get("available", True))
                resp_ticks = int(item.get("respawn_ticks", round(float(item.get("respawn_s", 0.0)) * 60)))
                self.charms.append(
                    Charm(id=cid, x=cx, y=cy, z=cz, available=avail, respawn_ticks=resp_ticks)
                )

    def _shade_speed(self) -> float:
        return SHADE_NIGHT3_SPEED if self.night == 3 else self.tuning.shade_speed

    def step(self, action: StepInput) -> list[dict[str, Any]]:
        """Execute one tick following the mandatory 12-step Ticket-02 order."""
        if self.state in ("won", "lost"):
            return []

        events: list[dict[str, Any]] = []
        self.tick += 1

        # Step 1: Read input (handle pause first)
        pause_edge = (not self._prev_pause) and bool(action.pause)
        jump_edge = (not self._prev_jump) and bool(action.jump)
        interact_edge = (not self._prev_interact) and bool(action.interact)
        pulse_edge = (not self._prev_pulse) and bool(action.pulse)
        dash_edge = (not self._prev_dash) and bool(action.dash)

        self._prev_pause = bool(action.pause)
        self._prev_jump = bool(action.jump)
        self._prev_interact = bool(action.interact)
        self._prev_pulse = bool(action.pulse)
        self._prev_dash = bool(action.dash)

        if pause_edge:
            if self.state == "playing":
                self.state = "paused"
                events.append({"type": "event", "tick": self.tick, "name": "paused", "data": {}})
                return events
            if self.state == "paused":
                self.state = "playing"
                events.append({"type": "event", "tick": self.tick, "name": "resumed", "data": {}})
                return events

        if self.state == "paused":
            return events

        # Active gameplay tick
        self.sim_tick += 1
        if not self._night_started_emitted:
            self._night_started_emitted = True
            events.append(
                {"type": "event", "tick": self.tick, "name": "night_start", "data": {"night": self.night}}
            )

        # Step 2: Decrement timers (time, cooldowns, invuln, stun, charm, dropped TTL, charm respawn)
        self.time_left_s = max(0.0, self.initial_time_left_s - (self.sim_tick / 60.0))

        if self.player.invuln_ticks > 0:
            self.player.invuln_ticks -= 1
        if self.player.dash_cd_ticks > 0:
            self.player.dash_cd_ticks -= 1
        if self.player.pulse_cd_ticks > 0:
            self.player.pulse_cd_ticks -= 1
        if self.player.charm_ticks > 0:
            self.player.charm_ticks -= 1
        if self.player.dash_ticks_left > 0:
            self.player.dash_ticks_left -= 1

        # Night 3 wind schedule
        if self.wind_enabled:
            if self.wind_active:
                self.wind_ticks_left -= 1
                if self.wind_ticks_left <= 0:
                    self.wind_active = False
            else:
                mod = self.sim_tick % WIND_INTERVAL_TICKS
                self.wind_warning = mod >= (WIND_INTERVAL_TICKS - WIND_WARN_TICKS)
                if self.sim_tick > 0 and mod == 0:
                    self.wind_active = True
                    self.wind_warning = False
                    self.wind_ticks_left = WIND_DURATION_TICKS
                    self.wind_dir_deg = round(self._rng.uniform(0.0, 360.0), 1)

        # Shade timers
        for shade in self.shades:
            if shade.push_ticks_left > 0:
                shade.push_ticks_left -= 1
            if shade.safe_push_ticks_left > 0:
                shade.safe_push_ticks_left -= 1
            if shade.state_ticks_left > 0:
                shade.state_ticks_left -= 1
                if shade.state_ticks_left == 0 and shade.state in ("stunned", "recoil", "spawning"):
                    dist = math.hypot(shade.x - self.player.x, shade.z - self.player.z)
                    shade.state = "chase" if dist <= SHADE_DETECT_RADIUS else "wander"

        # Drifter flee timers
        for drifter in self.drifters:
            if drifter.state == "flee" and drifter.flee_ticks_left > 0:
                drifter.flee_ticks_left -= 1
                if drifter.flee_ticks_left == 0:
                    drifter.state = "removed"

        # Dropped mote TTL
        if self.motes:
            kept_motes: list[Mote] = []
            for mote in self.motes:
                if mote.ttl_ticks is not None:
                    mote.ttl_ticks -= 1
                    if mote.ttl_ticks <= 0:
                        continue
                kept_motes.append(mote)
            self.motes = kept_motes

        # Charm respawn
        for charm in self.charms:
            if not charm.available and charm.respawn_ticks > 0:
                charm.respawn_ticks -= 1
                if charm.respawn_ticks == 0:
                    charm.available = True

        # Step 3: Move Mây (respawn wait, dash, jump, jump pad, wind, gravity, fall check)
        if self.player.respawn_ticks_left > 0:
            self.player.respawn_ticks_left -= 1
            self.player.vx = 0.0
            self.player.vy = 0.0
            self.player.vz = 0.0
            if self.player.respawn_ticks_left == 0:
                self.player.x = 0.0
                self.player.y = 0.0
                self.player.z = 0.0
                self.player.grounded = True
                self.player.launched = False
                self.player.invuln_ticks = INVULN_TICKS
        else:
            mx = float(action.move_x)
            mz = float(action.move_z)
            mag = math.hypot(mx, mz)
            if mag > 1.0:
                mx /= mag
                mz /= mag

            theta = math.radians(float(action.cam_yaw_deg))
            wx = mx * math.cos(theta) + mz * math.sin(theta)
            wz = -mx * math.sin(theta) + mz * math.cos(theta)
            if mag > 1e-9:
                self.player.yaw = math.atan2(wx, wz)

            # Dash trigger (ignored while already dashing; charm removes cooldown)
            has_charm = self.player.charm_ticks > 0
            if dash_edge and self.player.dash_ticks_left == 0 and (has_charm or self.player.dash_cd_ticks == 0):
                self.player.dash_ticks_left = DASH_DURATION_TICKS
                self.player.dash_cd_ticks = 0 if has_charm else DASH_COOLDOWN_TICKS
                if mag > 1e-9:
                    wmag = math.hypot(wx, wz)
                    self.player.dash_dir_x = wx / wmag
                    self.player.dash_dir_z = wz / wmag
                else:
                    self.player.dash_dir_x = math.sin(self.player.yaw)
                    self.player.dash_dir_z = math.cos(self.player.yaw)
                events.append({"type": "event", "tick": self.tick, "name": "dash", "data": {}})

            speed = CHARM_SPEED if has_charm else self.tuning.player_speed
            if self.player.dash_ticks_left > 0:
                vx = self.player.dash_dir_x * self.tuning.dash_speed
                vz = self.player.dash_dir_z * self.tuning.dash_speed
            elif self.player.launched:
                vx = self.player.launch_vx
                vz = self.player.launch_vz
            else:
                vx = wx * speed
                vz = wz * speed

            if self.wind_active:
                wrad = math.radians(self.wind_dir_deg)
                vx += math.cos(wrad) * WIND_PUSH_SPEED
                vz += math.sin(wrad) * WIND_PUSH_SPEED

            if jump_edge and self.player.grounded and self.player.dash_ticks_left == 0:
                self.player.vy = JUMP_VELOCITY
                self.player.grounded = False

            old_x, old_z = self.player.x, self.player.z
            new_x = old_x + vx * self.dt
            new_z = old_z + vz * self.dt
            new_x, new_z = resolve_obstacle_xz(self.night, old_x, old_z, new_x, new_z, self.player.y)
            self.player.x, self.player.z = new_x, new_z
            self.player.vx = (new_x - old_x) / self.dt
            self.player.vz = (new_z - old_z) / self.dt

            if self.player.dash_ticks_left > 0:
                # Dash in air keeps Y constant
                self.player.vy = 0.0
            else:
                self.player.y += self.player.vy * self.dt
                self.player.vy -= GRAVITY * self.dt
                gh = ground_height_at(self.night, self.player.x, self.player.z, self.player.y)
                if gh is not None and self.player.y <= gh and self.player.vy <= 0.0:
                    self.player.y = gh
                    self.player.vy = 0.0
                    self.player.grounded = True
                    self.player.launched = False
                else:
                    self.player.grounded = False

            # Jump pads
            for pad in night_jump_pads(self.night):
                if (
                    math.hypot(self.player.x - pad.x, self.player.z - pad.z) <= pad.radius + 1e-9
                    and abs(self.player.y - pad.y) <= 1.2
                    and not self.player.launched
                ):
                    self.player.vy = pad.vy
                    self.player.launch_vx = pad.dir_x * pad.vh
                    self.player.launch_vz = pad.dir_z * pad.vh
                    self.player.launched = True
                    self.player.grounded = False
                    break

            # Fall off island (Y < -10)
            if self.tuning.fall_enabled and self.player.y < -10.0:
                self.player.flames = max(0, self.player.flames - 1)
                lost = self.player.carried
                self.player.carried = 0
                self.player.dash_ticks_left = 0
                self.player.launched = False
                self.player.vx = 0.0
                self.player.vy = 0.0
                self.player.vz = 0.0
                events.append(
                    {
                        "type": "event",
                        "tick": self.tick,
                        "name": "player_hit",
                        "data": {
                            "by": "fall",
                            "flames": self.player.flames,
                            "dropped": 0,
                            "lost": lost,
                        },
                    }
                )
                if self.player.flames > 0:
                    self.player.respawn_ticks_left = RESPAWN_WAIT_TICKS

        # Step 4: Pickup motes and charms (not while respawning)
        if self.player.respawn_ticks_left == 0:
            if self.player.carried < self.tuning.carry_capacity and self.motes:
                rem_motes: list[Mote] = []
                for mote in self.motes:
                    if (
                        mote.spawn_tick < self.sim_tick
                        and self.player.carried < self.tuning.carry_capacity
                        and math.hypot(self.player.x - mote.x, self.player.z - mote.z)
                        <= self.tuning.pickup_radius + 1e-9
                        and abs(self.player.y - mote.y) <= 1.5 + 1e-9
                    ):
                        self.player.carried += 1
                        events.append(
                            {
                                "type": "event",
                                "tick": self.tick,
                                "name": "mote_picked",
                                "data": {"carried": self.player.carried},
                            }
                        )
                        continue
                    rem_motes.append(mote)
                self.motes = rem_motes

            for charm in self.charms:
                if (
                    charm.available
                    and charm.spawn_tick < self.sim_tick
                    and math.hypot(self.player.x - charm.x, self.player.z - charm.z)
                    <= self.tuning.pickup_radius + 1e-9
                    and abs(self.player.y - charm.y) <= 1.5 + 1e-9
                ):
                    charm.available = False
                    charm.respawn_ticks = CHARM_RESPAWN_TICKS
                    self.player.charm_ticks = CHARM_DURATION_TICKS
                    self.player.dash_cd_ticks = 0
                    events.append(
                        {
                            "type": "event",
                            "tick": self.tick,
                            "name": "charm_picked",
                            "data": {"charm_id": charm.id, "charm_ticks": CHARM_DURATION_TICKS},
                        }
                    )

        # Step 5: Interact with nearest unlit lantern (tie-break lowest id)
        newly_lit_lanterns: list[Lantern] = []
        if interact_edge and self.player.carried > 0 and self.player.respawn_ticks_left == 0:
            best_lantern: Lantern | None = None
            best_key: tuple[float, str] | None = None
            for lantern in self.lanterns:
                if lantern.lit:
                    continue
                dist = math.hypot(self.player.x - lantern.x, self.player.z - lantern.z)
                if dist <= self.tuning.interact_radius + 1e-9:
                    key = (round(dist, 9), lantern.id)
                    if best_key is None or key < best_key:
                        best_key = key
                        best_lantern = lantern

            if best_lantern is not None:
                needed = max(0, self.tuning.lantern_cost - best_lantern.deposited)
                amount = min(self.player.carried, needed)
                if amount > 0:
                    self.player.carried -= amount
                    best_lantern.deposited += amount
                    self.score += amount * self.tuning.score.per_mote_deposit
                    events.append(
                        {
                            "type": "event",
                            "tick": self.tick,
                            "name": "deposit",
                            "data": {
                                "lantern_id": best_lantern.id,
                                "amount": amount,
                                "deposited": best_lantern.deposited,
                            },
                        }
                    )
                    if best_lantern.deposited >= self.tuning.lantern_cost and not best_lantern.lit:
                        best_lantern.lit = True
                        newly_lit_lanterns.append(best_lantern)
                        self.score += self.tuning.score.per_lantern
                        events.append(
                            {
                                "type": "event",
                                "tick": self.tick,
                                "name": "lantern_lit",
                                "data": {"lantern_id": best_lantern.id},
                            }
                        )

        # Step 6: Update safe zones (push out shades caught inside newly lit lantern)
        for lantern in newly_lit_lanterns:
            for shade in self.shades:
                dx = shade.x - lantern.x
                dz = shade.z - lantern.z
                dist = math.hypot(dx, dz)
                if dist < self.tuning.safe_radius:
                    ux, uz = (dx / dist, dz / dist) if dist > 1e-9 else (1.0, 0.0)
                    rem = (self.tuning.safe_radius + 0.05) - dist
                    shade.safe_push_ticks_left = SAFE_PUSH_TICKS
                    shade.safe_push_vx = (ux * rem) / (SAFE_PUSH_TICKS * self.dt)
                    shade.safe_push_vz = (uz * rem) / (SAFE_PUSH_TICKS * self.dt)

        # Step 7: Pulse (Tỏa Sáng) — 3D distance <= 5.0m from (player.pos + [0, 0.8, 0])
        if (
            pulse_edge
            and self.player.respawn_ticks_left == 0
            and self.player.pulse_cd_ticks == 0
            and self.player.carried >= self.tuning.pulse_cost
        ):
            self.player.carried -= self.tuning.pulse_cost
            self.player.pulse_cd_ticks = PULSE_COOLDOWN_TICKS
            self.last_pulse_tick = self.tick
            px0, py0, pz0 = self.player.x, self.player.y + 0.8, self.player.z
            stunned_ids: list[str] = []

            for shade in self.shades:
                if shade.spawn_tick >= self.sim_tick:
                    continue
                dist3d = math.sqrt((shade.x - px0) ** 2 + (shade.y - py0) ** 2 + (shade.z - pz0) ** 2)
                if dist3d <= self.tuning.pulse_radius + 1e-9:
                    stunned_ids.append(shade.id)
                    shade.state = "stunned"
                    shade.state_ticks_left = PULSE_STUN_TICKS
                    dx = shade.x - px0
                    dz = shade.z - pz0
                    hdist = math.hypot(dx, dz)
                    ux, uz = (dx / hdist, dz / hdist) if hdist > 1e-9 else (1.0, 0.0)
                    shade.push_ticks_left = PULSE_PUSH_TICKS
                    shade.push_vx = (ux * self.tuning.pulse_push_m) / (PULSE_PUSH_TICKS * self.dt)
                    shade.push_vz = (uz * self.tuning.pulse_push_m) / (PULSE_PUSH_TICKS * self.dt)

            self.score += self.tuning.score.per_stun * len(stunned_ids)
            events.append(
                {
                    "type": "event",
                    "tick": self.tick,
                    "name": "pulse",
                    "data": {"stunned_ids": stunned_ids},
                }
            )

            # Pulse hits Drifters too (3D dist <= 5.0m)
            for drifter in self.drifters:
                if drifter.state == "removed" or drifter.spawn_tick >= self.sim_tick:
                    continue
                dist3d = math.sqrt(
                    (drifter.x - px0) ** 2 + (drifter.y - py0) ** 2 + (drifter.z - pz0) ** 2
                )
                if dist3d <= self.tuning.pulse_radius + 1e-9:
                    if drifter.state == "chase":
                        drifter.state = "flee"
                        drifter.flee_ticks_left = DRIFTER_FLEE_TICKS
                    elif drifter.state == "flee" and drifter.stolen > 0:
                        dropped_amt = drifter.stolen
                        drifter.stolen = 0
                        for i in range(dropped_amt):
                            ang = (i / max(1, dropped_amt)) * 2.0 * math.pi
                            mx = drifter.x + 0.6 * math.cos(ang)
                            mz = drifter.z + 0.6 * math.sin(ang)
                            gh = ground_height_at(self.night, mx, mz, drifter.y)
                            my = gh if gh is not None else 0.0
                            self.motes.append(
                                Mote(
                                    id=f"M{self._next_mote_seq}",
                                    x=mx,
                                    y=my,
                                    z=mz,
                                    kind="dropped",
                                    ttl_ticks=DROPPED_MOTE_TTL_TICKS,
                                    spawn_tick=self.sim_tick,
                                )
                            )
                            self._next_mote_seq += 1
                        drifter.flee_ticks_left = min(drifter.flee_ticks_left, DRIFTER_STUN_FLEE_TICKS)
                        events.append(
                            {
                                "type": "event",
                                "tick": self.tick,
                                "name": "drifter_drop",
                                "data": {"drifter_id": drifter.id, "amount": dropped_amt},
                            }
                        )

        # Step 8: Move Shades & Drifters
        lit_lanterns = [l for l in self.lanterns if l.lit]
        sh_speed = self._shade_speed()
        for shade in self.shades:
            if shade.spawn_tick >= self.sim_tick or shade.state == "spawning":
                continue

            old_sx, old_sz = shade.x, shade.z
            nx, nz = old_sx, old_sz

            if shade.safe_push_ticks_left > 0:
                nx = old_sx + shade.safe_push_vx * self.dt
                nz = old_sz + shade.safe_push_vz * self.dt
            elif shade.state == "stunned":
                if shade.push_ticks_left > 0:
                    cand_x = old_sx + shade.push_vx * self.dt
                    cand_z = old_sz + shade.push_vz * self.dt
                    rx, rz = resolve_obstacle_xz(self.night, old_sx, old_sz, cand_x, cand_z, shade.y)
                    if (rx, rz) != (cand_x, cand_z):
                        shade.push_ticks_left = 0
                    nx, nz = rx, rz
            elif shade.state == "recoil":
                nx = old_sx + shade.recoil_vx * self.dt
                nz = old_sz + shade.recoil_vz * self.dt
            else:
                # wander / chase state transitions
                dist_p = math.hypot(self.player.x - old_sx, self.player.z - old_sz)
                if shade.state == "wander" and dist_p <= SHADE_DETECT_RADIUS:
                    shade.state = "chase"
                elif shade.state == "chase" and dist_p > SHADE_LOSE_RADIUS:
                    shade.state = "wander"

                if shade.state == "chase":
                    if dist_p > 1e-9:
                        step_d = min(dist_p, sh_speed * self.dt)
                        nx = old_sx + ((self.player.x - old_sx) / dist_p) * step_d
                        nz = old_sz + ((self.player.z - old_sz) / dist_p) * step_d
                else:
                    shade.wander_angle += 0.02
                    nx = old_sx + math.cos(shade.wander_angle) * (sh_speed * 0.45) * self.dt
                    nz = old_sz + math.sin(shade.wander_angle) * (sh_speed * 0.45) * self.dt

            # Lit lantern safe_radius blocks outside shades
            if shade.safe_push_ticks_left == 0:
                for lantern in lit_lanterns:
                    ldx = nx - lantern.x
                    ldz = nz - lantern.z
                    ldist = math.hypot(ldx, ldz)
                    if ldist < self.tuning.safe_radius:
                        ux, uz = (ldx / ldist, ldz / ldist) if ldist > 1e-9 else (1.0, 0.0)
                        nx = lantern.x + ux * self.tuning.safe_radius
                        nz = lantern.z + uz * self.tuning.safe_radius

            shade.x, shade.z = resolve_obstacle_xz(self.night, old_sx, old_sz, nx, nz, shade.y)

        # Drifter movement
        for drifter in self.drifters:
            if drifter.state == "removed" or drifter.spawn_tick >= self.sim_tick:
                continue
            dist_p = math.hypot(self.player.x - drifter.x, self.player.z - drifter.z)
            if drifter.state == "idle":
                if self.player.carried >= DRIFTER_MIN_CARRIED and dist_p <= DRIFTER_DETECT_RADIUS:
                    drifter.state = "chase"
            elif drifter.state == "chase":
                if self.player.carried < DRIFTER_MIN_CARRIED or dist_p > DRIFTER_DETECT_RADIUS:
                    drifter.state = "idle"

            if drifter.state == "idle":
                drifter.idle_angle += 0.03
                drifter.x += math.cos(drifter.idle_angle) * DRIFTER_IDLE_SPEED * self.dt
                drifter.z += math.sin(drifter.idle_angle) * DRIFTER_IDLE_SPEED * self.dt
            elif drifter.state == "chase":
                if dist_p > 1e-9:
                    step_d = min(dist_p, DRIFTER_FAST_SPEED * self.dt)
                    drifter.x += ((self.player.x - drifter.x) / dist_p) * step_d
                    drifter.z += ((self.player.z - drifter.z) / dist_p) * step_d
            elif drifter.state == "flee":
                dx = drifter.x - self.player.x
                dz = drifter.z - self.player.z
                d = math.hypot(dx, dz)
                ux, uz = (dx / d, dz / d) if d > 1e-9 else (1.0, 0.0)
                drifter.x += ux * DRIFTER_FAST_SPEED * self.dt
                drifter.z += uz * DRIFTER_FAST_SPEED * self.dt

        # Step 9: Collisions — Drifters steal first, then Shades hit (ascending id)
        if self.player.respawn_ticks_left == 0:
            for drifter in sorted(self.drifters, key=lambda d: d.id):
                if drifter.spawn_tick >= self.sim_tick or drifter.has_stolen or drifter.state in ("flee", "removed"):
                    continue
                if math.hypot(drifter.x - self.player.x, drifter.z - self.player.z) <= DRIFTER_STEAL_RADIUS + 1e-9:
                    steal = min(DRIFTER_STEAL_CAP, self.player.carried)
                    self.player.carried -= steal
                    drifter.stolen = steal
                    drifter.has_stolen = True
                    drifter.state = "flee"
                    drifter.flee_ticks_left = DRIFTER_FLEE_TICKS
                    events.append(
                        {
                            "type": "event",
                            "tick": self.tick,
                            "name": "drifter_steal",
                            "data": {
                                "drifter_id": drifter.id,
                                "amount": steal,
                                "carried": self.player.carried,
                            },
                        }
                    )

            if self.player.invuln_ticks == 0:
                for shade in sorted(self.shades, key=lambda s: s.id):
                    if shade.spawn_tick >= self.sim_tick:
                        continue
                    if shade.state in ("spawning", "stunned", "recoil") or shade.safe_push_ticks_left > 0:
                        continue
                    xz_dist = math.hypot(shade.x - self.player.x, shade.z - self.player.z)
                    dy = abs(shade.y - self.player.y)
                    if xz_dist <= self.tuning.shade_hit_radius + 1e-9 and dy <= 1.5 + 1e-9:
                        self.player.flames = max(0, self.player.flames - 1)
                        dropped = int(math.floor(self.player.carried * self.tuning.hit_drop_ratio))
                        self.player.carried = max(0, self.player.carried - dropped)
                        self.player.invuln_ticks = INVULN_TICKS

                        # Spawn dropped motes on 1.5-2.5m ring
                        for _ in range(dropped):
                            ang = self._rng.uniform(0.0, 2.0 * math.pi)
                            rad = self._rng.uniform(1.5, 2.5)
                            mx = self.player.x + rad * math.cos(ang)
                            mz = self.player.z + rad * math.sin(ang)
                            gh = ground_height_at(self.night, mx, mz, self.player.y)
                            my = gh if gh is not None else self.player.y
                            self.motes.append(
                                Mote(
                                    id=f"M{self._next_mote_seq}",
                                    x=mx,
                                    y=my,
                                    z=mz,
                                    kind="dropped",
                                    ttl_ticks=DROPPED_MOTE_TTL_TICKS,
                                    spawn_tick=self.sim_tick,
                                )
                            )
                            self._next_mote_seq += 1

                        # Shade recoil 2m over 60 ticks
                        dx = shade.x - self.player.x
                        dz = shade.z - self.player.z
                        d = math.hypot(dx, dz)
                        ux, uz = (dx / d, dz / d) if d > 1e-9 else (1.0, 0.0)
                        shade.state = "recoil"
                        shade.state_ticks_left = RECOIL_TICKS
                        shade.recoil_vx = (ux * RECOIL_DIST_M) / (RECOIL_TICKS * self.dt)
                        shade.recoil_vz = (uz * RECOIL_DIST_M) / (RECOIL_TICKS * self.dt)

                        events.append(
                            {
                                "type": "event",
                                "tick": self.tick,
                                "name": "player_hit",
                                "data": {
                                    "by": "shade",
                                    "flames": self.player.flames,
                                    "dropped": dropped,
                                },
                            }
                        )
                        break

        # Step 10: Scheduled spawns (only active from next tick via spawn_tick)
        if self.random_motes and self.sim_tick % MOTE_SPAWN_INTERVAL_TICKS == 0:
            self._spawn_one_random_mote(self.sim_tick)

        if self.random_shades and self.sim_tick >= SHADE_FIRST_SPAWN_TICK:
            interval, _ = night_shade_schedule(self.night)
            if self.sim_tick == SHADE_FIRST_SPAWN_TICK:
                for _ in range(2):
                    s = self._spawn_one_shade(self.sim_tick)
                    if s is not None:
                        events.append(
                            {
                                "type": "event",
                                "tick": self.tick,
                                "name": "shade_spawned",
                                "data": {"id": s.id},
                            }
                        )
            elif (self.sim_tick - SHADE_FIRST_SPAWN_TICK) % interval == 0:
                s = self._spawn_one_shade(self.sim_tick)
                if s is not None:
                    events.append(
                        {
                            "type": "event",
                            "tick": self.tick,
                            "name": "shade_spawned",
                            "data": {"id": s.id},
                        }
                    )

        if (
            self.random_drifters
            and self.night in (2, 3)
            and self.sim_tick % DRIFTER_SPAWN_INTERVAL_TICKS == 0
        ):
            self._spawn_one_drifter(self.sim_tick)

        # Step 11: Win / Loss check (no_flames -> all_lit -> dawn)
        if self.player.flames <= 0:
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
        elif self.lanterns and all(l.lit for l in self.lanterns):
            self.state = "won"
            self.game_over_reason = "all_lit"
            time_bonus = int(math.floor(self.time_left_s)) * self.tuning.score.per_second_left
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
        """Return Test Contract v1.1 snapshot dictionary."""
        return {
            "type": "snapshot",
            "tick": self.tick,
            "sim_tick": self.sim_tick,
            "night": self.night,
            "state": self.state,
            "time_left_s": _round3(self.time_left_s),
            "score": self.score,
            "wind": {
                "active": self.wind_active,
                "dir_deg": _round3(self.wind_dir_deg),
            },
            "player": {
                "pos": self.player.pos,
                "vel": self.player.vel,
                "grounded": self.player.grounded,
                "flames": self.player.flames,
                "carried": self.player.carried,
                "invuln": self.player.invuln_ticks > 0,
                "dash_cd_s": _round3(self.player.dash_cd_ticks * FIXED_DT),
                "pulse_cd_s": _round3(self.player.pulse_cd_ticks * FIXED_DT),
                "charm_s": _round3(self.player.charm_ticks * FIXED_DT),
            },
            "lanterns": [l.to_snapshot() for l in self.lanterns],
            "shades": [s.to_snapshot() for s in self.shades],
            "motes": [m.to_snapshot() for m in self.motes],
            "motes_active": len(self.motes),
            "drifters": [d.to_snapshot() for d in self.drifters],
            "charms": [c.to_snapshot() for c in self.charms],
        }

    def ui_snapshot(self) -> dict[str, Any]:
        """Extended snapshot for 3D WebGL client & HUD."""
        snap = self.snapshot()
        snap["player_yaw"] = _round3(self.player.yaw)
        snap["wind_warning"] = self.wind_warning
        snap["respawning"] = self.player.respawn_ticks_left > 0
        snap["last_pulse_tick"] = self.last_pulse_tick
        snap["game_over_reason"] = self.game_over_reason
        snap["tuning"] = self.tuning.to_dict()
        return snap
