"""FastAPI dependency providers."""

from orchestration.breathing_baseline_pipeline import BreathingBaselinePipeline
from orchestration.image_pipeline import ImageRestPipeline
from orchestration.image_subpipelines.face_pipeline import FacePipeline
from orchestration.image_subpipelines.foot_triptych_pipeline import FootTriptychPipeline
from orchestration.image_subpipelines.isa_pipeline import IsaPipeline
from orchestration.image_subpipelines.rest_phase1_pipeline import RestPhase1Pipeline
from orchestration.image_subpipelines.scapula_static_pipeline import ScapulaStaticPipeline
from orchestration.isa_video_pipeline import IsaVideoPipeline
from orchestration.movement_pipeline import MovementAnalysisPipeline
from orchestration.rest_baseline_pipeline import RestBaselinePipeline
from orchestration.rest_pipeline import RestAnalysisPipeline
from orchestration.video_rest_pipeline import VideoRestPipeline
from pose.facemesh import MediaPipeFaceMeshExtractor
from pose.mediapipe_pose import MediaPipePoseExtractor


def get_rest_pipeline() -> RestAnalysisPipeline:
    """Build the legacy single-image resting-analysis pipeline dependency."""
    return RestAnalysisPipeline(pose_extractor=MediaPipePoseExtractor())


def get_image_rest_pipeline() -> ImageRestPipeline:
    """Build the grouped static-image analysis pipeline dependency."""
    pose_extractor = MediaPipePoseExtractor()
    return ImageRestPipeline(
        rest_phase1_pipeline=RestPhase1Pipeline(RestAnalysisPipeline(pose_extractor=pose_extractor)),
        face_pipeline=FacePipeline(MediaPipeFaceMeshExtractor()),
        foot_triptych_pipeline=FootTriptychPipeline(),
        isa_pipeline=IsaPipeline(pose_extractor=pose_extractor),
        scapula_pipeline=ScapulaStaticPipeline(pose_extractor=pose_extractor),
    )


def get_rest_baseline_pipeline() -> RestBaselinePipeline:
    """Build the mandatory image-plus-breathing baseline pipeline dependency."""
    pose_extractor = MediaPipePoseExtractor()
    isa_pipeline = IsaPipeline(pose_extractor=pose_extractor)
    breathing_pipeline = BreathingBaselinePipeline(pose_extractor=pose_extractor)
    image_pipeline = ImageRestPipeline(
        rest_phase1_pipeline=RestPhase1Pipeline(RestAnalysisPipeline(pose_extractor=pose_extractor)),
        face_pipeline=FacePipeline(MediaPipeFaceMeshExtractor()),
        foot_triptych_pipeline=FootTriptychPipeline(),
        isa_pipeline=isa_pipeline,
        scapula_pipeline=ScapulaStaticPipeline(pose_extractor=pose_extractor),
    )
    return RestBaselinePipeline(
        image_pipeline=image_pipeline,
        isa_video_pipeline=IsaVideoPipeline(
            isa_pipeline=isa_pipeline,
            breathing_pipeline=breathing_pipeline,
        ),
    )


def get_video_rest_pipeline() -> VideoRestPipeline:
    """Build the single-video multiview rest analysis pipeline dependency."""
    return VideoRestPipeline(rest_pipeline=RestAnalysisPipeline(pose_extractor=MediaPipePoseExtractor()))


def get_isa_video_pipeline() -> IsaVideoPipeline:
    """Build the dedicated ISA image plus breathing video pipeline dependency."""
    pose_extractor = MediaPipePoseExtractor()
    return IsaVideoPipeline(
        isa_pipeline=IsaPipeline(pose_extractor=pose_extractor),
        breathing_pipeline=BreathingBaselinePipeline(pose_extractor=pose_extractor),
    )


def get_movement_pipeline() -> MovementAnalysisPipeline:
    """Build the dedicated movement-analysis pipeline dependency."""
    return MovementAnalysisPipeline(
        pose_extractor=MediaPipePoseExtractor(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
    )


