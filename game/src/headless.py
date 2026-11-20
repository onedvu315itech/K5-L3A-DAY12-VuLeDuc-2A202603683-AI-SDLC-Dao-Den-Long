"""Headless Test Contract v1.0 CLI runner for Đảo Đèn Lồng."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

GAME_DIR = Path(__file__).resolve().parent.parent
if str(GAME_DIR) not in sys.path:
    sys.path.insert(0, str(GAME_DIR))

from src.core.engine import (  # noqa: E402
    ContractValidationError,
    GameEngine,
    StepInput,
    parse_inputs_frames,
)


def load_json_file(path: Path, label: str) -> Any:
    """Load and parse a JSON file, raising ContractValidationError on failure (exit code 2)."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractValidationError(f"Cannot read {label} file '{path}': {exc}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractValidationError(f"Malformed JSON in {label} file '{path}': {exc}") from exc


def run_contract_simulation(
    *,
    seed: int = 42,
    night: int = 1,
    ticks: int = 600,
    snapshot_every: int = 10,
    scenario: dict[str, Any] | None = None,
    inputs: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Run deterministic headless simulation and return JSONL records (snapshots, events, end)."""
    if night != 1:
        raise ValueError(f"Unsupported --night {night} (only night 1 is supported in Phase 1).")
    if ticks < 0:
        raise ValueError(f"--ticks must be >= 0 (got {ticks}).")
    if snapshot_every <= 0:
        raise ValueError(f"--snapshot-every must be >= 1 (got {snapshot_every}).")

    frames_by_tick: dict[int, dict[str, Any]] = {}
    if inputs is not None:
        frames_by_tick = parse_inputs_frames(inputs)

    if frames_by_tick:
        max_input_tick = max(frames_by_tick.keys())
        # Frames beyond --ticks are ignored cleanly, already validated for strict increase
        _ = max_input_tick

    engine = GameEngine(seed=seed, night=night)
    engine.reset(seed=seed, scenario=scenario)

    records: list[dict[str, Any]] = []
    # Tick 0 snapshot (after scenario setup, before any input)
    records.append(engine.snapshot())

    move_x = 0.0
    move_z = 0.0
    cam_yaw_deg = 0.0
    jump = False
    interact = False
    pulse = False
    dash = False

    for k in range(ticks):
        if engine.state != "playing":
            break

        frame = frames_by_tick.get(k)
        if frame is not None:
            if "move" in frame:
                move_x = float(frame["move"][0])
                move_z = float(frame["move"][1])
            if "cam_yaw_deg" in frame:
                cam_yaw_deg = float(frame["cam_yaw_deg"])
            if "jump" in frame:
                jump = bool(frame["jump"])
            if "interact" in frame:
                interact = bool(frame["interact"])
            if "pulse" in frame:
                pulse = bool(frame["pulse"])
            if "dash" in frame:
                dash = bool(frame["dash"])

        step_events = engine.step(
            StepInput(
                move_x=move_x,
                move_z=move_z,
                cam_yaw_deg=cam_yaw_deg,
                jump=jump,
                interact=interact,
                pulse=pulse,
                dash=dash,
            )
        )
        records.extend(step_events)

        if engine.tick % snapshot_every == 0:
            records.append(engine.snapshot())

        if engine.state != "playing":
            break

    records.append(
        {
            "type": "end",
            "ticks": engine.tick,
            "state": engine.state,
            "score": engine.score,
        }
    )
    return records


def format_jsonl(records: list[dict[str, Any]]) -> str:
    return "\n".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) for r in records) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Đảo Đèn Lồng — Headless Test Contract v1.0")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic RNG seed")
    parser.add_argument("--night", type=int, default=1, help="Night number (1 for Phase 1)")
    parser.add_argument("--scenario", type=Path, default=None, help="Path to scenario JSON file")
    parser.add_argument("--inputs", type=Path, default=None, help="Path to inputs JSON file")
    parser.add_argument("--ticks", type=int, default=600, help="Maximum simulation ticks to run")
    parser.add_argument("--out", type=Path, default=None, help="Output JSONL file path")
    parser.add_argument(
        "--snapshot-every",
        type=int,
        default=10,
        help="Emit snapshot every N ticks (default: 10)",
    )

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        return code

    try:
        scenario_data = load_json_file(args.scenario, "scenario") if args.scenario else None
        inputs_data = load_json_file(args.inputs, "inputs") if args.inputs else None
        records = run_contract_simulation(
            seed=args.seed,
            night=args.night,
            ticks=args.ticks,
            snapshot_every=args.snapshot_every,
            scenario=scenario_data,
            inputs=inputs_data,
        )
    except ContractValidationError as exc:
        print(f"Contract validation error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Headless runtime error: {exc}", file=sys.stderr)
        return 1

    output_text = format_jsonl(records)
    if args.out is not None:
        try:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output_text, encoding="utf-8")
        except OSError as exc:
            print(f"Cannot write output file '{args.out}': {exc}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(output_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
