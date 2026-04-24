# Fubao Character Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a second mascot character `fubao` that renders from pre-rendered ANSI image frames (not programmatic ASCII art), selectable via existing `character` userConfig.

**Architecture:** New character folder `characters/fubao/` with a `RENDERER = "frames"` constant. A build-time script (`scripts/prerender.py`) converts raw JPG/PNG/WebP images to ANSI text at three sizes using `chafa`. The runtime reads those text files — **no** `chafa` dependency in production. Existing `Animator` in `mcp_server/display.py` gets a dispatch branch on each character's `RENDERER` constant, preserving the current nabi pipeline untouched.

**Tech Stack:** Python 3.10+, pytest, chafa (developer only), tmux, uv.

**Spec:** `docs/superpowers/specs/2026-04-24-fubao-character-design.md`

---

## File Structure

### New files
- `characters/fubao/character.json` — metadata
- `characters/fubao/emotion_rules.json` — stop-hook triggers
- `characters/fubao/messages.ko.json` / `messages.en.json` — panda-tone dialogue
- `characters/fubao/art.py` — frames renderer with `RENDERER = "frames"`
- `characters/fubao/raw/*.jpg` — 21 raw images (7 emotions × 3 states), committed
- `characters/fubao/raw/SOURCES.md` — per-file attribution
- `characters/fubao/frames/{small,medium,large}/*.txt` — 63 pre-rendered ANSI files
- `scripts/prerender.py` — dev-only build tool
- `tests/test_fubao.py` — character-specific tests
- `tests/test_display_dispatch.py` — Animator dispatch branch tests

### Modified files
- `characters/nabi/art.py` — add `RENDERER = "programmatic"` constant (one line)
- `mcp_server/display.py` — extract `_compute_state()`, add RENDERER branch, pass `pane_height` into `Animator.__init__`
- `.claude-plugin/plugin.json` — add `"fubao"` to `character` enum
- `README.md` / `README.ko.md` — add fubao to character list, document build workflow
- `CHANGELOG.md` — v0.2.0 entry

---

## Task 1: Add `RENDERER` constant to nabi

**Files:**
- Modify: `characters/nabi/art.py:1-2`

- [ ] **Step 1: Add the constant**

Open `characters/nabi/art.py` and insert a module constant at the top (after the docstring):

```python
"""Nabi character art — frames and renderer."""

RENDERER = "programmatic"

# ── Colors ──
O  = "\033[38;5;208m"    # orange
# ... (rest unchanged)
```

- [ ] **Step 2: Verify no behavior change**

Run the existing suite:
```
uv run --extra dev pytest tests/ -v
```
Expected: all existing tests pass.

- [ ] **Step 3: Commit**

```
git add characters/nabi/art.py
git commit -m "feat(nabi): declare RENDERER=programmatic constant"
```

---

## Task 2: Scaffold fubao metadata files

**Files:**
- Create: `characters/fubao/character.json`
- Create: `characters/fubao/emotion_rules.json`
- Create: `characters/fubao/messages.ko.json`
- Create: `characters/fubao/messages.en.json`

- [ ] **Step 1: Write failing test for character loader**

