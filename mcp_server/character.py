"""Character loader — reads character.json, messages, and emotion rules from characters/<id>/."""

import json
import os
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
CHARACTERS_DIR = PLUGIN_ROOT / "characters"


def _character_dir(character_id: str) -> Path:
    d = CHARACTERS_DIR / character_id
    if not d.is_dir():
        raise FileNotFoundError(f"Character '{character_id}' not found at {d}")
    return d


def load_character(character_id: str) -> dict:
    """Load character.json metadata."""
    meta_path = _character_dir(character_id) / "character.json"
    with meta_path.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_language(meta: dict, requested: str) -> str:
    """Pick the effective language: requested if supported, else character default, else 'ko'."""
    supported = meta.get("supportedLanguages", [])
    if requested in supported:
        return requested
    return meta.get("defaultLanguage", "ko")


def load_messages(character_id: str, language: str) -> dict:
    """Load messages.<lang>.json — falls back to character default language if requested not supported."""
    meta = load_character(character_id)
    lang = resolve_language(meta, language)
    msg_path = _character_dir(character_id) / f"messages.{lang}.json"
    with msg_path.open(encoding="utf-8") as f:
        return json.load(f)


def load_emotion_rules(character_id: str) -> dict:
    """Load emotion_rules.json — returns dict with 'priority', 'patterns', 'default'."""
    rules_path = _character_dir(character_id) / "emotion_rules.json"
    with rules_path.open(encoding="utf-8") as f:
        return json.load(f)
