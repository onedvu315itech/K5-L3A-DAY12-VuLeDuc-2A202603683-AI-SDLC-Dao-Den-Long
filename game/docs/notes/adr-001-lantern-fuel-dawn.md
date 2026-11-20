# ADR-001: Lantern Fuel State Model & Dawn Survival Win Rule (Phase 3)

- **Status:** Accepted (Phase 3 — Ticket-03)
- **Context:** Playtesting showed skilled players lit all lanterns too early, ending the night with low late-game tension. Ticket-03 replaces permanent lanterns and early victory with decaying/drainable fuel and surviving until dawn.

## Decision
1. **Integer `1/60` Fuel Representation (`fuel_sixtieths`):**
   - Each lantern stores `fuel_sixtieths: int` (`0..6000`), where `60` units = `1.0` fuel.
   - Natural decay subtracts `1` unit/tick (`1.0/s`), and draining shades subtract `5` units/tick (`5.0/s`), eliminating floating-point drift across 18,000+ ticks.
   - External snapshots expose `round(fuel_sixtieths / 60.0, 1)` (`0.0` when `lit == false`).
2. **Lantern Lifecycle (`unlit` ↔ `lit` with `ever_lit`):**
   - Initial light requires `10` motes (`ever_lit: false -> true`, `fuel = 100.0`).
   - Lit lanterns can be refueled (`ceil((100 - fuel) / 10)` motes, `+10` fuel each); full lanterns (`6000`) are skipped during target selection.
   - Reaching `fuel_sixtieths <= 0` transitions `lit -> false`, clears `deposited = 0`, preserves `ever_lit = true`, and emits `lantern_out`.
   - Relighting an `ever_lit` lantern requires only `5` motes (`relight: true`, `relit_count += 1`).
3. **Weak-Lantern Vulnerability & `drain` State:**
   - Safe zone (`6.0m`) is active only when `lit && fuel >= 30.0` (`fuel_sixtieths >= 1800`).
   - `wander` shades target the nearest weak lit lantern (`fuel < 30`) and enter `drain` within `2.0m` XZ, emitting `fuel_drain` every 60 ticks.
4. **Dawn Survival Win Condition:**
   - Early win (`all_lit`) is removed. At tick `time_left_s == 0`, after `no_flames` check, `won` (`dawn_survived`) triggers iff `lit_count >= ceil(0.6 * total_lanterns)` (3/5, 4/6, 5/7).

## Consequences
- `test_mote_deposit_lantern_and_win` was replaced by `test_no_early_win_and_dawn_survived` to verify no early exit and dawn threshold scoring.
- `game.contract.json` bumped to `contract_version: "1.2"`.
