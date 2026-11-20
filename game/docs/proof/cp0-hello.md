# CP0 Verification Proof (Hello 3D + Headless)

## Traceability

| Requirement | Verification Method | Evidence | Result |
|---|---|---|---|
| Pure deterministic simulation core | `unittest` (`test_walk_and_light_hello_lantern`) | 3/3 tests passed in 0.542s | PASS |
| Headless execution & determinism | `game/scripts/verify.py` (2 independent runs of `src.headless --steps 90 --seed 42`) | Byte-identical JSON output (`tick: 90`, `lantern-hello` lit) | PASS |
| Playable 3D WebGL + HTTP bridge | `test_web_server_api_bridge` + live probe of `GET /`, `/api/state`, `/api/step`, `/api/reset` | All endpoints returned HTTP 200 and advanced simulation state | PASS |

## Command & Observed Output

Command: `python3.12 game/scripts/verify.py`

```text
test_determinism_identical_runs (test_hello.TestHelloSimulation.test_determinism_identical_runs) ... ok
test_walk_and_light_hello_lantern (test_hello.TestHelloSimulation.test_walk_and_light_hello_lantern) ... ok
test_web_server_api_bridge (test_hello.TestHelloSimulation.test_web_server_api_bridge) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.542s

OK
==> Determinism check: PASS (byte-identical outputs)
ALL CHECKS PASSED
```
