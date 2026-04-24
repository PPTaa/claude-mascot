# Changelog

All notable changes to claude-mascot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] — 2026-04-24

### Added
- `fubao` character (느긋한 판다) — image-based mascot rendered from CC-licensed panda photos pre-processed via `chafa`.
- Frames-based renderer architecture: each `characters/<id>/art.py` declares `RENDERER = "programmatic" | "frames"`; `Animator` dispatches accordingly.
- `scripts/prerender.py` dev-time build tool — converts raw character images to ANSI text frames at 3 sizes (10x10 / 20x20 / 30x30). End users do not need `chafa`.
- `pane_height` now flows into `Animator`, so the frames renderer can pick a size that fits the configured tmux pane and keep the message line on screen.

### Changed
- `character` userConfig description updated to accept `"nabi" | "fubao"` (still a free-form string — Claude Code's plugin schema does not support enum constraints yet).
- `_compute_state()` extracted from `Animator.tick()` so both render pipelines share state bookkeeping.

### Fixed
- `_compute_state()` no longer KeyErrors on characters whose EMOTIONS dict lacks `eyes` / `decos` keys.

## [0.1.0] — 2026-04-23

### Added
- Initial pre-stable release
- `nabi` tsundere cat character with 7 emotions
- MCP server exposing `show_character` and `list_emotions` tools
- 4 hooks: SessionStart (opens pane), SessionEnd (closes pane), Stop (keyword-driven emotion update), PostToolUse (inline ASCII for `show_character`)
- userConfig: `character`, `language` (ko/en), `paneHeight`, `stopHookEnabled`, `startupEmotion`
- Multi-tmux-session safety — panes are scoped per tmux session


## todo: 
- 나비랑 전용 대화 창
- 푸바오, 강아지, 
- 이미지추가.
