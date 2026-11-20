"""Local HTTP server bridging Three.js 3D viewport with Python simulation core (Nights 1-3)."""

from __future__ import annotations

import argparse
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading

GAME_DIR = Path(__file__).resolve().parent.parent
if str(GAME_DIR) not in sys.path:
    sys.path.insert(0, str(GAME_DIR))

from src.core.engine import GameEngine, StepInput  # noqa: E402


WEB_DIR = GAME_DIR / "web"


class GameServerState:
    def __init__(self, seed: int = 42, night: int = 1) -> None:
        self.lock = threading.Lock()
        self.engine = GameEngine(seed=seed, night=night)
        self.recent_events: list[dict] = []

    def payload(self, step_events: list[dict] | None = None) -> dict:
        snap = self.engine.ui_snapshot()
        snap["events"] = step_events or []
        snap["recent_events"] = self.recent_events[-8:]
        return snap


class GameRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, state: GameServerState, **kwargs) -> None:
        self.state = state
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return

    def _send_json(self, data: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/api/state":
            with self.state.lock:
                self._send_json(self.state.payload())
            return
        if self.path == "/health":
            self._send_json({"ok": True})
            return
        super().do_GET()

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, HTTPStatus.BAD_REQUEST)
            return

        with self.state.lock:
            if self.path == "/api/reset":
                seed = payload.get("seed")
                night = payload.get("night")
                self.state.engine.reset(
                    seed=seed,
                    night=int(night) if night is not None else self.state.engine.night,
                )
                self.state.recent_events.clear()
                self._send_json(self.state.payload())
                return
            if self.path == "/api/step":
                ticks = max(1, min(int(payload.get("ticks", 1)), 10))
                move_x = float(payload.get("move_x", 0.0))
                move_z = float(payload.get("move_z", 0.0))
                cam_yaw_deg = float(payload.get("cam_yaw_deg", 0.0))
                jump = bool(payload.get("jump", False))
                interact = bool(payload.get("interact", False))
                pulse = bool(payload.get("pulse", False))
                dash = bool(payload.get("dash", False))
                pause = bool(payload.get("pause", False))
                all_events: list[dict] = []
                for idx in range(ticks):
                    ev = self.state.engine.step(
                        StepInput(
                            move_x=move_x,
                            move_z=move_z,
                            cam_yaw_deg=cam_yaw_deg,
                            jump=jump if idx == 0 else False,
                            interact=interact if idx == 0 else False,
                            pulse=pulse if idx == 0 else False,
                            dash=dash if idx == 0 else False,
                            pause=pause if idx == 0 else False,
                        )
                    )
                    if ev:
                        all_events.extend(ev)
                        self.state.recent_events.extend(ev)
                self._send_json(self.state.payload(all_events))
                return

        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)


def main() -> None:
    parser = argparse.ArgumentParser(description="Play Đảo Đèn Lồng 3D (Nights 1-3)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--night", type=int, default=1)
    args = parser.parse_args()

    state = GameServerState(seed=args.seed, night=args.night)
    handler = partial(GameRequestHandler, state=state)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Đảo Đèn Lồng 3D running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
