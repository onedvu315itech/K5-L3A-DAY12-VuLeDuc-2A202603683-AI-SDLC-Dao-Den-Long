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

<!-- [Phase 1+] Append or update output schemas below with <!-- [Phase N] --> tags -->
