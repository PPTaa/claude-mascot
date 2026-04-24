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


from characters.fubao import art as fubao_art


def test_fubao_renderer_constant():
    assert fubao_art.RENDERER == "frames"


def test_fubao_emotions_dict_complete():
    expected = {"neutral", "happy", "angry", "shy", "sad", "surprised", "love"}
    assert set(fubao_art.EMOTIONS.keys()) == expected
    for emo, cfg in fubao_art.EMOTIONS.items():
        assert "msg" in cfg and cfg["msg"]
        assert "sp_msg" in cfg and cfg["sp_msg"]


def test_fubao_pick_size_boundaries():
    assert fubao_art._pick_size(8) == "small"
    assert fubao_art._pick_size(11) == "small"
    assert fubao_art._pick_size(12) == "medium"
    assert fubao_art._pick_size(20) == "medium"
    assert fubao_art._pick_size(21) == "large"
    assert fubao_art._pick_size(30) == "large"


def test_fubao_load_missing_returns_placeholder(tmp_path, monkeypatch):
    # Point the loader at an empty directory so all frames are missing.
    monkeypatch.setattr(fubao_art, "_FRAMES_DIR", tmp_path)
    lines = fubao_art._load("medium", "happy", "idle")
    assert len(lines) >= 1
    assert "missing" in lines[0].lower()


def test_fubao_render_preserves_message(tmp_path, monkeypatch):
    monkeypatch.setattr(fubao_art, "_FRAMES_DIR", tmp_path)
    (tmp_path / "medium").mkdir()
    (tmp_path / "medium" / "happy_idle.txt").write_text("line1\nline2\n")
    cfg = fubao_art.EMOTIONS["happy"]
    out = fubao_art.render(cfg, "happy", "idle", "안녕", pane_height=14)
    assert isinstance(out, list)
    assert any("안녕" in line for line in out)


def test_fubao_render_keeps_message_under_clip(tmp_path, monkeypatch):
    monkeypatch.setattr(fubao_art, "_FRAMES_DIR", tmp_path)
    (tmp_path / "small").mkdir()
    (tmp_path / "small" / "neutral_idle.txt").write_text("\n".join([f"row{i}" for i in range(20)]))
    cfg = fubao_art.EMOTIONS["neutral"]
    out = fubao_art.render(cfg, "neutral", "idle", "MSG", pane_height=8)
    # pane_lines for pane=8 is 7; render should truncate image so MSG survives lines[:7]
    truncated = out[:7]
    assert any("MSG" in line for line in truncated)
