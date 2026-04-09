"""Tests for movement knowledge transformation helpers."""

from pathlib import Path

from video.movement_knowledge_import import (
    discover_gemini_analysis_files,
    normalize_string_list,
    parse_gemini_analysis_file,
    should_skip_json_file,
)


def test_normalize_string_list_deduplicates_case_insensitively() -> None:
    values = normalize_string_list(["Hip", " hip ", "", None, "HIP", "Pelvis"])

    assert values == ["Hip", "Pelvis"]


def test_should_skip_json_file_for_aggregate_outputs() -> None:
    assert should_skip_json_file(Path("aggregate_newest_11_20.json"))
    assert should_skip_json_file(Path("aggregate.json"))
    assert should_skip_json_file(Path("run_summary.json"))
    assert not should_skip_json_file(Path("021_example.json"))


def test_parse_gemini_analysis_file_builds_units_and_taxonomy() -> None:
    path = Path("D:/sistema-biomecanico/data/knowledge/video_knowledge_drafts/conorharris_newest_21_30/021_Hu8_UCv4tLA.json")

    document = parse_gemini_analysis_file(path)

    assert document.source_video.external_video_id == "Hu8_UCv4tLA"
    assert document.analysis.content_kind == "mixed"
    assert document.analysis.body_regions
    assert len(document.knowledge_units) == 3
    assert ("unit_type", "corrective_exercise") in document.taxonomy_entries


def test_discover_gemini_analysis_files_returns_per_video_jsons() -> None:
    root = Path("D:/sistema-biomecanico/data/knowledge/video_knowledge_drafts/sample_classification_checks")

    files = discover_gemini_analysis_files(root)

    names = {path.name for path in files}
    assert "LhHzjljWriE.json" in names
    assert "aggregate.json" not in names
