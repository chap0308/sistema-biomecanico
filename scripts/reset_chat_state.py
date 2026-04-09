"""Reset chat data in Supabase and clear storage objects used by the chat flow.

This keeps public.profiles and public.chat_models intact, and removes only
conversation/message/attachment/job rows plus all objects stored in the chat
media buckets.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from psycopg import connect

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings
from src.storage.supabase_storage import SupabaseStorageClient, SupabaseStorageError
from video.movement_knowledge_import import get_database_url


@dataclass(slots=True, frozen=True)
class DeleteSummary:
    table_name: str
    rows_deleted: int


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset chat tables and clear chat storage buckets.")
    parser.add_argument(
        "--buckets",
        nargs="*",
        default=["chat-media", "Postura", "Postura-analisis"],
        help="Buckets whose objects will be deleted.",
    )
    parser.add_argument(
        "--skip-storage",
        action="store_true",
        help="Only truncate chat tables; keep bucket objects.",
    )
    args = parser.parse_args()

    summaries = truncate_chat_tables(
        [
            "public.chat_message_analysis_jobs",
            "public.chat_message_attachments",
            "public.chat_messages",
            "public.chat_conversations",
        ]
    )
    print("table-reset:")
    for summary in summaries:
        print(f"  {summary.table_name}: {summary.rows_deleted}")

    if args.skip_storage:
        print("storage-reset: skipped")
        return

    storage_client = SupabaseStorageClient()
    if not storage_client.is_configured:
        print("storage-reset: skipped (Supabase Storage not configured)")
        return

    for bucket in args.buckets:
        deleted = clear_bucket_objects(storage_client, bucket)
        print(f"bucket-reset: {bucket} deleted={deleted}")


def truncate_chat_tables(table_names: list[str]) -> list[DeleteSummary]:
    summaries: list[DeleteSummary] = []
    with connect(get_database_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            for table_name in table_names:
                cur.execute(f"truncate table {table_name} restart identity cascade")
                summaries.append(DeleteSummary(table_name=table_name, rows_deleted=cur.rowcount))
    return summaries


def clear_bucket_objects(storage_client: SupabaseStorageClient, bucket: str) -> int:
    storage_client.ensure_public_bucket(bucket)
    object_paths = list(iter_bucket_object_paths(storage_client, bucket))
    deleted = 0
    for chunk in chunked(object_paths, size=100):
        if not chunk:
            continue
        delete_bucket_objects(storage_client, bucket, chunk)
        deleted += len(chunk)
    return deleted


def iter_bucket_object_paths(storage_client: SupabaseStorageClient, bucket: str) -> Iterable[str]:
    settings = get_settings()
    session = requests.Session()
    headers = {
        "Authorization": f"Bearer {storage_client.service_key}",
        "apikey": storage_client.service_key,
        "Content-Type": "application/json",
    }
    prefix_stack = [""]
    seen_prefixes: set[str] = set()

    while prefix_stack:
        prefix = prefix_stack.pop()
        if prefix in seen_prefixes:
            continue
        seen_prefixes.add(prefix)
        response = session.post(
            f"{settings.supabase_url}/storage/v1/object/list/{quote(bucket, safe='')}",
            headers=headers,
            json={"prefix": prefix, "limit": 1000, "offset": 0, "sortBy": {"column": "name", "order": "asc"}},
            timeout=60,
        )
        if response.status_code not in {200, 201}:
            raise SupabaseStorageError(
                f"Failed to list objects in bucket '{bucket}': {response.status_code} {response.text}"
            )
        items = response.json() or []
        for item in items:
            name = str(item.get("name") or "")
            if not name:
                continue
            if item.get("metadata") is None and item.get("id") is None:
                next_prefix = f"{prefix}{name}/" if prefix else f"{name}/"
                prefix_stack.append(next_prefix)
                continue
            yield f"{prefix}{name}" if prefix else name


def delete_bucket_objects(storage_client: SupabaseStorageClient, bucket: str, object_paths: list[str]) -> None:
    settings = get_settings()
    response = requests.delete(
        f"{settings.supabase_url}/storage/v1/object/{quote(bucket, safe='')}",
        headers={
            "Authorization": f"Bearer {storage_client.service_key}",
            "apikey": storage_client.service_key,
            "Content-Type": "application/json",
        },
        json={"prefixes": object_paths},
        timeout=60,
    )
    if response.status_code not in {200, 201, 204}:
        raise SupabaseStorageError(
            f"Failed to delete objects from bucket '{bucket}': {response.status_code} {response.text}"
        )


def chunked(items: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]


if __name__ == "__main__":
    main()
