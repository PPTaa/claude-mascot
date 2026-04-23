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
