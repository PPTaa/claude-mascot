"""Tests for the fubao character."""
import pytest
from mcp_server import character


def test_fubao_character_loads():
    c = character.load_character("fubao")
    assert c["id"] == "fubao"
    assert set(c["supportedEmotions"]) == {
        "neutral", "happy", "angry", "shy", "sad", "surprised", "love"
    }


def test_fubao_messages_ko_has_all_emotions():
    msgs = character.load_messages("fubao", "ko")
    for emo in ["neutral", "happy", "angry", "shy", "sad", "surprised", "love"]:
        assert emo in msgs
        assert isinstance(msgs[emo], list)
        assert len(msgs[emo]) > 0


def test_fubao_messages_en_has_all_emotions():
    msgs = character.load_messages("fubao", "en")
    for emo in ["neutral", "happy", "angry", "shy", "sad", "surprised", "love"]:
        assert emo in msgs
        assert len(msgs[emo]) > 0


def test_fubao_emotion_rules_have_default():
    rules = character.load_emotion_rules("fubao")
    assert "priority" in rules
    assert "patterns" in rules
    assert rules["default"] == "neutral"
