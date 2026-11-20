# Phase 4 Verification Proof (`phase-4` & Release `v1.0.0` — Ticket-04 / Contract v1.3)

## 1. Requirement Traceability Matrix

| Requirement (Ticket-04 / Contract v1.3) | Verification Method | Evidence | Result |
|---|---|---|---|
| `game.contract.json` (`1.3`) with `bench_cmd` & `soak_cmd` | `test_contract_v13_json_matches_tuning` | `contract_version == "1.3"`, `tuning == TUNING.to_dict()` | PASS |
| Benchmark Mode (`bench.py --seed 42 --duration 30 --out bench.json`) | Live 30s run + `test_benchmark_scene_and_runner` | [bench.json](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/bench.json): `avg_fps: 274.3` (`>= 60`), `p1_low_fps: 192.5` (`>= 30`), `load_ms: 1` (`<= 10000`) | PASS |
| Soak Test (`soak.py --seed 7 --nights 10 --out soak.json`) | Live 10-night run + `test_soak_runner_stability_and_memory` | [soak.json](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/soak.json): `crashes: 0`, `mem_start_mb: 19.21 -> mem_end_mb: 19.25` (`<= 1.2x`) | PASS |
| Local Top-10 Leaderboard & `--export-leaderboard out.json` | `test_leaderboard_top10_sort_and_cli_export` + live CLI test | Persistent Top-10 sorted by `(-score, achieved_at)`, exported via `--export-leaderboard` | PASS |
| Accessibility: 9-action keybinds + conflict check + restore defaults, subtitles + shade arrow, reduce motion, `18px+` & `×1.25` large text | [game/web/index.html](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/web/index.html) | All 4 accessibility features implemented and persisted in `localStorage` | PASS |
| Packaging, 4-phase `CHANGELOG.md`, `CREDITS.md`, `LICENSE`, 1–2 page `retro.md` | [CHANGELOG.md](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/CHANGELOG.md), [CREDITS.md](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/CREDITS.md), [retro.md](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/docs/notes/retro.md) | Complete documentation & root copies of `LICENSE`, `CREDITS.md`, `CHANGELOG.md` | PASS |
| Full regression on Phases 1–3 (`16/16` unit/contract tests + Nights 1–3 determinism) | `python3.12 game/scripts/verify.py` | `16/16` tests passed; Nights 1, 2, 3 byte-identical JSONL | PASS |

---

## 2. Observed Benchmark & Soak Outputs (Machine: Windows 11 AMD64, Python 3.12.16)

### `bench.json` (`python3.12 game/src/bench.py --seed 42 --duration 30 --out bench.json`)
```json
{
  "contract_version": "1.3",
  "avg_fps": 274.3,
  "p1_low_fps": 192.5,
  "frame_ms_p95": 4.07,
  "frames": 8230,
  "load_ms": 1,
  "peak_mem_mb": 21.38,
  "vsync_off": true,
  "renderer": "Three.js r170 WebGL / Python 3.12.16 1280x720 Bench Scene",
  "os": "Windows 11 (AMD64)"
}
```

### `soak.json` (`python3.12 game/src/soak.py --seed 7 --nights 10 --out soak.json`)
```json
{
  "nights": 10,
  "crashes": 0,
  "results": ["lost", "lost", "lost", "lost", "lost", "lost", "lost", "lost", "lost", "lost"],
  "mem_start_mb": 19.21,
  "mem_end_mb": 19.25,
  "duration_s": 1.48
}
```
