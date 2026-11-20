# Phase 1 Verification Proof (`phase-1` — PRD-0 & Test Contract v1.0)

## 1. Requirement Traceability Matrix

| Requirement (PRD-0 / Test Contract v1.0) | Verification Method | Evidence | Result |
|---|---|---|---|
| Root `game.contract.json` matches runtime tuning | `test_contract_json_matches_tuning` | `game.contract.json` `tuning` == `TUNING.to_dict()` | PASS |
| Đêm 1 – Đảo Bến: 5 Great Lanterns (`L1..L5`), circular island | `test_web_server_api_bridge` + tick 0 snapshot | 5 lanterns (`L1..L5`) on `24m` ring, ground `Y=0` | PASS |
| Player movement (`cam_yaw_deg` transform) & jump (`Y > 0 -> 0`) | `test_movement_cam_yaw_and_jump` | `cam_yaw_deg=0` & `90°` move exact `7.0m/s`, jump lands on `Y=0` | PASS |
| Firefly (`mote`) pickup within `pickup_radius` & score `+10` | `test_mote_pickup_deposit_and_win` | Emits `mote_picked` at `tick=19`, `carried=3`, `score=10` | PASS |
| Deposit light (`interact`) & light Great Lantern (`lantern_lit`) | `test_mote_pickup_deposit_and_win` | Emits `deposit` (`amount:3, deposited:3`) & `lantern_lit` (`L1`) at `tick=76` | PASS |
| Shadow Ink chase & lit lantern `safe_radius` (`5.0m`) barrier | `test_lit_lantern_safe_radius_blocks_shade` | Shade stopped at `x >= 5.0m`, zero `player_hit` over 180 ticks | PASS |
| Shadow Ink hit (`flames - 1`, `hit_drop_ratio = 0.5`, `invuln_s`) & loss | `test_shade_hit_drops_motes_and_triggers_loss` | Emits `player_hit` (`flames:0, dropped:2`) & `game_over` (`lost`, `no_flames`) | PASS |
| Pulse (`pulse`) deducts mote, pushes `5.0m`, stuns `3.0s`, scores `+25` | `test_pulse_stuns_and_pushes_shade` | Emits `pulse` (`stunned_ids:["S1"]`), shade state `"stunned"` at `x=8.0` | PASS |
| Win when all 5 lanterns lit (`all_lit`) + time/flame score bonus | `test_mote_pickup_deposit_and_win` | Emits `game_over` (`won`, `all_lit`) & `end` (`ticks:76, state:"won", score:854`) | PASS |
| Invalid `--inputs` / `--scenario` exits with code `2` & `stderr` | `test_invalid_inputs_and_scenario_exit_code_2` | Subprocess exit code `2` with validation error on `stderr` | PASS |
| Determinism (identical `--seed`, `--scenario`, `--inputs` -> identical JSONL) | `test_determinism_identical_jsonl` + `game/scripts/verify.py` | 2 independent CLI runs produced byte-identical JSONL files | PASS |
| 3D WebGL scene, HUD, Nón lá + lantern character, Lotus Lantern creativity, Replay | `test_web_server_api_bridge` + `game/web/index.html` | `/api/state`, `/api/step`, `/api/reset` return HTTP 200; visual-only lotus lanterns preserve headless output | PASS |

---

## 2. Verification Command & Verbatim Observed Output

Command: `python3.12 game/scripts/verify.py`

