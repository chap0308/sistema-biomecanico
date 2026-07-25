from pathlib import Path
import subprocess

import cv2
import numpy as np

from src.squat.video_encoding import (
    encode_h264_mp4,
    normalize_h264_mp4,
    probe_video_codec,
)


def _write_mp4v(path: Path) -> None:
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        10.0,
        (64, 64),
    )
    assert writer.isOpened()
    for index in range(8):
        frame = np.full((64, 64, 3), index * 20, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_encode_h264_mp4_produces_browser_compatible_video(tmp_path: Path) -> None:
    source = tmp_path / "intermediate.mp4"
    output = tmp_path / "overlay.mp4"
    _write_mp4v(source)

    encode_h264_mp4(source, output)

    assert output.is_file()
    assert source.exists() is False
    assert probe_video_codec(output) == {
        "codec_name": "h264",
        "codec_tag_string": "avc1",
        "pix_fmt": "yuv420p",
    }
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"],
        check=True,
    )


def test_normalize_h264_mp4_is_idempotent(tmp_path: Path) -> None:
    video = tmp_path / "review.mp4"
    _write_mp4v(video)

    assert normalize_h264_mp4(video) is True
    assert normalize_h264_mp4(video) is False
