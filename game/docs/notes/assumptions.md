# Assumptions, Acceptance Criteria & Design Changes

## Phase 1 (PRD-0)
- **Chosen Tuning & Ambiguity Assumptions (Night 1 – Đảo Bến):**
  - **Island Geometry:** Circular island centered at `(0, 0, 0)`, ground at `Y = 0`, radius `42.0` m. `fall_enabled = false` (player is clamped inside island boundary; `fall` event is never emitted).
  - **5 Great Lanterns (`L1`..`L5`):** Placed symmetrically on a circle of radius `24.0` m around `(0, 0, 0)` (angles `0°, 72°, 144°, 216°, 288°` in XZ). Default `lantern_cost = 3` motes per lantern.
  - **Player Movement & Jump:** `player_speed = 7.0` m/s, `carry_capacity = 5`, `flames = 3`, `invuln_s = 1.5` s, `hit_drop_ratio = 0.5` (`dropped = int(carried * 0.5)`, rounded down; dropped motes are lost rather than respawned at feet so `motes_active` remains predictable). Jump is edge-triggered when grounded (`y == 0`), `jump_velocity = 7.5` m/s, `gravity = 20.0` m/s².
  - **Interactions & Pulse:** `pickup_radius = 1.8` m (auto-pickup on XZ distance `<= 1.8` while `carried < carry_capacity`), `interact_radius = 2.5` m (edge-triggered `interact` deposits `min(carried, lantern_cost - deposited)` into nearest unlit lantern in range), `pulse_cost = 1`, `pulse_radius = 6.0` m, `pulse_stun_s = 3.0` s, `pulse_push_m = 5.0` m (radial push away from player in XZ, clamped inside island), `pulse_cooldown_s = 3.0` s.
  - **Shadow Ink (Shades):** `shade_speed = 4.2` m/s, `shade_hit_radius = 1.2` m, `safe_radius = 5.0` m around **lit** lanterns only (unlit lanterns do not repel shades). Active shades move toward player along XZ; if entering a lit lantern's `safe_radius` (`<= 5.0` m), they stop/deflect along the safe-radius tangent outside the zone. Stunned shades stay in `"stunned"` state until stun timer expires.
  - **Random Spawning (when `random_motes=true` / `random_shades=true`):**
    - Motes: Start with `15` seeded motes scattered between `r = 5m` and `r = 38m`; periodically replenish up to `15` active motes every `6.0` s (`360` ticks) using seeded RNG.
    - Shades: Start with `2` seeded shades at `r = 28..36m`; spawn up to `5` shades (1 every `30s` / `1800` ticks) emitting `shade_spawned` with deterministic IDs (`S1`, `S2`, ...).
    - When `random_motes=false` or `random_shades=false` in `--scenario`, zero periodic spawning occurs.
  - **Night Duration & Scoring:** `night1_duration_s = 240` s (`14,400` ticks). `score`: `per_mote = 10` (on pickup), `per_lantern = 100` (on `lantern_lit`), `per_stun = 25` (per shade stunned in `pulse`), and on win (`all_lit`) bonus `per_second_left * int(time_left_s) + per_flame_left * flames` (`5` pts/sec left, `50` pts/flame left).
  - **Tick Termination:** If game wins/loses on step `k` (state transitions at tick `k+1`), emit `game_over`, emit snapshot only if `(k+1) % snapshot_every == 0`, emit final `end` line (`ticks = k+1`), and stop immediately.
- **Acceptance Criteria:**
  1. Given `game.contract.json` at repo root, running `headless_cmd` with `--seed 42 --night 1 --ticks 300 --out out.jsonl` exits `0` and produces valid JSONL ending with `{"type":"end",...}`.
  2. Given identical `--seed`, `--scenario`, `--inputs`, and `--ticks`, two runs produce byte-identical JSONL output.
  3. Given malformed `--inputs` (e.g., duplicate or decreasing `tick`) or invalid JSON, `headless.py` exits with code `2` and writes an error to `stderr`.
  4. Given a scenario with a mote at `[0, 0, 5]`, walking `+Z` (`move: [0, 1]`, `cam_yaw_deg: 0`) picks up the mote within `pickup_radius`, emits `mote_picked`, and increases `score` by `10`.
  5. Given `interact: true` (false->true edge) within `interact_radius` of an unlit lantern with `carried >= 3`, deposits `3`, emits `deposit` and `lantern_lit`, and marks `lit: true`.
  6. Given `pulse: true` within `pulse_radius` of a shade with `carried >= 1`, deducts `1`, pushes shade by `5.0m`, sets shade state to `"stunned"` for `3.0s`, emits `pulse`, and adds `25` score.
  7. Given an active shade touching player (`<= 1.2m`), reduces `flames` by `1`, drops `floor(carried * 0.5)`, emits `player_hit`, and grants `1.5s` invulnerability; when `flames == 0`, emits `game_over` (`lost`, `no_flames`).
  8. Given 3D web client (`python3 game/src/play.py`), player can walk, jump, rotate 3D camera/movement, collect fireflies, light all 5 lanterns or lose all flames/time, see HUD updates, and replay.
- **Test Suite Evolution Note (CP0 -> Phase 1):**
  - Updated `game/tests/test_hello.py` from the 3 CP0 placeholder hello-lantern tests to 9 Phase 1 `Test Contract v1.0` tests (`TestPhase1ContractAndSimulation`) because `PRD-0` replaced the temporary `lantern-hello` JSON output with the official `Test Contract v1.0` JSONL (`snapshot` / `event` / `end`) and `game.contract.json` tuning schema.

## Phase 2 (Ticket-02)
- **Clarifications / Updates to Phase 1 Assumptions:**
  - *(List any assumptions refined or overridden.)*
- **Acceptance Criteria:**
  - *(New criteria for Ticket-02.)*

## Phase 3 (Ticket-03)
- **Replaced / Modified Rules & Design Pivots:**
  - *(What changed, why, and which Phase 1/2 tests were updated or retired with reason.)*

## Phase 4 (Ticket-04)
- **Performance Targets & Hardware Specs:**
  - *(Record measured results and machine configuration.)*
