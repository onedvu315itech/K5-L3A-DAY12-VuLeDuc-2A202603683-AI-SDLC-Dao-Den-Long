"""Phase 1 regression + Phase 2 (Ticket-02 / Contract v1.1) unit, headless, and performance tests."""

from __future__ import annotations

from functools import partial
import http.client
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from src.core.config import TUNING
from src.core.engine import ContractValidationError, GameEngine, StepInput, parse_inputs_frames
from src.headless import format_jsonl, run_contract_simulation
from src.play import GameRequestHandler, GameServerState


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GAME_ROOT = Path(__file__).resolve().parent.parent


class TestPhase2ContractAndFeatures(unittest.TestCase):
    def test_contract_v11_json_matches_tuning(self) -> None:
        contract_path = REPO_ROOT / "game.contract.json"
        self.assertTrue(contract_path.is_file(), "game.contract.json must exist at repo root")
        data = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual(data["contract_version"], "1.1")
        self.assertEqual(data["tuning"], TUNING.to_dict())

    def test_standardized_movement_jump_and_dash(self) -> None:
        engine = GameEngine(seed=42, night=1)
        engine.reset(
            seed=42,
            night=1,
            scenario={"random_motes": False, "random_shades": False, "motes": [], "shades": []},
        )
        # Move +Z with cam_yaw_deg=0 for 60 ticks (1.0s) -> z = 6.0m
        for idx in range(60):
            engine.step(StepInput(move_x=0.0, move_z=1.0, cam_yaw_deg=0.0, jump=(idx == 0)))
        snap = engine.snapshot()
        self.assertAlmostEqual(snap["player"]["pos"][2], 6.0, places=2)
        self.assertTrue(snap["player"]["grounded"])

        # Dash for 12 ticks (0.2s) at 14.0 m/s -> +2.8m along +X (cam_yaw_deg=90, move=[0,1])
        events = engine.step(StepInput(move_x=0.0, move_z=1.0, cam_yaw_deg=90.0, dash=True))
        self.assertTrue(any(e["name"] == "dash" for e in events))
        for _ in range(11):
            engine.step(StepInput(move_x=0.0, move_z=1.0, cam_yaw_deg=90.0, dash=False))
        snap2 = engine.snapshot()
        self.assertAlmostEqual(snap2["player"]["pos"][0], 2.8, places=2)
        self.assertGreater(snap2["player"]["dash_cd_s"], 1.0)

    def test_pause_freezes_sim_tick_and_timers(self) -> None:
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [],
            "time_left_s": 100.0,
        }
        inputs = {
            "frames": [
                {"tick": 0, "move": [0, 1]},
                {"tick": 10, "pause": True},
                {"tick": 11, "pause": False},
                {"tick": 30, "pause": True},
                {"tick": 31, "pause": False},
            ]
        }
        records = run_contract_simulation(
            seed=1, night=1, ticks=40, snapshot_every=10, scenario=scenario, inputs=inputs
        )
        events = [r for r in records if r["type"] == "event"]
        self.assertTrue(any(e["name"] == "paused" and e["tick"] == 11 for e in events))
        self.assertTrue(any(e["name"] == "resumed" and e["tick"] == 31 for e in events))

        snap20 = [r for r in records if r["type"] == "snapshot" and r["tick"] == 20][0]
        self.assertEqual(snap20["state"], "paused")
        self.assertEqual(snap20["sim_tick"], 10)
        self.assertAlmostEqual(snap20["time_left_s"], 100.0 - 10 / 60.0, places=3)

    def test_mote_deposit_lantern_and_win(self) -> None:
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 9, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [[0, 0, 3]],
            "shades": [],
            "lanterns": [
                {"id": "L1", "pos": [0, 0, 8], "deposited": 0, "lit": False},
                {"id": "L2", "lit": True},
                {"id": "L3", "lit": True},
                {"id": "L4", "lit": True},
                {"id": "L5", "lit": True},
            ],
            "time_left_s": 120.0,
        }
        inputs = {
            "frames": [
                {"tick": 0, "move": [0, 1]},
                {"tick": 65, "move": [0, 0], "interact": True},
                {"tick": 66, "interact": False},
            ]
        }
        records = run_contract_simulation(
            seed=42, night=1, ticks=120, snapshot_every=20, scenario=scenario, inputs=inputs
        )
        events = [r for r in records if r["type"] == "event"]
        names = [e["name"] for e in events]
        self.assertIn("mote_picked", names)
        self.assertIn("deposit", names)
        self.assertIn("lantern_lit", names)
        self.assertEqual(records[-1]["state"], "won")

    def test_pulse_stuns_pushes_and_safe_zone_blocks(self) -> None:
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 4, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [{"id": "S1", "pos": [3.0, 1.0, 0.0], "state": "chase"}],
            "lanterns": [{"id": "L2", "lit": True}],
            "time_left_s": 120.0,
        }
        inputs = {"frames": [{"tick": 0, "pulse": True}, {"tick": 1, "pulse": False}]}
        records = run_contract_simulation(
            seed=7, night=1, ticks=20, snapshot_every=20, scenario=scenario, inputs=inputs
        )
        pulse_ev = [r for r in records if r["type"] == "event" and r["name"] == "pulse"][0]
        self.assertEqual(pulse_ev["data"]["stunned_ids"], ["S1"])
        snap20 = [r for r in records if r["type"] == "snapshot" and r["tick"] == 20][0]
        self.assertEqual(snap20["player"]["carried"], 1)
        self.assertEqual(snap20["shades"][0]["state"], "stunned")
        self.assertAlmostEqual(snap20["shades"][0]["pos"][0], 7.0, places=2)

    def test_fall_off_island_and_respawn(self) -> None:
        scenario = {
            "player": {"pos": [45, 0, 0], "carried": 4, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [],
            "time_left_s": 120.0,
        }
        records = run_contract_simulation(
            seed=2, night=1, ticks=150, snapshot_every=150, scenario=scenario, inputs=None
        )
        fall_ev = [
            r
            for r in records
            if r["type"] == "event" and r["name"] == "player_hit" and r["data"]["by"] == "fall"
        ][0]
        self.assertEqual(fall_ev["data"]["flames"], 2)
        self.assertEqual(fall_ev["data"]["lost"], 4)
        snap_end = [r for r in records if r["type"] == "snapshot" and r["tick"] == 150][0]
        self.assertEqual(snap_end["player"]["pos"], [0.0, 0.0, 0.0])
        self.assertTrue(snap_end["player"]["invuln"])

    def test_night2_jump_pad_and_drifter_steal_drop(self) -> None:
        # Test jump pad launch from (20,0,18) toward island B (70,0,0)
        engine = GameEngine(seed=10, night=2)
        engine.reset(
            seed=10,
            night=2,
            scenario={
                "player": {"pos": [20, 0, 18], "carried": 0, "flames": 3},
                "random_motes": False,
                "random_shades": False,
                "random_drifters": False,
                "motes": [],
                "shades": [],
                "drifters": [],
            },
        )
        for _ in range(100):
            engine.step(StepInput())
        snap = engine.snapshot()
        self.assertGreater(snap["player"]["pos"][0], 45.0)
        self.assertTrue(snap["player"]["grounded"])

        # Test Drifter stealing then dropping on Pulse
        scenario_d = {
            "player": {"pos": [0, 0, 0], "carried": 6, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "random_drifters": False,
            "motes": [],
            "shades": [],
            "drifters": [{"id": "D1", "pos": [0.5, 1.0, 0.0], "state": "chase", "stolen": 0}],
        }
        inputs_d = {"frames": [{"tick": 2, "pulse": True}, {"tick": 3, "pulse": False}]}
        recs = run_contract_simulation(
            seed=11, night=2, ticks=10, snapshot_every=10, scenario=scenario_d, inputs=inputs_d
        )
        evs = [r for r in recs if r["type"] == "event"]
        self.assertTrue(any(e["name"] == "drifter_steal" and e["data"]["amount"] == 3 for e in evs))
        self.assertTrue(any(e["name"] == "drifter_drop" and e["data"]["amount"] == 3 for e in evs))

    def test_night3_charm_and_tiers_and_wind(self) -> None:
        scenario = {
            "player": {"pos": [30, 0, 24.5], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "random_drifters": False,
            "wind_enabled": True,
            "motes": [],
            "shades": [],
            "drifters": [],
            "charms": [{"id": "C1", "pos": [30, 0, 25], "available": True}],
        }
        inputs = {
            "frames": [
                {"tick": 0, "move": [0, 1]},
                {"tick": 10, "dash": True},
                {"tick": 11, "dash": False},
            ]
        }
        recs = run_contract_simulation(
            seed=5, night=3, ticks=20, snapshot_every=20, scenario=scenario, inputs=inputs
        )
        evs = [r for r in recs if r["type"] == "event"]
        self.assertTrue(any(e["name"] == "charm_picked" and e["data"]["charm_id"] == "C1" for e in evs))
        snap20 = [r for r in recs if r["type"] == "snapshot" and r["tick"] == 20][0]
        self.assertEqual(snap20["player"]["dash_cd_s"], 0.0)
        self.assertGreater(snap20["player"]["charm_s"], 9.0)

    def test_full_night_21600_ticks_under_30s_and_deterministic(self) -> None:
        t0 = time.perf_counter()
        recs1 = run_contract_simulation(seed=77, night=3, ticks=21600, snapshot_every=60)
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 30.0)
        self.assertEqual(recs1[-1]["type"], "end")

        recs2 = run_contract_simulation(seed=77, night=3, ticks=21600, snapshot_every=60)
        self.assertEqual(format_jsonl(recs1), format_jsonl(recs2))

    def test_invalid_inputs_exit_code_2(self) -> None:
        with self.assertRaises(ContractValidationError):
            parse_inputs_frames({"frames": [{"tick": 5}, {"tick": 5}]})
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps({"frames": [{"tick": 5}, {"tick": 3}]}), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(GAME_ROOT / "src" / "headless.py"),
                    "--seed",
                    "42",
                    "--night",
                    "1",
                    "--inputs",
                    str(bad),
                    "--ticks",
                    "10",
                    "--out",
                    str(Path(tmp) / "out.jsonl"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)

    def test_web_server_api_bridge(self) -> None:
        state = GameServerState(seed=42, night=2)
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(GameRequestHandler, state=state))
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
            conn.request("GET", "/api/state")
            r1 = conn.getresponse()
            self.assertEqual(r1.status, 200)
            snap0 = json.loads(r1.read().decode("utf-8"))
            self.assertEqual(snap0["night"], 2)
            self.assertEqual(len(snap0["lanterns"]), 6)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