Create `tests/test_fubao.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify failure**

```
uv run --extra dev pytest tests/test_fubao.py -v
```
Expected: all 4 tests fail with `FileNotFoundError: Character 'fubao' not found`.

- [ ] **Step 3: Create `character.json`**

```json
{
  "id": "fubao",
  "displayName": "Fubao (느긋한 판다)",
  "description": "A cute, lazy panda that reacts to Claude Code activity through pre-rendered image frames",
  "license": "MIT",
  "renderer": "frames",
  "supportedEmotions": ["neutral", "happy", "angry", "shy", "sad", "surprised", "love"],
  "defaultLanguage": "ko",
  "supportedLanguages": ["ko", "en"]
}
```

- [ ] **Step 4: Create `emotion_rules.json`**

Copy from nabi — same triggers work fine:

```json
{
  "priority": ["angry", "happy", "sad", "shy", "surprised"],
  "patterns": {
    "angry": "(틀렸|잘못\\s*됐|같은\\s*실수|다시\\s*봐|wrong\\b|mistake|뒤질|뒤져|죽을래|화내|짜증|빡치|바보|멍청|꺼져|닥쳐|angry|shut\\s*up)",
    "happy": "(완료|성공|잘\\s*됐|잘됨|done\\b|works?\\b|passed|fixed|해결(?!\\s*안)|끝났)",
    "sad": "(에러|실패|fail(?:ed|ure)?|error|broken|안\\s*되|안됨|안된다|못\\s*해|못함|문제\\s*있)",
    "shy": "(감사|고마|thank|칭찬|잘했|굿굿|수고|최고)",
    "surprised": "(\\?!|어\\?|왜\\?|이상한데|wait\\b|갑자기|헉)"
  },
  "default": "neutral"
}
```

- [ ] **Step 5: Create `messages.ko.json`**

```json
{
  "happy": [
    "헤헤~ 기분 좋아",
    "냠냠 맛있어~",
    "우와~ 좋아 좋아!",
    "대나무 두 개 먹은 기분이야"
  ],
  "sad": [
    "흐엥... 슬퍼...",
    "쭈르륵...",
    "배고파서 슬퍼...",
    "힝... 대나무 없어"
  ],
  "angry": [
    "뿌우~ 삐졌어",
    "흥칫뿡이야!",
    "으르렁... 대나무 뺏지 마",
    "삐질 거야 진짜!"
  ],
  "surprised": [
    "헙?! 뭐야 뭐야?",
    "으아앗!",
    "냠?! 깜짝이야",
    "헙!"
  ],
  "shy": [
    "으응... 부끄부끄",
    "휘릭... 숨을래",
    "에헤... 쑥쓰러워",
    "뿌잉... 쳐다보지 마"
  ],
  "love": [
    "뿌잉뿌잉 ♥",
    "우효오~ ♥♥",
    "좋아좋아 대나무보다 좋아",
    "헤헤... 안아줘"
  ],
  "neutral": [
    "대나무 먹는 중...",
    "냠냠...",
    "음... 뭐하지",
    "꾸벅꾸벅... 졸려"
  ]
}
```

- [ ] **Step 6: Create `messages.en.json`**

```json
{
  "happy": [
    "Hehe~ feeling good",
    "Nom nom~ tasty bamboo",
    "Yay yay! So happy",
    "Two-bamboo kind of mood today"
  ],
  "sad": [
    "Uhn... so sad...",
    "Sniffle...",
    "Sad because hungry...",
    "No bamboo... sob"
  ],
  "angry": [
    "Hmph~ I'm pouting",
    "Don't steal my bamboo!",
    "Grrr... I'll roll on you",
    "Okay I'm really sulking now"
  ],
  "surprised": [
    "Huh?! What what?",
    "Whoa!",
    "Nom?! You startled me",
    "Eep!"
  ],
  "shy": [
    "Mmhm... embarrassing",
    "Rolling away to hide",
    "Ehe... don't look at me",
    "Poke... don't stare"
  ],
  "love": [
    "Fluff fluff ♥",
    "Woohoo~ ♥♥",
    "I like you more than bamboo",
    "Hehe... give me a hug"
  ],
  "neutral": [
    "Eating bamboo...",
    "Nom nom...",
    "Hmm... what to do",
    "Drifting off... sleepy"
  ]
}
```

- [ ] **Step 7: Run tests to verify pass**

```
uv run --extra dev pytest tests/test_fubao.py -v
```
Expected: all 4 tests pass.

- [ ] **Step 8: Commit**

```
git add characters/fubao/character.json characters/fubao/emotion_rules.json characters/fubao/messages.ko.json characters/fubao/messages.en.json tests/test_fubao.py
git commit -m "feat(fubao): scaffold character metadata, emotion rules, and messages"
```

---

## Task 3: Implement fubao `art.py` (renderer)

**Files:**
- Create: `characters/fubao/art.py`
- Create: `characters/fubao/frames/{small,medium,large}/` (empty dirs, `.gitkeep` files)
- Modify: `tests/test_fubao.py` (append new tests)

- [ ] **Step 1: Write failing tests for art.py**

Append to `tests/test_fubao.py`:

```python
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
    # Create a fake frame file so loader returns something
    (tmp_path / "medium").mkdir()
    (tmp_path / "medium" / "happy_idle.txt").write_text("line1\nline2\n")
    cfg = fubao_art.EMOTIONS["happy"]
    out = fubao_art.render(cfg, "happy", "idle", "안녕", pane_height=14)
    assert isinstance(out, list)
    assert any("안녕" in line for line in out)


