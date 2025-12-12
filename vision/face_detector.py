import cv2
import mediapipe as mp
import time
from typing import Optional
import numpy as np


class FacePresenceDetector:
    """Detects face presence and tracks absence duration for security."""

    def __init__(self, absence_timeout: float = 5.0) -> None:
        """
        Initialize face presence detector.

        Args:
            absence_timeout: Seconds without face detection before triggering absence
        """
        self.mp_face = mp.solutions.face_detection
        self.face = self.mp_face.FaceDetection(min_detection_confidence=0.6)

        self.absence_timeout = absence_timeout
        self.last_seen_time: float = time.time()
        self.face_present: bool = False

    def process(self, frame: np.ndarray) -> bool:
        """
        Process frame for face detection.

        Args:
            frame: Input video frame (BGR format)

        Returns:
            True if face has been absent longer than timeout, False otherwise
        """
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face.process(rgb)

            if results.detections:
                self.last_seen_time = time.time()
                self.face_present = True
            else:
                self.face_present = False

            return self._is_absent_too_long()

        except Exception as e:
            print(f"[Tutor] Face detection error: {e}")
            return False

    def _is_absent_too_long(self) -> bool:
        """
        Check if face has been absent for longer than the timeout period.

        Returns:
            True if absence timeout exceeded, False otherwise
        """
        if self.face_present:
            return False

        time_since_last_seen = time.time() - self.last_seen_time
        return time_since_last_seen > self.absence_timeout

    def get_absence_duration(self) -> float:
        """Get how long the face has been absent (seconds)."""
        if self.face_present:
            return 0.0
        return time.time() - self.last_seen_time
