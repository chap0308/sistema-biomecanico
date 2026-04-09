"""Tests for Gemini upgrade candidate selection."""

from __future__ import annotations

from argparse import Namespace

from scripts.upgrade_drafts_to_gemini import _select_candidates


class _FakeStore:
    def list_gemini_upgrade_candidates(self, *, limit: int, ascending: bool, cooldown_hours: int):
        return [{"draft_id": "a", "analysis_provider": "hf_structured", "analysis_quality": "standard", "source_url": "u1"}]

    def fetch_upgrade_candidates_by_urls(self, urls):
        return [
            {"draft_id": "a", "analysis_provider": "hf_structured", "analysis_quality": "standard", "source_url": urls[0]},
            {"draft_id": "b", "analysis_provider": "gemini", "analysis_quality": "premium", "source_url": urls[1]},
        ]


def test_select_candidates_uses_limit_mode() -> None:
    args = Namespace(urls=None, limit=5, order="asc", cooldown_hours=24)

    rows = _select_candidates(_FakeStore(), args)

    assert len(rows) == 1
    assert rows[0]["draft_id"] == "a"


def test_select_candidates_filters_existing_gemini_rows_in_url_mode() -> None:
    args = Namespace(urls=["https://a", "https://b"], limit=10, order="asc", cooldown_hours=24)

    rows = _select_candidates(_FakeStore(), args)

    assert len(rows) == 1
    assert rows[0]["analysis_provider"] == "hf_structured"
