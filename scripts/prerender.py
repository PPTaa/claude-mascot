"""Pre-render raw character images to ANSI text frames via chafa.

Usage:
    uv run scripts/prerender.py <character>            # render one character
    uv run scripts/prerender.py --all                  # all frames-renderer characters
    uv run scripts/prerender.py <character> --check    # report missing frames only
"""
import argparse
import json
import shutil
import subprocess
import sys
from itertools import product
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
CHARACTERS_DIR = PLUGIN_ROOT / "characters"

SIZES = {
    "small":  (10, 10),
    "medium": (20, 20),
    "large":  (30, 30),
}
STATES = ["idle", "blink", "special"]
RAW_EXTS = [".jpg", ".jpeg", ".png", ".webp"]


def find_raw_image(raw_dir: Path, emotion: str, state: str) -> Path | None:
    for ext in RAW_EXTS:
        candidate = raw_dir / f"{emotion}_{state}{ext}"
        if candidate.exists():
            return candidate
    return None


def missing_frames(char_dir: Path, emotions: list[str], states: list[str]) -> list[tuple[str, str, str]]:
    """Return list of (size, emotion, state) tuples whose frame text file is missing."""
    result = []
    for size_name in SIZES:
        for emotion, state in product(emotions, states):
            path = char_dir / "frames" / size_name / f"{emotion}_{state}.txt"
            if not path.exists():
                result.append((size_name, emotion, state))
    return result


def render_one(src: Path, out: Path, w: int, h: int) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["chafa", "-f", "symbols", "-c", "full",
         "--size", f"{w}x{h}", "--polite", "on", str(src)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"chafa failed on {src}: {result.stderr}")
    out.write_text(result.stdout, encoding="utf-8")


def render_character(character_id: str, check_only: bool = False) -> int:
    char_dir = CHARACTERS_DIR / character_id
    meta_path = char_dir / "character.json"
    if not meta_path.exists():
        print(f"error: character '{character_id}' not found at {char_dir}", file=sys.stderr)
        return 1

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("renderer") != "frames":
        print(f"error: '{character_id}' is not a frames-renderer character", file=sys.stderr)
        return 1

    emotions = meta["supportedEmotions"]

    if check_only:
        missing = missing_frames(char_dir, emotions, STATES)
        if missing:
            print(f"{len(missing)} missing frame file(s):")
            for size, emo, st in missing:
                print(f"  {size}/{emo}_{st}.txt")
            return 1
        print(f"all {len(SIZES) * len(emotions) * len(STATES)} frames present")
        return 0

    if shutil.which("chafa") is None:
        print("error: chafa not installed. Install with 'brew install chafa' (macOS) or your package manager.", file=sys.stderr)
        return 1

    raw_dir = char_dir / "raw"
    missing_raw = []
    rendered = 0
    for emotion, state in product(emotions, STATES):
        src = find_raw_image(raw_dir, emotion, state)
        if src is None:
            missing_raw.append(f"{emotion}_{state}")
            continue
        for size_name, (w, h) in SIZES.items():
            out = char_dir / "frames" / size_name / f"{emotion}_{state}.txt"
            render_one(src, out, w, h)
            rendered += 1

    print(f"rendered {rendered} frame files")
    if missing_raw:
        print(f"warning: {len(missing_raw)} raw image(s) missing:", file=sys.stderr)
        for name in missing_raw:
            print(f"  raw/{name}.<jpg|png|webp>", file=sys.stderr)
        return 1
    return 0


def list_frames_characters() -> list[str]:
    result = []
    for char_dir in CHARACTERS_DIR.iterdir():
        if not char_dir.is_dir():
            continue
        meta = char_dir / "character.json"
        if not meta.exists():
            continue
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if data.get("renderer") == "frames":
            result.append(char_dir.name)
    return result


def main():
    ap = argparse.ArgumentParser(description="Pre-render character images to ANSI text frames")
    ap.add_argument("character", nargs="?", help="Character id (e.g. 'fubao')")
    ap.add_argument("--all", action="store_true", help="Render all frames-renderer characters")
    ap.add_argument("--check", action="store_true", help="Only report missing frames, do not render")
    args = ap.parse_args()

    if args.all:
        chars = list_frames_characters()
        if not chars:
            print("no frames-renderer characters found")
            return 0
        exit_code = 0
        for c in chars:
            exit_code = max(exit_code, render_character(c, check_only=args.check))
        return exit_code

    if not args.character:
        ap.error("character id required (or pass --all)")

    return render_character(args.character, check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
