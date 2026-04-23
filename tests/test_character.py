import json
import os
import pytest
from pathlib import Path
from mcp_server import character


def test_load_character_returns_dict():
    c = character.load_character("nabi")
    assert c["id"] == "nabi"
    assert "happy" in c["supportedEmotions"]


def test_load_character_unknown_raises():
    with pytest.raises(FileNotFoundError):
        character.load_character("does-not-exist")


def test_resolve_language_explicit():
    c = character.load_character("nabi")
    assert character.resolve_language(c, "en") == "en"
    assert character.resolve_language(c, "ko") == "ko"


def test_resolve_language_fallback_to_default():
    c = character.load_character("nabi")
    assert character.resolve_language(c, "ja") == "ko"


def test_load_messages_returns_pool():
    msgs = character.load_messages("nabi", "ko")
    assert "happy" in msgs
    assert isinstance(msgs["happy"], list)
    assert len(msgs["happy"]) > 0


def test_load_emotion_rules():
    rules = character.load_emotion_rules("nabi")
    assert "priority" in rules
    assert "patterns" in rules
    assert rules["default"] == "neutral"
