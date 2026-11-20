# OUTPUTS.md — Output Formats & Ownership Registry

<!-- [CP0] Baseline output schemas and owning modules. Update when Test Contract changes. -->

## 1. Headless Test Contract Output
- **Owner:** `game/src/headless.py` (CLI formatting) ← `game/src/core/engine.py::GameEngine.snapshot()` (state data)
- **Trigger:** `python3.12 -m src.headless [--input <path.json>] [--steps N] [--seed S]` (from `game/`)
- **Format:** Sorted canonical JSON on `stdout`, floats rounded to 4 decimals, deterministic for identical `(seed, steps)`.
- **CP0 Baseline Schema:**
```json
{
  "seed": 42,
  "tick": 90,
  "time": 1.5,
  "player": {
    "x": 0.0,
    "y": 0.0,
    "z": -6.0,
    "yaw": 3.1416
  },
  "lanterns": [
    {
      "id": "lantern-hello",
      "x": 0.0,
      "y": 0.0,
      "z": -6.0,
      "lit": true
    }
  ]
}
```
- **Phase 1+ Note:** Replace/extend schema cleanly once `PRD-0` Test Contract is confirmed.

---

## 2. Live 3D Web Bridge API Output
- **Owner:** `game/src/play.py::GameRequestHandler` ← `game/src/core/engine.py::GameEngine`
- **Endpoints:**
  - `GET /health` → `200 OK` `{"ok": true}`
  - `GET /api/state` → `200 OK` current `GameEngine.snapshot()` JSON
  - `POST /api/step` (body: `{"move_x": float, "move_z": float, "ticks": int}`) → `200 OK` updated `GameEngine.snapshot()` JSON
  - `POST /api/reset` (body: `{"seed": int | null}`) → `200 OK` reset `GameEngine.snapshot()` JSON

---

## 3. Verification Runner Output
- **Owner:** `game/scripts/verify.py`
- **Trigger:** `python3.12 game/scripts/verify.py` (or `python3 game/scripts/verify.py`)
- **Contract:**
  - Runs `unittest` discovery in `game/tests/`
  - Runs `src.headless` twice with identical inputs and asserts byte-identical stdout
  - Exits `0` only if all tests pass and determinism holds; non-zero on any failure.

---

## 4. Phase Proof & Notes Artifacts
- **Owner:** `game/docs/proof/phase-N.md` (proof), `game/docs/proof/README.md` (index), `game/docs/notes/assumptions.md`, `game/docs/notes/ai-log.md`, `game/docs/notes/retro.md`
- **Required Proof Sections:**
  1. Traceability table: `Requirement | Verification Method | Evidence | Result (PASS / NOT MET)`
  2. Exact verification commands run & verbatim observed output (never hand-edited).

<!-- [Phase 1] Replaced CP0 placeholder contracts with Test Contract v1.0 specifications -->

## Phase 1: Test Contract v1.0 Schemas & Owners

### A. `game.contract.json` (Repository Root)
- **Owner:** `game.contract.json` (at repo root) ↔ constants in `game/src/core/config.py`
- **Requirement:** `tuning` fields MUST match `game/src/core/` runtime values identically; `build_cmd`, `run_cmd`, and `headless_cmd` must run on macOS/Linux.

### B. Headless CLI (`game/src/headless.py` ← `game/src/core/`)
- **Command:** `python3 game/src/headless.py --seed <int> --night 1 [--scenario <file.json>] [--inputs <file.json>] --ticks <int> --out <file.jsonl> [--snapshot-every <int=10>]`
- **Exit Codes:**
  - `0`: Completed `--ticks` or reached `won`/`lost` state.
  - `2`: Invalid `--scenario` or `--inputs` JSON/schema (e.g., non-increasing `tick`, malformed fields), with error message on `stderr`.
  - Non-zero (`1`): Other CLI/runtime errors, with error message on `stderr`.

### C. JSONL Output File (`--out <file.jsonl>`)
- **Owner:** `game/src/headless.py` (writer) ← `game/src/core/engine.py` (snapshots & events)
- **Rounding:** All coordinates rounded to **3 decimal places**.
- **Line Types:**
  1. **Snapshot** (at `tick = 0` after scenario load, and every `--snapshot-every` ticks):
     ```json
     {"type":"snapshot","tick":120,"sim_tick":120,"state":"playing","time_left_s":238.0,"score":20,
      "player":{"pos":[0.0,0.0,12.0],"flames":3,"carried":2},
      "lanterns":[{"id":"L1","pos":[0.0,0.0,22.0],"lit":false,"deposited":0}],
      "shades":[{"id":"S1","pos":[10.0,1.0,2.0],"state":"chase"}],
      "motes":[{"id":"M1","pos":[0.0,0.0,5.0]}],
      "motes_active":19}
     ```
  2. **Event** (emitted immediately at `tick = k + 1` during step `k`):
     - `mote_picked`: `{"carried": n}`
     - `deposit`: `{"lantern_id": "L1", "amount": n, "deposited": n}`
     - `lantern_lit`: `{"lantern_id": "L1"}`
     - `pulse`: `{"stunned_ids": ["S1"]}`
     - `player_hit`: `{"by": "shade", "flames": n, "dropped": n}`
     - `shade_spawned`: `{"id": "S3"}`
     - `game_over`: `{"result": "won"|"lost", "reason": "all_lit"|"dawn"|"no_flames"}`
  3. **End** (mandatory final line):
     ```json
     {"type":"end","ticks":4800,"state":"won","score":1730}
     ```