def test_fubao_render_keeps_message_under_clip(tmp_path, monkeypatch):
    monkeypatch.setattr(fubao_art, "_FRAMES_DIR", tmp_path)
    (tmp_path / "small").mkdir()
    # 20-line "image" — larger than the smallest pane could show
    (tmp_path / "small" / "neutral_idle.txt").write_text("\n".join([f"row{i}" for i in range(20)]))
    cfg = fubao_art.EMOTIONS["neutral"]
    out = fubao_art.render(cfg, "neutral", "idle", "MSG", pane_height=8)
    # pane_lines for pane=8 is 7; render should truncate image so MSG survives lines[:7]
    truncated = out[:7]
    assert any("MSG" in line for line in truncated)
```

- [ ] **Step 2: Run tests to verify failure**

```
uv run --extra dev pytest tests/test_fubao.py -v
```
Expected: 6 new tests fail with `ModuleNotFoundError: characters.fubao.art`.

- [ ] **Step 3: Create `characters/fubao/art.py`**

```python
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
    """state ∈ {idle, blink, special}. Returns list[str] sized so that
    display.py's lines[:pane_lines] clip never drops the message row."""
    size = _pick_size(pane_height)
    pane_lines = max(7, min(29, pane_height - 1))
    img_lines = _load(size, emotion, state)
    # Reserve last 3 rows for [blank, message, blank]; clip image bottom.
    img_budget = max(1, pane_lines - 3)
    return img_lines[:img_budget] + ["", f"  {message}", ""]
```

- [ ] **Step 4: Create empty frame directories with `.gitkeep`**

```
mkdir -p characters/fubao/frames/small characters/fubao/frames/medium characters/fubao/frames/large
touch characters/fubao/frames/small/.gitkeep characters/fubao/frames/medium/.gitkeep characters/fubao/frames/large/.gitkeep
```

- [ ] **Step 5: Run tests to verify pass**

```
uv run --extra dev pytest tests/test_fubao.py -v
```
Expected: all 10 tests pass.

- [ ] **Step 6: Commit**

```
git add characters/fubao/art.py characters/fubao/frames/ tests/test_fubao.py
git commit -m "feat(fubao): implement frames-based art.py renderer"
```

---

## Task 4: Extract `_compute_state()` from Animator

**Files:**
- Modify: `mcp_server/display.py:20-69`
- Create: `tests/test_display_dispatch.py`

Current `Animator.tick()` mixes state computation and render call. Pull the state part into its own method so two rendering paths can share it.

- [ ] **Step 1: Write failing test for _compute_state**

Create `tests/test_display_dispatch.py`:

```python
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
    # Force next_blink/special far in the future so we stay idle
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
```

- [ ] **Step 2: Run test to verify failure**

```
uv run --extra dev pytest tests/test_display_dispatch.py -v
```
Expected: all 4 tests fail with `AttributeError: ... '_compute_state'`.

- [ ] **Step 3: Refactor `Animator.tick()`**

Replace `mcp_server/display.py:39-69` with:

```python
    def _compute_state(self):
        """Compute current animation state. Returns dict with keys:
        state ('idle'|'blink'|'special'), eyes, msg, deco, shake."""
        c = self.cfg
        if self.mode == "idle":
            if self.t >= self._next_special:
                self.mode = "special"
                self.mode_end = self.t + 4
                self._cur_sp_eyes = c["sp_eyes"]
                self._schedule("special", 25, 40)
            elif self.t >= self._next_blink:
                self.mode = "blink"
                self.mode_end = self.t + 2
                self._schedule("blink", 8, 15)
        elif self.t >= self.mode_end:
            self.mode = "idle"

        eyes = c["eyes"]
        msg = c["msg"]
        shake = 0
        state_name = "idle"
        if self.mode == "special":
            eyes = self._cur_sp_eyes
            msg = c["sp_msg"]
            if self.emo == "angry":
                shake = self.t % 2
            state_name = "special"
        elif self.mode == "blink":
            eyes = "= ="
            state_name = "blink"
        elif self.t % 20 < 3:
            eyes = c["alt_eyes"]

        deco = c["decos"][self.t % len(c["decos"])]
        return {"state": state_name, "eyes": eyes, "msg": msg, "deco": deco, "shake": shake}

    def tick(self):
        self.t += 1
        state = self._compute_state()
        return self.art_mod.render(
            self.cfg, state["eyes"], state["msg"], state["deco"], self.t, state["shake"],
        )
