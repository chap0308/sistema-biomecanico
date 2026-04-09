"""Qdrant storage wrapper for retrieval-ready segments."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.core.models import Segment
from src.indexing.embeddings import embed_text
from src.indexing.payloads import make_qdrant_payload
from src.indexing.sparse import build_sparse_weights

QDRANT_POINT_NAMESPACE = uuid.UUID("4f2bf22d-d92b-4c98-b79e-6ea58f6f8844")


@dataclass(slots=True)
class QdrantPoint:
    """Serializable point representation independent of a live Qdrant client."""

    point_id: str
    dense_vector: list[float]
    sparse_weights: dict[str, float]
    payload: dict[str, object]


@dataclass(slots=True)
class QdrantSearchResult:
    """One retrieval result coming back from Qdrant."""

    point_id: str
    score: float
    payload: dict[str, object]


def make_qdrant_point_id(segment_id: str) -> str:
    """Return a deterministic UUID so local Qdrant accepts stable point ids."""
    return str(uuid.uuid5(QDRANT_POINT_NAMESPACE, segment_id))


def segment_to_point(segment: Segment, *, dense_dimensions: int = 32) -> QdrantPoint:
    """Convert one segment into a Qdrant-ready point representation."""
    retrieval_text = segment.retrieval_text.strip()
    return QdrantPoint(
        point_id=make_qdrant_point_id(segment.segment_id or ""),
        dense_vector=embed_text(retrieval_text, dimensions=dense_dimensions),
        sparse_weights=build_sparse_weights(retrieval_text),
        payload=make_qdrant_payload(segment),
    )


def segments_to_points(segments: Iterable[Segment], *, dense_dimensions: int = 32) -> list[QdrantPoint]:
    """Convert multiple segments into Qdrant-ready points."""
    return [segment_to_point(segment, dense_dimensions=dense_dimensions) for segment in segments]


class QdrantStore:
    """Thin wrapper for future Qdrant operations."""

    def __init__(
        self,
        *,
        url: str | None = None,
        path: str | None = None,
        api_key: str | None = None,
        collection_name: str,
        dense_dimensions: int = 32,
    ) -> None:
        self.url = url
        self.path = str(Path(path).resolve()) if path else None
        self.api_key = api_key
        self.collection_name = collection_name
        self.dense_dimensions = dense_dimensions

    def _make_client(self):
        from qdrant_client import QdrantClient

        if self.path:
            return QdrantClient(path=self.path)
        if not self.url:
            raise ValueError("QdrantStore requires either url or path.")
        api_key = self.api_key or None
        return QdrantClient(url=self.url, api_key=api_key)

    def collection_exists(self) -> bool:
        """Return whether the target collection is visible to the active Qdrant endpoint."""
        client = self._make_client()
        try:
            collections = {item.name for item in client.get_collections().collections}
            return self.collection_name in collections
        finally:
            client.close()

    def build_points(self, segments: Iterable[Segment]) -> list[QdrantPoint]:
        """Build points without requiring a live Qdrant server."""
        return segments_to_points(segments, dense_dimensions=self.dense_dimensions)

    def ensure_collection(self) -> None:
        """Create the collection if it does not already exist."""
        from qdrant_client.http import models

        client = self._make_client()
        try:
            if self.collection_exists():
                self.ensure_source_id_index()
                return
            try:
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=self.dense_dimensions, distance=models.Distance.COSINE),
                )
            except Exception:
                # Retry one visibility check before surfacing the failure. This helps when
                # Qdrant creates the collection but the first HTTP response races with local state.
                if self.collection_exists():
                    self.ensure_source_id_index()
                    return
                raise
            self.ensure_source_id_index()
        finally:
            client.close()

    def ensure_source_id_index(self) -> None:
        """Ensure payload filtering by source_id works on Qdrant backends that require indexes."""
        from qdrant_client.http import models

        if not self.collection_exists():
            return
        client = self._make_client()
        try:
            try:
                client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="source_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                    wait=True,
                )
            except Exception as exc:
                message = str(exc).lower()
                if "already exists" in message or "conflict" in message:
                    return
                raise
        finally:
            client.close()

    def upsert_segments(self, segments: Iterable[Segment]) -> int:
        """Upsert segments into Qdrant."""
        from qdrant_client.http import models

        points = self.build_points(segments)
        if not points:
            return 0

        self.ensure_collection()
        client = self._make_client()
        try:
            client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point.point_id,
                        vector=point.dense_vector,
                        payload={
                            **point.payload,
                            "_sparse_weights": point.sparse_weights,
                        },
                    )
                    for point in points
                ],
            )
        finally:
            client.close()
        return len(points)

    def delete_by_source_id(self, source_id: str) -> int:
        """Delete all points for one source from the active collection."""
        from qdrant_client.http import models
        from qdrant_client.http.exceptions import UnexpectedResponse

        if not source_id or not self.collection_exists():
            return 0

        client = self._make_client()
        try:
            try:
                result = client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.FilterSelector(
                        filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="source_id",
                                    match=models.MatchValue(value=source_id),
                                )
                            ]
                        )
                    ),
                    wait=True,
                )
            except UnexpectedResponse as exc:
                lowered = str(exc).lower()
                if "index required but not found" in lowered and "source_id" in lowered:
                    self.ensure_source_id_index()
                    result = client.delete(
                        collection_name=self.collection_name,
                        points_selector=models.FilterSelector(
                            filter=models.Filter(
                                must=[
                                    models.FieldCondition(
                                        key="source_id",
                                        match=models.MatchValue(value=source_id),
                                    )
                                ]
                            )
                        ),
                        wait=True,
                    )
                elif "doesn't exist" in lowered or "not found: collection" in lowered:
                    return 0
                else:
                    raise
        finally:
            client.close()

        operation_id = getattr(result, "operation_id", None)
        return 1 if operation_id is not None else 0

    def query(self, query_text: str, *, limit: int = 5) -> list[QdrantSearchResult]:
        """Query Qdrant using the same embedding function as indexing."""
        from qdrant_client.http.exceptions import UnexpectedResponse

        query_vector = embed_text(query_text, dimensions=self.dense_dimensions)
        client = self._make_client()
        try:
            try:
                response = client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False,
                )
            except UnexpectedResponse as exc:
                if "doesn't exist" in str(exc).lower() or "not found: collection" in str(exc).lower():
                    return []
                raise
        finally:
            client.close()

        return [
            QdrantSearchResult(
                point_id=str(point.id),
                score=float(point.score or 0.0),
                payload=dict(point.payload or {}),
            )
            for point in response.points
        ]
