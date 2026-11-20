"""Local HTTP server bridging Three.js 3D viewport with Python simulation core."""

from __future__ import annotations

import argparse
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from src.core.engine import GameEngine, StepInput


WEB_DIR = Path(__file__).resolve().parent.parent / "web"


class GameServerState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.engine = GameEngine()


class GameRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, state: GameServerState, **kwargs) -> None:
        self.state = state
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return  # Keep console clean during interactive play

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
                self._send_json(self.state.engine.snapshot())
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
                self._send_json(self.state.engine.reset(seed=seed))
                return
            if self.path == "/api/step":
                ticks = max(1, min(int(payload.get("ticks", 1)), 10))
                action = StepInput(
                    move_x=float(payload.get("move_x", 0.0)),
                    move_z=float(payload.get("move_z", 0.0)),
                )
                snap = self.state.engine.snapshot()
                for _ in range(ticks):
                    snap = self.state.engine.step(action)
                self._send_json(snap)
                return

        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)


def main() -> None:
    parser = argparse.ArgumentParser(description="Play Dao Den Long 3D")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    state = GameServerState()
    handler = partial(GameRequestHandler, state=state)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Dao Den Long 3D running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
