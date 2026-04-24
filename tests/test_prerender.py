"""Tests for the prerender build script."""
import pytest
from pathlib import Path
from scripts import prerender


def test_sizes_constant_is_square():
    for name, (w, h) in prerender.SIZES.items():
        assert w == h, f"{name} is not square: {w}x{h}"
    assert prerender.SIZES["small"] == (10, 10)
    assert prerender.SIZES["medium"] == (20, 20)
    assert prerender.SIZES["large"] == (30, 30)


def test_states_constant():
    assert prerender.STATES == ["idle", "blink", "special"]


def test_find_raw_image_accepts_multiple_extensions(tmp_path):
    (tmp_path / "happy_idle.webp").write_bytes(b"fake")
    result = prerender.find_raw_image(tmp_path, "happy", "idle")
    assert result is not None
    assert result.suffix == ".webp"


def test_find_raw_image_returns_none_if_missing(tmp_path):
    assert prerender.find_raw_image(tmp_path, "happy", "idle") is None


def test_check_mode_reports_missing_frames(tmp_path):
    char_dir = tmp_path / "fubao"
    (char_dir / "frames" / "medium").mkdir(parents=True)
    (char_dir / "frames" / "medium" / "happy_idle.txt").write_text("x")
    missing = prerender.missing_frames(char_dir, ["happy"], ["idle"])
    # small and large are absent for (happy, idle); medium is present
    assert len(missing) == 2
    assert all(("happy", "idle") == (e, s) for _, e, s in missing)