### D. Live 3D Web Bridge (`game/src/play.py`)
- **Owner:** `game/src/play.py` ← `game/src/core/engine.py`
- Exposes `GET /health`, `GET /api/state` (full snapshot + HUD metadata like `carry_capacity`, `lantern_cost`, `pulse_cooldown_left_s`, `last_pulse_tick`), `POST /api/step` (`move_x`, `move_z`, `cam_yaw_deg`, `jump`, `interact`, `pulse`, `ticks`), and `POST /api/reset`.

---

<!-- [Phase 2] Upgraded to Test Contract v1.1 (Ticket-02) -->

## Phase 2: Test Contract v1.1 Deltas & Owners

### A. `game.contract.json` (Repository Root, `contract_version: "1.1"`)
- Standardized tuning values from Ticket-02 Part 1, plus new keys:
  - `dash_speed: 14.0`, `dash_duration_s: 0.2`, `dash_cooldown_s: 1.5`
  - `night1_duration_s: 300.0`, `night2_duration_s: 330.0`, `night3_duration_s: 360.0`
  - `fall_enabled: true`
  - Standardized: `player_speed: 6.0`, `carry_capacity: 10`, `lantern_cost: 10`, `pickup_radius: 1.0`, `interact_radius: 2.0`, `pulse_cost: 3`, `pulse_radius: 5.0`, `pulse_stun_s: 2.0`, `pulse_push_m: 4.0`, `pulse_cooldown_s: 3.0`, `safe_radius: 6.0`, `shade_speed: 4.0`, `shade_hit_radius: 1.0`, `invuln_s: 1.5`, `hit_drop_ratio: 0.5`, `score: {per_mote: 0, per_lantern: 100, per_stun: 5, per_second_left: 2, per_flame_left: 50}` (`+10` per mote deposited in engine).

### B. Headless CLI (`game/src/headless.py`)
- `--night` accepts `1`, `2`, or `3`. Full night (`21,600` ticks) completes in `<= 30s`.

### C. JSONL Output v1.1 (`--out <file.jsonl>`)
1. **Snapshot additions:**
   - Top-level: `night` (`1|2|3`), `wind`: `{"active": bool, "dir_deg": float}`
   - `player`: adds `vel` (`[vx, vy, vz]`), `grounded` (`bool`), `invuln` (`bool`), `dash_cd_s` (`float`), `pulse_cd_s` (`float`), `charm_s` (`float`)
   - `motes`: `[{"id": str, "pos": [x,y,z], "kind": "random"|"dropped", "ttl_s": float|null}]`
   - `shades`: `state` MUST be `"spawning" | "wander" | "chase" | "recoil" | "stunned"`
   - `drifters`: `[{"id": str, "pos": [x,y,z], "state": "idle"|"chase"|"flee"|"removed", "stolen": int}]`
   - `charms`: `[{"id": str, "available": bool, "respawn_s": float}]`
2. **Scenario & Input v1.1 additions:**
   - Scenario: `player.{invuln_ticks, dash_cd_ticks, pulse_cd_ticks, charm_ticks}`, `shades[].{state, state_ticks_left}`, `drifters`, `charms`, `random_drifters`, `wind_enabled`.
   - Input: `dash` (`bool`, edge `false->true`), `pause` (`bool`, edge `false->true`).
3. **New Event types:**
   - `dash {}`, `charm_picked {"charm_id": str, "charm_ticks": int}`, `drifter_steal {"drifter_id": str, "amount": int, "carried": int}`, `drifter_drop {"drifter_id": str, "amount": int}`, `night_start {"night": int}`, `paused {}`, `resumed {}`, `player_hit` with `lost` on fall.

---

<!-- [Phase 3] Upgraded to Test Contract v1.2 (Ticket-03) -->

## Phase 3: Test Contract v1.2 Deltas & Owners

### A. `game.contract.json` (`contract_version: "1.2"`)
- Added tuning keys: `fuel_max: 100`, `fuel_decay_per_s: 1.0`, `fuel_per_mote: 10`, `relight_cost: 5`, `win_ratio: 0.6`, `drain_per_s: 5`, `low_fuel_threshold: 30`, `capacity_max: 20`.
- Updated durations: `night1_duration_s: 240.0`, `night2_duration_s: 270.0`, `night3_duration_s: 300.0`.
- Updated `score`: `per_stun: 5` (engine awards `+15` if shade was in `drain` before pulse), `+5` per mote deposited, `+100` first light, `+40` relight, dawn bonus `+50 + floor(fuel)` per lit lantern + `50 * flames` (no time bonus).

### B. JSONL & Scenario v1.2 Deltas
1. **Snapshot:**
   - `lanterns[]`: adds `fuel` (1-decimal float; `0.0` if unlit), `ever_lit` (`bool`), `relit_count` (`int`).
   - `player`: adds `capacity` (`int`, `10..20`).
   - `shades[].state`: adds `"drain"`.
2. **Scenario:**
   - `lanterns[]`: supports `lit`, `fuel`, `ever_lit` (`lit: true` without `fuel` defaults `fuel: 100`).
   - `player`: supports `successful_lights` (`int`).
   - `shades[]`: supports `target_lantern_id` (`str | null`).
3. **Events:**
   - `refuel`: `{"lantern_id": str, "amount": int, "fuel": float}`
   - `lantern_out`: `{"lantern_id": str}`
   - `fuel_drain`: `{"lantern_id": str, "shade_id": str, "fuel": float}` (emitted every `60` ticks while draining)
   - `lantern_lit`: `{"lantern_id": str, "relight": bool}`
   - `game_over.reason`: `"dawn_survived"` | `"dawn"` | `"no_flames"` (`"all_lit"` removed).
