# Phase Evaluations & Final Retrospective — Đảo Đèn Lồng (Day 12 AI SDLC)

## 1. Per-Phase Evaluation Summary

### Phase 1 (`phase-1` — PRD-0 & Contract v1.0)
- **Met:** Full playable Night 1 (*Đảo Bến*) with 5 Great Lanterns, camera-relative movement, jump, firefly pickup, lantern deposit/lighting, Shadow Ink chase + lit-lantern safe zone + hit/drop/invulnerability, Pulse stun/push/cooldown, Whimsical Nightscape 3D visuals (+ shoreline floating lotus lanterns), root `game.contract.json`, exit code `2` validation, and byte-identical JSONL determinism (`9/9` tests).
- **Not met / partial:** None.
- **Harness / process adjustments:** Established the **Mandatory Pre-Code Gate** in `AGENTS.md` routing requirements into `DESIGNS.md`, `SKILLS.md`, `OUTPUTS.md`, and `assumptions.md` before writing code.

### Phase 2 (`phase-2` — Ticket-02 "Ba hòn đảo" & Contract v1.1)
- **Met:** Standardized all tuning constants (`6.0 m/s` run, `10` capacity, `10` lantern cost, `3` pulse cost, `fall_enabled=true`, 12-step tick order, `paused` state), added Nights 2 (*Đảo Cau* twin islands + bamboo bridge + jump pads) & 3 (*Đảo Chuông* 3 tiers + ramps + bell tower + wind gusts), Dash, **Gió Lạc (Drifters)**, **Bùa Gió (Charms)**, 3-Night campaign menus/intro/pause/settings, full HUD + off-screen arrow, procedural Web Audio SFX, and `21,600`-tick headless execution in `1.605s` (`<= 30s` budget).
- **Regression status on Phase 1:** All Phase 1 mechanics passed under the standardized tuning values (`11/11` tests).
- **Harness / process adjustments:** Extracted `game/src/core/maps.py` from `engine.py` so multi-night terrain, cliff, ramp, and jump-pad math stayed isolated and token-cheap to read.

### Phase 3 (`phase-3` — Ticket-03 "Đèn cạn dầu" & Contract v1.2)
- **Met:** Replaced permanent lanterns and early win (`all_lit`) with integer-60th fuel (`0..100`, decay `1.0/s`, refuel `+10/mote`, `lantern_out`, `5`-mote `ever_lit` relight), Shade `drain` state (`5/s` drain on `fuel < 30`, `fuel_drain` every 60 ticks, safe zone disabled `< 30`), progressive capacity (`10..20`), `dawn_survived` win rule (`>= 60%` lit at dawn), new scoring, per-lantern fuel bars + `1 Hz` blink + `20%` unlit squash, Colorblind Mode, `ADR-001`, and `CHANGELOG.md` (`13/13` tests).
- **Rule pivots & updated tests:** Explicitly replaced `test_mote_deposit_lantern_and_win` with `test_no_early_win_and_dawn_survived` with documented rationale in `assumptions.md` and `ADR-001`.

### Phase 4 (`phase-4` — Ticket-04 "Bình minh: phát hành v1.0.0" & Contract v1.3)
- **Met:** Implemented `bench.py` (`bench.json`), `soak.py` (`soak.json`, 10 nights with `0` crashes and `+0.04 MB` RSS delta), persistent Top-10 local leaderboard + `--export-leaderboard`, `18px+` UI + `×1.25` Large Text mode, 9-action key remapping with conflict detection + restore defaults, subtitles + shade-spawn directional edge arrow, Reduce Motion toggle, complete 4-phase docs, and Release `v1.0.0` readiness.

---

## 2. Final Project Retrospective

