"""Inline ASCII printer for PostToolUse hook — prints the character's current
emotion ASCII to stdout (shows up in the chat transcript).

Reads hook stdin JSON and extracts the emotion from the tool_input."""

import json
import os
import sys
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))


def get_ascii_art(character_id: str, emotion: str) -> str:
    ascii_dir = PLUGIN_ROOT / "characters" / character_id / "ascii"
    path = ascii_dir / f"{emotion}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    fallback = ascii_dir / "neutral.txt"
    if fallback.exists():
        return fallback.read_text(encoding="utf-8")
    return ""


def main():
    character_id = os.environ.get("CLAUDE_PLUGIN_USERCONFIG_CHARACTER", "nabi")
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    emotion = payload.get("tool_input", {}).get("emotion", "neutral")
    art = get_ascii_art(character_id, emotion)
    if art:
        GRAY = "\033[38;5;245m"
        RESET = "\033[0m"
        bar = f"{GRAY}{'─' * 36}{RESET}"
        sys.stdout.write(f"\n{bar}\n{art}\n{bar}\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
