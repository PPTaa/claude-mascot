# claude-mascot Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the existing tsundere-cat feature (MCP server + 4 hooks) as a Claude Code plugin (`claude-mascot`) ready for open-source distribution via GitHub marketplace.

**Architecture:** Python MCP server bootstrapped via `uv run`, driven by userConfig env vars, with filesystem-based character discovery. tmux-only display. Character assets live under `characters/<id>/` for future extensibility (v1 ships only `nabi`).

**Tech Stack:** Python ≥3.10, `mcp` package, `uv` for dep management, `pytest` for tests, `tmux` for display. MIT license.

**Reference Source:** `/Users/jungchul/Projects/ToyProject/claude_warp_custom/` contains the working prototype. Port files from there with the adaptations specified per task.

**Target Repo:** `/Users/jungchul/Projects/ToyProject/claude_plugin/claude-mascot/` (git already initialized).

---

## Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `README.md` (stub, fleshed out in Task 21)

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "claude-mascot"
version = "0.1.0"
description = "Terminal mascot reacting to Claude Code activity (tsundere cat and friends)"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
dependencies = ["mcp>=1.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["mcp_server"]
```

- [ ] **Step 2: Create `LICENSE`** (standard MIT text)

```
MIT License

Copyright (c) 2026 <owner>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

(Replace `<owner>` with the actual author name provided by the user when setting up the repo.)

- [ ] **Step 3: Create `.gitignore`**

```
__pycache__/
*.pyc
.venv/
.pytest_cache/
.DS_Store
/tmp/nabi_debug.log
dist/
build/
*.egg-info/
```

- [ ] **Step 4: Create `README.md`** (stub — filled in Task 21)

```markdown
# claude-mascot

A terminal mascot that reacts to Claude Code activity in a tmux pane.

Full docs in Task 21.
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml LICENSE .gitignore README.md
git commit -m "chore: project skeleton (pyproject, license, gitignore, readme stub)"
```

---

## Task 2: Plugin Manifest (plugin.json)

**Files:**
- Create: `.claude-plugin/plugin.json`

- [ ] **Step 1: Create the manifest**

```json
{
  "name": "claude-mascot",
  "version": "0.1.0",
  "description": "A tsundere cat mascot (and friends) reacting to Claude Code activity in a tmux pane",
  "author": { "name": "<owner>", "url": "https://github.com/<owner>" },
  "license": "MIT",
  "repository": "https://github.com/<owner>/claude-mascot",
  "keywords": ["claude-code", "plugin", "tmux", "mascot", "tsundere"],
  "requirements": {
    "claudeCode": ">=1.0.0",
    "externalTools": ["tmux", "uv"]
  },
  "mcpServers": "./.mcp.json",
  "hooks": "./hooks/hooks.json",
  "userConfig": {
    "character": {
      "type": "string",
      "description": "Which mascot character to display",
      "default": "nabi",
      "enum": ["nabi"]
    },
    "language": {
      "type": "string",
      "description": "Message language (ko | en)",
      "default": "ko",
      "enum": ["ko", "en"]
    },
    "paneHeight": {
      "type": "number",
      "description": "Height of the tmux pane in rows",
      "default": 14,
      "minimum": 8,
      "maximum": 30
    },
    "stopHookEnabled": {
      "type": "boolean",
      "description": "Auto-update mascot emotion at end of each Claude response",
      "default": true
    },
    "startupEmotion": {
      "type": "string",
      "description": "Emotion shown when a new session starts",
      "default": "happy",
      "enum": ["neutral", "happy", "angry", "shy", "sad", "surprised", "love"]
    }
  }
}
```

(`<owner>` to be replaced during repo setup.)

- [ ] **Step 2: Validate JSON**

```bash
python3 -m json.tool .claude-plugin/plugin.json > /dev/null && echo OK
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "feat: plugin.json manifest with userConfig schema"
```

---

## Task 3: Marketplace Manifest

**Files:**
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Create single-plugin marketplace manifest**

```json
{
  "name": "claude-mascot-marketplace",
  "description": "Home of the claude-mascot plugin",
  "owner": { "name": "<owner>", "url": "https://github.com/<owner>" },
  "plugins": [
    { "name": "claude-mascot", "source": "./" }
  ]
}
```

- [ ] **Step 2: Validate JSON**

```bash
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && echo OK
```

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat: single-plugin marketplace manifest"
```

---

## Task 4: Nabi character.json

**Files:**
- Create: `characters/nabi/character.json`

- [ ] **Step 1: Create character metadata**

```json
{
  "id": "nabi",
  "displayName": "Nabi (츤데레 고양이)",
  "description": "A tsundere orange cat that reacts to Claude Code activity",
  "license": "MIT",
  "supportedEmotions": ["neutral", "happy", "angry", "shy", "sad", "surprised", "love"],
  "defaultLanguage": "ko",
  "supportedLanguages": ["ko", "en"]
}
```

- [ ] **Step 2: Validate JSON**

```bash
python3 -m json.tool characters/nabi/character.json > /dev/null && echo OK
```

- [ ] **Step 3: Commit**

```bash
git add characters/nabi/character.json
git commit -m "feat(nabi): character metadata"
```

---

## Task 5: Port Nabi Art Frames

**Files:**
- Create: `characters/nabi/art.py`
- Reference: `/Users/jungchul/Projects/ToyProject/claude_warp_custom/mcp_server/nabi_display.py` (EMOTIONS dict + render function)

- [ ] **Step 1: Port EMOTIONS dict and render()**

Copy the entire contents of `claude_warp_custom/mcp_server/nabi_display.py` EXCEPT the `main()` function (bottom) and the `emotion`/`custom_message` argv parsing at top. Keep everything in the file as a module that exposes `EMOTIONS` and `render(cfg, eyes, msg, deco, tail_t, shake=0)` as the public API. Keep ANSI color constants (`O`, `W`, `PK`, etc.) at module top.

Target file shape:

```python
"""Nabi character art — frames and renderer."""

# ANSI Color codes (as in source)
O  = "\033[38;5;208m"
# ... (copy all color constants from source) ...

EMOTIONS = {
    # ... copy unchanged from source ...
}

def render(cfg, eyes, msg, deco, tail_t, shake=0):
    # ... copy unchanged from source ...
```

**Do NOT copy**: `import sys`, argv parsing, `signal` setup, `HIDE`/`SHOW`/`CLR`/`HOME`/`EL` ANSI codes (those belong in display.py), `INTERVAL`, `PANE_LINES`, `Animator` class, `main()`, `if __name__ == "__main__"`.

- [ ] **Step 2: Smoke-test the module imports and has expected shape**

```bash
uv run python -c "
from characters.nabi import art
assert 'happy' in art.EMOTIONS
assert 'neutral' in art.EMOTIONS
assert len(art.EMOTIONS) == 7
frame = art.render(art.EMOTIONS['happy'], '^ ^', 'test', '', 0)
assert isinstance(frame, list)
assert len(frame) >= 10
print('OK')
"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add characters/nabi/art.py
git commit -m "feat(nabi): port emotion frames and renderer"
```

---

## Task 6: Nabi Messages (Korean + English)

**Files:**
- Create: `characters/nabi/messages.ko.json`
- Create: `characters/nabi/messages.en.json`

- [ ] **Step 1: Korean message pool**

```json
{
  "happy": [
    "흥, 이 정도는 기본이라냥.",
    "후훗... 잘 됐네, 좋아하는 거 아니라구!",
    "뭐, 어쩌다 맞혔네냥.",
    "됐냥! ...칭찬은 됐어."
  ],
  "sad": [
    "으... 이거 안 풀리네냥...",
    "치... 내 잘못 아니거든...",
    "미안... 좀만 더 시간 줘...",
    "하아... 뭐가 잘못됐지..."
  ],
  "angry": [
    "뭐?! 같은 실수 또 할 거냥?!",
    "하아... 진짜 답답하다냥!",
    "!! 정신차려냥 !!",
    "또?! 한 번만 더 하면 할퀸다냥!"
  ],
  "surprised": [
    "냐?! 뭐, 뭐야 갑자기?!",
    "어?! 그런 것도 있었냥?",
    "헉! 그건 예상 못 했다냥!"
  ],
  "shy": [
    "뭐, 뭐야... 고맙다고 하지 마...",
    "칭찬해도 안 기뻐하거든...!",
    "그, 그런 말 하지 마라냥..."
  ],
  "love": [
    "...좋아하는 거 아니거든!",
    "그냥... 심심해서 도와준 거야.",
    "좋, 좋아하는 거 아니라구!"
  ],
  "neutral": [
    "흥, 볼일 있냐?",
    "뭐, 다음은?",
    "계속 해봐라냥.",
    "그래서... 뭐?"
  ]
}
```

- [ ] **Step 2: English message pool** (preserves tsundere tone as closely as possible)

```json
{
  "happy": [
    "Hmph, that was basic, meow.",
    "Heh... it worked out. Not that I'm happy or anything!",
    "Well, you got lucky this time.",
    "There! ...Don't thank me."
  ],
  "sad": [
    "Ugh... this won't resolve, meow...",
    "Tch... it's not my fault, okay?",
    "Sorry... give me a minute...",
    "Haah... what went wrong..."
  ],
  "angry": [
    "What?! You're making the same mistake AGAIN?!",
    "Haah... you're really frustrating, meow!",
    "!! Get it together, meow !!",
    "Again?! One more time and I claw you!"
  ],
  "surprised": [
    "Nya?! What, what is it suddenly?!",
    "Huh?! Was that even a thing?",
    "Hah! Didn't see that coming, meow!"
  ],
  "shy": [
    "Wh-what... don't say thanks...",
    "I'm not happy about compliments, okay...!",
    "Don't... don't say stuff like that, meow..."
  ],
  "love": [
    "...I don't LIKE you or anything!",
    "Just... had nothing better to do.",
    "I-it's not that I like you, got it?!"
  ],
  "neutral": [
    "Hmph, what do you want?",
    "Well, what's next?",
    "Keep going, meow.",
    "So... what?"
  ]
}
```

- [ ] **Step 3: Validate both JSON files**

```bash
python3 -m json.tool characters/nabi/messages.ko.json > /dev/null && \
python3 -m json.tool characters/nabi/messages.en.json > /dev/null && echo OK
```

- [ ] **Step 4: Commit**

```bash
git add characters/nabi/messages.ko.json characters/nabi/messages.en.json
git commit -m "feat(nabi): message pools (ko, en)"
```

---

## Task 7: Nabi Emotion Rules

**Files:**
- Create: `characters/nabi/emotion_rules.json`

- [ ] **Step 1: Externalize regex rules from on_stop.py**

```json
{
  "priority": ["angry", "happy", "sad", "shy", "surprised"],
  "patterns": {
    "angry": "(틀렸|잘못\\s*됐|같은\\s*실수|다시\\s*봐|wrong\\b|mistake)",
    "happy": "(완료|성공|잘\\s*됐|잘됨|done\\b|works?\\b|passed|fixed|해결(?!\\s*안)|끝났)",
    "sad": "(에러|실패|fail(?:ed|ure)?|error|broken|안\\s*되|안됨|안된다|못\\s*해|못함|문제\\s*있)",
    "shy": "(감사|고마|thank|칭찬|잘했|굿굿|수고|최고)",
    "surprised": "(\\?!|어\\?|왜\\?|이상한데|wait\\b|갑자기|헉)"
  },
  "default": "neutral"
}
```

- [ ] **Step 2: Validate JSON**

```bash
python3 -m json.tool characters/nabi/emotion_rules.json > /dev/null && echo OK
```

- [ ] **Step 3: Commit**

```bash
git add characters/nabi/emotion_rules.json
git commit -m "feat(nabi): externalize emotion classification rules"
```

---

## Task 8: Copy Nabi Static ASCII Textures

**Files:**
- Create: `characters/nabi/ascii/neutral.txt`, `happy.txt`, `angry.txt`, `shy.txt`, `sad.txt`, `surprised.txt`, `love.txt`
- Source: `/Users/jungchul/Projects/ToyProject/claude_warp_custom/mcp_server/characters/tsundere_cat/ascii/*.txt`

- [ ] **Step 1: Copy all 7 ASCII files verbatim**

```bash
mkdir -p characters/nabi/ascii
cp /Users/jungchul/Projects/ToyProject/claude_warp_custom/mcp_server/characters/tsundere_cat/ascii/*.txt characters/nabi/ascii/
ls characters/nabi/ascii/
```

Expected: 7 files (`neutral.txt`, `happy.txt`, `angry.txt`, `shy.txt`, `sad.txt`, `surprised.txt`, `love.txt`).

- [ ] **Step 2: Commit**

```bash
git add characters/nabi/ascii/
git commit -m "feat(nabi): static ASCII textures (inline mode)"
```

---

## Task 9: Character Loader (TDD)

**Files:**
- Create: `mcp_server/__init__.py` (empty)
- Create: `mcp_server/character.py`
- Create: `tests/__init__.py` (empty)
- Create: `tests/test_character.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_character.py
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
    # Unsupported language → falls back to character's defaultLanguage
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
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
uv run --extra dev pytest tests/test_character.py -v
```

Expected: All 6 tests fail with `ModuleNotFoundError` or `AttributeError`.

- [ ] **Step 3: Implement `mcp_server/character.py`**

```python
"""Character loader — reads character.json, messages, and emotion rules from characters/<id>/."""

import json
import os
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
CHARACTERS_DIR = PLUGIN_ROOT / "characters"


def _character_dir(character_id: str) -> Path:
    d = CHARACTERS_DIR / character_id
    if not d.is_dir():
        raise FileNotFoundError(f"Character '{character_id}' not found at {d}")
    return d


def load_character(character_id: str) -> dict:
    """Load character.json metadata."""
    meta_path = _character_dir(character_id) / "character.json"
    with meta_path.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_language(meta: dict, requested: str) -> str:
    """Pick the effective language: requested if supported, else character default, else 'ko'."""
    supported = meta.get("supportedLanguages", [])
    if requested in supported:
        return requested
    return meta.get("defaultLanguage", "ko")


def load_messages(character_id: str, language: str) -> dict:
    """Load messages.<lang>.json — falls back to character default language if file missing."""
    meta = load_character(character_id)
    lang = resolve_language(meta, language)
    msg_path = _character_dir(character_id) / f"messages.{lang}.json"
    with msg_path.open(encoding="utf-8") as f:
        return json.load(f)


def load_emotion_rules(character_id: str) -> dict:
    """Load emotion_rules.json — returns dict with 'priority', 'patterns', 'default'."""
    rules_path = _character_dir(character_id) / "emotion_rules.json"
    with rules_path.open(encoding="utf-8") as f:
        return json.load(f)
```

- [ ] **Step 4: Re-run tests**

```bash
CLAUDE_PLUGIN_ROOT="$(pwd)" uv run --extra dev pytest tests/test_character.py -v
```

Expected: All 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add mcp_server/__init__.py mcp_server/character.py tests/
git commit -m "feat: character loader with tests"
```

---

## Task 10: Emotion Classifier & Message Picker (TDD)

**Files:**
- Create: `mcp_server/emotion.py`
- Create: `tests/test_emotion.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_emotion.py
import pytest
from mcp_server import emotion


RULES = {
    "priority": ["angry", "happy", "sad"],
    "patterns": {
        "angry": r"(틀렸|wrong\b)",
        "happy": r"(완료|done\b|해결(?!\s*안))",
        "sad": r"(에러|error|failed)",
    },
    "default": "neutral",
}


def test_pick_emotion_happy():
    assert emotion.pick_emotion("빌드 완료!", RULES) == "happy"


def test_pick_emotion_sad():
    assert emotion.pick_emotion("에러 발생", RULES) == "sad"


def test_pick_emotion_angry_wins_over_sad():
    # Both "틀렸" (angry) and "에러" (sad) present → angry wins per priority
    assert emotion.pick_emotion("에러가 나서 틀렸네", RULES) == "angry"


def test_pick_emotion_happy_wins_over_sad_for_resolution():
    # "에러 해결 완료" → happy (해결 completes + 완료 matches happy)
    assert emotion.pick_emotion("에러 해결 완료", RULES) == "happy"


def test_pick_emotion_default_when_no_match():
    assert emotion.pick_emotion("그냥 일반 문장", RULES) == "neutral"


def test_pick_message_returns_from_pool():
    msgs = {"happy": ["a", "b", "c"]}
    picked = emotion.pick_message("happy", msgs)
    assert picked in ["a", "b", "c"]


def test_pick_message_fallback_to_neutral():
    msgs = {"neutral": ["default"]}
    picked = emotion.pick_message("angry", msgs)  # no 'angry' key
    assert picked == "default"


def test_pick_message_empty_pool_returns_empty_string():
    picked = emotion.pick_message("angry", {})
    assert picked == ""
```

- [ ] **Step 2: Run tests, verify failure**

```bash
uv run --extra dev pytest tests/test_emotion.py -v
```

Expected: All 8 tests fail with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mcp_server/emotion.py`**

```python
"""Emotion classification and message selection — pure functions."""

import random
import re


def pick_emotion(text: str, rules: dict) -> str:
    """Classify text into an emotion based on priority-ordered regex rules."""
    patterns = rules.get("patterns", {})
    for emo in rules.get("priority", []):
        pat = patterns.get(emo)
        if pat and re.search(pat, text, re.IGNORECASE):
            return emo
    return rules.get("default", "neutral")


def pick_message(emotion: str, messages: dict) -> str:
    """Pick a random message from the pool for the given emotion.
    Falls back to 'neutral' pool, then empty string."""
    pool = messages.get(emotion) or messages.get("neutral") or []
    if not pool:
        return ""
    return random.choice(pool)
```

- [ ] **Step 4: Re-run tests**

```bash
uv run --extra dev pytest tests/test_emotion.py -v
```

Expected: All 8 tests pass.

- [ ] **Step 5: Commit**

```bash
git add mcp_server/emotion.py tests/test_emotion.py
git commit -m "feat: emotion classifier and message picker with tests"
```

---

## Task 11: Pane Manager (port from server.py)

**Files:**
- Create: `mcp_server/pane.py`
- Source: `/Users/jungchul/Projects/ToyProject/claude_warp_custom/mcp_server/server.py` (functions `_pane_id_file`, `_get_active_target`, `_find_nabi_pane`, `_update_tmux_pane`, `_kill_orphan_nabi_panes`)

- [ ] **Step 1: Port tmux pane logic with userConfig env var support**

```python
"""tmux pane lifecycle — creation, respawn, kill, orphan cleanup.
Scoped to the current tmux session only; does not touch panes in other tmux sessions."""

import os
import subprocess
import sys
from pathlib import Path

NABI_PANE_ID_DIR = Path("/tmp")
DISPLAY_SCRIPT = Path(__file__).parent / "display.py"


def _pane_height() -> int:
    try:
        return max(8, min(30, int(os.environ.get("CLAUDE_PLUGIN_USERCONFIG_PANEHEIGHT", "14"))))
    except ValueError:
        return 14


def _pane_id_file(session: str) -> Path:
    safe = session.replace("/", "_").replace(":", "_")
    return NABI_PANE_ID_DIR / f"claude_mascot_pane_id_{safe}"


def get_active_target() -> str | None:
    """Return 'session:window' of the currently-attached active window, or None."""
    try:
        result = subprocess.run(
            ["tmux", "list-windows", "-F",
             "#{session_name}:#{window_index} #{window_active}"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode != 0:
            return None
        for line in result.stdout.strip().splitlines():
            parts = line.rsplit(" ", 1)
            if len(parts) == 2 and parts[1] == "1":
                return parts[0]
    except Exception:
        pass
    return None


def _find_mascot_pane(target: str | None) -> str | None:
    if not target:
        return None
    session_name = target.split(":")[0]
    pf = _pane_id_file(session_name)
    if not pf.exists():
        return None
    pane_id = pf.read_text().strip()
    if not pane_id:
        return None
    try:
        result = subprocess.run(
            ["tmux", "list-panes", "-s", "-t", session_name, "-F", "#{pane_id}"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0 and pane_id in result.stdout.split():
            return pane_id
    except Exception:
        pass
    pf.unlink(missing_ok=True)
    return None


def _kill_orphan_mascot_panes(session_name: str, keep_pane_id: str | None = None):
    """Kill mascot panes in the CURRENT tmux session (except keep_pane_id).
    Does NOT touch other tmux sessions (multi-tab safety)."""
    try:
        result = subprocess.run(
            ["tmux", "list-panes", "-s", "-t", session_name,
             "-F", "#{pane_id} #{pane_pid}"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode != 0:
            return
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) != 2:
                continue
            pid, ppid = parts
            if pid == keep_pane_id:
                continue
            try:
                ps = subprocess.run(
                    ["ps", "-o", "command=", "-p", ppid],
                    capture_output=True, text=True, timeout=3,
                )
                if "mcp_server.display" not in ps.stdout and "display.py" not in ps.stdout:
                    continue
            except Exception:
                continue
            subprocess.run(["tmux", "kill-pane", "-t", pid],
                           capture_output=True, timeout=3)
    except Exception:
        pass

    # Clean up pane_id files pointing to dead panes (global sweep, safe)
    try:
        live = subprocess.run(
            ["tmux", "list-panes", "-a", "-F", "#{pane_id}"],
            capture_output=True, text=True, timeout=3,
        )
        live_set = set(live.stdout.split()) if live.returncode == 0 else set()
        for pf in NABI_PANE_ID_DIR.glob("claude_mascot_pane_id_*"):
            try:
                content = pf.read_text().strip()
            except Exception:
                continue
            if content and content not in live_set:
                pf.unlink(missing_ok=True)
    except Exception:
        pass


def update_pane(character: str, language: str, emotion: str, message: str = ""):
    """Respawn or create the mascot pane showing the given emotion/message."""
    target = get_active_target()
    if not target:
        return

    python_path = sys.executable or "python3"
    pane_id = _find_mascot_pane(target)
    height = _pane_height()
    # Pass character + language + paneHeight + emotion + message via argv.
    # (tmux split-window does NOT inherit our env vars, so argv is the reliable transport.)
    cmd = [
        python_path, "-m", "mcp_server.display",
        character, language, str(height), emotion,
    ]
    if message:
        cmd.append(message)

    session_name = target.split(":")[0]
    active: str | None = None
    try:
        if pane_id:
            subprocess.run(
                ["tmux", "respawn-pane", "-k", "-t", pane_id] + cmd,
                capture_output=True, timeout=3,
            )
            active = pane_id
        else:
            result = subprocess.run(
                ["tmux", "split-window", "-v", "-l", str(height), "-d",
                 "-t", target, "-P", "-F", "#{pane_id}"] + cmd,
                capture_output=True, text=True, timeout=3,
            )
            if result.returncode == 0:
                active = result.stdout.strip()
                _pane_id_file(session_name).write_text(active)
    except Exception:
        pass

    _kill_orphan_mascot_panes(session_name, keep_pane_id=active)


def kill_current_session_pane():
    """Kill the mascot pane associated with the current tmux session and remove its id file."""
    target = get_active_target()
    if not target:
        return
    session_name = target.split(":")[0]
    pf = _pane_id_file(session_name)
    if not pf.exists():
        return
    pane_id = pf.read_text().strip()
    if pane_id:
        try:
            subprocess.run(["tmux", "kill-pane", "-t", pane_id],
                           capture_output=True, timeout=3)
        except Exception:
            pass
    pf.unlink(missing_ok=True)
```

Key differences from the source:
- `PANE_ID_DIR` filename prefix `claude_mascot_pane_id_*` (instead of `nabi_pane_id_*`) — namespacing since plugin is generic.
- `_pane_height()` reads `CLAUDE_PLUGIN_USERCONFIG_PANEHEIGHT` env var.
- `update_pane` takes `character` and `language` args and passes them into the display subprocess (previous code only passed emotion/message).
- `DISPLAY_SCRIPT` executed via `python -m mcp_server.display` so it runs as a package module.

- [ ] **Step 2: Smoke-test the module imports**

```bash
uv run python -c "
from mcp_server import pane
assert callable(pane.update_pane)
assert callable(pane.kill_current_session_pane)
print('OK')
"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add mcp_server/pane.py
git commit -m "feat: tmux pane manager (character-aware, env-var driven)"
```

---

## Task 12: Display Animator (port from nabi_display.py main loop)

**Files:**
- Create: `mcp_server/display.py`
- Source: `/Users/jungchul/Projects/ToyProject/claude_warp_custom/mcp_server/nabi_display.py` (`Animator` class + `main()`)

- [ ] **Step 1: Port the animation loop, character-aware**

```python
"""Display animator — runs inside a tmux pane, renders a character's frames in a loop.
Invoked as `python -m mcp_server.display <character> <language> <emotion> [message]`."""

import random
import signal
import sys
import time
from importlib import import_module

# Terminal control
HIDE = "\033[?25l"
SHOW = "\033[?25h"
CLR  = "\033[2J"
HOME = "\033[H"
EL   = "\033[2K"

INTERVAL = 0.4     # 2.5 FPS


class Animator:
    def __init__(self, character_id: str, emotion: str, custom_message: str = ""):
        art_mod = import_module(f"characters.{character_id}.art")
        self.art_mod = art_mod
        self.cfg = art_mod.EMOTIONS.get(emotion, art_mod.EMOTIONS["neutral"])
        if custom_message:
            self.cfg = dict(self.cfg)
            self.cfg["msg"] = custom_message
        self.emo = emotion
        self.t = 0
        self.mode = "idle"
        self.mode_end = 0
        self._cur_sp_eyes = None
        self._schedule("blink", 8, 15)
        self._schedule("special", 25, 40)

    def _schedule(self, key, lo, hi):
        setattr(self, f"_next_{key}", self.t + random.randint(lo, hi))

    def tick(self):
        self.t += 1
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
        if self.mode == "special":
            eyes = self._cur_sp_eyes
            msg = c["sp_msg"]
            if self.emo == "angry":
                shake = self.t % 2
        elif self.mode == "blink":
            eyes = "= ="
        elif self.t % 20 < 3:
            eyes = c["alt_eyes"]

        deco = c["decos"][self.t % len(c["decos"])]
        return self.art_mod.render(c, eyes, msg, deco, self.t, shake)


def main():
    # argv: <script> <character> <language> <pane_height> <emotion> [message]
    # (env vars don't cross tmux pane boundary — everything arrives via argv)
    character_id = sys.argv[1] if len(sys.argv) > 1 else "nabi"
    _language = sys.argv[2] if len(sys.argv) > 2 else "ko"          # reserved for future use
    try:
        pane_height = int(sys.argv[3]) if len(sys.argv) > 3 else 14
    except ValueError:
        pane_height = 14
    pane_lines = max(7, min(29, pane_height - 1))
    emotion = sys.argv[4] if len(sys.argv) > 4 else "neutral"
    custom_message = sys.argv[5] if len(sys.argv) > 5 else ""

    def cleanup(*_):
        sys.stdout.write(SHOW)
        sys.stdout.flush()
        sys.exit(0)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    sys.stdout.write(CLR + HOME + HIDE)
    sys.stdout.flush()

    anim = Animator(character_id, emotion, custom_message)

    try:
        while True:
            lines = anim.tick()
            buf = HOME
            for line in lines[:pane_lines]:
                buf += EL + line + "\n"
            sys.stdout.write(buf)
            sys.stdout.flush()
            time.sleep(INTERVAL)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        sys.stdout.write(SHOW)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Import smoke test**

```bash
uv run python -c "from mcp_server import display; assert callable(display.main); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add mcp_server/display.py
git commit -m "feat: character-aware display animator"
```

---

## Task 13: Inline ASCII (PostToolUse, port from animate.py)

**Files:**
- Create: `mcp_server/inline.py`
- Source: `/Users/jungchul/Projects/ToyProject/claude_warp_custom/mcp_server/animate.py`

- [ ] **Step 1: Port inline ASCII display with character awareness**

```python
"""Inline ASCII printer for PostToolUse hook — prints the character's current
emotion ASCII to stdout (shows up in the chat transcript).

Reads hook stdin JSON and extracts the emotion from the tool_input."""

import json
import os
import sys
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))


def get_ascii_art(character_id: str, emotion: str) -> str:
    ascii_dir = PLUGIN_ROOT / "characters" / character_id / "ascii"
    path = ascii_dir / f"{emotion}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    fallback = ascii_dir / "neutral.txt"
    if fallback.exists():
        return fallback.read_text(encoding="utf-8")
    return ""


def main():
    character_id = os.environ.get("CLAUDE_PLUGIN_USERCONFIG_CHARACTER", "nabi")
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    emotion = payload.get("tool_input", {}).get("emotion", "neutral")
    art = get_ascii_art(character_id, emotion)
    if art:
        # Print with separator bars (same as original animate.py)
        GRAY = "\033[38;5;245m"
        RESET = "\033[0m"
        bar = f"{GRAY}{'─' * 36}{RESET}"
        sys.stdout.write(f"\n{bar}\n{art}\n{bar}\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test with mock stdin**

```bash
echo '{"tool_input":{"emotion":"happy"}}' | CLAUDE_PLUGIN_ROOT="$(pwd)" uv run python -m mcp_server.inline
```

Expected: nabi happy ASCII art printed with gray separator bars.

- [ ] **Step 3: Commit**

```bash
git add mcp_server/inline.py
git commit -m "feat: inline ASCII printer for PostToolUse"
```

---

## Task 14: MCP Server (show_character, list_emotions)

**Files:**
- Create: `mcp_server/server.py`
- Source: `/Users/jungchul/Projects/ToyProject/claude_warp_custom/mcp_server/server.py` (MCP tool definitions only)

- [ ] **Step 1: Implement server.py**

```python
"""MCP server exposing `show_character` and `list_emotions` tools.
Reads active character/language from CLAUDE_PLUGIN_USERCONFIG_* env vars."""

import os
from mcp.server.fastmcp import FastMCP

from mcp_server import character as char_loader
from mcp_server import pane


mcp = FastMCP("claude-mascot")


def _active_character() -> str:
    return os.environ.get("CLAUDE_PLUGIN_USERCONFIG_CHARACTER", "nabi")


def _active_language() -> str:
    return os.environ.get("CLAUDE_PLUGIN_USERCONFIG_LANGUAGE", "ko")


@mcp.tool()
def show_character(emotion: str, message: str = "") -> str:
    """Display the active mascot character with the given emotion and optional message in the tmux pane.

    Must be called at the end of every response.

    Args:
        emotion: One of neutral, happy, angry, shy, sad, surprised, love.
        message: Optional tsundere one-liner. If empty, the character's default emotion message is used.
    """
    character_id = _active_character()
    language = _active_language()
    meta = char_loader.load_character(character_id)
    supported = meta.get("supportedEmotions", ["neutral"])
    if emotion not in supported:
        emotion = "neutral"

    pane.update_pane(character_id, language, emotion, message)

    # Return the static ASCII so the tool result is visible in the transcript
    from mcp_server.inline import get_ascii_art
    return get_ascii_art(character_id, emotion)


@mcp.tool()
def list_emotions() -> str:
    """List the emotions supported by the active character."""
    character_id = _active_character()
    meta = char_loader.load_character(character_id)
    lines = [f"Character: {meta.get('displayName', character_id)}", "Supported emotions:"]
    for e in meta.get("supportedEmotions", []):
        lines.append(f"  - {e}")
    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test server starts**

```bash
# Start server briefly (will hang waiting for stdio; kill after 1s)
timeout 1 uv run python -m mcp_server.server; echo "exit=$?"
```

Expected: `exit=124` (timeout killed it cleanly — meaning server was running and waiting for stdin).

- [ ] **Step 3: Commit**

```bash
git add mcp_server/server.py
git commit -m "feat: MCP server with show_character and list_emotions"
```

---

## Task 15: SessionStart Hook

**Files:**
- Create: `mcp_server/hooks/__init__.py` (empty)
- Create: `mcp_server/hooks/session_start.py`

- [ ] **Step 1: Create empty `__init__.py`**

```bash
touch mcp_server/hooks/__init__.py
```

- [ ] **Step 2: Implement session_start.py**

```python
"""SessionStart hook — opens the mascot pane with emotion derived from the session source."""

import json
import os
import random
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

# Messages per source (key: emotion). If missing we fall back to random from messages pool.
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

    # Pick a message — first try source hint, else random from pool
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
```

- [ ] **Step 3: Smoke-test (mock stdin)**

```bash
echo '{"source":"startup","hook_event_name":"SessionStart"}' | \
  CLAUDE_PLUGIN_ROOT="$(pwd)" uv run python -m mcp_server.hooks.session_start; \
echo "exit=$?"; \
tail -3 /tmp/claude_mascot_debug.log
```

Expected: `exit=0`, debug log shows `source=startup character=nabi lang=ko emotion=happy`.

- [ ] **Step 4: Commit**

```bash
git add mcp_server/hooks/__init__.py mcp_server/hooks/session_start.py
git commit -m "feat(hooks): SessionStart opens mascot pane with source-aware emotion"
```

---

## Task 16: SessionEnd Hook

**Files:**
- Create: `mcp_server/hooks/session_end.py`

- [ ] **Step 1: Implement session_end.py**

```python
"""SessionEnd hook — closes the mascot pane for the current tmux session."""

import json
import sys
from datetime import datetime
from pathlib import Path

from mcp_server import pane

DEBUG_LOG = Path("/tmp/claude_mascot_debug.log")


def _log(msg: str):
    try:
        with DEBUG_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[session_end] {datetime.now().isoformat()} {msg}\n")
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    reason = payload.get("reason", "")
    _log(f"reason={reason}")
    try:
        pane.kill_current_session_pane()
    except Exception as e:
        _log(f"error: {e}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test**

```bash
echo '{"reason":"logout","hook_event_name":"SessionEnd"}' | \
  CLAUDE_PLUGIN_ROOT="$(pwd)" uv run python -m mcp_server.hooks.session_end; \
echo "exit=$?"; \
tail -2 /tmp/claude_mascot_debug.log
```

Expected: `exit=0`, debug log shows `reason=logout`.

- [ ] **Step 3: Commit**

```bash
git add mcp_server/hooks/session_end.py
git commit -m "feat(hooks): SessionEnd closes mascot pane"
```

---

## Task 17: Stop Hook (contextual emotion)

**Files:**
- Create: `mcp_server/hooks/on_stop.py`

- [ ] **Step 1: Implement on_stop.py**

```python
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
```

- [ ] **Step 2: Smoke-test — write fake transcript and verify emotion classification**

```bash
python3 -c "
import json
from pathlib import Path
Path('/tmp/mascot_test_tx.jsonl').write_text(
    json.dumps({'message':{'role':'assistant','content':[{'type':'text','text':'빌드 완료! 테스트 통과.'}]}}) + '\n'
)
"
echo '{"transcript_path":"/tmp/mascot_test_tx.jsonl","hook_event_name":"Stop"}' | \
  CLAUDE_PLUGIN_ROOT="$(pwd)" uv run python -m mcp_server.hooks.on_stop; \
echo "exit=$?"; \
tail -2 /tmp/claude_mascot_debug.log
rm -f /tmp/mascot_test_tx.jsonl
```

Expected: `exit=0`, debug log shows `emotion=happy` (because "완료" and "통과" both match happy pattern).

- [ ] **Step 3: Verify `stopHookEnabled=false` disables the hook**

```bash
echo '{"transcript_path":"/nonexistent","hook_event_name":"Stop"}' | \
  CLAUDE_PLUGIN_ROOT="$(pwd)" CLAUDE_PLUGIN_USERCONFIG_STOPHOOKENABLED=false \
  uv run python -m mcp_server.hooks.on_stop; \
echo "exit=$?"; \
tail -1 /tmp/claude_mascot_debug.log
```

Expected: `exit=0`, no new `[on_stop]` line appended (returned early before any work).

- [ ] **Step 4: Commit**

```bash
git add mcp_server/hooks/on_stop.py
git commit -m "feat(hooks): Stop updates emotion from transcript keyword analysis"
```

---

## Task 18: Plugin `.mcp.json` and `hooks/hooks.json`

**Files:**
- Create: `.mcp.json`
- Create: `hooks/hooks.json`

- [ ] **Step 1: MCP server registration**

`.mcp.json`:

```json
{
  "mcpServers": {
    "claude-mascot": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory", "${CLAUDE_PLUGIN_ROOT}",
        "python", "-m", "mcp_server.server"
      ]
    }
  }
}
```

- [ ] **Step 2: Hook registration**

`hooks/hooks.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory ${CLAUDE_PLUGIN_ROOT} python -m mcp_server.hooks.session_start"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory ${CLAUDE_PLUGIN_ROOT} python -m mcp_server.hooks.session_end"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "async": true,
            "command": "uv run --directory ${CLAUDE_PLUGIN_ROOT} python -m mcp_server.hooks.on_stop"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "mcp__claude-mascot__show_character",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory ${CLAUDE_PLUGIN_ROOT} python -m mcp_server.inline"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Validate both JSON files**

```bash
python3 -m json.tool .mcp.json > /dev/null && \
python3 -m json.tool hooks/hooks.json > /dev/null && echo OK
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add .mcp.json hooks/hooks.json
git commit -m "feat: wire MCP server and 4 hooks via plugin manifests"
```

---

## Task 19: README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write comprehensive README**

```markdown
# claude-mascot

A tsundere cat mascot (and friends) reacting to Claude Code activity in a tmux pane.

![demo](docs/demo.gif)

## Features

- A persistent mascot pane at the bottom of your tmux window
- Auto-opens when you start a Claude session, auto-closes when the session ends
- Updates its emotion/dialog at the end of every Claude response, based on what Claude said
- The `show_character` MCP tool lets Claude also trigger explicit reactions mid-conversation
- Only one mascot pane alive per tmux session — safe to use across multiple terminal tabs
- Language-configurable (Korean and English bundled)

## Requirements

- macOS or Linux
- [`tmux`](https://github.com/tmux/tmux) ≥ 3.0 (required — claude-mascot is tmux-only)
- [`uv`](https://docs.astral.sh/uv/) ≥ 0.4 (manages the Python venv automatically)
- Claude Code ≥ 1.0

Install prerequisites:

```bash
# macOS (Homebrew)
brew install tmux uv

# Linux (example for Ubuntu)
sudo apt install tmux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

In Claude Code, add this repo as a marketplace and install the plugin:

```
/plugins marketplace add github:<owner>/claude-mascot
/plugins install claude-mascot@claude-mascot-marketplace
```

Next time you open `claude` inside a tmux session, the mascot pane appears automatically.

## Configuration

All options live under `pluginConfigs["claude-mascot@claude-mascot-marketplace"].options` in `~/.claude/settings.json`:

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `character` | string | `"nabi"` | Which mascot character to display (currently only `nabi`) |
| `language` | `"ko" \| "en"` | `"ko"` | Message language |
| `paneHeight` | number (8–30) | `14` | Height of the tmux pane in rows |
| `stopHookEnabled` | boolean | `true` | Auto-update emotion at end of every Claude response |
| `startupEmotion` | emotion enum | `"happy"` | Emotion shown on fresh session start |

Example:

```json
{
  "pluginConfigs": {
    "claude-mascot@claude-mascot-marketplace": {
      "options": {
        "language": "en",
        "paneHeight": 16,
        "startupEmotion": "neutral"
      }
    }
  }
}
```

## Emotion Trigger Keywords (Stop hook)

When `stopHookEnabled` is on, the mascot reacts to Claude's last response based on keywords:

| Emotion | Sample keywords |
| --- | --- |
| angry | 틀렸, 잘못 됐, wrong, mistake |
| happy | 완료, 성공, 해결, done, passed, fixed |
| sad | 에러, 실패, error, failed, broken |
| shy | 감사, 고마, thank, 칭찬 |
| surprised | ?!, 어?, wait, 갑자기 |
| neutral | (fallback) |

Exact patterns live in `characters/nabi/emotion_rules.json`.

## Troubleshooting

- **Pane doesn't appear**: confirm `tmux` is running (`echo $TMUX` should be non-empty when you launch `claude`).
- **Python errors in MCP log**: check `uv` is installed and on PATH. Run `uv --version`.
- **Hook debug log**: `/tmp/claude_mascot_debug.log` shows hook invocations with timestamps.
- **Multi-tab fighting**: each tmux session gets its own independent mascot pane — if you see one pane dying when another starts, file a bug.

## Contributing

### Adding a new character

1. Create `characters/<id>/` with:
   - `character.json` (metadata: id, displayName, supportedEmotions, supportedLanguages, defaultLanguage)
   - `art.py` (`EMOTIONS` dict + `render()` function matching the signature in `characters/nabi/art.py`)
   - `messages.<lang>.json` per supported language
   - `emotion_rules.json` (priority + regex patterns)
   - `ascii/<emotion>.txt` per emotion
2. Add the id to the `character` enum in `.claude-plugin/plugin.json`
3. Test locally, then open a PR

### Running tests

```bash
uv run --extra dev pytest
```

## License

MIT — see `LICENSE`.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: comprehensive README with install, config, troubleshooting"
```

---

## Task 20: CHANGELOG

**Files:**
- Create: `CHANGELOG.md`

- [ ] **Step 1: Seed changelog**

```markdown
# Changelog

All notable changes to claude-mascot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-04-23

### Added
- Initial pre-stable release
- `nabi` tsundere cat character with 7 emotions
- MCP server exposing `show_character` and `list_emotions` tools
- 4 hooks: SessionStart (opens pane), SessionEnd (closes pane), Stop (keyword-driven emotion update), PostToolUse (inline ASCII for `show_character`)
- userConfig: `character`, `language` (ko/en), `paneHeight`, `stopHookEnabled`, `startupEmotion`
- Multi-tmux-session safety — panes are scoped per tmux session
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: CHANGELOG for v0.1.0"
```

---

## Task 21: End-to-End Local Install Verification

**Purpose:** Before tagging v0.1.0, verify the plugin installs and functions end-to-end from Claude Code.

- [ ] **Step 1: Ensure all unit tests pass**

```bash
cd /Users/jungchul/Projects/ToyProject/claude_plugin/claude-mascot
uv run --extra dev pytest -v
```

Expected: all tests green.

- [ ] **Step 2: Register as local marketplace**

Manually edit `~/.claude/settings.json` and add under `extraKnownMarketplaces`:

```json
"claude-mascot-local": {
  "source": {
    "source": "directory",
    "path": "/Users/jungchul/Projects/ToyProject/claude_plugin/claude-mascot"
  }
}
```

- [ ] **Step 3: Install the plugin via Claude Code**

Launch `claude` in a fresh terminal inside tmux. Run `/plugins` and install `claude-mascot@claude-mascot-local`. Exit (`Ctrl-D`).

- [ ] **Step 4: Confirm all hooks fire on next session**

In a fresh tmux window:
1. Start `claude` → mascot pane should appear at bottom with `happy` emotion.
2. Ask Claude anything with "완료" or "done" in the expected reply → confirm pane updates to happy.
3. Ask something that would prompt "에러" → pane updates to sad.
4. Type `/clear` → pane closes, reopens with `surprised`.
5. Exit `claude` → pane closes; check `ls /tmp/claude_mascot_pane_id_*` (should be empty).

- [ ] **Step 5: Verify multi-tab safety**

Open two tmux sessions (e.g. `tmux new -s A`, `tmux new -s B`). Run `claude` in each. Confirm each has its own independent pane and neither kills the other's.

- [ ] **Step 6: Clean up existing claude_warp_custom hooks**

Now that the plugin owns this behavior, remove the project-level hooks from `/Users/jungchul/.claude/settings.json` (the ones pointing at `claude_warp_custom/mcp_server/...`). Otherwise both plugin and global hooks fire and fight over the pane.

Open `~/.claude/settings.json` and delete the `hooks` block that references `claude_warp_custom`. Keep the plugin-managed hooks (which come from the plugin's `hooks/hooks.json`, not from user settings).

Also remove the now-redundant `tsundere-cat` MCP server from `~/.claude.json` top-level `mcpServers` (the plugin registers `claude-mascot` instead).

- [ ] **Step 7: Final smoke test after cleanup**

Open a fresh tmux tab, start `claude`, confirm mascot pane still appears (now via plugin path, not `claude_warp_custom`).

- [ ] **Step 8: Tag and push**

```bash
cd /Users/jungchul/Projects/ToyProject/claude_plugin/claude-mascot
git tag v0.1.0
# (manual) create GitHub repo <owner>/claude-mascot
# git remote add origin git@github.com:<owner>/claude-mascot.git
# git push -u origin main --tags
```

---

## Verification Summary

After all tasks complete, the repo at `/Users/jungchul/Projects/ToyProject/claude_plugin/claude-mascot/` should contain:

```
claude-mascot/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── .mcp.json
├── hooks/
│   └── hooks.json
├── mcp_server/
│   ├── __init__.py
│   ├── server.py
│   ├── pane.py
│   ├── display.py
│   ├── inline.py
│   ├── character.py
│   ├── emotion.py
│   └── hooks/
│       ├── __init__.py
│       ├── session_start.py
│       ├── session_end.py
│       └── on_stop.py
├── characters/
│   └── nabi/
│       ├── character.json
│       ├── art.py
│       ├── messages.ko.json
│       ├── messages.en.json
│       ├── emotion_rules.json
│       └── ascii/
│           └── *.txt (7)
├── tests/
│   ├── __init__.py
│   ├── test_character.py
│   └── test_emotion.py
├── docs/superpowers/
│   ├── specs/2026-04-23-claude-mascot-plugin-design.md
│   └── plans/2026-04-23-claude-mascot-plugin.md
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

All unit tests pass (`uv run --extra dev pytest -v`), end-to-end install verified, `v0.1.0` tagged.
