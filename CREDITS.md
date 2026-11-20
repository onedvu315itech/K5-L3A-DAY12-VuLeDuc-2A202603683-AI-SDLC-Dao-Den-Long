# Credits & Attributions

## Original Lab Concept
- **Đảo Đèn Lồng** (Mây, Ông Đăng, Great Lanterns, Fireflies, Shadow Ink, Gió Lạc, Bùa Gió, Đảo Bến, Đảo Cau, Đảo Chuông) — original game concept from Day 12 AI SDLC Lab.

## Libraries & Runtime
- **Python 3.12 Standard Library** (`PSF License`) — 60Hz deterministic simulation core (`game/src/core/`), headless Contract v1.3 CLI (`game/src/headless.py`), benchmark (`game/src/bench.py`), soak test (`game/src/soak.py`), leaderboard persistence (`game/src/core/leaderboard.py`), and HTTP bridge (`game/src/play.py`).
- **Three.js r170** (`MIT License`, https://threejs.org/) — 3D WebGL scene rendering (`game/web/index.html`).

## Audio & 3D Visuals
- **3D Prefabs & Procedural Canvas Textures:** Procedural Three.js geometry, lathe silhouettes, and Canvas 2D textures (`game/web/art.js`, `game/web/index.html`), styled after the Whimsical Nightscape design system (`game/DESIGNS.md`).
- **2D Reference & UI Backdrop Illustrations (`game/web/assets/`):** `lake.jpg`, `bush.jpg`, `stone.jpg`, `tree.jpg`, `lamp_post.jpg`, `blinking_light.jpg`, `noel_moon.jpg`, `ghost.jpg`, `double_character.jpg`, and `conical_hat.jpg` — user-provided Whimsical Nightscape reference illustrations used for menu/intro backdrops and 3D prefab modeling blueprints.
- **Music & Sound Effects:** Background music track `game/web/assets/bgm.mp3` (user-provided) paired with procedural real-time Web Audio API synthesis (`game/web/index.html` — synthesized SFX for pickup, lantern ignition, pulse, hit, jump, dash, shade spawn, 10s countdown, win, and loss).

## AI Tools Used
- **Antigravity AI coding assistant (Gemini)** — requirements triage, harness maintenance (`AGENTS.md`, `DESIGNS.md`, `SKILLS.md`, `OUTPUTS.md`), core/3D implementation, and automated test verification (human-directed and verified at every phase gate).