```

- [ ] **Step 4: Run both test suites to verify pass**

```
uv run --extra dev pytest tests/ -v
```
Expected: all existing nabi/character/emotion tests still pass + 4 new dispatch tests pass.

- [ ] **Step 5: Commit**

```
git add mcp_server/display.py tests/test_display_dispatch.py
git commit -m "refactor(display): extract Animator._compute_state() for dispatch reuse"
```

---

## Task 5: Add RENDERER dispatch branch + `pane_height` pass-through

**Files:**
- Modify: `mcp_server/display.py` (Animator.__init__, tick, main)
- Modify: `tests/test_display_dispatch.py` (append)

- [ ] **Step 1: Write failing test for frames dispatch**

Append to `tests/test_display_dispatch.py`:

```python
def test_animator_accepts_pane_height():
    a = Animator("nabi", "neutral", pane_height=22)
    assert a.pane_height == 22


def test_animator_pane_height_defaults_to_14():
    a = Animator("nabi", "neutral")
    assert a.pane_height == 14


def test_animator_dispatches_to_frames_renderer():
    a = Animator("fubao", "happy", pane_height=14)
    # tick() should call art.render with the frames signature and return list[str]
    lines = a.tick()
    assert isinstance(lines, list)
    # Message from EMOTIONS should appear (either msg or sp_msg depending on state)
    from characters.fubao.art import EMOTIONS
    joined = "\n".join(lines)
    assert EMOTIONS["happy"]["msg"] in joined or EMOTIONS["happy"]["sp_msg"] in joined


def test_animator_dispatches_to_programmatic_renderer():
    a = Animator("nabi", "happy", pane_height=14)
    lines = a.tick()
    assert isinstance(lines, list)
    assert len(lines) > 0
```

- [ ] **Step 2: Run tests to verify failure**

```
uv run --extra dev pytest tests/test_display_dispatch.py -v
```
Expected: new tests fail (pane_height param not accepted; fubao dispatch branch missing).

- [ ] **Step 3: Modify Animator.__init__ to accept `pane_height`**

In `mcp_server/display.py`, change the `Animator` class:

```python
class Animator:
    def __init__(self, character_id: str, emotion: str, custom_message: str = "", pane_height: int = 14):
        art_mod = import_module(f"characters.{character_id}.art")
        self.art_mod = art_mod
        self.cfg = art_mod.EMOTIONS.get(emotion, art_mod.EMOTIONS["neutral"])
        if custom_message:
            self.cfg = dict(self.cfg)
            self.cfg["msg"] = custom_message
        self.emo = emotion
        self.pane_height = pane_height
        self.t = 0
        self.mode = "idle"
        self.mode_end = 0
        self._cur_sp_eyes = None
        self._schedule("blink", 8, 15)
        self._schedule("special", 25, 40)
```

- [ ] **Step 4: Add RENDERER dispatch in `tick()`**

Replace the current `tick()` body (keeping `_compute_state()` intact):

```python
    def tick(self):
        self.t += 1
        state = self._compute_state()
        renderer = getattr(self.art_mod, "RENDERER", "programmatic")
        if renderer == "frames":
            return self.art_mod.render(
                self.cfg, self.emo, state["state"], state["msg"], self.pane_height,
            )
        return self.art_mod.render(
            self.cfg, state["eyes"], state["msg"], state["deco"], self.t, state["shake"],
        )
```

- [ ] **Step 5: Pass `pane_height` from `main()` into `Animator`**

In `mcp_server/display.py`, update the `main()` body:

```python
    anim = Animator(character_id, emotion, custom_message, pane_height=pane_height)
```

(Replace the current `anim = Animator(character_id, emotion, custom_message)` line.)

- [ ] **Step 6: Run all tests**

```
uv run --extra dev pytest tests/ -v
```
Expected: all 20+ tests pass.

- [ ] **Step 7: Commit**

```
git add mcp_server/display.py tests/test_display_dispatch.py
git commit -m "feat(display): dispatch on art.RENDERER and pass pane_height into Animator"
```

---

## Task 6: Build `scripts/prerender.py`

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/prerender.py`
- Create: `tests/test_prerender.py`

