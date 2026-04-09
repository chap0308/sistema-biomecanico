"""Analysis routes segmented by analysis type."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from api.schemas.baseline import RestBaselineAnalysisResponse, RestBaselineMultipartRequest
from api.schemas.image import ImageRestAnalysisResponse, ImageRestMultipartRequest
from api.schemas.isa import IsaVideoAnalysisResponse, IsaVideoMultipartRequest
from api.schemas.movement import MovementAnalysisResponse, MovementVideoMultipartRequest
from api.schemas.rest import RestAnalysisResponse
from app.dependencies import (
    get_image_rest_pipeline,
    get_isa_video_pipeline,
    get_movement_pipeline,
    get_rest_baseline_pipeline,
    get_rest_pipeline,
    get_video_rest_pipeline,
)
from orchestration.image_pipeline import ImageRestPipeline
from orchestration.isa_video_pipeline import IsaVideoPipeline
from orchestration.movement_pipeline import MovementAnalysisPipeline
from orchestration.rest_baseline_pipeline import RestBaselinePipeline
from orchestration.rest_pipeline import RestAnalysisPipeline
from orchestration.video_rest_pipeline import VideoRestPipeline
from pose.facemesh import FaceLandmarksNotFoundError, FaceMeshExtractionError
from pose.mediapipe_pose import PoseExtractionError, PoseLandmarksNotFoundError

router = APIRouter()

_SUPPORTED_VIDEO_ANALYSIS_TYPES = {
    "rest",
    "breathing_cycle",
    "cervical_rotation",
    "active_weight_shift",
    "arch_reformation",
    "knee_valgus_dynamic",
    "wall_stack",
    "scapulohumeral_rhythm",
    "exercise_form",
}
_IMPLEMENTED_VIDEO_ANALYSIS_TYPES = {"rest"}
_VIDEO_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"}


def _raise_if_invalid_image_upload(image: UploadFile) -> None:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only image uploads are supported by the image analysis endpoint.",
        )


def _raise_if_invalid_video_upload(video: UploadFile) -> None:
    if not video.content_type or video.content_type not in _VIDEO_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only video uploads are supported by the video analysis endpoint.",
        )


def _validate_video_analysis_type(video_analysis_type: str) -> str:
    normalized_type = video_analysis_type.strip().lower()
    if normalized_type not in _SUPPORTED_VIDEO_ANALYSIS_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported video_analysis_type "
                f"'{video_analysis_type}'. Expected one of: {', '.join(sorted(_SUPPORTED_VIDEO_ANALYSIS_TYPES))}."
            ),
        )
    if normalized_type not in _IMPLEMENTED_VIDEO_ANALYSIS_TYPES:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                f"Video analysis type '{normalized_type}' is recognized but not implemented yet. "
                "Only 'rest' is currently available."
            ),
        )
    return normalized_type


@router.post(
    "/analyze/video/isa",
    response_model=IsaVideoAnalysisResponse,
    summary="Analyze static ISA reference plus dynamic breathing from one dedicated endpoint",
)
async def analyze_isa_video(
    request: IsaVideoMultipartRequest = Depends(IsaVideoMultipartRequest.as_form),
    pipeline: IsaVideoPipeline = Depends(get_isa_video_pipeline),
) -> IsaVideoAnalysisResponse:
    """Run ISA static-reference analysis plus breathing dynamics in one request."""
    try:
        result = pipeline.analyze(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PoseLandmarksNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except PoseExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return IsaVideoAnalysisResponse.model_validate(result)


@router.post(
    "/analyze/video/movement",
    response_model=MovementAnalysisResponse,
    summary="Analyze shoulder abduction using the posterior movement-video workflow",
)
async def analyze_movement_video(
    request: MovementVideoMultipartRequest = Depends(MovementVideoMultipartRequest.as_form),
    pipeline: MovementAnalysisPipeline = Depends(get_movement_pipeline),
) -> MovementAnalysisResponse:
    """Run the dedicated movement-analysis contract for shoulder abduction."""
    try:
        result = pipeline.analyze(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PoseLandmarksNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except PoseExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return MovementAnalysisResponse.model_validate(result)


@router.post(
    "/analyze/rest/baseline",
    response_model=RestBaselineAnalysisResponse,
    summary="Analyze the mandatory rest baseline from grouped images plus breathing video",
)
async def analyze_rest_baseline(
    request: RestBaselineMultipartRequest = Depends(RestBaselineMultipartRequest.as_form),
    pipeline: RestBaselinePipeline = Depends(get_rest_baseline_pipeline),
) -> RestBaselineAnalysisResponse:
    """Run the new baseline contract with static groups plus mandatory breathing video."""
    try:
        result = pipeline.analyze(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except (PoseLandmarksNotFoundError, FaceLandmarksNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except (PoseExtractionError, FaceMeshExtractionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return RestBaselineAnalysisResponse.model_validate(result)


@router.post(
    "/analyze/image/rest",
    response_model=ImageRestAnalysisResponse,
    summary="Analyze grouped static images for the initial rest workflow",
)
async def analyze_rest_image(
    request: ImageRestMultipartRequest = Depends(ImageRestMultipartRequest.as_form),
    pipeline: ImageRestPipeline = Depends(get_image_rest_pipeline),
) -> ImageRestAnalysisResponse:
    """Run grouped static analysis using explicit multipart field names.

    Supported field names follow the convention `<group>_<slot>`:
    `rest_phase1_front`, `rest_phase1_side`, `rest_phase1_back`,
    `face_front_face`, `foot_triptych_front`, `foot_triptych_back`,
    `foot_triptych_left_arch`, `foot_triptych_right_arch`,
    `isa_front_torso`, `scapula_back_upper_body`.
    """
    try:
        result = pipeline.analyze(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except (PoseLandmarksNotFoundError, FaceLandmarksNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except (PoseExtractionError, FaceMeshExtractionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ImageRestAnalysisResponse.model_validate(result)


@router.post(
    "/analyze/video/rest",
    response_model=ImageRestAnalysisResponse,
    summary="Analyze phase-1 front, side and back metrics from a single rotating rest video",
)
async def analyze_rest_video(
    video: UploadFile = File(..., description="Single rotating rest video covering front, side and back views."),
    include_placeholders: bool = Form(default=True),
    aggregation: str = Form(default="median"),
    frame_step: int = Form(default=10),
    max_frames: int = Form(default=18),
    reject_outliers: bool = Form(default=True),
    pipeline: VideoRestPipeline = Depends(get_video_rest_pipeline),
) -> ImageRestAnalysisResponse:
    """Run the phase-1 multiview analysis from a single uploaded video."""
    _raise_if_invalid_video_upload(video)

    try:
        payload = await video.read()
        import tempfile
        from pathlib import Path

        suffix = Path(video.filename or "upload.mp4").suffix or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(payload)
            tmp_path = Path(tmp_file.name)
        try:
            result = pipeline.analyze_video_path(
                tmp_path,
                include_placeholders=include_placeholders,
                aggregation=aggregation,
                frame_step=frame_step,
                max_frames=max_frames,
                reject_outliers=reject_outliers,
            )
        finally:
            tmp_path.unlink(missing_ok=True)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PoseLandmarksNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except PoseExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ImageRestAnalysisResponse.model_validate(result)


@router.post(
    "/analyze/video",
    response_model=RestAnalysisResponse,
    summary="Analyze a biomechanical video according to its declared test type",
)
async def analyze_video(
    video: UploadFile = File(..., description="Short video clip for biomechanical analysis."),
    video_analysis_type: str = Form(..., description="Type of video test to run, e.g. 'rest'."),
    view: str = Form(default="front"),
    include_placeholders: bool = Form(default=True),
    aggregation: str = Form(default="median"),
    frame_step: int = Form(default=5),
    max_frames: int = Form(default=9),
    reject_outliers: bool = Form(default=True),
    pipeline: RestAnalysisPipeline = Depends(get_rest_pipeline),
) -> RestAnalysisResponse:
    """Run video analysis using the declared video test type."""
    _raise_if_invalid_video_upload(video)
    normalized_type = _validate_video_analysis_type(video_analysis_type)

    try:
        payload = await video.read()
        if normalized_type != "rest":
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Video analysis type '{normalized_type}' is not implemented yet.",
            )
        import tempfile
        from pathlib import Path

        suffix = Path(video.filename or "upload.mp4").suffix or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(payload)
            tmp_path = Path(tmp_file.name)
        try:
            result = pipeline.analyze_video_path(
                tmp_path,
                view=view,
                include_placeholders=include_placeholders,
                aggregation=aggregation,
                frame_step=frame_step,
                max_frames=max_frames,
                reject_outliers=reject_outliers,
            )
        finally:
            tmp_path.unlink(missing_ok=True)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PoseLandmarksNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except PoseExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return RestAnalysisResponse.model_validate(asdict(result))


@router.post(
    "/analyze/rest",
    response_model=RestAnalysisResponse,
    deprecated=True,
    summary="Deprecated alias for the old single-image rest analysis",
)
async def analyze_rest(
    image: UploadFile = File(..., description="Single image frame for resting-posture analysis."),
    view: str = Form(default="front"),
    include_placeholders: bool = Form(default=True),
    pipeline: RestAnalysisPipeline = Depends(get_rest_pipeline),
) -> RestAnalysisResponse:
    """Backward-compatible alias for the old single-image rest endpoint."""
    _raise_if_invalid_image_upload(image)

    try:
        payload = await image.read()
        result = pipeline.analyze_image_bytes(
            payload,
            view=view,
            include_placeholders=include_placeholders,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PoseLandmarksNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except PoseExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return RestAnalysisResponse.model_validate(asdict(result))

