# Phase Evaluations & Final Retrospective

## Per-Phase Quick Evaluation

### Phase 1 (`phase-1`)
- Met:
  - Full `PRD-0` gameplay loop on Đêm 1 – Đảo Bến (5 Great Lanterns `L1..L5`, Mây movement + jump + 3D camera yaw, firefly pickup, lantern deposit/lighting, Shadow Ink chase + lit lantern `safe_radius` protection + hit/invuln/drop, pulse stun/push/cooldown, win/loss/score/HUD/replay, and visual shoreline lotus lanterns).
  - Full `Test Contract v1.0` compliance: root `game.contract.json` synced with `TUNING`, headless CLI flags, exit code `2` on invalid scenario/inputs, 60Hz tick model, 3-decimal JSONL (`snapshot`, `event`, `end`), and byte-identical determinism.
- Not met / partial (honest status): None — all Phase 1 requirements and Test Contract v1.0 checks passed (`9/9` unit/contract tests).
- Harness / process adjustments:
  - Enforced the Pre-Code Gate (`AGENTS.md` -> `DESIGNS.md`, `SKILLS.md`, `OUTPUTS.md`, `assumptions.md`) before writing code, which avoided schema drift between `game.contract.json` and `engine.py`.

### Phase 2 (`phase-2`)
- Met:
  - Standardized all Ticket-02 constants (`6.0 m/s`, `10` motes, `10` lantern cost, `3` pulse cost, `fall_enabled=true`, 12-step tick order, `paused` freeze).
  - Implemented all 3 Nights (*Đảo Bến*, *Đảo Cau*, *Đảo Chuông*), Dash, Jump Pads, Ramps, Bell Tower, Wind Gusts, Gió Lạc (Drifters), Bùa Gió (Charms), 3-Night Menu/Intro/Settings/Pause/Dawn UI, full HUD + off-screen arrow, Web Audio SFX, and Contract v1.1 (`21,600` ticks in `2.573s`).
- Regression status on Phase 1:
  - All Phase 1 mechanics (movement, camera yaw, jump, pickup, deposit/light, safe zone, pulse, hit/loss, exit code 2, determinism) continue passing under Ticket-02's standardized constants.
- Harness / process adjustments:
  - Split `game/src/core/maps.py` out of `engine.py` so 3-night geometry stays modular and easy to extend in Phases 3–4.

### Phase 3 (`phase-3`)
- Met:
- Rule pivots & updated tests:
- Harness / process adjustments:

### Phase 4 (`phase-4`)
- Met:
- Benchmarks & release readiness:

---

## Final Retrospective
- **What worked well with AI:**
- **Where AI struggled & how it was caught:**
- **Most useful harness component:**
- **Token/cost summary & savings:**
- **What I would do differently next time:**
