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
