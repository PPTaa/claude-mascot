"""Display animator — runs inside a tmux pane, renders a character's frames in a loop.
Invoked as `python -m mcp_server.display <character> <language> <pane_height> <emotion> [message]`."""

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