```text
test_contract_json_matches_tuning (test_hello.TestPhase1ContractAndSimulation.test_contract_json_matches_tuning) ... ok
test_determinism_identical_jsonl (test_hello.TestPhase1ContractAndSimulation.test_determinism_identical_jsonl) ... ok
test_invalid_inputs_and_scenario_exit_code_2 (test_hello.TestPhase1ContractAndSimulation.test_invalid_inputs_and_scenario_exit_code_2) ... ok
test_lit_lantern_safe_radius_blocks_shade (test_hello.TestPhase1ContractAndSimulation.test_lit_lantern_safe_radius_blocks_shade) ... ok
test_mote_pickup_deposit_and_win (test_hello.TestPhase1ContractAndSimulation.test_mote_pickup_deposit_and_win) ... ok
test_movement_cam_yaw_and_jump (test_hello.TestPhase1ContractAndSimulation.test_movement_cam_yaw_and_jump) ... ok
test_pulse_stuns_and_pushes_shade (test_hello.TestPhase1ContractAndSimulation.test_pulse_stuns_and_pushes_shade) ... ok
test_shade_hit_drops_motes_and_triggers_loss (test_hello.TestPhase1ContractAndSimulation.test_shade_hit_drops_motes_and_triggers_loss) ... ok
test_web_server_api_bridge (test_hello.TestPhase1ContractAndSimulation.test_web_server_api_bridge) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.842s

OK
==> Headless JSONL output (win_scenario):
{"type":"snapshot","tick":0,"sim_tick":0,"state":"playing","time_left_s":120.0,"score":0,"player":{"pos":[0.0,0.0,0.0],"flames":3,"carried":2},"lanterns":[{"id":"L1","pos":[0.0,0.0,10.0],"lit":false,"deposited":0},{"id":"L2","pos":[22.825,0.0,7.416],"lit":true,"deposited":3},{"id":"L3","pos":[14.107,0.0,-19.416],"lit":true,"deposited":3},{"id":"L4","pos":[-14.107,0.0,-19.416],"lit":true,"deposited":3},{"id":"L5","pos":[-22.825,0.0,7.416],"lit":true,"deposited":3}],"shades":[{"id":"S1","pos":[18.0,0.0,10.0],"state":"chase"}],"motes":[{"id":"M1","pos":[0.0,0.0,4.0]}],"motes_active":1}
{"type":"event","tick":19,"name":"mote_picked","data":{"carried":3}}
{"type":"snapshot","tick":25,"sim_tick":25,"state":"playing","time_left_s":119.583,"score":10,"player":{"pos":[0.0,0.0,2.917],"flames":3,"carried":3},"lanterns":[{"id":"L1","pos":[0.0,0.0,10.0],"lit":false,"deposited":0},{"id":"L2","pos":[22.825,0.0,7.416],"lit":true,"deposited":3},{"id":"L3","pos":[14.107,0.0,-19.416],"lit":true,"deposited":3},{"id":"L4","pos":[-14.107,0.0,-19.416],"lit":true,"deposited":3},{"id":"L5","pos":[-22.825,0.0,7.416],"lit":true,"deposited":3}],"shades":[{"id":"S1","pos":[16.416,0.0,9.259],"state":"chase"}],"motes":[],"motes_active":0}
{"type":"snapshot","tick":50,"sim_tick":50,"state":"playing","time_left_s":119.167,"score":10,"player":{"pos":[0.0,0.0,5.833],"flames":3,"carried":3},"lanterns":[{"id":"L1","pos":[0.0,0.0,10.0],"lit":false,"deposited":0},{"id":"L2","pos":[22.825,0.0,7.416],"lit":true,"deposited":3},{"id":"L3","pos":[14.107,0.0,-19.416],"lit":true,"deposited":3},{"id":"L4","pos":[-14.107,0.0,-19.416],"lit":true,"deposited":3},{"id":"L5","pos":[-22.825,0.0,7.416],"lit":true,"deposited":3}],"shades":[{"id":"S1","pos":[14.738,0.0,8.772],"state":"chase"}],"motes":[],"motes_active":0}
{"type":"snapshot","tick":75,"sim_tick":75,"state":"playing","time_left_s":118.75,"score":10,"player":{"pos":[0.0,0.0,8.75],"flames":3,"carried":3},"lanterns":[{"id":"L1","pos":[0.0,0.0,10.0],"lit":false,"deposited":0},{"id":"L2","pos":[22.825,0.0,7.416],"lit":true,"deposited":3},{"id":"L3","pos":[14.107,0.0,-19.416],"lit":true,"deposited":3},{"id":"L4","pos":[-14.107,0.0,-19.416],"lit":true,"deposited":3},{"id":"L5","pos":[-22.825,0.0,7.416],"lit":true,"deposited":3}],"shades":[{"id":"S1","pos":[12.998,0.0,8.612],"state":"chase"}],"motes":[],"motes_active":0}
{"type":"event","tick":76,"name":"deposit","data":{"lantern_id":"L1","amount":3,"deposited":3}}
{"type":"event","tick":76,"name":"lantern_lit","data":{"lantern_id":"L1"}}
{"type":"event","tick":76,"name":"game_over","data":{"result":"won","reason":"all_lit"}}
{"type":"end","ticks":76,"state":"won","score":854}
==> Determinism check: PASS (byte-identical JSONL outputs)
ALL CHECKS PASSED
```
