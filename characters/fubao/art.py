"""Fubao character art — frames-based renderer.

Each emotion has 3 state files (idle/blink/special) pre-rendered to ANSI
text by scripts/prerender.py at 3 sizes (small/medium/large). The runtime
just reads those text files — no chafa or image libraries needed.
"""
from pathlib import Path
import sys

RENDERER = "frames"

EMOTIONS = {
    "neutral":   dict(msg="대나무 먹는 중...",  sp_msg="으앙 졸려..."),
    "happy":     dict(msg="헤헤~ 기분 좋아",    sp_msg="냠냠 맛있어~"),
    "angry":     dict(msg="뿌우~ 삐졌어",       sp_msg="흥칫뿡이야!"),
    "shy":       dict(msg="으응... 부끄부끄",   sp_msg="휘릭... 숨을래"),
    "sad":       dict(msg="흐엥... 슬퍼...",    sp_msg="쭈르륵..."),
    "surprised": dict(msg="헙?! 뭐야 뭐야?",    sp_msg="으아앗!"),
    "love":      dict(msg="뿌잉뿌잉 ♥",         sp_msg="우효오~ ♥♥"),
}

_FRAMES_DIR = Path(__file__).parent / "frames"


def _pick_size(pane_height: int) -> str:
    if pane_height <= 11:
        return "small"
    if pane_height <= 20:
        return "medium"
    return "large"


def _load(size: str, emotion: str, state: str) -> list[str]:
    path = _FRAMES_DIR / size / f"{emotion}_{state}.txt"
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        print(f"[fubao] frame missing: {size}/{emotion}_{state}.txt", file=sys.stderr)
        return [f"[frame missing: {emotion}_{state}]"]


def render(cfg, emotion, state, message, pane_height):
    """state in {idle, blink, special}. Returns list[str] sized so that
    display.py's lines[:pane_lines] clip never drops the message row."""
    size = _pick_size(pane_height)
    pane_lines = max(7, min(29, pane_height - 1))
    img_lines = _load(size, emotion, state)
    # Reserve last 3 rows for [blank, message, blank]; clip image bottom.
    img_budget = max(1, pane_lines - 3)
    return img_lines[:img_budget] + ["", f"  {message}", ""]
