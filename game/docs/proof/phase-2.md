# Phase 2 Verification Proof (`phase-2` — Ticket-02 & Test Contract v1.1)

## 1. Requirement Traceability Matrix

| Requirement (Ticket-02 / Contract v1.1) | Verification Method | Evidence | Result |
|---|---|---|---|
| Root `game.contract.json` (`1.1`) matches standardized tuning | `test_contract_v11_json_matches_tuning` | `game.contract.json` `tuning` == `TUNING.to_dict()` | PASS |
| Standardized move (`6.0`), jump (`7.0`, `-20`), dash (`14.0`, `0.2s`, `1.5s` cd) | `test_standardized_movement_jump_and_dash` | Walk `+6.0m/s`, Dash `+2.8m` in `12` ticks, `dash_cd_s > 1.0` | PASS |
| Pause (`pause: true` / `Esc` / `P`) freezes `sim_tick` & timers | `test_pause_freezes_sim_tick_and_timers` | `paused` at tick 11, `resumed` at tick 31, `sim_tick` stayed `10` at tick `20` | PASS |
| `10`-mote lantern deposit, `+10/mote`, `+100/lantern`, win bonus | `test_mote_deposit_lantern_and_win` | `mote_picked`, `deposit`, `lantern_lit`, `state == "won"` | PASS |
| Pulse (`3` motes, `5m` 3D radius, `120`-tick stun, `4m` push) & safe zone | `test_pulse_stuns_pushes_and_safe_zone_blocks` | `stunned_ids:["S1"]`, `carried:1`, pushed to `x=7.0` | PASS |
| Fall off island (`Y < -10`) `-1` flame, lose all motes, 60-tick respawn + `90` invuln | `test_fall_off_island_and_respawn` | `player_hit {by:"fall", flames:2, lost:4}`, respawn `[0,0,0]` with `invuln:true` | PASS |
| Night 2 (*Đảo Cau*): twin islands, jump pads, Gió Lạc steal & Pulse drop | `test_night2_jump_pad_and_drifter_steal_drop` | Launch lands `x > 45.0` grounded; `drifter_steal:3` then `drifter_drop:3` | PASS |
| Night 3 (*Đảo Chuông*): 3 tiers, ramps, bell tower, Bùa Gió, wind | `test_night3_charm_and_tiers_and_wind` | `charm_picked` (`C1`), `dash_cd_s == 0.0`, `charm_s > 9.0` | PASS |
| Full night `21,600` ticks in `<= 30s` & byte-identical determinism | `test_full_night_21600_ticks_under_30s_and_deterministic` + `verify.py` | Night 3 (`21,600` ticks) finished in **`2.573s`**; Nights 1/2/3 byte-identical | PASS |
| Invalid `--inputs` / `--scenario` exits with code `2` | `test_invalid_inputs_exit_code_2` | Subprocess returned exit code `2` | PASS |
| 3D WebGL 3-Night campaign, standardized palette, HUD, menus, Web Audio | `test_web_server_api_bridge` + `game/web/index.html` | `/api/state` Night 2 (`6` lanterns) HTTP 200; full menus/HUD/SFX implemented | PASS |

---

## 2. Verification Command & Verbatim Observed Output

Command: `python3.12 game/scripts/verify.py`

```text
test_contract_v11_json_matches_tuning (test_hello.TestPhase2ContractAndFeatures.test_contract_v11_json_matches_tuning) ... ok
test_fall_off_island_and_respawn (test_hello.TestPhase2ContractAndFeatures.test_fall_off_island_and_respawn) ... ok
test_full_night_21600_ticks_under_30s_and_deterministic (test_hello.TestPhase2ContractAndFeatures.test_full_night_21600_ticks_under_30s_and_deterministic) ... ok
test_invalid_inputs_exit_code_2 (test_hello.TestPhase2ContractAndFeatures.test_invalid_inputs_exit_code_2) ... ok
test_mote_deposit_lantern_and_win (test_hello.TestPhase2ContractAndFeatures.test_mote_deposit_lantern_and_win) ... ok
test_night2_jump_pad_and_drifter_steal_drop (test_hello.TestPhase2ContractAndFeatures.test_night2_jump_pad_and_drifter_steal_drop) ... ok
test_night3_charm_and_tiers_and_wind (test_hello.TestPhase2ContractAndFeatures.test_night3_charm_and_tiers_and_wind) ... ok
test_pause_freezes_sim_tick_and_timers (test_hello.TestPhase2ContractAndFeatures.test_pause_freezes_sim_tick_and_timers) ... ok
test_pulse_stuns_pushes_and_safe_zone_blocks (test_hello.TestPhase2ContractAndFeatures.test_pulse_stuns_pushes_and_safe_zone_blocks) ... ok
test_standardized_movement_jump_and_dash (test_hello.TestPhase2ContractAndFeatures.test_standardized_movement_jump_and_dash) ... ok
test_web_server_api_bridge (test_hello.TestPhase2ContractAndFeatures.test_web_server_api_bridge) ... ok

----------------------------------------------------------------------
Ran 11 tests in 3.422s

OK
==> Night 1 (1200 ticks) elapsed=1.276s | Determinism: PASS
==> Night 2 (1200 ticks) elapsed=1.423s | Determinism: PASS
==> Night 3 (21600 ticks) elapsed=2.573s | Determinism: PASS
ALL CHECKS PASSED
```
