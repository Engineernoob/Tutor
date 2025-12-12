import time
from typing import Optional, Tuple

import cv2

from gestures.actions import DesktopActions
from gestures.gesture_mapper import GestureMapper
from security.lock_screen import lock_screen
from utils.blur import apply_blur
from vision.camera import Camera
from vision.face_detector import FacePresenceDetector
from vision.face_recognition import FaceRecognizer
from vision.hand_tracker import HandTracker
from utils.ui import polybar

camera = Camera()
BLUR_DURATION = 1.5
WINDOW_NAME = "Tutor - Gesture-Controlled Desktop"

class SecurityState:
    """Manages security-related state and transitions."""

    def __init__(self):
        self.blur_start_time: Optional[float] = None
        self.lock_triggered = False
        self.blur_strength = 5

    def start_blur(self) -> None:
        """Start the blur countdown."""
        self.blur_start_time = time.time()
        self.lock_triggered = True

    def reset(self) -> None:
        """Reset security state."""
        self.blur_start_time = None
        self.lock_triggered = False
        self.blur_strength = 5

    def should_lock(self) -> bool:
        """Check if it's time to lock the screen."""
        if self.blur_start_time is None:
            return False
        elapsed = time.time() - self.blur_start_time
        return elapsed >= BLUR_DURATION

    def update_blur_progress(self) -> int:
        """Update and return current blur strength based on progress."""
        if self.blur_start_time is None:
            return self.blur_strength

        elapsed = time.time() - self.blur_start_time
        progress = min(elapsed / BLUR_DURATION, 1.0)
        self.blur_strength = int(5 + progress * 45)
        return self.blur_strength


def render_ui(
    frame, gesture_on: bool, identity: str
) -> None:
    """Render the user interface overlay on the frame."""

    polybar(frame, gesture_on, identity)


def handle_security_warnings(
    frame, identity: str, face_absent: bool, security_state: SecurityState
) -> None:
    """Handle security warnings and blur effects."""
    height = frame.shape[0]

    if identity == "UNKNOWN" and not security_state.lock_triggered:
        # Apply progressive blur for unknown face
        blur_strength = security_state.update_blur_progress()
        frame = apply_blur(frame, blur_strength)


        if security_state.should_lock():
            lock_screen()
            security_state.reset()

    elif face_absent and not security_state.lock_triggered:
        # Start countdown for face absence
        security_state.start_blur()

    polybar(
    frame,
    False,
    identity if identity != "UNKNOWN" else "UNREGISTERED"
)


def initialize_components() -> Tuple[
    cv2.VideoCapture,
    HandTracker,
    FacePresenceDetector,
    FaceRecognizer,
    DesktopActions,
    GestureMapper,
]:
    """Initialize all required components."""
    cap = Camera()
    if not camera.is_opened():
        raise RuntimeError("Failed to open camera")

    hand_tracker = HandTracker()
    face_detector = FacePresenceDetector(absence_timeout=0.1)
    face_recognizer = FaceRecognizer()
    actions = DesktopActions()
    mapper = GestureMapper(actions)

    return cap, hand_tracker, face_detector, face_recognizer, actions, mapper


def main():
    """Main application loop."""
    try:
        # Initialize components
        cap, hand_tracker, face_detector, face_recognizer, actions, mapper = (
            initialize_components()
        )

        # Initialize security state
        security_state = SecurityState()

        print("[Tutor] Starting Gesture-Controlled Desktop...")

        while True:
            ret, frame = camera.read()
            if not ret:
                print("[Tutor] Failed to read frame from camera")
                break

            # Process gestures and face recognition
            gesture = hand_tracker.process(frame)
            mapper.handle(gesture)

            face_absent = face_detector.process(frame)
            identity = face_recognizer.process(frame)

            # Handle security warnings and blur effects
            handle_security_warnings(frame, identity, face_absent, security_state)

            # Render UI
            render_ui(frame, gesture.on, identity)

            # Display frame
            cv2.imshow(WINDOW_NAME, frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord("r"):
                success = face_recognizer.register_face(frame)
                print(
                    "[Tutor] Face registered"
                    if success
                    else "[Tutor] Face not detected"
                )
            elif key == ord("q"):
                break

    except KeyboardInterrupt:
        print("[Tutor] Interrupted by user")
    except Exception as e:
        print(f"[Tutor] Error: {e}")
    finally:
        # Cleanup
        if "camera" in locals():
            camera.release()
        cv2.destroyAllWindows()
        print("[Tutor] Shutdown complete")


if __name__ == "__main__":
    main()
