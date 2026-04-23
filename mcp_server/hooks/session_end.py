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