- [ ] **Step 1: Create package init**

```
mkdir -p scripts
```
Create `scripts/__init__.py` as an empty file.

- [ ] **Step 2: Write failing tests**

Create `tests/test_prerender.py`:

```python
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


def test_check_mode_reports_missing_frames(tmp_path, capsys):
    char_dir = tmp_path / "fubao"
    (char_dir / "frames" / "medium").mkdir(parents=True)
    (char_dir / "frames" / "medium" / "happy_idle.txt").write_text("x")
    missing = prerender.missing_frames(char_dir, ["happy"], ["idle"])
    # small and large are absent for (happy, idle); medium is present
    assert len(missing) == 2
    assert all(("happy", "idle") == (e, s) for _, e, s in missing)
```

- [ ] **Step 3: Run tests to verify failure**

```
uv run --extra dev pytest tests/test_prerender.py -v
```
Expected: all fail with `ModuleNotFoundError: scripts.prerender` or `AttributeError`.

- [ ] **Step 4: Implement `scripts/prerender.py`**

```python
"""Pre-render raw character images to ANSI text frames via chafa.

Usage:
    uv run scripts/prerender.py <character>            # render one character
    uv run scripts/prerender.py --all                  # all frames-renderer characters
    uv run scripts/prerender.py <character> --check    # report missing frames only
"""
import argparse
import json
import shutil
import subprocess
import sys
from itertools import product
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
CHARACTERS_DIR = PLUGIN_ROOT / "characters"

SIZES = {
    "small":  (10, 10),
    "medium": (20, 20),
    "large":  (30, 30),
}
STATES = ["idle", "blink", "special"]
RAW_EXTS = [".jpg", ".jpeg", ".png", ".webp"]


def find_raw_image(raw_dir: Path, emotion: str, state: str) -> Path | None:
    for ext in RAW_EXTS:
        candidate = raw_dir / f"{emotion}_{state}{ext}"
        if candidate.exists():
            return candidate
    return None


def missing_frames(char_dir: Path, emotions: list[str], states: list[str]) -> list[tuple[str, str, str]]:
    """Return list of (size, emotion, state) tuples whose frame text file is missing."""
    result = []
    for size_name in SIZES:
        for emotion, state in product(emotions, states):
            path = char_dir / "frames" / size_name / f"{emotion}_{state}.txt"
            if not path.exists():
                result.append((size_name, emotion, state))
    return result


def render_one(src: Path, out: Path, w: int, h: int) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["chafa", "-f", "symbols", "-c", "full",
         "--size", f"{w}x{h}", "--polite", "on", str(src)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"chafa failed on {src}: {result.stderr}")
    out.write_text(result.stdout, encoding="utf-8")


def render_character(character_id: str, check_only: bool = False) -> int:
    char_dir = CHARACTERS_DIR / character_id
    meta_path = char_dir / "character.json"
    if not meta_path.exists():
        print(f"error: character '{character_id}' not found at {char_dir}", file=sys.stderr)
        return 1

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("renderer") != "frames":
        print(f"error: '{character_id}' is not a frames-renderer character", file=sys.stderr)
        return 1

    emotions = meta["supportedEmotions"]

    if check_only:
        missing = missing_frames(char_dir, emotions, STATES)
        if missing:
            print(f"{len(missing)} missing frame file(s):")
            for size, emo, st in missing:
                print(f"  {size}/{emo}_{st}.txt")
            return 1
        print(f"all {len(SIZES) * len(emotions) * len(STATES)} frames present")
        return 0

    if shutil.which("chafa") is None:
        print("error: chafa not installed. Install with 'brew install chafa' (macOS) or your package manager.", file=sys.stderr)
        return 1

    raw_dir = char_dir / "raw"
    missing_raw = []
    rendered = 0
    for emotion, state in product(emotions, STATES):
        src = find_raw_image(raw_dir, emotion, state)
        if src is None:
            missing_raw.append(f"{emotion}_{state}")
            continue
        for size_name, (w, h) in SIZES.items():
            out = char_dir / "frames" / size_name / f"{emotion}_{state}.txt"
            render_one(src, out, w, h)
            rendered += 1

    print(f"rendered {rendered} frame files")
    if missing_raw:
        print(f"warning: {len(missing_raw)} raw image(s) missing:", file=sys.stderr)
        for name in missing_raw:
            print(f"  raw/{name}.<jpg|png|webp>", file=sys.stderr)
        return 1
    return 0


def list_frames_characters() -> list[str]:
    result = []
    for char_dir in CHARACTERS_DIR.iterdir():
        if not char_dir.is_dir():
            continue
        meta = char_dir / "character.json"
        if not meta.exists():
            continue
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if data.get("renderer") == "frames":
            result.append(char_dir.name)
    return result


def main():
    ap = argparse.ArgumentParser(description="Pre-render character images to ANSI text frames")
    ap.add_argument("character", nargs="?", help="Character id (e.g. 'fubao')")
    ap.add_argument("--all", action="store_true", help="Render all frames-renderer characters")
    ap.add_argument("--check", action="store_true", help="Only report missing frames, do not render")
    args = ap.parse_args()

    if args.all:
        chars = list_frames_characters()
        if not chars:
            print("no frames-renderer characters found")
            return 0
        exit_code = 0
        for c in chars:
            exit_code = max(exit_code, render_character(c, check_only=args.check))
        return exit_code

    if not args.character:
        ap.error("character id required (or pass --all)")

    return render_character(args.character, check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify pass**

```
uv run --extra dev pytest tests/test_prerender.py -v
```
Expected: all 5 tests pass.

- [ ] **Step 6: Commit**

```
git add scripts/__init__.py scripts/prerender.py tests/test_prerender.py
git commit -m "feat(scripts): add prerender.py build tool (chafa image → ANSI text frames)"
```

---

## Task 7: Source raw panda images + attribution

**Files:**
- Create: `characters/fubao/raw/{emotion}_{state}.{jpg|png|webp}` × 21
- Create: `characters/fubao/raw/SOURCES.md`

This task has a manual component: the implementer must obtain CC-licensed or public-domain panda images. Use search sources in this order:
1. **Wikimedia Commons** (Category: Giant pandas) — CC-BY / CC-BY-SA / PD
2. **Flickr Creative Commons** (filter: CC-BY / CC-BY-SA / PD)
3. **Unsplash / Pexels** (generic pandas, free commercial use)

Avoid images of the real Fubao panda from Everland unless under a clearly reusable license — the character name is a nod to her, but assets should be generic pandas for safety.

- [ ] **Step 1: Gather 7 base panda images**

Pick 7 panda images that loosely map to emotions (calm, playful, grumpy, curled, lying/sad, alert, cuddly). Each should be reasonably square, ≤ 300 KB after resizing. Save to `characters/fubao/raw/` with these base filenames:

- `neutral_idle.jpg` — panda sitting or chewing bamboo calmly
- `happy_idle.jpg` — panda playing or rolling
- `angry_idle.jpg` — panda with grumpy/closed-eye pose
- `shy_idle.jpg` — panda half-hidden / peeking
- `sad_idle.jpg` — panda lying down
- `surprised_idle.jpg` — panda alert / ears up
- `love_idle.jpg` — panda cuddling / hugging something

- [ ] **Step 2: Derive blink + special variants**

For each emotion, provide two more variants. Simplest approach: duplicate the idle image and the name changes only — the prerendered output will be identical, which is fine for v1 (no real animation). Later iterations can swap in distinct shots.

```
# From within characters/fubao/raw/:
for emo in neutral happy angry shy sad surprised love; do
  cp ${emo}_idle.jpg ${emo}_blink.jpg
  cp ${emo}_idle.jpg ${emo}_special.jpg
