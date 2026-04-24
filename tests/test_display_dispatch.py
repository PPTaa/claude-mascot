"""Tests for Animator dispatch and state computation."""
import pytest
from mcp_server.display import Animator


def test_animator_compute_state_returns_expected_keys():
    a = Animator("nabi", "neutral")
    a.t = 0
    state = a._compute_state()
    assert set(state.keys()) == {"state", "eyes", "msg", "deco", "shake"}
    assert state["state"] in ("idle", "blink", "special")


def test_animator_compute_state_idle_by_default():
    a = Animator("nabi", "neutral")
    a.t = 1
    a._next_blink = 9999
    a._next_special = 9999
    state = a._compute_state()
    assert state["state"] == "idle"


def test_animator_compute_state_blink():
    a = Animator("nabi", "neutral")
    a.t = 1
    a._next_blink = 1
    a._next_special = 9999
    state = a._compute_state()
    assert state["state"] == "blink"
    assert state["eyes"] == "= ="


def test_animator_compute_state_special_uses_sp_msg():
    a = Animator("nabi", "happy")
    a.t = 1
    a._next_blink = 9999
    a._next_special = 1
    state = a._compute_state()
    assert state["state"] == "special"
    assert state["msg"] == a.cfg["sp_msg"]


def test_animator_accepts_pane_height():
    a = Animator("nabi", "neutral", pane_height=22)
    assert a.pane_height == 22


def test_animator_pane_height_defaults_to_14():
    a = Animator("nabi", "neutral")
    assert a.pane_height == 14


def test_animator_dispatches_to_frames_renderer():
    a = Animator("fubao", "happy", pane_height=14)
    lines = a.tick()
    assert isinstance(lines, list)
    from characters.fubao.art import EMOTIONS
    joined = "\n".join(lines)
    assert EMOTIONS["happy"]["msg"] in joined or EMOTIONS["happy"]["sp_msg"] in joined


def test_animator_dispatches_to_programmatic_renderer():
    a = Animator("nabi", "happy", pane_height=14)
    lines = a.tick()
    assert isinstance(lines, list)
    assert len(lines) > 0
