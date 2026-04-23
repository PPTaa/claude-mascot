import pytest
from mcp_server import emotion


RULES = {
    "priority": ["angry", "happy", "sad"],
    "patterns": {
        "angry": r"(틀렸|wrong\b)",
        "happy": r"(완료|done\b|해결(?!\s*안))",
        "sad": r"(에러|error|failed)",
    },
    "default": "neutral",
}


def test_pick_emotion_happy():
    assert emotion.pick_emotion("빌드 완료!", RULES) == "happy"


def test_pick_emotion_sad():
    assert emotion.pick_emotion("에러 발생", RULES) == "sad"


def test_pick_emotion_angry_wins_over_sad():
    assert emotion.pick_emotion("에러가 나서 틀렸네", RULES) == "angry"


def test_pick_emotion_happy_wins_over_sad_for_resolution():
    assert emotion.pick_emotion("에러 해결 완료", RULES) == "happy"


def test_pick_emotion_default_when_no_match():
    assert emotion.pick_emotion("그냥 일반 문장", RULES) == "neutral"


def test_pick_message_returns_from_pool():
    msgs = {"happy": ["a", "b", "c"]}
    picked = emotion.pick_message("happy", msgs)
    assert picked in ["a", "b", "c"]


def test_pick_message_fallback_to_neutral():
    msgs = {"neutral": ["default"]}
    picked = emotion.pick_message("angry", msgs)
    assert picked == "default"


def test_pick_message_empty_pool_returns_empty_string():
    picked = emotion.pick_message("angry", {})
    assert picked == ""