done
```

(If you have distinct "blink" or "special" images, save those instead of copying.)

- [ ] **Step 3: Verify all 21 raw files exist**

```
ls characters/fubao/raw/*.{jpg,jpeg,png,webp} 2>/dev/null | wc -l
```
Expected: `21`

- [ ] **Step 4: Write `SOURCES.md`**

Create `characters/fubao/raw/SOURCES.md`:

```markdown
# Fubao raw image sources

All images are licensed for reuse. For each source URL, note the license
and attribution as required.

| File | Source URL | Author | License | Modifications |
|------|------------|--------|---------|---------------|
| neutral_idle.jpg | <url> | <author> | CC-BY 4.0 | resized |
| neutral_blink.jpg | (copy of neutral_idle.jpg) | — | — | duplicate |
| neutral_special.jpg | (copy of neutral_idle.jpg) | — | — | duplicate |
| happy_idle.jpg | <url> | <author> | CC-BY-SA 4.0 | resized |
| ... | | | | |
```

Fill in real URLs, authors, licenses for each non-duplicate file.

- [ ] **Step 5: Commit**

```
git add characters/fubao/raw/
git commit -m "feat(fubao): add raw panda images and source attribution"
```

---

## Task 8: Run prerender to generate `frames/`

**Files:**
- Generated: `characters/fubao/frames/{small,medium,large}/*.txt` (63 files)

- [ ] **Step 1: Verify chafa is installed**

```
which chafa || brew install chafa
```

- [ ] **Step 2: Run the prerender script**

```
uv run scripts/prerender.py fubao
```
Expected output: `rendered 63 frame files`

- [ ] **Step 3: Verify file count**

```
ls characters/fubao/frames/small/*.txt characters/fubao/frames/medium/*.txt characters/fubao/frames/large/*.txt | wc -l
```
Expected: `63`

- [ ] **Step 4: Verify `--check` passes**

```
uv run scripts/prerender.py fubao --check
```
Expected: `all 63 frames present`

- [ ] **Step 5: Remove `.gitkeep` placeholders**

```
rm -f characters/fubao/frames/small/.gitkeep characters/fubao/frames/medium/.gitkeep characters/fubao/frames/large/.gitkeep
```

- [ ] **Step 6: Commit**

```
git add characters/fubao/frames/
git commit -m "feat(fubao): add pre-rendered ANSI frame files (63 × text)"
```

---

## Task 9: Wire fubao into `plugin.json` userConfig

**Files:**
- Modify: `.claude-plugin/plugin.json:15-20`

- [ ] **Step 1: Update the `character` field**

Replace the current `"character"` block in `.claude-plugin/plugin.json`:

```json
    "character": {
      "type": "string",
      "title": "Character",
      "description": "Which mascot character to display (nabi | fubao)",
      "enum": ["nabi", "fubao"],
      "default": "nabi"
    },
```

- [ ] **Step 2: Validate JSON syntax**

```
uv run python -c "import json; json.load(open('.claude-plugin/plugin.json'))"
```
Expected: no output, exit 0.

- [ ] **Step 3: Commit**

```
git add .claude-plugin/plugin.json
git commit -m "feat(plugin): expose fubao in character userConfig enum"
```

---

## Task 10: End-to-end smoke test

**Files:**
- Modify: `tests/test_fubao.py` (append integration test)

- [ ] **Step 1: Append end-to-end test**

```python
def test_fubao_animator_produces_non_empty_output():
    """Full path: load fubao, render one frame, check non-empty and message present."""
    from mcp_server.display import Animator
    from characters.fubao.art import EMOTIONS

    a = Animator("fubao", "happy", pane_height=14)
    lines = a.tick()
    assert isinstance(lines, list)
    assert len(lines) > 0
    joined = "\n".join(lines)
    # Some content from the rendered panda frame
    assert any(line.strip() for line in lines)
    # Message or sp_msg must appear
    assert EMOTIONS["happy"]["msg"] in joined or EMOTIONS["happy"]["sp_msg"] in joined
```

- [ ] **Step 2: Run the test**

```
uv run --extra dev pytest tests/test_fubao.py::test_fubao_animator_produces_non_empty_output -v
```
Expected: pass.

- [ ] **Step 3: Run the entire test suite**

```
uv run --extra dev pytest tests/ -v
```
Expected: all tests pass (no regression in nabi / character / emotion / display_dispatch / prerender).

- [ ] **Step 4: Commit**

```
git add tests/test_fubao.py
git commit -m "test(fubao): add end-to-end animator smoke test"
```

---

## Task 11: Manual tmux verification

**Files:** none (manual step)

- [ ] **Step 1: Set character to fubao**

In a tmux session with Claude Code configured to use this plugin, set `character: "fubao"` in plugin user config (or export `CLAUDE_PLUGIN_USERCONFIG_CHARACTER=fubao` before launching `claude`).

- [ ] **Step 2: Start Claude Code and confirm pane**

Start `claude`. The mascot pane should appear at the bottom and show a rendered panda image.

- [ ] **Step 3: Verify each emotion**

Use the `show_character` MCP tool to cycle through all 7 emotions:
```
neutral, happy, angry, shy, sad, surprised, love
```
Each should render without `[frame missing: …]` placeholders.

- [ ] **Step 4: Verify pane-size adaptation**

Change `paneHeight` to 10, 14, and 25 in turn (restart Claude each time). Confirm:
- pane=10 → small frame renders, panda fits, message visible
- pane=14 → medium frame renders
- pane=25 → large frame renders

- [ ] **Step 5: Report verification**

Note any visual issues in a comment on the implementation PR. If adjustments needed (e.g., sizes ±2 cells), update `SIZES` in `scripts/prerender.py` and `_pick_size` thresholds in `characters/fubao/art.py`, re-run prerender, commit.

---

## Task 12: Documentation updates

**Files:**
- Modify: `README.md`, `README.ko.md`
- Modify: `CHANGELOG.md`
- Modify: `.claude-plugin/plugin.json` (version bump)
- Modify: `pyproject.toml` (version bump)

- [ ] **Step 1: Update `README.md`**

Add a "Characters" section after "Installation" (or extend an existing one):

```markdown
## Characters

This plugin ships with two characters, selectable via the `character` userConfig:

| ID      | Name                    | Style                                           |
|---------|-------------------------|-------------------------------------------------|
| `nabi`  | Nabi (tsundere cat)     | Programmatic ASCII art, default                 |
| `fubao` | Fubao (cute lazy panda) | Pre-rendered ANSI image frames (via chafa)      |

### Adding your own character

The plugin supports two renderers:

- **Programmatic** — Python function returns ANSI lines per frame (see `characters/nabi/art.py`).
- **Frames** — pre-rendered ANSI text files loaded at runtime (see `characters/fubao/art.py`).

To add a frames-based character:

1. Create `characters/<name>/` mirroring `characters/fubao/` (metadata, messages, emotion rules, `art.py` with `RENDERER = "frames"`).
2. Drop raw images into `characters/<name>/raw/` as `<emotion>_<state>.jpg` (also accepts `.png`, `.webp`).
3. Install `chafa` locally (`brew install chafa` on macOS).
4. Run `uv run scripts/prerender.py <name>` to generate frame files.
5. Add `<name>` to the `character` enum in `.claude-plugin/plugin.json`.

End users don't need `chafa` — frames are committed to the repo.
```

- [ ] **Step 2: Update `README.ko.md`**

Mirror the same additions in Korean.

- [ ] **Step 3: Update `CHANGELOG.md`**

Add a new v0.2.0 entry at the top:

```markdown
## [0.2.0] - 2026-04-24

### Added
- New `fubao` character (cute lazy panda) with image-based rendering.
- Frames-based renderer architecture: each character declares `RENDERER = "programmatic" | "frames"`.
- `scripts/prerender.py` build tool to convert raw images to ANSI text via chafa.
- `pane_height` now flows into `Animator` so frames renderer can pick size.

### Changed
- `character` userConfig is now an enum of `["nabi", "fubao"]`.
```

- [ ] **Step 4: Bump version to 0.2.0**

`.claude-plugin/plugin.json`: change `"version": "0.1.0"` → `"version": "0.2.0"`.

`pyproject.toml`: change `version = "0.1.0"` → `version = "0.2.0"`.

- [ ] **Step 5: Final test run**

```
uv run --extra dev pytest tests/ -v
```
Expected: all tests pass.

- [ ] **Step 6: Commit**

```
git add README.md README.ko.md CHANGELOG.md .claude-plugin/plugin.json pyproject.toml
git commit -m "docs: v0.2.0 — add fubao character and frames-renderer docs"
```

- [ ] **Step 7: Tag the release**

```
git tag -a v0.2.0 -m "v0.2.0 — add fubao character (image-based rendering)"
```

(Do **not** push the tag yet — leave that for user approval.)

---

## Summary

- **12 tasks**, each a self-contained commit.
- **Test coverage**: test_fubao (10+ tests), test_display_dispatch (8 tests), test_prerender (5 tests), plus existing suite unchanged.
- **Git history** stays clean: one concept per commit, easy to revert individual tasks if needed.
- **Manual gate**: Tasks 7 (source images) and 11 (tmux visual verification) require human judgment — don't skip them.
- **Rollback safety**: at any point before Task 9 (userConfig update), fubao is invisible to end users even if partially scaffolded.
