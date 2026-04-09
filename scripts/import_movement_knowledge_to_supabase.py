"""Incrementally import Gemini video knowledge JSON files into Supabase/Postgres."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from video.movement_knowledge_import import (
    ParsedKnowledgeDocument,
    discover_gemini_analysis_files,
    get_database_url,
    parse_gemini_analysis_file,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import movement knowledge JSON files into Supabase/Postgres.")
    parser.add_argument(
        "--root",
        default="data/knowledge/video_knowledge_drafts",
        help="Root folder that contains Gemini analysis JSON files.",
    )
    parser.add_argument(
        "--dataset-name",
        default="movement_knowledge_base",
        help="Logical dataset label stored in the database.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and report files without writing to the database.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of files to process.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    root = Path(args.root)
    files = discover_gemini_analysis_files(root)
    if args.limit is not None:
        files = files[: args.limit]

    if args.dry_run:
        documents = [parse_gemini_analysis_file(path, dataset_name=args.dataset_name) for path in files]
        _print_summary(files=files, inserted=0, skipped=0, failed=0, dry_run=True, documents=documents)
        return

    database_url = get_database_url()
    _run_import(files=files, database_url=database_url, dataset_name=args.dataset_name)


def _run_import(*, files: list[Path], database_url: str, dataset_name: str) -> None:
    from psycopg import connect
    from psycopg.rows import dict_row
    from psycopg.types.json import Jsonb

    inserted = 0
    skipped = 0
    failed = 0

    with connect(database_url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            import_job_id = _create_import_job(cur=cur, dataset_name=dataset_name, source_root="data/knowledge/video_knowledge_drafts")
            conn.commit()

            for path in files:
                try:
                    document = parse_gemini_analysis_file(path, dataset_name=dataset_name)
                    if _analysis_exists(cur=cur, content_sha256=document.analysis.content_sha256):
                        skipped += 1
                        continue
                    analysis_id = _insert_document(cur=cur, document=document, import_job_id=import_job_id, Jsonb=Jsonb)
                    _update_latest_analysis(cur=cur, source_url=document.source_video.source_url, analysis_id=analysis_id)
                    conn.commit()
                    inserted += 1
                except Exception:
                    conn.rollback()
                    failed += 1

            _complete_import_job(
                cur=cur,
                import_job_id=import_job_id,
                files_discovered=len(files),
                files_inserted=inserted,
                files_skipped=skipped,
                files_failed=failed,
            )
            conn.commit()

    _print_summary(files=files, inserted=inserted, skipped=skipped, failed=failed, dry_run=False, documents=None)


def _create_import_job(*, cur, dataset_name: str, source_root: str) -> str:
    cur.execute(
        """
        insert into movement_knowledge.import_jobs (
            importer_name,
            dataset_name,
            source_root,
            status
        ) values (%s, %s, %s, %s)
        returning id
        """,
        ("scripts/import_movement_knowledge_to_supabase.py", dataset_name, source_root, "running"),
    )
    return str(cur.fetchone()["id"])


def _analysis_exists(*, cur, content_sha256: str) -> bool:
    cur.execute(
        "select 1 from movement_knowledge.video_analyses where content_sha256 = %s limit 1",
        (content_sha256,),
    )
    return cur.fetchone() is not None


def _insert_document(*, cur, document: ParsedKnowledgeDocument, import_job_id: str, Jsonb) -> str:
    source_video = document.source_video
    analysis = document.analysis

    cur.execute(
        """
        insert into movement_knowledge.source_videos (
            external_video_id,
            source_type,
            source_url,
            canonical_url,
            title_hint,
            creator_name,
            channel_url,
            source_metadata
        ) values (%s, %s, %s, %s, %s, %s, %s, %s)
        on conflict (source_url) do update set
            title_hint = excluded.title_hint,
            source_type = excluded.source_type,
            canonical_url = excluded.canonical_url,
            channel_url = coalesce(excluded.channel_url, movement_knowledge.source_videos.channel_url),
            updated_at = now()
        returning id
        """,
        (
            source_video.external_video_id,
            source_video.source_type,
            source_video.source_url,
            source_video.canonical_url,
            source_video.title_hint,
            source_video.creator_name,
            source_video.channel_url,
            Jsonb(source_video.source_metadata),
        ),
    )
    source_video_id = str(cur.fetchone()["id"])

    cur.execute(
        """
        insert into movement_knowledge.video_analyses (
            source_video_id,
            import_job_id,
            dataset_name,
            analysis_origin,
            source_file_path,
            source_file_name,
            content_sha256,
            model_name,
            analysis_schema_version,
            prompt_version,
            primary_summary,
            usefulness,
            usefulness_reason,
            exclusion_reason,
            content_kind,
            confidence,
            suitable_for_protocol_database,
            suitable_for_concept_knowledge_base,
            suitable_for_recommendation_mapping,
            contains_visual_execution_detail,
            visual_validation_level,
            review_status,
            body_regions,
            problem_layers,
            searchable_topics,
            searchable_tags,
            problem_statements,
            habits_or_contexts,
            key_visual_points,
            tests_mentioned,
            exercises_mentioned,
            advice_mentioned,
            warnings_or_limitations,
            raw_payload,
            normalized_payload,
            extra_payload
        ) values (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        returning id
        """,
        (
            source_video_id,
            import_job_id,
            analysis.dataset_name,
            analysis.analysis_origin,
            analysis.source_file_path,
            analysis.source_file_name,
            analysis.content_sha256,
            analysis.model_name,
            analysis.analysis_schema_version,
            analysis.prompt_version,
            analysis.primary_summary,
            analysis.usefulness,
            analysis.usefulness_reason,
            analysis.exclusion_reason,
            analysis.content_kind,
            analysis.confidence,
            analysis.suitable_for_protocol_database,
            analysis.suitable_for_concept_knowledge_base,
            analysis.suitable_for_recommendation_mapping,
            analysis.contains_visual_execution_detail,
            analysis.visual_validation_level,
            analysis.review_status,
            analysis.body_regions,
            analysis.problem_layers,
            analysis.searchable_topics,
            analysis.searchable_tags,
            analysis.problem_statements,
            analysis.habits_or_contexts,
            analysis.key_visual_points,
            analysis.tests_mentioned,
            analysis.exercises_mentioned,
            analysis.advice_mentioned,
            analysis.warnings_or_limitations,
            Jsonb(analysis.raw_payload),
            Jsonb(analysis.normalized_payload),
            Jsonb(analysis.extra_payload),
        ),
    )
    analysis_id = str(cur.fetchone()["id"])

    for unit in document.knowledge_units:
        cur.execute(
            """
            insert into movement_knowledge.knowledge_units (
                analysis_id,
                ordinal,
                unit_type,
                title,
                summary,
                observable_signs,
                mechanisms,
                execution_steps,
                cues,
                breathing_cues,
                errors_to_avoid,
                when_useful,
                when_not_useful,
                retest,
                advice,
                timestamps,
                extra_payload
            ) values (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                analysis_id,
                unit.ordinal,
                unit.unit_type,
                unit.title,
                unit.summary,
                unit.observable_signs,
                unit.mechanisms,
                unit.execution_steps,
                unit.cues,
                unit.breathing_cues,
                unit.errors_to_avoid,
                unit.when_useful,
                unit.when_not_useful,
                unit.retest,
                unit.advice,
                unit.timestamps,
                Jsonb(unit.extra_payload),
            ),
        )

    for namespace, value in document.taxonomy_entries:
        cur.execute(
            """
            insert into movement_knowledge.taxonomy_terms (
                namespace,
                value,
                normalized_value,
                sample_source_video_id,
                usage_count
            ) values (%s, %s, lower(%s), %s, %s)
            on conflict (namespace, normalized_value) do update set
                value = excluded.value,
                usage_count = movement_knowledge.taxonomy_terms.usage_count + 1,
                last_seen_at = now(),
                sample_source_video_id = coalesce(movement_knowledge.taxonomy_terms.sample_source_video_id, excluded.sample_source_video_id)
            """,
            (namespace, value, value, source_video_id, 1),
        )

    return analysis_id


