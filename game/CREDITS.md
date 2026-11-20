# Credits & Attributions

## Original Lab Concept
- **Đảo Đèn Lồng** (Mây, Ông Đăng, Great Lanterns, Fireflies, Shadow Ink, Gió Lạc, Bùa Gió, Đảo Bến, Đảo Cau, Đảo Chuông) — original game concept from Day 12 AI SDLC Lab.

## Libraries & Runtime
- **Python 3.12 Standard Library** (`PSF License`) — 60Hz deterministic simulation core (`game/src/core/`), headless Contract v1.3 CLI (`game/src/headless.py`), benchmark (`game/src/bench.py`), soak test (`game/src/soak.py`), leaderboard persistence (`game/src/core/leaderboard.py`), and HTTP bridge (`game/src/play.py`).
- **Three.js r170** (`MIT License`, https://threejs.org/) — 3D WebGL scene rendering (`game/web/index.html`).

## Audio & 3D Visuals
- **3D Models & Textures:** 100% procedural Three.js geometry and materials (`game/web/index.html`), styled after the Whimsical Nightscape & Ticket-02 standardized palette (`game/DESIGNS.md`). No external copyrighted 3D models or textures were used.
- **Music & Sound Effects:** 100% procedural real-time Web Audio API synthesis (`game/web/index.html` — dual-oscillator ambient night drone and synthesized SFX for pickup, lantern ignition, pulse, hit, jump, dash, shade spawn, 10s countdown, win, and loss).

## AI Tools Used
- **Antigravity AI coding assistant (Gemini)** — requirements triage, harness maintenance (`AGENTS.md`, `DESIGNS.md`, `SKILLS.md`, `OUTPUTS.md`), core/3D implementation, and automated test verification (human-directed and verified at every phase gate).
