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

<!-- [Phase 1] PRD-0 & Test Contract v1.0 additions to single-job skills -->

## Phase 1 Skill Extensions
- **Skill 2 (Build Character):** Add conical hat (*nón lá*) with hanging small lantern to Mây; render jump height (`player.pos[1]`), stun pulse wave effect, and invulnerability blink feedback.
- **Skill 3 (Build Environment):** Render circular *Đảo Bến* (`R = 42m`, ground `Y = 0`), shoreline markers, and dynamic ambient/fog brightening proportional to `lit_lanterns / 5`.
- **Skill 4 (Build Movement & Core Logic):** Implement `cam_yaw_deg`-rotated normalized `move` (`x' = x*cosθ + z*sinθ`, `z' = -x*sinθ + z*cosθ`), edge-triggered `jump` (`Y = 0` ground + gravity), `60Hz` fixed timestep, `time_left_s`, and circular island clamping (`fall_enabled = false`).
- **Skill 5 (Build Entities & Interactions):** Implement 5 Great Lanterns (`L1..L5`), firefly spawning/pickup (`pickup_radius`, `carry_capacity`), edge-triggered `interact` deposit (`interact_radius`, `lantern_cost`), edge-triggered `pulse` (`pulse_cost`, `pulse_radius`, `pulse_push_m`, `pulse_stun_s`, `pulse_cooldown_s`), Shadow Ink chase/safe-radius avoidance/hit (`shade_speed`, `safe_radius`, `shade_hit_radius`, `invuln_s`, `hit_drop_ratio`), and scoring/win/loss rules.
- **Skill 6 (Build Headless & Test Contract CLI):** Update `game/src/headless.py` to support `--seed`, `--night 1`, `--scenario`, `--inputs`, `--ticks`, `--out`, `--snapshot-every`, strict schema validation (exit code `2` on invalid scenario/inputs), and exact JSONL output per `game/OUTPUTS.md`. Sync all tuning constants with root `game.contract.json`.
- **Skill 8 (Build HUD & Replay Flow):** *(Added in Phase 1)* Display flames, carried motes, lit lanterns (`x/5`), score, timer, pulse cooldown, and Win/Lose modal with Play Again reset in `game/web/index.html`.

<!-- [Phase 2] Ticket-02 ("Ba hòn đảo") extensions across core, 3-night maps, audio, HUD/menus, and Contract v1.1 -->

## Phase 2 Skill Extensions
- **Skill 2 (Build Character):** Update Mây's palette (`#E8E2D0` cloak, `#C8102E` scarf, *nón lá*) and add dash trail + wind-charm aura visuals.
- **Skill 3 (Build Environment):** Render all 3 Night maps (*Đảo Bến*, *Đảo Cau* twin islands + bridge + jump pads, *Đảo Chuông* 3-tier + ramps + bell tower + jump pad + wind gust leaves), using Ticket-02 standardized palette & ambient light formula.
- **Skill 4 (Build Movement & Core Logic):** Enforce Ticket-02 standardized constants (`6.0 m/s` run, `<=0.1s` accel/stop, `7.0 m/s` jump, `-20 m/s²` gravity), Dash (`14 m/s`, `0.2s`, `1.5s` cd), multi-island / multi-tier / ramp / jump-pad physics, Night 3 wind gusts, fall & respawn (`Y < -10`, 60-tick wait, 90-tick invuln), and the mandatory 12-step tick order + `paused` freeze.
- **Skill 5 (Build Entities & Interactions):** Implement standardized motes (cap `10`, `20` start -> `30` max, `240`-tick spawn, dropped motes `480`-tick TTL), `10`-mote lanterns + 30-tick safe-radius push-out, `3`-mote Pulse (`5m`, `120`-tick stun, `15`-tick `4m` push), Shade states (`spawning`, `wander`, `chase`, `recoil`, `stunned`), **Gió Lạc (Drifters)** (`D1, D2`), and **Bùa Gió (Charms)** (`C1, C2`).
- **Skill 6 (Build Headless & Test Contract CLI):** Upgrade `game/src/headless.py` & root `game.contract.json` to **Contract v1.1** (`--night 1|2|3`, new snapshot/scenario/input/event fields, `<= 30s` for `21,600` ticks).
- **Skill 8 (Build HUD, Menus & Audio):** Implement 3-Night campaign flow (Main Menu, Night Intro with Ông Đăng, Pause `Esc`/`P`, Settings persisted in `localStorage`, Dawn Victory screen), full Ticket-02 HUD (10-slot bar, red blinking timer `<=30s`, off-screen lantern arrow), and Web Audio API sound effects/ambience.
