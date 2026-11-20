"""Persistent Top-10 local leaderboard for Đảo Đèn Lồng (Ticket-04 / Contract v1.3)."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any


GAME_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_LEADERBOARD_PATH = GAME_DIR / "data" / "leaderboard.json"
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_À-ỹ]{3,12}$")


def validate_player_name(name: Any) -> str:
    if not isinstance(name, str):
        raise ValueError("Tên người chơi phải là chuỗi ký tự.")
    cleaned = name.strip()
    if not NAME_PATTERN.match(cleaned):
        raise ValueError("Tên phải từ 3–12 ký tự (chữ cái, số, dấu gạch dưới hoặc tiếng Việt).")
    return cleaned


def load_leaderboard(path: Path = DEFAULT_LEADERBOARD_PATH) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data.get("entries", []) if isinstance(data, dict) else []
        return list(entries)[:10]
    except (OSError, json.JSONDecodeError):
        return []


def save_leaderboard(entries: list[dict[str, Any]], path: Path = DEFAULT_LEADERBOARD_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"entries": entries[:10]}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_leaderboard_entry(
    *,
    name: str,
    score: int,
    nights_won: int,
    seed: int = 42,
    achieved_at: str | None = None,
    path: Path = DEFAULT_LEADERBOARD_PATH,
) -> list[dict[str, Any]]:
    valid_name = validate_player_name(name)
    ts = achieved_at or datetime.now().astimezone().isoformat(timespec="seconds")
    entry = {
        "name": valid_name,
        "score": int(score),
        "nights_won": max(0, min(3, int(nights_won))),
        "achieved_at": ts,
        "seed": int(seed),
    }
    entries = load_leaderboard(path)
    entries.append(entry)
    # Sort by score descending; Python's Timsort is stable so earlier achieved entries stay above ties
    entries.sort(key=lambda item: (-int(item.get("score", 0)), str(item.get("achieved_at", ""))))
    top10 = entries[:10]
    save_leaderboard(top10, path)
    return top10


def export_leaderboard(out_path: Path, src_path: Path = DEFAULT_LEADERBOARD_PATH) -> dict[str, Any]:
    entries = load_leaderboard(src_path)
    payload = {"entries": entries}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
