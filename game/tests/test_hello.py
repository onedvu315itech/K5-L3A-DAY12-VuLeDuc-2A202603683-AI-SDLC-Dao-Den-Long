"""Phase 1 unit, Test Contract v1.0 headless CLI, determinism, and HTTP bridge tests."""

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
import unittest

from src.core.config import TUNING
from src.core.engine import ContractValidationError, GameEngine, StepInput, parse_inputs_frames
from src.headless import format_jsonl, run_contract_simulation
from src.play import GameRequestHandler, GameServerState


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GAME_ROOT = Path(__file__).resolve().parent.parent


class TestPhase1ContractAndSimulation(unittest.TestCase):
    def test_contract_json_matches_tuning(self) -> None:
        contract_path = REPO_ROOT / "game.contract.json"
        self.assertTrue(contract_path.is_file(), "game.contract.json must exist at repo root")
        data = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual(data["contract_version"], "1.0")
        self.assertEqual(data["tuning"], TUNING.to_dict())

    def test_movement_cam_yaw_and_jump(self) -> None:
        engine = GameEngine(seed=42)
        engine.reset(
            seed=42,
            scenario={"random_motes": False, "random_shades": False, "motes": [], "shades": []},
        )
        # Move +Z with cam_yaw_deg=0 for 60 ticks (1.0s) -> z = 7.0
        for idx in range(60):
            engine.step(StepInput(move_x=0.0, move_z=1.0, cam_yaw_deg=0.0, jump=(idx == 0)))
        snap = engine.snapshot()
        self.assertAlmostEqual(snap["player"]["pos"][0], 0.0, places=3)
        self.assertAlmostEqual(snap["player"]["pos"][2], 7.0, places=2)
        self.assertEqual(snap["player"]["pos"][1], 0.0)  # Landed within 1s (flight time = 2*7.5/20 = 0.75s)

        # Move with cam_yaw_deg=90 and move=[0, 1] -> x' = sin(90)=1, z' = cos(90)=0
        for _ in range(60):
            engine.step(StepInput(move_x=0.0, move_z=1.0, cam_yaw_deg=90.0))
        snap2 = engine.snapshot()
        self.assertAlmostEqual(snap2["player"]["pos"][0], 7.0, places=2)
        self.assertAlmostEqual(snap2["player"]["pos"][2], 7.0, places=2)

    def test_mote_pickup_deposit_and_win(self) -> None:
        scenario = json.loads(
            (GAME_ROOT / "tests" / "scenarios" / "win_scenario.json").read_text(encoding="utf-8")
        )
        inputs = json.loads(
            (GAME_ROOT / "tests" / "scenarios" / "win_inputs.json").read_text(encoding="utf-8")
        )
        records = run_contract_simulation(
            seed=42, night=1, ticks=200, snapshot_every=25, scenario=scenario, inputs=inputs
        )
        events = [r for r in records if r["type"] == "event"]
        names = [e["name"] for e in events]
        self.assertIn("mote_picked", names)
        self.assertIn("deposit", names)
        self.assertIn("lantern_lit", names)
        self.assertIn("game_over", names)

        end_rec = records[-1]
        self.assertEqual(end_rec["type"], "end")
        self.assertEqual(end_rec["state"], "won")
        self.assertEqual(end_rec["ticks"], 76)
        self.assertGreater(end_rec["score"], 700)

    def test_pulse_stuns_and_pushes_shade(self) -> None:
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 2, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [{"id": "S1", "pos": [3.0, 0.0, 0.0]}],
            "time_left_s": 120,
        }
        inputs = {"frames": [{"tick": 0, "pulse": True}, {"tick": 1, "pulse": False}]}
        records = run_contract_simulation(
            seed=7, night=1, ticks=5, snapshot_every=1, scenario=scenario, inputs=inputs
        )
        pulse_events = [r for r in records if r.get("type") == "event" and r.get("name") == "pulse"]
        self.assertEqual(len(pulse_events), 1)
        self.assertEqual(pulse_events[0]["data"]["stunned_ids"], ["S1"])

        snap1 = [r for r in records if r.get("type") == "snapshot" and r.get("tick") == 1][0]
        self.assertEqual(snap1["player"]["carried"], 1)
        self.assertEqual(snap1["shades"][0]["state"], "stunned")
        # Pushed from x=3.0 by pulse_push_m=5.0 -> x=8.0
        self.assertAlmostEqual(snap1["shades"][0]["pos"][0], 8.0, places=3)

    def test_lit_lantern_safe_radius_blocks_shade(self) -> None:
        engine = GameEngine(seed=1)
        engine.reset(
            seed=1,
            scenario={
                "player": {"pos": [0, 0, 0], "carried": 0, "flames": 3},
                "random_motes": False,
                "random_shades": False,
                "motes": [],
                "shades": [{"id": "S1", "pos": [8.0, 0.0, 0.0]}],
                "lanterns": [{"id": "L1", "pos": [0, 0, 0], "lit": True}],
            },
        )
        for _ in range(180):
            events = engine.step(StepInput())
            self.assertFalse(any(e["name"] == "player_hit" for e in events))
        snap = engine.snapshot()
        self.assertGreaterEqual(snap["shades"][0]["pos"][0], TUNING.safe_radius - 1e-3)
        self.assertEqual(snap["player"]["flames"], 3)

    def test_shade_hit_drops_motes_and_triggers_loss(self) -> None:
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 4, "flames": 1},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [{"id": "S1", "pos": [1.0, 0.0, 0.0]}],
            "time_left_s": 60,
        }
        records = run_contract_simulation(
            seed=1, night=1, ticks=10, snapshot_every=5, scenario=scenario, inputs=None
        )
        events = [r for r in records if r["type"] == "event"]
        hit_ev = [e for e in events if e["name"] == "player_hit"][0]
        self.assertEqual(hit_ev["data"], {"by": "shade", "flames": 0, "dropped": 2})
        over_ev = [e for e in events if e["name"] == "game_over"][0]
        self.assertEqual(over_ev["data"], {"result": "lost", "reason": "no_flames"})
        self.assertEqual(records[-1]["state"], "lost")

    def test_invalid_inputs_and_scenario_exit_code_2(self) -> None:
        with self.assertRaises(ContractValidationError):
            parse_inputs_frames({"frames": [{"tick": 5}, {"tick": 5}]})
        with self.assertRaises(ContractValidationError):
            parse_inputs_frames({"frames": [{"tick": 5}, {"tick": 3}]})

        with tempfile.TemporaryDirectory() as tmp:
            bad_inputs = Path(tmp) / "bad_inputs.json"
            out_jsonl = Path(tmp) / "out.jsonl"
            bad_inputs.write_text(
                json.dumps({"frames": [{"tick": 10, "move": [0, 1]}, {"tick": 9, "move": [0, 0]}]}),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(GAME_ROOT / "src" / "headless.py"),
                    "--seed",
                    "42",
                    "--night",
                    "1",
                    "--inputs",
                    str(bad_inputs),
                    "--ticks",
                    "20",
                    "--out",
                    str(out_jsonl),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertTrue(len(proc.stderr.strip()) > 0)

    def test_determinism_identical_jsonl(self) -> None:
        out_a = format_jsonl(run_contract_simulation(seed=123, night=1, ticks=240, snapshot_every=20))
        out_b = format_jsonl(run_contract_simulation(seed=123, night=1, ticks=240, snapshot_every=20))
        self.assertEqual(out_a, out_b)

    def test_web_server_api_bridge(self) -> None:
        state = GameServerState(seed=42)
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
            self.assertEqual(snap0["tick"], 0)
            self.assertEqual(len(snap0["lanterns"]), 5)

            conn.request(
                "POST",
                "/api/step",
                body=json.dumps({"move_x": 0.0, "move_z": 1.0, "cam_yaw_deg": 0.0, "ticks": 10}),
                headers={"Content-Type": "application/json"},
            )
            r2 = conn.getresponse()
            self.assertEqual(r2.status, 200)
            snap1 = json.loads(r2.read().decode("utf-8"))
            self.assertEqual(snap1["tick"], 10)
            self.assertGreater(snap1["player"]["pos"][2], 0.0)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
