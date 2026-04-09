"""Tests for Gemini knowledge extraction helpers."""

from pathlib import Path

from video.gemini_knowledge import load_gemini_api_key


def test_load_gemini_api_key_reads_from_env_example() -> None:
    key = load_gemini_api_key()

    assert key
    assert isinstance(key, str)
