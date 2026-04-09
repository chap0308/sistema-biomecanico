"""MediaPipe FaceMesh adapter for static facial asymmetry analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np


class FaceMeshExtractionError(RuntimeError):
    """Raised when the face extraction layer cannot process an image."""


class FaceLandmarksNotFoundError(FaceMeshExtractionError):
    """Raised when MediaPipe FaceMesh does not detect a face."""


@dataclass(slots=True, frozen=True)
class FacePoint:
    """Normalized 2D point in image coordinates."""

    x: float
    y: float


@dataclass(slots=True, frozen=True)
class FaceMeshExtractionMetadata:
    """Metadata describing one face-mesh extraction pass."""

    detector: str
    image_width: int
    image_height: int
    landmark_count: int


@dataclass(slots=True, frozen=True)
class FaceMeshExtractionResult:
    """Normalized MediaPipe FaceMesh output used by the pipeline."""

    landmarks: dict[int, FacePoint]
    metadata: FaceMeshExtractionMetadata


@dataclass(slots=True)
class MediaPipeFaceMeshExtractor:
    """Extract FaceMesh landmarks from a single image using MediaPipe."""

    static_image_mode: bool = True
    max_num_faces: int = 1
    refine_landmarks: bool = True
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5

    def extract_from_image_bytes(self, image_bytes: bytes) -> FaceMeshExtractionResult:
        """Decode image bytes and run face extraction."""
        if not image_bytes:
            raise FaceMeshExtractionError("Empty image payload.")

        image_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image_bgr = cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)
        if image_bgr is None:
            raise FaceMeshExtractionError("Unable to decode the uploaded image.")
        return self.extract_from_image_array(image_bgr)

    def extract_from_image_array(self, image_bgr: np.ndarray) -> FaceMeshExtractionResult:
        """Run MediaPipe FaceMesh on an in-memory BGR image array."""
        if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
            raise FaceMeshExtractionError("FaceMesh extraction expects a color image with 3 channels.")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        result = self._run_mesh(image_rgb)
        faces = getattr(result, "multi_face_landmarks", None)
        if not faces:
            raise FaceLandmarksNotFoundError("No facial landmarks detected in the provided image.")

        landmark_list = faces[0].landmark
        landmarks = {index: FacePoint(x=point.x, y=point.y) for index, point in enumerate(landmark_list)}
        metadata = FaceMeshExtractionMetadata(
            detector="mediapipe_facemesh",
            image_width=int(image_bgr.shape[1]),
            image_height=int(image_bgr.shape[0]),
            landmark_count=len(landmark_list),
        )
        return FaceMeshExtractionResult(landmarks=landmarks, metadata=metadata)

    def _run_mesh(self, image_rgb: np.ndarray) -> Any:
        """Execute MediaPipe FaceMesh for a single RGB image."""
        try:
            import mediapipe as mp
        except ImportError as exc:
            raise FaceMeshExtractionError("MediaPipe is not installed in the current environment.") from exc

        face_mesh_module = mp.solutions.face_mesh
        with face_mesh_module.FaceMesh(
            static_image_mode=self.static_image_mode,
            max_num_faces=self.max_num_faces,
            refine_landmarks=self.refine_landmarks,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        ) as mesh:
            return mesh.process(image_rgb)


__all__ = [
    "FaceLandmarksNotFoundError",
    "FaceMeshExtractionError",
    "FaceMeshExtractionMetadata",
    "FaceMeshExtractionResult",
    "FacePoint",
    "MediaPipeFaceMeshExtractor",
]
