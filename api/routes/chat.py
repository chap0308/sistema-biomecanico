"""Chat routes for conversations, image analysis, and grounded replies."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from api.schemas.chat import (
    AnalysisJobResponse,
    AttachmentResponse,
    ChatImageAnalysisResponse,
    ChatModelSummary,
    ChatModelsResponse,
    ConversationMessagesResponse,
    ConversationSummaryResponse,
    ConversationsResponse,
    CreateConversationRequest,
    MessageResponse,
    SendChatMessageRequest,
    SendChatMessageResponse,
)
from api.schemas.image import ImageRestMultipartRequest, UploadedStaticImage
from app.config import get_settings
from app.dependencies import get_image_rest_pipeline
from orchestration.image_pipeline import ImageRestPipeline
from pose.facemesh import FaceLandmarksNotFoundError, FaceMeshExtractionError
from pose.mediapipe_pose import PoseExtractionError, PoseLandmarksNotFoundError
from src.core.chat_models import ChatMessageAnalysisJob, ChatMessageAttachment
from src.rag.answering import answer_query
from src.rag.chat_flow import (
    build_chat_query,
    build_rendered_blocks,
    build_rest_phase1_findings_and_deficiencies,
    create_chat_artifact_dir,
    debug_public_url_for_path,
    generate_static_debug_artifacts,
    save_uploaded_group_images,
)
from src.retrieval.hybrid import retrieve_for_query
from src.storage.chat_store import SupabaseChatStore
from src.storage.supabase_store import SupabaseRagStore
from src.storage.supabase_storage import SupabaseStorageClient, SupabaseStorageError

router = APIRouter()


@router.get("/chat/models", response_model=ChatModelsResponse, summary="List selectable chat models")
def list_chat_models() -> ChatModelsResponse:
    store = SupabaseChatStore()
    models = [
        ChatModelSummary(
            model_key=item.model_key,
            provider=item.provider,
            display_name=item.display_name,
            description=item.description,
            answer_backend=item.answer_backend,
            answer_model=item.answer_model,
            supports_images=item.supports_images,
            supports_audio=item.supports_audio,
            supports_reasoning=item.supports_reasoning,
            is_default=item.is_default,
        )
        for item in store.list_models()
    ]
    return ChatModelsResponse(models=models)


@router.get("/chat/conversations", response_model=ConversationsResponse, summary="List chat conversations")
def list_chat_conversations(user_id: UUID, limit: int = 50) -> ConversationsResponse:
    store = SupabaseChatStore()
    items = [_conversation_to_summary(item) for item in store.list_conversations(user_id=user_id, limit=limit)]
    return ConversationsResponse(items=items)


@router.post("/chat/conversations", response_model=ConversationSummaryResponse, summary="Create a new conversation")
def create_chat_conversation(request: CreateConversationRequest) -> ConversationSummaryResponse:
    store = SupabaseChatStore()
    selected_model_key = request.selected_model_key or _resolve_default_model_key(store)
    conversation = store.create_conversation(
        user_id=request.user_id,
        title=request.title,
        selected_model_key=selected_model_key,
        metadata=request.metadata,
    )
    return _conversation_to_summary(conversation)


@router.get(
    "/chat/conversations/{conversation_id}/messages",
    response_model=ConversationMessagesResponse,
    summary="Fetch the full message history for one conversation",
)
def get_chat_messages(conversation_id: UUID, user_id: UUID) -> ConversationMessagesResponse:
    store = SupabaseChatStore()
    conversation = store.get_conversation(conversation_id=conversation_id, user_id=user_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    messages = store.list_messages(conversation_id=conversation_id)
    attachments_by_message = _group_attachments_by_message(
        store.list_attachments_for_messages(message_ids=[item.message_id for item in messages])
    )
    jobs_by_message = _group_jobs_by_message(
        [job for message in messages for job in store.list_analysis_jobs_for_message(message_id=message.message_id)]
    )
    return ConversationMessagesResponse(
        conversation=_conversation_to_summary(conversation),
        messages=[
            _message_to_response(
                message=item,
                attachments=attachments_by_message.get(item.message_id, []),
                analysis_jobs=jobs_by_message.get(item.message_id, []),
                slim_for_client=True,
            )
            for item in messages
        ],
    )


@router.post("/chat/image-analysis", response_model=ChatImageAnalysisResponse, summary="Analyze rest_phase1 images for chat")
async def analyze_chat_images(
    user_id: Annotated[UUID, Form()],
    conversation_id: Annotated[UUID, Form()],
    selected_model_key: Annotated[str | None, Form()] = None,
    note_text: Annotated[str | None, Form()] = None,
    include_placeholders: Annotated[bool, Form()] = True,
    rest_phase1_front: Annotated[UploadFile | None, File()] = None,
    rest_phase1_side: Annotated[UploadFile | None, File()] = None,
    rest_phase1_back: Annotated[UploadFile | None, File()] = None,
    pipeline: ImageRestPipeline = Depends(get_image_rest_pipeline),
) -> ChatImageAnalysisResponse:
    store = SupabaseChatStore()
    conversation = store.get_conversation(conversation_id=conversation_id, user_id=user_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    if selected_model_key and selected_model_key != conversation.selected_model_key:
        conversation = store.update_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            selected_model_key=selected_model_key,
        )

    image_request = await _build_rest_phase1_chat_request(
        include_placeholders=include_placeholders,
        rest_phase1_front=rest_phase1_front,
        rest_phase1_side=rest_phase1_side,
        rest_phase1_back=rest_phase1_back,
    )

    analysis_message = store.add_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        message_kind="analysis",
        content_text=note_text or "Analizar imágenes de referencia",
        selected_model_key=selected_model_key or conversation.selected_model_key,
        input_context={
            "requested_groups": ["rest_phase1"],
            "source_endpoint": "/api/v1/chat/image-analysis",
            "underlying_analysis_endpoint": "/api/v1/analyze/image/rest",
            "deficiency_rules_source": "rest_baseline_detection_rules",
        },
        processing_status="processing",
    )
    analysis_job_id = uuid4()
    job = store.create_analysis_job(
        ChatMessageAnalysisJob(
            analysis_job_id=analysis_job_id,
            conversation_id=conversation_id,
            message_id=analysis_message.message_id,
            attachment_id=None,
            user_id=user_id,
            analysis_kind="image_metrics",
            endpoint_name="/api/v1/chat/image-analysis",
            status="running",
            detected_deficiencies=[],
            metrics_payload={},
            request_payload={
                "requested_groups": ["rest_phase1"],
                "note_text": note_text or "",
                "underlying_analysis_endpoint": "/api/v1/analyze/image/rest",
                "future_baseline_endpoint": "/api/v1/analyze/rest/baseline",
                "deficiency_rules_source": "rest_baseline_detection_rules",
            },
            response_payload={},
            error_code=None,
            error_message=None,
            completed_at=None,
        )
    )

    artifact_dir = create_chat_artifact_dir(conversation_id=conversation_id, message_id=analysis_message.message_id)
    saved_input_paths, original_artifacts = save_uploaded_group_images(request=image_request, artifact_dir=artifact_dir)

    try:
        analysis_payload = pipeline.analyze(image_request)
    except ValueError as exc:
        store.create_analysis_job(
            job.model_copy(update={"status": "error", "error_code": "validation_error", "error_message": str(exc)})
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (PoseLandmarksNotFoundError, FaceLandmarksNotFoundError) as exc:
        store.create_analysis_job(
            job.model_copy(update={"status": "error", "error_code": "landmarks_not_found", "error_message": str(exc)})
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except (PoseExtractionError, FaceMeshExtractionError) as exc:
        store.create_analysis_job(
            job.model_copy(update={"status": "error", "error_code": "analysis_error", "error_message": str(exc)})
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    findings, deficiencies = build_rest_phase1_findings_and_deficiencies(analysis_payload)
    debug_artifacts = generate_static_debug_artifacts(
        request=image_request,
        analysis_payload=analysis_payload,
        saved_input_paths=saved_input_paths,
        artifact_dir=artifact_dir,
    )
    original_attachments = _persist_chat_artifacts(
        store=store,
        user_id=user_id,
        message_id=analysis_message.message_id,
        conversation_id=conversation_id,
        artifacts=original_artifacts,
    )
    debug_image_artifacts = [artifact for artifact in debug_artifacts if artifact.artifact_kind == "debug_image"]
    persisted_debug_attachments = _persist_chat_artifacts(
        store=store,
        user_id=user_id,
        message_id=analysis_message.message_id,
        conversation_id=conversation_id,
        artifacts=debug_image_artifacts,
    )
    debug_artifact_specs = [
        {
            "path": item.storage_path,
            "artifact_kind": item.attachment_kind,
            "title": item.original_filename,
            "metadata": item.metadata,
            "storage_public_url": item.public_url,
        }
        for item in persisted_debug_attachments
    ]

    completed_job = store.create_analysis_job(
        job.model_copy(
            update={
                "status": "completed",
                "detected_deficiencies": deficiencies,
                "metrics_payload": {"groups": analysis_payload.get("groups", {}), "findings": findings},
                "response_payload": {**analysis_payload, "debug_artifacts": debug_artifact_specs},
                "completed_at": datetime.now(timezone.utc),
            }
        )
    )

    analysis_message = store.update_message(
        message_id=analysis_message.message_id,
        conversation_id=conversation_id,
        content_text=analysis_message.content_text,
        input_context={
            "requested_groups": ["rest_phase1"],
            "analysis_job_id": str(completed_job.analysis_job_id),
            "detected_deficiencies": deficiencies,
            "findings": findings,
            "source_endpoint": "/api/v1/chat/image-analysis",
            "underlying_analysis_endpoint": "/api/v1/analyze/image/rest",
            "future_baseline_endpoint": "/api/v1/analyze/rest/baseline",
            "deficiency_rules_source": "rest_baseline_detection_rules",
        },
        processing_status="completed",
    )

    response_json_artifact = next((item for item in debug_artifacts if item.path.name == "response.json"), None)
    return ChatImageAnalysisResponse(
        conversation_id=conversation_id,
        analysis_message=_message_to_response(
            message=analysis_message,
            attachments=original_attachments,
            analysis_jobs=[completed_job],
        ),
        analysis_job=_analysis_job_to_response(completed_job),
        detected_deficiencies=deficiencies,
        debug_attachments=[_attachment_to_response(item) for item in persisted_debug_attachments],
        response_artifact_path=str(response_json_artifact.path) if response_json_artifact else None,
    )


@router.post("/chat/messages", response_model=SendChatMessageResponse, summary="Send a chat message and receive the assistant reply")
def send_chat_message(request: SendChatMessageRequest) -> SendChatMessageResponse:
    store = SupabaseChatStore()
    rag_store = SupabaseRagStore()
    conversation = store.get_conversation(conversation_id=request.conversation_id, user_id=request.user_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    selected_model = _resolve_model(store, request.selected_model_key or conversation.selected_model_key)
    if request.selected_model_key and request.selected_model_key != conversation.selected_model_key:
        conversation = store.update_conversation(
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            selected_model_key=request.selected_model_key,
        )
    analysis_jobs = [
        item.model_dump(mode="json")
        for item in store.fetch_analysis_jobs_by_ids(analysis_job_ids=request.related_analysis_job_ids, user_id=request.user_id)
    ]
    analysis_job_records = store.fetch_analysis_jobs_by_ids(
        analysis_job_ids=request.related_analysis_job_ids,
        user_id=request.user_id,
    )
    deficiencies = [
        deficiency
        for job in analysis_jobs
        for deficiency in job.get("detected_deficiencies", [])
        if isinstance(deficiency, dict)
    ]
    augmented_query = build_chat_query(
        user_message=request.content_text,
        deficiencies=deficiencies,
        analysis_jobs=analysis_jobs,
    )

    user_message = store.add_message(
        conversation_id=request.conversation_id,
        user_id=request.user_id,
        role="user",
        message_kind="chat",
        content_text=request.content_text,
        selected_model_key=selected_model.model_key,
        input_context={
            "related_analysis_job_ids": [str(item) for item in request.related_analysis_job_ids],
            "detected_deficiencies": deficiencies,
            "augmented_query": augmented_query,
        },
        processing_status="completed",
        metadata=request.metadata,
    )

    bundle = retrieve_for_query(augmented_query, quality=request.response_quality, supabase_store=rag_store)
    answer_payload = answer_query(
        augmented_query,
        bundle,
        backend=selected_model.answer_backend,
        model_override=selected_model.answer_model,
        model_profile=request.answer_profile,
    )
    rendered_blocks = build_rendered_blocks(answer_payload=answer_payload, deficiencies=deficiencies)
    assistant_message = store.add_message(
        conversation_id=request.conversation_id,
        user_id=request.user_id,
        role="assistant",
        message_kind="analysis",
        content_text=None,
        selected_model_key=selected_model.model_key,
        rendered_blocks=rendered_blocks,
        output_context={
            "retrieval_quality": answer_payload.get("retrieval_quality"),
            "used_collections": answer_payload.get("used_collections", []),
            "selected_model_key": selected_model.model_key,
            "model_used": answer_payload.get("model_used"),
            "answer_backend": answer_payload.get("answer_backend"),
            "related_analysis_job_ids": [str(item) for item in request.related_analysis_job_ids],
            "citations": answer_payload.get("citations", []),
            "attempted_backends": answer_payload.get("attempted_backends", []),
            "fallback_error_code": answer_payload.get("fallback_error_code", ""),
        },
        processing_status="completed",
        metadata={"response_quality": request.response_quality},
    )

    cloned_debug_attachments: list[ChatMessageAttachment] = []
    for analysis_job in analysis_job_records:
        response_payload = analysis_job.response_payload if isinstance(analysis_job.response_payload, dict) else {}
        for spec in response_payload.get("debug_artifacts", []):
            if not isinstance(spec, dict):
                continue
            cloned_debug_attachments.append(
                store.add_attachment(
                    _debug_attachment_from_spec(
                        spec=spec,
                        message_id=assistant_message.message_id,
                        source_analysis_job_id=str(analysis_job.analysis_job_id),
                    )
                )
            )

    return SendChatMessageResponse(
        conversation_id=request.conversation_id,
        user_message=_message_to_response(message=user_message, attachments=[], analysis_jobs=[]),
        assistant_message=_message_to_response(
            message=assistant_message,
            attachments=cloned_debug_attachments,
            analysis_jobs=[],
        ),
        debug_attachments=[_attachment_to_response(item) for item in cloned_debug_attachments],
    )


def _conversation_to_summary(item: Any) -> ConversationSummaryResponse:
    return ConversationSummaryResponse(
        conversation_id=item.conversation_id,
        title=item.title,
        selected_model_key=item.selected_model_key,
        conversation_status=item.conversation_status,
        last_message_preview=item.last_message_preview,
        last_message_at=item.last_message_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _message_to_response(
    *,
    message: Any,
    attachments: list[ChatMessageAttachment],
    analysis_jobs: list[ChatMessageAnalysisJob],
    slim_for_client: bool = False,
) -> MessageResponse:
    input_context = message.input_context
    output_context = message.output_context
    job_items = analysis_jobs
    if slim_for_client:
        input_context = _slim_message_context(message)
        output_context = _slim_output_context(message.output_context)
        job_items = [_slim_analysis_job(item) for item in analysis_jobs]
    return MessageResponse(
        message_id=message.message_id,
        role=message.role,
        message_kind=message.message_kind,
        content_text=message.content_text,
        rendered_blocks=message.rendered_blocks,
        input_context=input_context,
        output_context=output_context,
        selected_model_key=message.selected_model_key,
        processing_status=message.processing_status,
        attachments=[_attachment_to_response(item) for item in attachments],
        analysis_jobs=[_analysis_job_to_response(item) for item in job_items],
        created_at=message.created_at,
    )


def _attachment_to_response(item: ChatMessageAttachment) -> AttachmentResponse:
    return AttachmentResponse(
        attachment_id=item.attachment_id,
        attachment_kind=item.attachment_kind,
        original_filename=item.original_filename,
        mime_type=item.mime_type,
        storage_provider=item.storage_provider,
        storage_path=item.storage_path,
        public_url=item.public_url,
        thumbnail_url=item.thumbnail_url,
        analysis_status=item.analysis_status,
        analysis_payload=item.analysis_payload,
        metadata=item.metadata,
    )


def _analysis_job_to_response(item: ChatMessageAnalysisJob) -> AnalysisJobResponse:
    return AnalysisJobResponse(
        analysis_job_id=item.analysis_job_id,
        analysis_kind=item.analysis_kind,
        endpoint_name=item.endpoint_name,
        status=item.status,
        detected_deficiencies=item.detected_deficiencies,
        metrics_payload=item.metrics_payload,
        response_payload=item.response_payload,
        error_code=item.error_code,
        error_message=item.error_message,
        completed_at=item.completed_at,
    )


def _slim_message_context(message: Any) -> dict[str, Any]:
    if message.role == "user" and message.message_kind == "analysis":
        context = message.input_context if isinstance(message.input_context, dict) else {}
        return {
            "analysis_job_id": context.get("analysis_job_id"),
            "detected_deficiencies": context.get("detected_deficiencies", []),
            "findings": context.get("findings", []),
            "requested_groups": context.get("requested_groups", []),
        }
    if message.role == "user" and message.message_kind == "chat":
        context = message.input_context if isinstance(message.input_context, dict) else {}
        return {
            "related_analysis_job_ids": context.get("related_analysis_job_ids", []),
            "detected_deficiencies": context.get("detected_deficiencies", []),
        }
    return {}


def _slim_output_context(output_context: dict[str, Any] | None) -> dict[str, Any]:
    context = output_context if isinstance(output_context, dict) else {}
    return {
        "retrieval_quality": context.get("retrieval_quality"),
        "used_collections": context.get("used_collections", []),
        "selected_model_key": context.get("selected_model_key"),
        "model_used": context.get("model_used"),
        "answer_backend": context.get("answer_backend"),
        "citations": context.get("citations", []),
        "attempted_backends": context.get("attempted_backends", []),
        "fallback_error_code": context.get("fallback_error_code", ""),
    }


def _slim_analysis_job(job: ChatMessageAnalysisJob) -> ChatMessageAnalysisJob:
    return job.model_copy(
        update={
            "metrics_payload": {},
            "request_payload": {},
            "response_payload": {},
        }
    )


def _build_debug_attachments_from_specs(specs: list[dict[str, Any]]) -> list[ChatMessageAttachment]:
    attachments: list[ChatMessageAttachment] = []
    for spec in specs:
        local_path = Path(str(spec.get("path") or ""))
        if not local_path.as_posix():
            continue
        debug_url = str(spec.get("storage_public_url") or spec.get("debug_public_url") or debug_public_url_for_path(local_path))
        attachments.append(
            ChatMessageAttachment(
                attachment_id=uuid4(),
                message_id=UUID(int=0),
                attachment_kind=str(spec.get("artifact_kind") or "debug_image"),
                storage_provider="local_ref",
                original_filename=local_path.name,
                mime_type="image/png",
                file_size_bytes=0,
                storage_path=str(local_path),
                public_url=debug_url,
                thumbnail_url=debug_url,
                analysis_status="completed",
                analysis_payload={
                    "artifact_title": spec.get("title"),
                    "debug_public_url": debug_url,
                },
                metadata=dict(spec.get("metadata") or {}),
            )
        )
    return attachments


def _debug_attachment_from_spec(*, spec: dict[str, Any], message_id: UUID, source_analysis_job_id: str) -> ChatMessageAttachment:
    local_path = Path(str(spec.get("path") or ""))
    debug_url = str(spec.get("storage_public_url") or spec.get("debug_public_url") or "")
    if not debug_url and local_path.as_posix():
        debug_url = debug_public_url_for_path(local_path)
    return ChatMessageAttachment(
        attachment_id=uuid4(),
        message_id=message_id,
        attachment_kind=str(spec.get("artifact_kind") or "debug_image"),
        storage_provider="local_ref",
        original_filename=local_path.name,
        mime_type="image/png",
        file_size_bytes=0,
        storage_path=str(local_path),
        public_url=debug_url,
        thumbnail_url=debug_url,
        analysis_status="completed",
        analysis_payload={
            "artifact_title": spec.get("title"),
            "debug_public_url": debug_url,
        },
        metadata={**dict(spec.get("metadata") or {}), "source_analysis_job_id": source_analysis_job_id},
    )


def _group_attachments_by_message(
    attachments: list[ChatMessageAttachment],
) -> dict[UUID, list[ChatMessageAttachment]]:
    grouped: dict[UUID, list[ChatMessageAttachment]] = defaultdict(list)
    for item in attachments:
        grouped[item.message_id].append(item)
    return grouped


def _group_jobs_by_message(jobs: list[ChatMessageAnalysisJob]) -> dict[UUID, list[ChatMessageAnalysisJob]]:
    grouped: dict[UUID, list[ChatMessageAnalysisJob]] = defaultdict(list)
    for item in jobs:
        grouped[item.message_id].append(item)
    return grouped


def _resolve_default_model_key(store: SupabaseChatStore) -> str | None:
    model = store.get_default_model()
    return model.model_key if model else None


def _resolve_model(store: SupabaseChatStore, model_key: str | None) -> Any:
    model = store.get_model(model_key) if model_key else store.get_default_model()
    if model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active chat model is available.")
    return model


def _guess_mime_type(path: Any) -> str:
    suffix = str(getattr(path, "suffix", "")).lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".json":
        return "application/json"
    if suffix == ".csv":
        return "text/csv"
    return "application/octet-stream"


async def _build_rest_phase1_chat_request(
    *,
    include_placeholders: bool,
    rest_phase1_front: UploadFile | None,
    rest_phase1_side: UploadFile | None,
    rest_phase1_back: UploadFile | None,
) -> ImageRestMultipartRequest:
    uploads = {
        "front": rest_phase1_front,
        "side": rest_phase1_side,
        "back": rest_phase1_back,
    }
    missing = [f"rest_phase1_{slot}" for slot, upload in uploads.items() if upload is None]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El MVP requiere las tres imágenes de rest_phase1. Faltan: {', '.join(missing)}.",
        )

    image_groups: dict[str, dict[str, UploadedStaticImage]] = {"rest_phase1": {}}
    for slot_name, upload in uploads.items():
        assert upload is not None
        if not upload.content_type or not upload.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Field 'rest_phase1_{slot_name}' must be uploaded as an image.",
            )
        image_groups["rest_phase1"][slot_name] = UploadedStaticImage(
            filename=upload.filename or f"rest_phase1_{slot_name}.jpg",
            content_type=upload.content_type,
            payload=await upload.read(),
        )

    return ImageRestMultipartRequest(image_groups=image_groups, include_placeholders=include_placeholders)


def _persist_chat_artifacts(
    *,
    store: SupabaseChatStore,
    user_id: UUID,
    message_id: UUID,
    conversation_id: UUID,
    artifacts: list[Any],
) -> list[ChatMessageAttachment]:
    settings = get_settings()
    storage_client = SupabaseStorageClient()
    attachments: list[ChatMessageAttachment] = []
    storage_root = f"{user_id}/chat/{conversation_id}/{message_id}"

    for artifact in artifacts:
        local_path = Path(artifact.path)
        mime_type = _guess_mime_type(local_path)
        storage_provider = "local_ref"
        storage_path = str(local_path)
        debug_url = debug_public_url_for_path(local_path)
        public_url = debug_url
        thumbnail_url = debug_url if artifact.artifact_kind == "debug_image" else None
        analysis_payload = {"artifact_title": artifact.title}

        if storage_client.is_configured:
            try:
                target_bucket = (
                    settings.supabase_posture_bucket
                    if artifact.metadata.get("artifact_role") == "original"
                    else settings.supabase_posture_analysis_bucket
                )
                uploaded = storage_client.upload_file(
                    local_path=local_path,
                    path=f"{storage_root}/{local_path.name}",
                    content_type=mime_type,
                    bucket=target_bucket,
                )
                storage_provider = "supabase_storage"
                storage_path = uploaded.path
                public_url = uploaded.public_url
                thumbnail_url = uploaded.public_url if artifact.artifact_kind == "debug_image" else None
                analysis_payload["storage_bucket"] = uploaded.bucket
                analysis_payload["storage_public_url"] = uploaded.public_url
                analysis_payload["storage_path"] = uploaded.path
                analysis_payload["debug_public_url"] = debug_url
            except SupabaseStorageError as exc:
                analysis_payload["storage_error"] = str(exc)

        attachments.append(
            store.add_attachment(
                ChatMessageAttachment(
                    attachment_id=uuid4(),
                    message_id=message_id,
                    attachment_kind=artifact.artifact_kind,
                    storage_provider=storage_provider,
                    original_filename=local_path.name,
                    mime_type=mime_type,
                    file_size_bytes=local_path.stat().st_size,
                    storage_path=storage_path,
                    public_url=public_url,
                    thumbnail_url=thumbnail_url,
                    analysis_status="completed",
                    analysis_payload=analysis_payload,
                    metadata=artifact.metadata,
                )
            )
        )

    return attachments