### What Worked Well with AI
1. **Strict Core / Render Separation from CP0:** Keeping `game/src/core/` 100% pure Python stdlib (zero browser, OpenGL, or I/O dependencies) allowed headless simulation, soak tests, and unit tests to run in milliseconds-to-seconds (`21,600` ticks in `~1.6–3.2s`) while the Three.js WebGL client (`game/web/index.html`) rendered snapshots directly.
2. **Pre-Code `.md` Triage Gate:** Forcing every incoming specification (`PRD-0`, `Ticket-02`, `Ticket-03`, `Ticket-04`) to be triaged into `AGENTS.md`, `DESIGNS.md`, `SKILLS.md`, `OUTPUTS.md`, and `assumptions.md` *before* touching code eliminated speculative rewrites and ensured `game.contract.json` never drifted from `config.py`.
3. **Procedural Three.js + Web Audio API:** Using procedural Three.js meshes and Web Audio oscillators avoided external asset download/licensing issues, kept repo size tiny, and allowed instant palette/accessibility switches (such as Phase 3 Colorblind Mode and Phase 4 Reduce Motion).

### Where AI Struggled & How We Caught It
| Phase | Issue / Near-Miss | How Caught | Fix & Harness Prevention |
|---|---|---|---|
| Phase 1 | Strict whitelist on `--scenario` root keys could reject harmless grader metadata fields | Pre-test schema inspection against Contract v1.0 section D | Allowed root metadata keys while enforcing strict validation on all contract fields and strictly increasing `frames[].tick` (`exit code 2`) |
| Phase 1 | `urllib.request` in Windows sandbox routed `127.0.0.1` through system proxy (`HTTP 400`) | Live server probe command failed with `400 Direct IP access is not allowed` | Switched HTTP bridge tests to direct `http.client.HTTPConnection("127.0.0.1", port)` |
| Phase 3 | Floating-point subtraction (`1/60` and `5/60` fuel per tick) risked rounding drift at boundary `fuel == 30.0` or `0.0` | Ticket-03 section 1 note on exact `1/60` arithmetic | Represented fuel internally as integer sixtieths (`0..6000`) in `ADR-001`, rounding only on snapshot/event serialization |
| Phase 4 | `ctypes` `GetCurrentProcess()` on 64-bit Windows truncated the pseudo-handle `-1` without explicit `restype`, returning fallback `24.0 MB` in `soak.json` | Inspected `soak.json` output immediately after running `soak.py` (`mem_start_mb == 24.0`) | Added `restype = wintypes.HANDLE` and explicit `argtypes` on `K32GetProcessMemoryInfo`, verifying live RSS (`19.21 MB -> 19.25 MB`) |

### Most Useful Harness Components
1. **`AGENTS.md` + 4-Doc Action Routing (`DESIGNS.md`, `SKILLS.md`, `OUTPUTS.md`):** Kept `AGENTS.md` under 45 lines so every turn paid minimal context overhead while routing visual, logic, and contract tasks to dedicated files.
2. **`game/scripts/verify.py` + `verify-phase` Skill:** Single command running all unit tests, `game.contract.json` sync assertions, exit-code-2 checks, and two-run byte-identical JSONL determinism checks across Nights 1–3.
3. **`test_contract_v1X_json_matches_tuning`:** Automated unit test asserting `json.loads(Path("game.contract.json"))["tuning"] == TUNING.to_dict()`, making tuning desynchronization impossible.

### Token & Cost Summary
- **Total Estimated Tokens Across CP0 + Phases 1–4:** `~160k` tokens (`~$0.47` estimated cost).
  - CP0: `~18k` | Phase 1: `~32k` | Phase 2: `~48k` | Phase 3: `~26k` | Phase 4: `~36k`.
- **How We Saved Tokens:**
  - Read only the target module per skill (`maps.py` vs `engine.py` vs `index.html`) rather than dumping the entire repo into context.
  - Used `edit_file` for targeted surgical replacements in `index.html` and `test_hello.py` during Phases 3 and 4 instead of regenerating full files.
  - Caught contract edge cases in the Pre-Code `.md` triage step before writing code.

### What I Would Do Differently Next Time
- Split `game/web/index.html` into separate `styles.css`, `scene.js`, and `ui.js` modules starting in Phase 1 so visual and HUD edits in Phases 2–4 can target even smaller files.
- Add the cross-platform RSS memory helper (`get_rss_mb()`) to `scripts/verify.py` right in CP0 so memory stability is tracked from Phase 1 onward.
