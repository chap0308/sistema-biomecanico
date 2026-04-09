"""MediaPipe Pose adapter for single-image resting posture analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from pose.converters import to_pose_landmark_map, to_resting_landmarks
from pose.schemas import PoseExtractionMetadata, PoseExtractionResult


class PoseExtractionError(RuntimeError):
    """Raised when the pose extraction layer cannot process an image."""


class PoseLandmarksNotFoundError(PoseExtractionError):
    """Raised when MediaPipe Pose does not detect body landmarks."""


@dataclass(slots=True)
class MediaPipePoseExtractor:
    """Extract pose landmarks from a single image using MediaPipe Pose."""

    static_image_mode: bool = True
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    model_complexity: int = 1

    def extract_from_image_bytes(self, image_bytes: bytes) -> PoseExtractionResult:
        """Decode image bytes and run pose extraction."""
        if not image_bytes:
            raise PoseExtractionError("Empty image payload.")

        image_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image_bgr = cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)
        if image_bgr is None:
            raise PoseExtractionError("Unable to decode the uploaded image.")
        return self.extract_from_image_array(image_bgr)

    def extract_from_image_array(self, image_bgr: np.ndarray) -> PoseExtractionResult:
        """Run MediaPipe Pose on an in-memory BGR image array."""
        if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
            raise PoseExtractionError("Pose extraction expects a color image with 3 channels.")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        result = self._run_pose(image_rgb)
        pose_landmarks = getattr(result, "pose_landmarks", None)
        if pose_landmarks is None or not getattr(pose_landmarks, "landmark", None):
            raise PoseLandmarksNotFoundError("No pose landmarks detected in the provided image.")

        landmark_list = pose_landmarks.landmark
        named_landmarks = to_pose_landmark_map(landmark_list)
        resting_landmarks = to_resting_landmarks(landmark_list)
        metadata = PoseExtractionMetadata(
            detector="mediapipe_pose",
            image_width=int(image_bgr.shape[1]),
            image_height=int(image_bgr.shape[0]),
            landmark_count=len(landmark_list),
            relevant_landmark_count=len(named_landmarks),
            min_visibility=min(point.visibility for point in named_landmarks.values()),
        )
        return PoseExtractionResult(
            named_landmarks=named_landmarks,
            resting_landmarks=resting_landmarks,
            metadata=metadata,
        )

    def _run_pose(self, image_rgb: np.ndarray) -> Any:
        """Execute MediaPipe Pose for a single RGB image."""
        try:
            import mediapipe as mp
        except ImportError as exc:
            raise PoseExtractionError("MediaPipe is not installed in the current environment.") from exc

        pose_module = mp.solutions.pose
        with pose_module.Pose(
            static_image_mode=self.static_image_mode,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
            model_complexity=self.model_complexity,
        ) as pose:
            return pose.process(image_rgb)


__all__ = [
    "MediaPipePoseExtractor",
    "PoseExtractionError",
    "PoseLandmarksNotFoundError",
]
