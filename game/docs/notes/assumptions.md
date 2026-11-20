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

## Phase 2 (Ticket-02 — "Ba hòn đảo" & Contract v1.1)
- **Updates / Overrides to Phase 1 Assumptions:**
  - All Phase 1 self-chosen constants are replaced by Ticket-02 Part 1 standardized constants (`player_speed=6.0`, `carry_capacity=10`, `lantern_cost=10`, `pickup_radius=1.0`, `interact_radius=2.0`, `pulse_cost=3`, `pulse_radius=5.0`, `safe_radius=6.0`, `shade_speed=4.0` / Night 3 `4.5`, `shade_hit_radius=1.0`, `night1=300s`, `fall_enabled=true`, and standardized scoring: `+10/mote deposited`, `+100/lantern`, `+5/shade stunned`, `+floor(time_left)*2 + 50*flames` on win).
  - `score.per_mote` in `game.contract.json` is set to `0` (pickup no longer scores; depositing scores `+10` per mote deposited).
  - Phase 1 unit tests that asserted old Phase 1 tuning numbers (e.g., `player_speed=7.0`, `lantern_cost=3`, `pulse_cost=1`, `per_mote` on pickup) are updated to match Ticket-02 standardized constants.
- **Ambiguities & Chosen Assumptions for Ticket-02:**
  - **Acceleration / Stopping (`<= 0.1s`):** Instant velocity response (0 ticks lag, `<= 0.1s`) when grounded or airborne, except during Dash (`14 m/s` for `12` ticks) or Jump Pad launch (horizontal launch velocity preserved until landing, though Dash is still allowed in air).
  - **Fall & Respawn (`Y < -10`):** When `player.y < -10`, if not already respawning: `-1` flame, `lost = carried`, `carried = 0`, emit `player_hit` (`by: "fall", flames, dropped: lost, lost`). If `flames == 0`, game ends immediately (`no_flames`); otherwise enter 60-tick respawn wait (no pickup, no shade hit), then respawn at `(0, 0, 0)` with `vel = [0, 0, 0]` and `90` ticks invulnerability.
  - **Safe Radius Push-Out:** When a lantern lights (`lit=true`), any non-stunned shade inside `6.0m` enters `recoil` (or push-out) and moves radially outward to `6.0m` within at most `30` ticks without dealing damage during push-out.
  - **Shade States (`spawning | wander | chase | recoil | stunned`):** Spawned shades start in `chase` (or `wander` if `> 12m` from player); `chase` drops to `wander` if distance `> 18m` (circling/drifting near spawn/patrol); hitting Mây puts that shade in `recoil` (`2m` back over `60` ticks); Pulse puts shades in `stunned` (`120` ticks, first `15` ticks pushed `4m` horizontally, stopping on obstacles/cliffs).
  - **Obstacles & Cliffs:** Night 3 Bell Tower (`R=2m` cylinder at `(0,6,0)`, `H=8m`) blocks player/shade/pulse push horizontally. Tier ledges (`Y=0/3/6`) are vertical cliffs (cannot walk up except via the 2 `3m`-wide ramps at `30°` and `150°`; walking off drops to the lower tier).
  - **Night 3 Wind (`wind_enabled`):** Default `true` on Night 3 (`false` on Nights 1–2 unless overridden in scenario). Every `30s` (`1800` ticks), a `5s` (`300` ticks) gust pushes Mây at `2.0 m/s` in a seeded random direction, with `2s` (`120` ticks) visual/audio telegraph beforehand.
  - **Dropped Motes:** `floor(carried / 2)` motes spawn on the ground at seeded angles on a `1.5–2.5m` ring around Mây (clamped to valid island surface if near edge) with `ttl_s = 8.0s` (`480` ticks), pickable from tick `k+1`.
  - **Score per Deposit:** `+10 * amount` awarded on `deposit` event; `+100` on `lantern_lit`; `+5 * len(stunned_ids)` on `pulse`; `+ int(math.floor(time_left_s)) * 2 + 50 * flames` on `won`.
