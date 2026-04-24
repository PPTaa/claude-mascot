# Fubao Character — Image-Based Mascot Design

**Date:** 2026-04-24
**Status:** Approved (brainstorming)
**Author:** Jake.Lee (with Claude)

## Summary

Add a second mascot character, `fubao` (the Everland panda), that renders
from image assets instead of programmatic ASCII art. Images are pre-rendered
to ANSI text at build time using `chafa`, so the end-user does **not** need
`chafa` installed. The existing `nabi` character is untouched and both
coexist behind the existing `character` userConfig.

## Goals

- Support an additional rendering pipeline ("frames") alongside the existing
  programmatic pipeline, selectable per-character.
- Ship pre-rendered ANSI text assets so runtime has zero extra dependencies.
- Keep the existing animator loop and emotion state machine intact — only
  the per-tick frame source changes.
- Provide a repeatable developer workflow for converting raw images to
  ANSI text frames.

## Non-Goals

- Live/dynamic image rendering at runtime (no runtime `chafa` dependency).
- Replacing `nabi`. Nabi remains the default.
- True pixel-level animation. "Animation" is limited to the 3-state swap
  already used by the animator (idle / blink / special).
- Kitty/iTerm2/Sixel graphics protocols. Output is always plain ANSI text
  so it works inside tmux and in any terminal.

## Folder Layout

```
characters/fubao/
├── character.json              # metadata (mirrors nabi)
├── emotion_rules.json          # stop-hook emotion triggers
├── messages.ko.json            # cute/lazy panda tone
├── messages.en.json
├── raw/                        # original images, committed to git
│   ├── neutral_idle.jpg
│   ├── neutral_blink.jpg
│   ├── neutral_special.jpg
│   ├── ... (7 emotions × 3 states = 21 files)
│   └── SOURCES.md              # per-file license / attribution
├── frames/                     # pre-rendered ANSI text, committed
│   ├── small/                  # 6×6 cells    (pane_height 8–11)
│   ├── medium/                 # 10×10 cells  (pane_height 12–20, default 14)
│   └── large/                  # 18×18 cells  (pane_height 21–30)
│       ├── neutral_idle.txt
│       └── ... (21 text files per size, 63 total)
└── art.py                      # frame loader + render()

scripts/
└── prerender.py                # developer build tool (raw/ → frames/)
```

Total committed text assets: 21 raw images + 63 ANSI text files.

## Runtime Renderer

Each character's `art.py` declares a module-level constant indicating which
rendering mode it uses:

```python
# characters/nabi/art.py
RENDERER = "programmatic"    # existing code, one added line

# characters/fubao/art.py
RENDERER = "frames"
```

### Fubao `art.py`

```python
from pathlib import Path

RENDERER = "frames"

EMOTIONS = {
    "neutral":   dict(msg="대나무 먹는 중...",  sp_msg="으앙 졸려..."),
    "happy":     dict(msg="헤헤~ 기분 좋아",   sp_msg="냠냠 맛있어~"),
    "angry":     dict(msg="뿌우~ 삐졌어",      sp_msg="흥칫뿡이야!"),
    "shy":       dict(msg="으응... 부끄부끄",  sp_msg="휘릭... 숨을래"),
    "sad":       dict(msg="흐엥... 슬퍼...",   sp_msg="쭈르륵..."),
    "surprised": dict(msg="헙?! 뭐야 뭐야?",   sp_msg="으아앗!"),
    "love":      dict(msg="뿌잉뿌잉 ♥",        sp_msg="우효오~ ♥♥"),
}

_FRAMES_DIR = Path(__file__).parent / "frames"

def _pick_size(pane_height: int) -> str:
    if pane_height <= 11: return "small"
    if pane_height <= 20: return "medium"
    return "large"

def _load(size: str, emotion: str, state: str) -> list[str]:
    path = _FRAMES_DIR / size / f"{emotion}_{state}.txt"
    try:
        return path.read_text().splitlines()
    except FileNotFoundError:
        return [f"[frame missing: {emotion}_{state}]"]

def render(cfg, emotion, state, message, pane_height):
    """state ∈ {idle, blink, special}. Returns list[str] sized to fit pane."""
    size = _pick_size(pane_height)
    pane_lines = max(7, min(29, pane_height - 1))
    img_lines = _load(size, emotion, state)
    # Reserve last 3 rows for the message; clip image bottom if needed so
    # display.py's lines[:pane_lines] never drops the message row.
    img_budget = max(1, pane_lines - 3)
    return img_lines[:img_budget] + ["", f"  {message}", ""]
```

