"""Headless CLI runner for deterministic simulation checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.core.engine import GameEngine, StepInput


def run_headless(steps: list[dict[str, Any]], seed: int = 42) -> dict[str, Any]:
    """Execute a sequence of input steps headlessly and return final state."""
    engine = GameEngine(seed=seed)
    for item in steps:
        action = StepInput(
            move_x=float(item.get("move_x", 0.0)),
            move_z=float(item.get("move_z", 0.0)),
        )
        engine.step(action)
    return engine.snapshot()


def default_hello_steps(count: int = 90) -> list[dict[str, float]]:
    """Walk straight north (-Z) toward the hello lantern."""
    return [{"move_x": 0.0, "move_z": -1.0} for _ in range(count)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Dao Den Long headless runner")
    parser.add_argument("--input", type=Path, help="Optional JSON file with {seed, steps}")
    parser.add_argument("--steps", type=int, default=90, help="Steps for default hello run")
    parser.add_argument("--seed", type=int, default=42, help="Simulation seed")
    args = parser.parse_args()

    if args.input:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        seed = int(payload.get("seed", args.seed))
        steps = list(payload.get("steps", []))
    else:
        seed = args.seed
        steps = default_hello_steps(args.steps)

    result = run_headless(steps, seed=seed)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
