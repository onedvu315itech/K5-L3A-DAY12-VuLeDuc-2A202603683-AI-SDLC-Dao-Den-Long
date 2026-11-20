# SKILLS.md — Single-Job Coding Agent Skills

<!-- [CP0] Atomic single-purpose skills; each skill owns ONE job only -->

Use **one skill per focused task**. Do not mix unrelated edits (e.g., do not edit gameplay physics while styling 3D meshes).

---

## Skill 1: Triage Phase Context (Pre-Code Gate)
- **Goal:** Convert a new PRD/Ticket into structured docs **before** writing any game code.
- **Read:** New ticket text + current `AGENTS.md`, `game/DESIGNS.md`, `game/SKILLS.md`, `game/OUTPUTS.md`, `game/docs/notes/assumptions.md`.
- **Steps:**
  1. Extract mandatory specs (numbers, commands, Test Contract schemas) vs ambiguities.
  2. Route visual rules -> `game/DESIGNS.md`, single-job workflows -> `game/SKILLS.md`, output formats -> `game/OUTPUTS.md`, general rules/routing -> `AGENTS.md`, assumptions/criteria -> `game/docs/notes/assumptions.md`.
  3. Mark all new/changed lines with `<!-- [Phase N] ... -->` comments.
  4. **STOP** and ask the user to review & confirm before touching `game/src/`, `game/web/`, or `game/tests/`.

## Skill 2: Build Character (3D Visuals Only)
- **Goal:** Create or refine Mây's 3D mesh, lantern light, and orientation/animation in the browser.
- **Read:** `game/DESIGNS.md`, `game/OUTPUTS.md` (`player` snapshot schema), `game/web/index.html`.
- **Rules:** Pure Three.js presentation in `game/web/` only. Read `snap.player` (`x, y, z, yaw`, etc.) — never compute position or collisions in JS.
- **Done check:** Character renders cleanly, faces movement direction, and syncs accurately to `/api/state`.

## Skill 3: Build Environment (3D Scene & Lighting Only)
- **Goal:** Build island terrain, sky, fog, moonlight, ambient props, and camera framing.
- **Read:** `game/DESIGNS.md`, `game/web/index.html`.
- **Rules:** Pure Three.js presentation in `game/web/` only. Visual landmarks/decorations must never alter simulation state or headless output.
- **Done check:** Scene loads with zero console errors and matches `game/DESIGNS.md` palette/camera rules.

## Skill 4: Build Movement & Core Logic (Headless Simulation Only)
- **Goal:** Implement deterministic movement, island bounds, fixed-timestep loop, timers, and RNG in Python.
- **Read:** `AGENTS.md`, `game/OUTPUTS.md`, `game/src/core/`.
- **Rules:** Pure Python stdlib in `game/src/core/` only. Zero browser, OpenGL, or file/network I/O. Use fixed `dt` and seeded RNG only.
- **Done check:** Unit tests in `game/tests/` pass and two headless runs produce identical output.

## Skill 5: Build Entities & Interactions
- **Goal:** Implement game objects (fireflies, Great Lanterns, Shadow Ink, win/loss/score rules) and mirror them in 3D.
- **Read:** `game/DESIGNS.md`, `game/OUTPUTS.md`, `game/src/core/`, `game/web/`.
- **Rules:** All interaction rules, spawn logic, and state transitions live in `game/src/core/`; `game/web/` only renders snapshot arrays/fields.
- **Done check:** Unit tests cover each interaction rule; 3D view reflects every state transition.

## Skill 6: Build Headless & Test Contract CLI
- **Goal:** Keep `game/src/headless.py` compliant with the exact phase Test Contract.
- **Read:** `game/OUTPUTS.md`, `game/src/headless.py`.
- **Rules:** Accept exact CLI args/input format, drive `game/src/core/`, emit exact schema (no extra debug noise on stdout).
- **Done check:** Sample scenario runs cleanly via CLI and matches `game/OUTPUTS.md`.

## Skill 7: Verify Phase & Save Proof
- **Goal:** Run real verification and document traceable proof before tagging.
- **Read:** `.agents/skills/verify-phase/SKILL.md`, `game/OUTPUTS.md`.
- **Steps:** Run `python3.12 game/scripts/verify.py`, record actual command output in `game/docs/proof/phase-N.md`, update `game/docs/notes/ai-log.md` and `game/docs/notes/retro.md`.
- **Done check:** Exit code `0`, proof matches real output, honest `PASS` / `NOT MET` status recorded.

<!-- [Phase 1+] Add new single-job skills below with <!-- [Phase N] --> tags as needed -->
