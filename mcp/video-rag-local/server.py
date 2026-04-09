"""Skeleton MCP server for local video RAG workflows."""

from __future__ import annotations

from typing import Any


class VideoRagLocalServer:
    """Minimal project MCP surface for future integration."""

    def ingest_source(self, uri: str, source_type: str | None = None) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "method": "ingest_source",
            "uri": uri,
            "source_type": source_type,
        }

    def analyze_with_gemini(self, source_id: str) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "method": "analyze_with_gemini",
            "source_id": source_id,
        }

    def analyze_local(self, source_id: str) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "method": "analyze_local",
            "source_id": source_id,
        }

    def build_segments(self, source_id: str) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "method": "build_segments",
            "source_id": source_id,
        }

    def index_source(self, source_id: str) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "method": "index_source",
            "source_id": source_id,
        }

    def query_segments(self, query: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "method": "query_segments",
            "query": query,
            "filters": filters or {},
        }

    def show_timeline(self, source_id: str) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "method": "show_timeline",
            "source_id": source_id,
        }


if __name__ == "__main__":
    server = VideoRagLocalServer()
    print(
        {
            "server": "video-rag-local",
            "status": "skeleton_ready",
            "available_methods": [
                "ingest_source",
                "analyze_with_gemini",
                "analyze_local",
                "build_segments",
                "index_source",
                "query_segments",
                "show_timeline",
            ],
        }
    )
