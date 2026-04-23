"""Emotion classification and message selection — pure functions."""

import random
import re


def pick_emotion(text: str, rules: dict) -> str:
    """Classify text into an emotion based on priority-ordered regex rules."""
    patterns = rules.get("patterns", {})
    for emo in rules.get("priority", []):
        pat = patterns.get(emo)
        if pat and re.search(pat, text, re.IGNORECASE):
            return emo
    return rules.get("default", "neutral")


def pick_message(emotion: str, messages: dict) -> str:
    """Pick a random message from the pool for the given emotion.
    Falls back to 'neutral' pool, then empty string."""
    pool = messages.get(emotion) or messages.get("neutral") or []
    if not pool:
        return ""
    return random.choice(pool)