- **Acceptance Criteria (Part 3 & Contract v1.1):**
  1. `game.contract.json` (`contract_version: "1.1"`) matches `TUNING` and passes regression + Phase 2 headless scenarios.
  2. Movement (`6.0 m/s`), Jump (`7.0 m/s`, `-20 m/s²`), and Dash (`14 m/s`, `0.2s`, `1.5s` cd) behave identically in headless and 3D.
  3. Night 2 twin islands, bamboo bridge, and both jump pads launch Mây across the gap (`~1.4s` flight) and land safely on the opposite island.
  4. Night 3 3-tier geometry, 2 ramps (`30°`, `150°`), jump pad to Tier 2, Bell Tower collision, and periodic wind gusts work deterministically.
  5. Gió Lạc (`D1, D2`) transitions `idle -> chase -> flee -> removed`, steals up to 3 motes, and drops stolen motes when hit by Pulse while fleeing.
  6. Bùa Gió (`C1, C2`) grants `7.2 m/s` speed and `0s` Dash cooldown for `600` ticks and respawns after `2700` ticks.
  7. Pause (`Esc`/`P` or `pause: true` input) freezes `sim_tick`, timers, spawns, and TTLs with `state: "paused"`, and resumes cleanly.
  8. Full 21,600-tick headless Night runs in `<= 30s`; 3D client runs smoothly (`>= 30 FPS` at `1280×720`) with full HUD, 3-Night campaign flow, saved settings, and Web Audio SFX.

## Phase 3 (Ticket-03 — "Đèn cạn dầu" & Contract v1.2)
- **Replaced Rules (`[THAY THẾ]`):**
  1. Lit lanterns now have `fuel` (`0..100`, tracked in integer `1/60` units = `0..6000`), decay `1.0/s`, can be refueled (`+10/mote`), go out at `0` (`lantern_out`), and relight for `5` motes (`ever_lit = true`).
  2. Lanterns with `fuel < 30` lose their `6m` safe zone; `wander` shades target the nearest weak lit lantern (`fuel < 30`) or nearest unlit lantern, enter `drain` at `<= 2m` XZ (`5/s` drain + `fuel_drain` every 60 ticks), and are pushed out if refueled `>= 30`.
  3. Nights no longer end early on lighting all lanterns; Nights 1/2/3 last `240/270/300s`, winning requires surviving to dawn with `lit >= ceil(0.6 * total)` (`dawn_survived`).
  4. Scoring replaced: `+5` per mote deposited, `+100` first light, `+40` relight, `+5` pulse (`+15` if shade was `drain`), dawn bonus `+50 + floor(fuel)` per lit lantern + `50 * flames` (time bonus removed).
- **Ambiguities & Assumptions:**
  - `fuel_drain` counter: each draining shade increments its own `drain_ticks` counter while in `drain`, emitting `fuel_drain` every 60 ticks (`drain_ticks % 60 == 0`).
  - `wander` target when no weak lit lantern (`fuel < 30`) exists: shade drifts toward nearest unlit lantern (with small patrol orbit so it doesn't freeze on top of the post).
  - `player_hit` / `all_lit` Phase 2 win test (`test_mote_deposit_lantern_and_win`) will be updated to verify lighting `L1` does NOT end the night early, and surviving to dawn with `>= 3/5` lit triggers `dawn_survived`.
- **Acceptance Criteria:**
  1. `game.contract.json` (`1.2`) matches `TUNING` and all Phase 3 keys.
  2. Integer `1/60` fuel math decays `1.0/s`, refuels `min(carried, ceil((100-fuel)/10))`, skips full lanterns, emits `lantern_out`, and relights for `5` motes.
  3. Shade `wander -> drain -> chase/stunned/wander` transitions, `5/s` drain, `fuel_drain` every 60 ticks, `< 30` safe-zone loss, and `>= 30` refuel push-out work deterministically.
  4. Winning at dawn requires `lit >= ceil(0.6 * total)` (`dawn_survived`), while `flames == 0` always loses (`no_flames`) first.
  5. `capacity = min(20, 10 + 2 * successful_lights)` updates on first light & relight, not scenario pre-lit lanterns.
  6. New scoring (`+5` deposit, `+100`/`+40` light, `+15` drain-pulse, dawn lantern+flame bonus) matches Ticket-03.
  7. Colorblind Mode toggle persists in `localStorage` and updates shade rim/eyes (`#00B3FF`), danger UI (`#FFFFFF` + `⚠`), and non-color unlit/low-fuel cues.

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
