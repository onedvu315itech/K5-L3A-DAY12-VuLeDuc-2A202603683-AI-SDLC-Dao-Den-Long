# AGENTS.md — Project Guide for AI Agents

<!-- [CP0] Baseline stack, architecture rules, doc routing, and pre-code confirmation gate -->

## 1. Mandatory Pre-Code Gate (STOP & CONFIRM FIRST)
Whenever new phase requirements or tickets arrive (`PRD-0`, `Ticket-02`, `Ticket-03`, `Ticket-04`), **DO NOT write or edit game code yet**:
1. Triage the new context into:
   - `AGENTS.md` (general rules, commands, routing — tag new additions with `<!-- [Phase N] ... -->` comments)
   - [game/DESIGNS.md](game/DESIGNS.md) (visual template, character styles, colors, environment)
   - [game/SKILLS.md](game/SKILLS.md) (single-job agent skills)
   - [game/OUTPUTS.md](game/OUTPUTS.md) (exact output schemas and owning modules)
   - [game/docs/notes/assumptions.md](game/docs/notes/assumptions.md) (ambiguities, assumptions, acceptance criteria)
2. Present the `.md` updates to the user and **wait for explicit confirmation** before implementing code in `game/src/`, `game/web/`, or `game/tests/`.

## 2. Action Routing (Read Only What the Task Needs)
- **Before designing visuals / meshes / colors:** Read [game/DESIGNS.md](game/DESIGNS.md)
- **Before coding a specific module (1 job per skill):** Read [game/SKILLS.md](game/SKILLS.md)
- **Before changing CLI, API, Test Contract, or proof formats:** Read [game/OUTPUTS.md](game/OUTPUTS.md)
- **Before finishing or tagging a phase:** Follow [.agents/skills/verify-phase/SKILL.md](.agents/skills/verify-phase/SKILL.md) and update [game/docs/proof/](game/docs/proof/README.md), [game/docs/notes/assumptions.md](game/docs/notes/assumptions.md), and [game/docs/notes/ai-log.md](game/docs/notes/ai-log.md)

## 3. Stack & Commands
- **Project folder:** All game code, tests, scripts, and docs live under `game/`.
- **Language:** Python >=3.11 (stdlib only for core/headless/tests) + Three.js WebGL client (`game/web/`).
- **Verify all (unit tests + headless + determinism):** `python3.12 game/scripts/verify.py` (or `python3 game/scripts/verify.py` on macOS/Linux).
- **Run headless (from `game/`):** `python3.12 -m src.headless`
- **Run 3D game (from `game/`):** `python3.12 -m src.play` -> open `http://127.0.0.1:8000`

## 4. Architecture & Integrity Rules
1. **Strict core/render separation:** Game rules, physics, timers, RNG, and state transitions MUST live in `game/src/core/` with zero browser, OpenGL, or I/O dependencies.
2. **Headless is the source of truth:** `game/src/headless.py` and `game/src/play.py` both drive `game/src/core/`. Never duplicate game logic in `game/web/`.
3. **Determinism:** Fixed timestep (`dt`) and seeded deterministic RNG only. Same inputs MUST yield identical headless output.
4. **No test/proof fakery:** Never weaken assertions, hand-edit proof outputs, or silently skip invalidated tests (update/remove with reason in `game/docs/notes/assumptions.md`).
5. **Preserve harness & secrets:** Never commit `.env` or keys. Never delete `AGENTS.md`, `game/DESIGNS.md`, `game/SKILLS.md`, `game/OUTPUTS.md`, `.agents/`, or `.github/workflows/`.
