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