### Animator Dispatch (`mcp_server/display.py`)

The existing Animator already computes `idle` / `blink` / `special` state
each tick. Add a branch that picks the right render signature based on the
character's `RENDERER` constant:

```python
class Animator:
    def __init__(self, character_id, emotion, custom_message="", pane_height=14):
        ...
        self.pane_height = pane_height  # new: passed through from main()

    def tick(self):
        self.t += 1
        state = self._compute_state()  # returns dict with state/eyes/msg/deco/shake

        if self.art_mod.RENDERER == "frames":
            return self.art_mod.render(
                self.cfg, self.emo, state["state"],
                state["msg"], self.pane_height,
            )
        else:  # "programmatic"
            return self.art_mod.render(
                self.cfg, state["eyes"], state["msg"],
                state["deco"], self.t, state["shake"],
            )
```

`_compute_state()` is a small refactor of the existing logic in `tick()`
that currently returns nothing and relies on local variables. It will be
extracted so both render paths can share it.

`main()` passes `pane_height` into `Animator(...)`.

### Animation State Mapping

| State     | Trigger               | Duration | Fubao frame file       |
|-----------|-----------------------|----------|------------------------|
| `idle`    | baseline              | default  | `{emotion}_idle.txt`   |
| `blink`   | every 8–15 ticks      | 2 ticks  | `{emotion}_blink.txt`  |
| `special` | every 25–40 ticks     | 4 ticks  | `{emotion}_special.txt`|

Sizing rationale: sizes are square (W = H) so chafa preserves image aspect
on roughly 2:1 terminal cells — the rendered panda will appear slightly
squished vertically, which is the expected terminal-image look. Each
rendered frame plus 3 lines (blank + message + blank) should fit inside
`pane_lines = max(7, min(29, pane_height-1))`; at the smallest panes
(8–9 rows) the image may be clipped from the bottom. The renderer in
`art.py` builds the lines with the message positioned so that
`lines[:pane_lines]` always keeps the message row — that is, image bottom
is sacrificed before the message. Final dimensions may adjust by ±2 cells
after visual testing on real panes.

Notes:
- `sp_msg` replaces `msg` only during `special` state (existing behavior).
- `shake` (used by nabi for angry) is **not applied** in frames mode —
  pixel shake doesn't translate. Instead, use a more intense
  `angry_special.jpg` to convey impact.
- Decorations (`♪ ♥ !`) are **not rendered** around fubao; panda styling
  stays minimal.

## Build Pipeline

### Script: `scripts/prerender.py`

Usage:
```
uv run scripts/prerender.py fubao          # single character
uv run scripts/prerender.py --all          # all frames-renderer characters
uv run scripts/prerender.py fubao --check  # verify frames complete, no render
```

Behavior:
- Load the character's `character.json`; abort if `renderer != "frames"`.
- For each `(emotion, state)` in the character's supported set, look up the
  matching raw file (accept `.jpg`, `.png`, `.webp`).
- For each size in `{small: (6,6), medium: (10,10), large: (18,18)}`,
  invoke:
  ```
  chafa -f symbols -c full --size {W}x{H} --polite on {raw}
  ```
  and write stdout to `frames/{size}/{emotion}_{state}.txt`.
