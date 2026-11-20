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

from src.bench import build_benchmark_engine, run_benchmark
from src.core.config import TUNING
from src.core.engine import ContractValidationError, GameEngine, StepInput, parse_inputs_frames
from src.core.leaderboard import add_leaderboard_entry, export_leaderboard, load_leaderboard
from src.headless import format_jsonl, run_contract_simulation
from src.play import GameRequestHandler, GameServerState
from src.soak import run_soak_test


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GAME_ROOT = Path(__file__).resolve().parent.parent


class TestPhase4ContractAndRelease(unittest.TestCase):
    def test_contract_v13_json_matches_tuning(self) -> None:
        contract_path = REPO_ROOT / "game.contract.json"
        self.assertTrue(contract_path.is_file(), "game.contract.json must exist at repo root")
        data = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual(data["contract_version"], "1.3")
        self.assertIn("bench_cmd", data)
        self.assertIn("soak_cmd", data)
        self.assertEqual(data["tuning"], TUNING.to_dict())

    def test_benchmark_scene_and_runner(self) -> None:
        b_eng = build_benchmark_engine(seed=42)
        self.assertEqual(len(b_eng.shades), 200)
        self.assertEqual(len(b_eng.motes), 100)
        self.assertEqual(sum(1 for l in b_eng.lanterns if l.lit and l.fuel == 100.0), 3)

        rep = run_benchmark(seed=42, duration_s=0.4, warmup_s=0.1)
        self.assertEqual(rep["contract_version"], "1.3")
        self.assertGreaterEqual(rep["avg_fps"], 60.0)
        self.assertGreaterEqual(rep["p1_low_fps"], 30.0)
        self.assertLessEqual(rep["load_ms"], 10000)

    def test_soak_runner_stability_and_memory(self) -> None:
        rep = run_soak_test(seed=7, nights=3)
        self.assertEqual(rep["crashes"], 0)
        self.assertEqual(len(rep["results"]), 3)
        self.assertLessEqual(rep["mem_end_mb"], 1.2 * rep["mem_start_mb"] + 1.0)

    def test_leaderboard_top10_sort_and_cli_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lb_path = Path(tmp) / "lb.json"
            out_path = Path(tmp) / "export.json"
            for i in range(12):
                add_leaderboard_entry(
                    name=f"May_{i:02d}",
                    score=100 + (i % 5) * 50,
                    nights_won=i % 4,
                    seed=42,
                    achieved_at=f"2026-11-20T17:00:{i:02d}+07:00",
                    path=lb_path,
                )
            loaded = load_leaderboard(lb_path)
            self.assertEqual(len(loaded), 10)
            self.assertGreaterEqual(loaded[0]["score"], loaded[1]["score"])
            exported = export_leaderboard(out_path, src_path=lb_path)
            self.assertEqual(len(exported["entries"]), 10)

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

    def test_no_early_win_and_dawn_survived(self) -> None:
        """Updated from Phase 2: lighting all lanterns no longer wins early; must survive to dawn >= 60%."""
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 9, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [[0, 0, 3]],
            "shades": [],
            "lanterns": [
                {"id": "L1", "pos": [0, 0, 8], "deposited": 0, "lit": False},
                {"id": "L2", "lit": True, "fuel": 100},
                {"id": "L3", "lit": True, "fuel": 100},
                {"id": "L4", "lit": True, "fuel": 100},
                {"id": "L5", "lit": True, "fuel": 100},
            ],
            "time_left_s": 5.0,
        }
        inputs = {
            "frames": [
                {"tick": 0, "move": [0, 1]},
                {"tick": 65, "move": [0, 0], "interact": True},
                {"tick": 66, "interact": False},
            ]
        }
        records = run_contract_simulation(
            seed=42, night=1, ticks=400, snapshot_every=100, scenario=scenario, inputs=inputs
        )
        events = [r for r in records if r["type"] == "event"]
        lit_ev = [e for e in events if e["name"] == "lantern_lit"][0]
        self.assertFalse(lit_ev["data"]["relight"])

        # Did NOT end early at tick 66; ran until dawn at tick 300
        self.assertEqual(records[-1]["ticks"], 300)
        self.assertEqual(records[-1]["state"], "won")
        go_ev = [e for e in events if e["name"] == "game_over"][0]
        self.assertEqual(go_ev["data"]["reason"], "dawn_survived")

    def test_fuel_decay_refuel_lantern_out_and_relight(self) -> None:
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 10, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [],
            "lanterns": [{"id": "L1", "pos": [0, 0, 0], "lit": True, "fuel": 2.0}],
            "time_left_s": 10.0,
        }
        # Refuel at tick 1 (fuel ~1.98 -> needs ceil(98/10)=10 motes -> fuel=100),
        # and verify second scenario for lantern_out + relight for 5 motes + capacity increase
        inputs = {"frames": [{"tick": 0, "interact": True}, {"tick": 1, "interact": False}]}
        recs = run_contract_simulation(
            seed=1, night=1, ticks=5, snapshot_every=5, scenario=scenario, inputs=inputs
        )
        refuel_ev = [r for r in recs if r["type"] == "event" and r["name"] == "refuel"][0]
        self.assertEqual(refuel_ev["data"]["amount"], 10)
        self.assertEqual(refuel_ev["data"]["fuel"], 100.0)

        # Lantern out + relight for 5 motes + capacity increases to 12
        scenario2 = {
            "player": {"pos": [0, 0, 0], "carried": 8, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [],
            "lanterns": [{"id": "L1", "pos": [0, 0, 0], "lit": True, "fuel": 0.5}],
            "time_left_s": 20.0,
        }
        inputs2 = {"frames": [{"tick": 40, "interact": True}, {"tick": 41, "interact": False}]}
        recs2 = run_contract_simulation(
            seed=1, night=1, ticks=60, snapshot_every=60, scenario=scenario2, inputs=inputs2
        )
        evs2 = [r for r in recs2 if r["type"] == "event"]
        self.assertTrue(any(e["name"] == "lantern_out" for e in evs2))
        relit_ev = [e for e in evs2 if e["name"] == "lantern_lit"][0]
        self.assertTrue(relit_ev["data"]["relight"])
        snap60 = [r for r in recs2 if r["type"] == "snapshot" and r["tick"] == 60][0]
        self.assertEqual(snap60["player"]["capacity"], 12)
        self.assertEqual(snap60["lanterns"][0]["relit_count"], 1)

    def test_shade_drain_and_drain_pulse_bonus(self) -> None:
        scenario = {
            "player": {"pos": [20, 0, 0], "carried": 5, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [{"id": "S1", "pos": [0.5, 1.0, 0.0], "state": "wander"}],
            "lanterns": [{"id": "L1", "pos": [0, 0, 0], "lit": True, "fuel": 20.0}],
            "time_left_s": 30.0,
        }
        # Let shade drain for 65 ticks (emits fuel_drain at tick 60), then verify score on pulse
        recs = run_contract_simulation(
            seed=3, night=1, ticks=70, snapshot_every=70, scenario=scenario, inputs=None
        )
        evs = [r for r in recs if r["type"] == "event"]
        self.assertTrue(any(e["name"] == "fuel_drain" and e["data"]["shade_id"] == "S1" for e in evs))
        snap70 = [r for r in recs if r["type"] == "snapshot" and r["tick"] == 70][0]
        self.assertEqual(snap70["shades"][0]["state"], "drain")

        # Pulse a draining shade awards +15
        scenario_p = {
            "player": {"pos": [1.0, 0, 0], "carried": 3, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [{"id": "S1", "pos": [0.0, 1.0, 0.0], "state": "drain", "target_lantern_id": "L1"}],
            "lanterns": [{"id": "L1", "pos": [0, 0, 0], "lit": True, "fuel": 20.0}],
            "time_left_s": 10.0,
        }
        inputs_p = {"frames": [{"tick": 0, "pulse": True}, {"tick": 1, "pulse": False}]}
        recs_p = run_contract_simulation(
            seed=3, night=1, ticks=5, snapshot_every=5, scenario=scenario_p, inputs=inputs_p
        )
        snap5 = [r for r in recs_p if r["type"] == "snapshot" and r["tick"] == 5][0]
        self.assertEqual(snap5["score"], 15)

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

            conn.request("GET", "/art.js")
            r_art = conn.getresponse()
            self.assertEqual(r_art.status, 200)
            art_js = r_art.read().decode("utf-8")
            self.assertIn("createMayPrefab", art_js)

            conn.request("GET", "/assets/lake.jpg")
            r_img = conn.getresponse()
            self.assertEqual(r_img.status, 200)
            self.assertGreater(len(r_img.read()), 1000)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
