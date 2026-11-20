# Changelog

## [v1.0.0 / Phase 4] — Ticket-04 ("Bình minh: phát hành v1.0.0", Contract v1.3)
### Added
- **Benchmark Mode (`game/src/bench.py`):** Standardized Night 1 scene (`200` wandering shades, `100` motes, `L1–L3` lit, `15s` CCW camera orbit at `R=30m, Y=15m`, `3s` warmup + `--duration`s measurement) outputting `bench.json`.
- **Soak Test (`game/src/soak.py`):** 10-Night continuous single-process soak test with seeded random inputs and cross-platform RSS tracking (`soak.json`).
- **Local Top-10 Leaderboard (`game/src/core/leaderboard.py`):** Persistent leaderboard (`game/data/leaderboard.json`), in-game Leaderboard view, end-of-run name entry (`3–12` chars `[A-Za-z0-9_]` / Vietnamese), and `--export-leaderboard <out.json>` CLI.
- **Accessibility:** `18px+` base UI font (`1280×720`) + `×1.25` Large Text toggle, 9-action key remapping with duplicate detection & Restore Defaults, on-screen subtitles + edge directional arrow for Shade spawns, and Reduce Motion toggle.

## [Phase 3] — Ticket-03 ("Đèn cạn dầu", Contract v1.2)
### Breaking Changes
- **Contract version:** Bumped `game.contract.json` from `1.1` to `1.2`.
- **Win condition replaced (`[THAY THẾ]`):** Removed early win (`all_lit`). Players must survive to dawn (`240s` / `270s` / `300s`) with at least `ceil(0.6 * total_lanterns)` lit (`3/5`, `4/6`, `5/7`) for `reason: "dawn_survived"`.
- **Lantern fuel & relight (`[THAY THẾ]`):** Lit lanterns consume `1.0` fuel/s, can be refueled (`+10` fuel/mote), extinguish at `0` (`lantern_out`), and relight for `5` motes (`relight: true`).
- **Safe zone & Shade `drain` (`[THAY THẾ]`):** Lit lanterns with `fuel < 30` lose their `6m` safe zone; `wander` shades target weak lanterns and drain `5` fuel/s in the new `drain` state (`fuel_drain` event every 60 ticks).
- **Scoring replaced (`[THAY THẾ]`):** `+5`/mote deposited, `+100` first light, `+40` relight, `+5` pulse (`+15` if draining), dawn bonus `+50 + floor(fuel)` per lit lantern + `50 * flames`. Time-left bonus removed.
### Added
- Progressive carry capacity (`10 + 2 * successful_lights`, max `20`), per-lantern fuel bars, `1 Hz` low-fuel blink, non-color unlit distinction (`20%` squash + tear marks), Colorblind Mode (`#00B3FF` shades, `#FFFFFF` + `⚠` danger UI), and `ADR-001`.

## [Phase 2] — Ticket-02 ("Ba hòn đảo", Contract v1.1)
### Breaking Changes
- Standardized all tuning constants (`6.0 m/s` run, `10` capacity, `10` lantern cost, `3` pulse cost, `fall_enabled=true`, 12-step tick order).
### Added
- 3 Nights (*Đảo Bến*, *Đảo Cau* twin islands + bridge + jump pads, *Đảo Chuông* 3-tier + ramps + bell tower + wind gusts), Dash (`14 m/s`), **Gió Lạc (Drifters)**, **Bùa Gió (Charms)**, Pause (`Esc`/`P`), persisted Settings, full HUD + off-screen lantern arrow, and procedural Web Audio API soundscape.

## [Phase 1] — PRD-0 ("Đảo Đèn Lồng", Contract v1.0)
### Added
- Playable Night 1 (*Đảo Bến*) with 5 Great Lanterns, Mây third-person movement/jump/camera, firefly pickup, lantern deposit/lighting, Shadow Ink chase/safe-zone/hit, Pulse stun/push, Three.js Whimsical Nightscape 3D renderer (+ shoreline floating lotus lanterns), and deterministic 60Hz headless CLI (`Contract v1.0`).
