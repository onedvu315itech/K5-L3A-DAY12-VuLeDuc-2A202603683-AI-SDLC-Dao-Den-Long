---
name: verify-phase
description: Run full verification (unit tests, headless contract check, determinism check) and save phase proof before tagging a release.
---

# Verify Phase Skill

Use this skill before ending work on any phase (`phase-1` through `phase-4`).

## Steps
1. Run the verification suite from the repository root:
   - Windows: `python3.12 game/scripts/verify.py`
   - macOS/Linux: `python3 game/scripts/verify.py`
2. Confirm exit code is `0` and all checks pass:
   - Unit tests (`game/tests/`)
   - Headless CLI execution (`src.headless` inside `game/`)
   - Determinism check (two independent runs produce identical JSON output)
3. Update the phase proof file in `game/docs/proof/` with the exact command run, observed output, and requirement traceability table.
4. Confirm git working tree only contains intended changes and no secrets (`.env`, API keys).
5. Only after verification passes, report results accurately citing only observed outputs.
