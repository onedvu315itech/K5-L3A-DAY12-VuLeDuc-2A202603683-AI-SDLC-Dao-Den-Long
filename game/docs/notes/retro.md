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
- Regression status on Phase 1:
- Harness / process adjustments:

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
