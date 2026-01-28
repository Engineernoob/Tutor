# vision/camera.py
from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2


@dataclass(frozen=True)
class CameraInfo:
    index: int
    backend: int
    width: int
    height: int
    fps: float


def _default_backend() -> int:
    # On macOS, AVFoundation is the least chaotic option.
    if sys.platform == "darwin":
        return cv2.CAP_AVFOUNDATION
    return cv2.CAP_ANY


def _try_open(
    index: int, backend: int, warmup_frames: int = 3, timeout_s: float = 1.5
) -> Optional[cv2.VideoCapture]:
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        cap.release()
        return None

    start = time.time()
    good = 0
    while time.time() - start < timeout_s and good < warmup_frames:
        ok, frame = cap.read()
        if ok and frame is not None and frame.size > 0:
            good += 1

    if good < warmup_frames:
        cap.release()
        return None

    return cap


def list_working_cameras(
    max_index: int = 6, backend: Optional[int] = None
) -> List[CameraInfo]:
    backend = _default_backend() if backend is None else backend
    found: List[CameraInfo] = []

    for idx in range(max_index + 1):
        cap = _try_open(idx, backend)
        if cap is None:
            continue

        info = CameraInfo(
            index=idx,
            backend=backend,
            width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0),
            height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0),
            fps=float(cap.get(cv2.CAP_PROP_FPS) or 0.0),
        )
        found.append(info)
        cap.release()

    return found


class Camera:
    """
    Deterministic camera wrapper:
      - Can probe for working indices
      - Can force a specific index (recommended on macOS w/ Continuity Camera)
    """

    def __init__(
        self,
        index: Optional[int] = None,
        max_index: int = 6,
        backend: Optional[int] = None,
        request_size: Tuple[int, int] = (1280, 720),
        request_fps: float = 30.0,
    ):
        self.backend = _default_backend() if backend is None else backend
        self.index = index
        self.max_index = max_index
        self.request_size = request_size
        self.request_fps = request_fps

        self.cap: Optional[cv2.VideoCapture] = None
        self.info: Optional[CameraInfo] = None

        self._open()

    def _open(self) -> None:
        candidates = list_working_cameras(
            max_index=self.max_index, backend=self.backend
        )
        if not candidates:
            raise RuntimeError(
                "No working cameras found.\n"
                "Fixes:\n"
                "  • Close apps using camera (Zoom/FaceTime/Browser).\n"
                "  • macOS: System Settings → Privacy & Security → Camera → allow Terminal/Python.\n"
                "  • Try --max-camera-index 10.\n"
            )

        chosen: Optional[CameraInfo] = None

        if self.index is not None:
            for c in candidates:
                if c.index == self.index:
                    chosen = c
                    break
            if chosen is None:
                raise RuntimeError(
                    f"Camera index {self.index} not usable.\n"
                    f"Working indices: {[c.index for c in candidates]}\n"
                    "Run with one of those: --camera <index>"
                )
        else:
            # Default: first working camera.
            # If Continuity Camera keeps hijacking index 0, use --camera explicitly.
            chosen = candidates[0]

        cap = cv2.VideoCapture(chosen.index, chosen.backend)
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to open camera index {chosen.index}")

        # Best-effort capture settings
        w, h = self.request_size
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(w))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(h))
        cap.set(cv2.CAP_PROP_FPS, float(self.request_fps))

        self.cap = cap
        self.info = CameraInfo(
            index=chosen.index,
            backend=chosen.backend,
            width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0),
            height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0),
            fps=float(cap.get(cv2.CAP_PROP_FPS) or 0.0),
        )

    @staticmethod
    def probe(max_index: int = 6, backend: Optional[int] = None) -> List[CameraInfo]:
        return list_working_cameras(max_index=max_index, backend=backend)

    def is_opened(self) -> bool:
        return self.cap is not None and self.cap.isOpened()

    def read(self):
        if self.cap is None:
            return False, None
        return self.cap.read()

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
