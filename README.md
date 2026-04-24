# claude-mascot

**English** · [한국어](README.ko.md)

A tsundere cat mascot (and friends) reacting to Claude Code activity in a tmux pane.

## Features

- A persistent mascot pane at the bottom of your tmux window
- Auto-opens when a Claude session starts, auto-closes when it ends
- Reacts at the end of every Claude response:
  - **Preferred path**: Claude calls `show_character` with a contextual tsundere one-liner generated from the current turn
  - **Fallback path**: if Claude forgot, the `Stop` hook scans the transcript for emotion keywords and picks a random line from the character's message pool
- Only one mascot pane alive per tmux session — safe across multiple terminal tabs
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

# Linux (Ubuntu example)
sudo apt install tmux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

Inside Claude Code, register this repo as a marketplace, then install the plugin:

```
/plugin marketplace add PPTaa/claude-mascot
/plugin install claude-mascot@claude-mascot-marketplace
```

Then run `claude` inside a tmux session — the mascot pane appears at the bottom automatically.

## Characters

Two characters ship with the plugin. Switch between them via the `character` userConfig.

| ID | Name | Renderer | Notes |
| --- | --- | --- | --- |
| `nabi` | Nabi (tsundere cat) | `programmatic` | Programmatic ANSI art with blinking, tail, and decorations. Default. |
| `fubao` | Fubao (느긋한 판다) | `frames` | Pre-rendered ANSI image frames produced from CC-licensed panda photos via `chafa`. |

Adding a frames-renderer character of your own:

1. Mirror `characters/fubao/` — `character.json` (`"renderer": "frames"`), `emotion_rules.json`, `messages.<lang>.json`, `art.py` with `RENDERER = "frames"`.
2. Drop raw images into `characters/<name>/raw/` as `<emotion>_<state>.{jpg,png,webp}`.
3. Install `chafa` locally (`brew install chafa` on macOS).
4. Run `uv run scripts/prerender.py <name>` — generates `frames/{small,medium,large}/*.txt`.
5. Add your id to the `character` enum in `.claude-plugin/plugin.json`.

End users don't need `chafa` installed — the committed `frames/` files are all the runtime needs.

## Configuration

All options live under `pluginConfigs["claude-mascot@claude-mascot-marketplace"].options` in `~/.claude/settings.json`:

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `character` | `"nabi" \| "fubao"` | `"nabi"` | Which mascot character to display |
| `language` | `"ko" \| "en"` | `"ko"` | Message language |
| `paneHeight` | number (8–30) | `14` | Height of the tmux pane in rows |
| `stopHookEnabled` | boolean | `true` | Enable the transcript-scanning fallback at end of every response |
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

## How reactions are chosen

Each Claude turn the pane gets updated exactly once:

1. If Claude called `show_character(emotion, message)` during the turn, a session-scoped marker file is written and that message stays on the pane. The `Stop` hook sees the marker and skips its fallback.
2. Otherwise the `Stop` hook reads both the last user message and last assistant message from the transcript, runs regex classification, and picks a random line from the matching emotion pool defined in `characters/<id>/messages.<lang>.json`.

### Emotion trigger keywords (fallback path)

| Emotion | Sample keywords |
| --- | --- |
| angry | 틀렸, 잘못 됐, wrong, mistake, 뒤질, 짜증, 바보, 멍청, angry, shut up |
| happy | 완료, 성공, 해결, done, passed, fixed |
| sad | 에러, 실패, error, failed, broken |
| shy | 감사, 고마, thank, 칭찬, 잘했 |
| surprised | ?!, 어?, wait, 갑자기 |
| neutral | (fallback when nothing matches) |

Exact patterns: `characters/nabi/emotion_rules.json`.

## Troubleshooting

- **Pane doesn't appear** — confirm `tmux` is running (`echo $TMUX` should be non-empty when you launch `claude`).
- **Python errors in MCP log** — check `uv` is installed and on PATH: `uv --version`.
- **Hook debug log** — `/tmp/claude_mascot_debug.log` shows hook invocations with timestamps. A `skipped: claude already called show_character this turn` entry means the marker path worked; a `character=… emotion=… user_len=… assistant_len=…` entry means the fallback ran.
- **Mascot stops reacting after plugin code changes** — the MCP server is a long-lived process. Run `/mcp` → reconnect `claude-mascot`, or restart Claude Code.
- **Multi-tab conflicts** — each tmux session gets its own independent mascot pane; cross-session kills are suppressed.

## Contributing

### Adding a new character

See the "Characters" section above for the quick recipe. Both renderers are supported:

- **`RENDERER = "programmatic"`** — Python `render()` returns ANSI lines per tick (see `characters/nabi/art.py`). Good for ASCII art with live tweens.
- **`RENDERER = "frames"`** — pre-rendered ANSI text files loaded at runtime (see `characters/fubao/art.py`). Good for photo- or illustration-based characters.

Update the `character` enum in `.claude-plugin/plugin.json` to include your new id. Test locally, open a PR.

### Running tests

```bash
uv run --extra dev pytest
```

## License

MIT — see `LICENSE`.
