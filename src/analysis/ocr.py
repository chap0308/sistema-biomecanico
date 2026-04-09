"""OCR helpers for sampled video frames."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

import cv2


@dataclass(slots=True)
class OcrObservation:
    """OCR text extracted from one representative frame."""

    sec: float
    path: str
    text: str
    confidence: float | None = None


def tesseract_available() -> bool:
    """Return whether the tesseract executable is available."""
    return _resolve_tesseract_cmd() is not None


def _resolve_tesseract_cmd() -> str | None:
    """Resolve the tesseract executable from env, PATH, or common Windows install path."""
    env_cmd = os.getenv("TESSERACT_CMD", "").strip().strip('"')
    if env_cmd and Path(env_cmd).exists():
        return env_cmd

    from_path = shutil.which("tesseract")
    if from_path:
        return from_path

    common_windows_path = Path("C:/Program Files/Tesseract-OCR/tesseract.exe")
    if common_windows_path.exists():
        return str(common_windows_path)

    return None


def run_ocr_on_frames(frame_paths_with_secs: list[tuple[float, str]]) -> tuple[list[OcrObservation], str]:
    """Run OCR over sampled frames when pytesseract and tesseract are available."""
    try:
        import pytesseract
    except Exception:
        return [], "pytesseract_unavailable"

    tesseract_cmd = _resolve_tesseract_cmd()
    if not tesseract_cmd:
        return [], "tesseract_binary_unavailable"
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    observations: list[OcrObservation] = []
    for sec, frame_path in frame_paths_with_secs:
        image = cv2.imread(str(frame_path))
        if image is None:
            continue
        try:
            text = pytesseract.image_to_string(image).strip()
        except Exception:
            continue
        if not text:
            continue
        observations.append(
            OcrObservation(
                sec=float(sec),
                path=str(frame_path),
                text=text,
                confidence=None,
            )
        )
    return observations, "ok" if observations else "no_ocr_text"
