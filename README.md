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
