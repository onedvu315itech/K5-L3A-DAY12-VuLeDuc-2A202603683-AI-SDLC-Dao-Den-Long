"""Unit and headless tests for CP0 starter."""

from __future__ import annotations

from functools import partial
import http.client
from http.server import ThreadingHTTPServer
import json
import threading
import unittest

from src.core.engine import GameEngine, StepInput
from src.headless import default_hello_steps, run_headless
from src.play import GameRequestHandler, GameServerState


class TestHelloSimulation(unittest.TestCase):
    def test_walk_and_light_hello_lantern(self) -> None:
        engine = GameEngine(seed=42)
        self.assertFalse(engine.lanterns[0].lit)

        for _ in range(90):
            snap = engine.step(StepInput(move_x=0.0, move_z=-1.0))

        self.assertEqual(snap["tick"], 90)
        self.assertTrue(snap["lanterns"][0]["lit"])
        self.assertLess(snap["player"]["z"], -4.5)

    def test_determinism_identical_runs(self) -> None:
        steps = default_hello_steps(90)
        out_a = json.dumps(run_headless(steps, seed=99), sort_keys=True)
        out_b = json.dumps(run_headless(steps, seed=99), sort_keys=True)
        self.assertEqual(out_a, out_b)

    def test_web_server_api_bridge(self) -> None:
        state = GameServerState()
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

            conn.request(
                "POST",
                "/api/step",
                body=json.dumps({"move_x": 0.0, "move_z": -1.0, "ticks": 10}),
                headers={"Content-Type": "application/json"},
            )
            r2 = conn.getresponse()
            self.assertEqual(r2.status, 200)
            snap1 = json.loads(r2.read().decode("utf-8"))
            self.assertEqual(snap1["tick"], 10)
            self.assertLess(snap1["player"]["z"], 0.0)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