- If `chafa` is missing, print install guide and exit 1.
- Report any missing raw files as a summary at the end. Script is
  non-destructive to other characters.

### Git Policy

| Path                              | Committed? | Reason |
|-----------------------------------|------------|--------|
| `characters/fubao/raw/**`         | yes        | so rebuilds are possible |
| `characters/fubao/raw/SOURCES.md` | yes        | attribution / license proof |
| `characters/fubao/frames/**`      | yes        | end-user runs without chafa |

Raw files should be ≤ ~300 KB each to keep repo size reasonable; downsample
before committing if needed.

## Asset Sourcing

- Use only CC-licensed or public-domain sources (Wikimedia Commons,
  compatible Flickr, official press kits that allow editorial reuse).
- `raw/SOURCES.md` records for each file: URL, author, license, any
  modifications.
- Avoid Everland-copyrighted professional photos unless under a clear
  reusable license.

## Configuration

Update `plugin.json`:

```json
"character": {
  "type": "string",
  "title": "Character",
  "description": "Which mascot character to display (nabi | fubao)",
  "enum": ["nabi", "fubao"],
  "default": "nabi"
}
```

Other userConfig fields (`language`, `paneHeight`, `stopHookEnabled`,
`startupEmotion`) apply unchanged.

## Error Handling

- **Missing frame file at runtime**: `_load()` returns a single-line
  placeholder `[frame missing: <emotion>_<state>]` and writes a one-line
  warning to stderr. The animator loop keeps running.
- **Missing `frames/` directory entirely**: detected at Animator init, logs
  a clear message pointing at `scripts/prerender.py`, falls back to a
  minimal text-only "fubao unavailable" pane that still respects the loop
  cadence (so the pane doesn't churn).
- **`chafa` missing during build**: script exits with install instructions;
  does not attempt to install anything.
- **Malformed `raw/` filename**: logged and skipped, overall build
  continues.

## Testing

`tests/test_fubao.py`:
- `RENDERER == "frames"` constant present.
- `EMOTIONS` dict contains all 7 expected keys with `msg` and `sp_msg`.
- `_pick_size()` boundary values: 11 → small, 12 → medium, 20 → medium,
  21 → large.
- `render()` returns a `list[str]` whose last non-empty line contains the
  passed message.
- Missing-frame fallback: `_load("medium", "nonexistent", "idle")` returns
  a non-empty list without raising.

Integration test (can be skipped in CI if assets aren't yet in place):
- All 63 expected `frames/*/*.txt` files exist and are non-empty when
  the fubao character is considered "shipped".

`scripts/prerender.py` itself is exercised via `--check` mode rather than
unit tests (actual chafa invocation is dev-only).

## Documentation

- `README.md` / `README.ko.md`:
  - Add fubao to the character list with a short description.
  - Add a short "Adding your own character" section: drop raw images into
    `characters/<name>/raw/`, mirror the fubao file layout, run
    `uv run scripts/prerender.py <name>`.
  - Note that `chafa` is only needed for authors, not end users.
- `CHANGELOG.md`: `v0.2.0` entry — "Add fubao character (image-based
  rendering) and frames renderer".

## Open Questions

- Exact asset sources — to be identified during implementation. If
  CC-licensed fubao imagery is insufficient, fall back to generic "cute
  panda" imagery and document the substitution in `SOURCES.md`.
- Whether to bundle `scripts/prerender.py` as a console entry in
  `pyproject.toml`. Low-cost to add; decision deferred to implementation.

## Rollout

1. Scaffold `characters/fubao/` structure (no art yet).
2. Add `RENDERER` constant to nabi (no behavior change).
3. Extract `_compute_state()` in display.py, add dispatch branch.
4. Implement `scripts/prerender.py`.
5. Source raw images, populate `raw/` + `SOURCES.md`.
6. Run prerender, commit `frames/`.
7. Update userConfig enum, README, CHANGELOG.
8. Tests pass locally; tag `v0.2.0`.
