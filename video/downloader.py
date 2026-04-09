"""Utilities for video download from remote storage."""

from pathlib import Path

import requests


def download_video(video_url: str, destination: Path, timeout: int = 120) -> Path:
    """Download a remote video into local temporary storage.

    TODO:
    - Integrate signed URL handling for Supabase Storage.
    - Add retry strategy and checksum validation.
    - Replace sync requests with async client if needed.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(video_url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with destination.open("wb") as file_handler:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file_handler.write(chunk)

    return destination

