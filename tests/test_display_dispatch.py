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
