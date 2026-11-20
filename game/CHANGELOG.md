# Changelog

## [Phase 3] — Ticket-03 ("Đèn cạn dầu", Contract v1.2)

### Breaking Changes
- **Contract version:** Bumped `game.contract.json` from `1.1` to `1.2`.
- **Win condition replaced (`[THAY THẾ]`):** Removed early win (`all_lit`). Players must survive to dawn (`240s` / `270s` / `300s`) with at least `ceil(0.6 * total_lanterns)` lit (`3/5`, `4/6`, `5/7`) for `reason: "dawn_survived"`.
- **Lantern fuel & relight (`[THAY THẾ]`):** Lit lanterns now consume `1.0` fuel/s, can be refueled (`+10` fuel/mote), extinguish at `0` (`lantern_out`), and relight for `5` motes (`relight: true`).
- **Safe zone & Shade `drain` (`[THAY THẾ]`):** Lit lanterns with `fuel < 30` lose their `6m` safe zone; `wander` shades target weak lanterns and drain `5` fuel/s in the new `drain` state (`fuel_drain` event every 60 ticks).
- **Scoring replaced (`[THAY THẾ]`):** `+5`/mote deposited, `+100` first light, `+40` relight, `+5` pulse (`+15` if draining), dawn bonus `+50 + floor(fuel)` per lit lantern + `50 * flames`. Time-left bonus removed.
- **Snapshot & Scenario schema:** Added `player.capacity`, `lantern.{fuel, ever_lit, relit_count}`, `shade.state="drain"`, `player.successful_lights`, and `shades[].target_lantern_id`.

### Added
- Progressive carry capacity (`10 + 2 * successful_lights`, max `20`).
- Per-lantern fuel bars, `1 Hz` low-fuel blink, non-color unlit distinction (`20%` squash + tear marks), and persisted Colorblind Mode (`#00B3FF` shades, `#FFFFFF` + `⚠` danger UI).