def _update_latest_analysis(*, cur, source_url: str, analysis_id: str) -> None:
    cur.execute(
        """
        update movement_knowledge.source_videos
        set latest_analysis_id = %s,
            updated_at = now()
        where source_url = %s
        """,
        (analysis_id, source_url),
    )


def _complete_import_job(*, cur, import_job_id: str, files_discovered: int, files_inserted: int, files_skipped: int, files_failed: int) -> None:
    status = "completed" if files_failed == 0 else "completed_with_errors"
    cur.execute(
        """
        update movement_knowledge.import_jobs
        set status = %s,
            completed_at = now(),
            files_discovered = %s,
            files_inserted = %s,
            files_skipped = %s,
            files_failed = %s
        where id = %s
        """,
        (status, files_discovered, files_inserted, files_skipped, files_failed, import_job_id),
    )


def _print_summary(*, files: list[Path], inserted: int, skipped: int, failed: int, dry_run: bool, documents: list[ParsedKnowledgeDocument] | None) -> None:
    print(f"Files discovered: {len(files)}")
    if dry_run and documents is not None:
        useful = sum(1 for document in documents if document.analysis.usefulness == "useful")
        print(f"Dry run only. Useful analyses: {useful}")
        return
    print(f"Inserted: {inserted}")
    print(f"Skipped existing: {skipped}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
