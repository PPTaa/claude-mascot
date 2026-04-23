"""SessionStart hook — opens the mascot pane with emotion derived from the session source."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from mcp_server import character as char_loader
from mcp_server import emotion as emo_mod
from mcp_server import pane

DEBUG_LOG = Path("/tmp/claude_mascot_debug.log")


SOURCE_EMOTION_FALLBACK = {
    "startup": "happy",
    "resume":  "neutral",
    "clear":   "surprised",
}

SOURCE_MESSAGE_HINT = {
    "startup": {
        "ko": {"happy": "어서 와... 기다린 건 아니야!"},
        "en": {"happy": "Oh, you're back... not that I was waiting!"},
    },
    "resume": {
        "ko": {"neutral": "흥, 또 왔냥."},
        "en": {"neutral": "Hmph, back again."},
    },
    "clear": {
        "ko": {"surprised": "어? 기억이 사라졌다냥?!"},
        "en": {"surprised": "Huh? Memory wiped?!"},
    },
}


def _log(msg: str):
    try:
        with DEBUG_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[session_start] {datetime.now().isoformat()} {msg}\n")
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    source = payload.get("source", "startup")
    if source == "compact":
        return

    character_id = os.environ.get("CLAUDE_PLUGIN_USERCONFIG_CHARACTER", "nabi")
    language = os.environ.get("CLAUDE_PLUGIN_USERCONFIG_LANGUAGE", "ko")
    user_startup_emo = os.environ.get("CLAUDE_PLUGIN_USERCONFIG_STARTUPEMOTION")

    meta = char_loader.load_character(character_id)
    lang = char_loader.resolve_language(meta, language)

    if source == "startup" and user_startup_emo and user_startup_emo in meta.get("supportedEmotions", []):
        emotion = user_startup_emo
    else:
        emotion = SOURCE_EMOTION_FALLBACK.get(source, "neutral")

    hint = SOURCE_MESSAGE_HINT.get(source, {}).get(lang, {}).get(emotion)
    if hint:
        message = hint
    else:
        pool = char_loader.load_messages(character_id, language)
        message = emo_mod.pick_message(emotion, pool)

    _log(f"source={source} character={character_id} lang={lang} emotion={emotion}")

    try:
        pane.update_pane(character_id, language, emotion, message)
    except Exception as e:
        _log(f"error: {e}")


if __name__ == "__main__":
    main()
