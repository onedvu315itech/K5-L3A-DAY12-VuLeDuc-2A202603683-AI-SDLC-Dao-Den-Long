# Phase 3 Verification Proof (`phase-3` — Ticket-03 & Test Contract v1.2)

## 1. Requirement Traceability Matrix

| Requirement (Ticket-03 / Contract v1.2) | Verification Method | Evidence | Result |
|---|---|---|---|
| `game.contract.json` (`1.2`) synced with `TUNING` | `test_contract_v12_json_matches_tuning` | All v1.2 keys (`fuel_max`, `win_ratio`, `capacity_max`, etc.) match | PASS |
| Fuel decay (`1/s`), refuel (`ceil((100-fuel)/10)`), `lantern_out`, `5`-mote relight | `test_fuel_decay_refuel_lantern_out_and_relight` | `refuel` (`amount:10, fuel:100.0`), `lantern_out`, `lantern_lit {relight:true}`, `relit_count:1` | PASS |
| Progressive capacity (`10 + 2 * successful_lights`, max `20`) | `test_fuel_decay_refuel_lantern_out_and_relight` | `capacity` increased from `10` to `12` after relight | PASS |
| Shade `drain` (`fuel < 30` loses safe zone, `5/s` drain, `fuel_drain` @ 60t, `+15` pulse) | `test_shade_drain_and_drain_pulse_bonus` | `fuel_drain` emitted, `state == "drain"`, pulse score `+15` | PASS |
| No early win; `dawn_survived` at `time_left_s == 0` with `>= 60%` lit | `test_no_early_win_and_dawn_survived` | Ran full `300` ticks to dawn (`reason: "dawn_survived"`) | PASS |
| Phase 1–2 non-replaced regression & `<= 30s` 21,600-tick run | `verify.py` (`13/13` tests + Nights 1–3 headless) | Night 3 (`21,600` ticks) completed in `3.248s`, byte-identical | PASS |
| Colorblind mode, fuel bars, `1 Hz` blink, 20% unlit squash | `game/web/index.html` + `test_web_server_api_bridge` | Persisted `ddl_colorblind` toggle (`#00B3FF` shades, `#FFFFFF` + `⚠`) | PASS |

## 2. Observed Output (`python3.12 game/scripts/verify.py`)

```text
Ran 13 tests in 4.769s

OK
==> Night 1 (1200 ticks) elapsed=1.325s | Determinism: PASS
==> Night 2 (1200 ticks) elapsed=1.325s | Determinism: PASS
==> Night 3 (21600 ticks) elapsed=3.248s | Determinism: PASS
ALL CHECKS PASSED
```
