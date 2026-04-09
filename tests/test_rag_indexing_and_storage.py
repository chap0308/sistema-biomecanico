"""Tests for indexing and storage-adjacent RAG helpers."""

import shutil
import uuid
from pathlib import Path

from src.chunking.segment_builder import build_segment
from src.core.models import Source
from src.indexing.embeddings import embed_text
from src.indexing.qdrant_store import QdrantStore, make_qdrant_point_id, segment_to_point
from src.indexing.sparse import build_sparse_weights, tokenize
from src.pipelines.process_video_local import process_video_local
from src.storage.supabase_store import compute_segment_sha


def test_embed_text_returns_fixed_dimension_vector() -> None:
    vector = embed_text("shoulder internal rotation", dimensions=12)

    assert len(vector) == 12
    assert vector == embed_text("shoulder internal rotation", dimensions=12)


def test_sparse_weights_normalize_term_frequency() -> None:
    weights = build_sparse_weights("hip hip rotation")

    assert tokenize("hip hip rotation") == ["hip", "hip", "rotation"]
    assert weights["hip"] > weights["rotation"]


def test_segment_to_point_builds_dense_sparse_and_payload() -> None:
    segment = build_segment(
        source_id="src_1",
        segment_index=1,
        start_sec=0.0,
        end_sec=5.0,
        transcript="Hip rotation drill",
        topics=["hip"],
        keywords=["rotation"],
        payload={"source_type": "youtube"},
    )

    point = segment_to_point(segment, dense_dimensions=10)

    assert point.point_id == make_qdrant_point_id(segment.segment_id)
    assert len(point.dense_vector) == 10
    assert point.sparse_weights
    assert point.payload["segment_id"] == segment.segment_id


def test_make_qdrant_point_id_is_stable_uuid() -> None:
    point_id = make_qdrant_point_id("seg_example_1")

    assert point_id == make_qdrant_point_id("seg_example_1")
    assert len(point_id) == 36


def test_compute_segment_sha_changes_with_content() -> None:
    segment_a = build_segment(source_id="src_1", segment_index=1, start_sec=0.0, end_sec=5.0, transcript="A")
    segment_b = build_segment(source_id="src_1", segment_index=1, start_sec=0.0, end_sec=5.0, transcript="B")

    assert compute_segment_sha(segment_a) != compute_segment_sha(segment_b)


def test_process_video_local_creates_bootstrap_segment() -> None:
    source = Source(source_type="local_video", uri="D:/videos/example.mp4", title="Example video", duration_sec=12.0, tags=["scapula"])

    result = process_video_local(source)

    assert result["status"] == "bootstrap_ready"
    assert len(result["segments"]) == 1
    assert result["segments"][0].retrieval_text


def test_qdrant_store_embedded_upsert_and_query() -> None:
    segment = build_segment(
        source_id="src_1",
        segment_index=1,
        start_sec=0.0,
        end_sec=5.0,
        transcript="Scapular upward rotation drill",
        topics=["scapula"],
        keywords=["rotation", "drill"],
        payload={"source_type": "youtube", "title": "Test"},
    )

    test_dir = Path("data/test-qdrant") / f"qdrant_{uuid.uuid4().hex}"
    shutil.rmtree(test_dir, ignore_errors=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    store = QdrantStore(path=str(test_dir), collection_name="test_segments", dense_dimensions=16)

    try:
        assert store.upsert_segments([segment]) == 1

        results = store.query("scapular rotation", limit=3)

        assert results
        assert results[0].payload["segment_id"] == segment.segment_id
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
