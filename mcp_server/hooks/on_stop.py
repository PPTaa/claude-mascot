"""Stop hook — at end of each Claude response, analyze last assistant message
and update mascot pane emotion via keyword classification."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from mcp_server import character as char_loader
from mcp_server import emotion as emo_mod
from mcp_server import pane

DEBUG_LOG = Path("/tmp/claude_mascot_debug.log")


def _log(msg: str):
    try:
        with DEBUG_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[on_stop] {datetime.now().isoformat()} {msg}\n")
    except Exception:
        pass


def _truthy_env(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


def _extract_last_assistant_text(transcript_path: str) -> str:
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").strip().splitlines()
    except Exception:
        return ""
    for line in reversed(lines):
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        msg = obj.get("message") if isinstance(obj.get("message"), dict) else obj
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [
                b.get("text", "") for b in content
                if isinstance(b, dict) and b.get("type") == "text"
            ]
            if parts:
                return "\n".join(parts)
    return ""


def main():
    if not _truthy_env("CLAUDE_PLUGIN_USERCONFIG_STOPHOOKENABLED", True):
        return

    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    character_id = os.environ.get("CLAUDE_PLUGIN_USERCONFIG_CHARACTER", "nabi")
    language = os.environ.get("CLAUDE_PLUGIN_USERCONFIG_LANGUAGE", "ko")

    transcript_path = payload.get("transcript_path", "")
    text = _extract_last_assistant_text(transcript_path) if transcript_path else ""

    rules = char_loader.load_emotion_rules(character_id)
    emotion = emo_mod.pick_emotion(text, rules)
    messages = char_loader.load_messages(character_id, language)
    message = emo_mod.pick_message(emotion, messages)

    _log(f"character={character_id} lang={language} emotion={emotion} text_len={len(text)}")

    try:
        pane.update_pane(character_id, language, emotion, message)
    except Exception as e:
        _log(f"error: {e}")


if __name__ == "__main__":
    main()
