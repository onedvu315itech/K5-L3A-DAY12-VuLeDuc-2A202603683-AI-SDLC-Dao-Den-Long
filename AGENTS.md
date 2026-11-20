# AGENTS.md — Project Guide for AI Agents

<!-- [CP0] Baseline stack, architecture rules, doc routing, and pre-code confirmation gate -->
<!-- [Phase 1] Added PRD-0 / Test Contract v1.0 rules: root game.contract.json, 60Hz tick model, exit codes, and JSONL output -->
<!-- [Phase 2] Upgraded to Ticket-02 ("Ba hòn đảo") & Test Contract v1.1: 3 nights (1/2/3), standardized tuning, 12-step tick order, pause, drifters, charms, wind, <=30s headless budget -->
<!-- [Phase 3] Upgraded to Ticket-03 ("Đèn cạn dầu") & Test Contract v1.2: lantern fuel/decay/drain, dawn_survived win rule, progressive capacity, new scoring, colorblind mode, ADR + CHANGELOG -->
<!-- [Phase 4] Upgraded to Ticket-04 ("Bình minh: phát hành v1.0.0") & Test Contract v1.3: bench_cmd, soak_cmd, --export-leaderboard, accessibility (18px+ UI, large text, keybinds, subtitles, reduce motion), Release v1.0.0 -->

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
<!-- [Phase 1] Contract headless CLI from repo root: `python3 game/src/headless.py --seed <int> --night 1 [--scenario <file.json>] [--inputs <file.json>] --ticks <int> --out <file.jsonl> [--snapshot-every 10]` -->
<!-- [Phase 2] Contract v1.1: `--night` accepts `1`, `2`, or `3`; full night (up to 21,600 ticks) MUST complete in <= 30s; follow exact 12-step tick order and pause semantics -->
- **Run 3D game (from `game/`):** `python3.12 -m src.play` -> open `http://127.0.0.1:8000`
<!-- [Phase 4] Contract v1.3 CLI: `python3 game/src/bench.py --seed 42 --duration 30 --out bench.json`, `python3 game/src/soak.py --seed 7 --nights 10 --out soak.json`, `python3 game/src/play.py --export-leaderboard out.json` -->
<!-- [Phase 1] Root contract manifest: `game.contract.json` MUST live at repository root and its `tuning` numbers MUST match `game/src/core/` constants exactly -->

## 4. Architecture & Integrity Rules
1. **Strict core/render separation:** Game rules, physics, timers, RNG, and state transitions MUST live in `game/src/core/` with zero browser, OpenGL, or I/O dependencies.
2. **Headless is the source of truth:** `game/src/headless.py` and `game/src/play.py` both drive `game/src/core/`. Never duplicate game logic in `game/web/`.
3. **Determinism:** Fixed timestep (`dt`) and seeded deterministic RNG only. Same inputs MUST yield identical headless output.
4. **No test/proof fakery:** Never weaken assertions, hand-edit proof outputs, or silently skip invalidated tests (update/remove with reason in `game/docs/notes/assumptions.md`).
5. **Preserve harness & secrets:** Never commit `.env` or keys. Never delete `AGENTS.md`, `game/DESIGNS.md`, `game/SKILLS.md`, `game/OUTPUTS.md`, `.agents/`, or `.github/workflows/`.
