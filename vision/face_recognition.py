import cv2
import mediapipe as mp
import numpy as np
import os
from typing import Optional, Union


class FaceRecognizer:
    """Face recognition using MediaPipe Face Mesh landmarks."""

    def __init__(self, threshold: float = 0.6, save_path: str = "data/face_embedding.npy") -> None:
        """
        Initialize face recognizer.

        Args:
            threshold: Distance threshold for face matching (lower = stricter)
            save_path: Path to save/load face embedding data
        """
        self.threshold = threshold
        self.save_path = save_path

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

        self.reference_embedding: Optional[np.ndarray] = None
        self._load_reference_embedding()

    def _load_reference_embedding(self) -> None:
        """Load reference face embedding from disk if it exists."""
        try:
            if os.path.exists(self.save_path):
                self.reference_embedding = np.load(self.save_path)
                print(f"[Tutor] Loaded face embedding from {self.save_path}")
        except (IOError, ValueError) as e:
            print(f"[Tutor] Failed to load face embedding: {e}")
            self.reference_embedding = None

    def process(self, frame: np.ndarray) -> Optional[str]:
        """
        Process frame and return face recognition result.

        Returns:
            None: No face detected
            "UNREGISTERED": No reference face registered
            "UNKNOWN": Face detected but doesn't match reference
            "AUTHORIZED": Face matches reference
        """
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return None  # No face detected

            landmarks = results.multi_face_landmarks[0]
            embedding = self._extract_embedding(landmarks)

            if self.reference_embedding is None:
                return "UNREGISTERED"

            distance = np.linalg.norm(embedding - self.reference_embedding)

            return "UNKNOWN" if distance > self.threshold else "AUTHORIZED"

        except Exception as e:
            print(f"[Tutor] Face recognition error: {e}")
            return None

    def register_face(self, frame: np.ndarray) -> bool:
        """
        Register a new face from the current frame.

        Args:
            frame: Input frame containing face to register

        Returns:
            True if registration successful, False otherwise
        """
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return False

            landmarks = results.multi_face_landmarks[0]
            embedding = self._extract_embedding(landmarks)

            # Ensure directory exists
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

            # Save embedding
            np.save(self.save_path, embedding)
            self.reference_embedding = embedding

            print(f"[Tutor] Face registered successfully to {self.save_path}")
            return True

        except Exception as e:
            print(f"[Tutor] Face registration error: {e}")
            return False

    def _extract_embedding(self, landmarks) -> np.ndarray:
        """
        Extract face embedding from landmarks.

        Uses all 468 facial landmark coordinates (x, y, z) as features.
        This creates a 1404-dimensional feature vector.
        """
        points = []
        for lm in landmarks.landmark:
            points.extend([lm.x, lm.y, lm.z])
        return np.array(points, dtype=np.float32)
