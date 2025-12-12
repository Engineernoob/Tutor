import cv2
import mediapipe as mp
import time
import math
from collections import deque
from typing import List, Optional
import numpy as np


class HandTracker:
    """Hand gesture detection and tracking using MediaPipe."""

    # Gesture constants
    GESTURES = {
        "NO_HAND": "NO_HAND",
        "OPEN_PALM": "OPEN_PALM",
        "FIST": "FIST",
        "POINT": "POINT",
        "PINCH": "PINCH",
        "UNKNOWN": "UNKNOWN"
    }

    def __init__(
        self,
        max_hands: int = 1,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.7,
        hold_frames: int = 8,
        cooldown: float = 0.6,
    ) -> None:
        """
        Initialize hand tracker.

        Args:
            max_hands: Maximum number of hands to detect
            detection_confidence: Minimum confidence for initial detection
            tracking_confidence: Minimum confidence for tracking
            hold_frames: Number of frames to hold gesture for stability
            cooldown: Minimum time between gesture changes (seconds)
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Gesture stability system
        self.gesture_buffer: deque = deque(maxlen=hold_frames)
        self.last_stable_gesture = self.GESTURES["NO_HAND"]
        self.last_emit_time = 0.0
        self.cooldown = cooldown

        # Landmark indices for gesture detection
        self.finger_tips = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
        self.finger_joints = [2, 6, 10, 14, 18]  # corresponding PIP joints

    def process(self, frame: np.ndarray) -> str:
        """
        Process frame for hand gesture detection.

        Args:
            frame: Input video frame (BGR format)

        Returns:
            Detected gesture name (stable, with cooldown)
        """
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            if not results.multi_hand_landmarks:
                self._update_buffer(self.GESTURES["NO_HAND"])
                return self._stable_gesture()

            # Process first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]

            # Draw landmarks on frame
            self.mp_draw.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
            )

            gesture = self._classify_gesture(hand_landmarks)
            self._update_buffer(gesture)

            return self._stable_gesture()

        except Exception as e:
            print(f"[Tutor] Hand tracking error: {e}")
            return self.GESTURES["UNKNOWN"]

    def _update_buffer(self, gesture: str) -> None:
        """Update gesture stability buffer."""
        self.gesture_buffer.append(gesture)

    def _stable_gesture(self) -> str:
        """
        Return stable gesture using majority voting and cooldown.

        Only emits gesture if:
        1. It's the most common in recent frames
        2. Cooldown period has passed since last change
        """
        if len(self.gesture_buffer) == 0:
            return self.last_stable_gesture

        # Find most common gesture in buffer
        most_common = max(set(self.gesture_buffer), key=self.gesture_buffer.count)

        now = time.time()
        if (
            most_common != self.last_stable_gesture
            and now - self.last_emit_time > self.cooldown
        ):
            self.last_stable_gesture = most_common
            self.last_emit_time = now

        return self.last_stable_gesture

    def _distance(self, a, b) -> float:
        """Calculate Euclidean distance between two landmarks."""
        return math.hypot(a.x - b.x, a.y - b.y)

    def _classify_gesture(self, landmarks) -> str:
        """
        Classify hand gesture based on finger positions.

        Uses geometric analysis of finger tip and joint positions.
        """
        fingers_extended = []

        # Check thumb (horizontal extension)
        fingers_extended.append(
            landmarks.landmark[self.finger_tips[0]].x >
            landmarks.landmark[self.finger_joints[0]].x
        )

        # Check other fingers (vertical extension)
        for i in range(1, 5):
            fingers_extended.append(
                landmarks.landmark[self.finger_tips[i]].y <
                landmarks.landmark[self.finger_joints[i]].y
            )

        total_extended = sum(fingers_extended)

        # Special case: pinch detection (thumb + index close together)
        pinch_distance = self._distance(
            landmarks.landmark[4],  # thumb tip
            landmarks.landmark[8]   # index tip
        )

        if pinch_distance < 0.04:
            return self.GESTURES["PINCH"]

        # Standard gesture classification
        if total_extended == 5:
            return self.GESTURES["OPEN_PALM"]
        elif total_extended == 0:
            return self.GESTURES["FIST"]
        elif total_extended == 1 and fingers_extended[1]:  # only index extended
            return self.GESTURES["POINT"]
        else:
            return self.GESTURES["UNKNOWN"]
