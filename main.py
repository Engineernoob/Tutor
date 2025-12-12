import time
import cv2

from core.state import TutorState
from gestures.actions import DesktopActions
from gestures.gesture_mapper import GestureMapper
from security.lock_screen import lock_screen
from utils.blur import apply_blur
from utils.ui import polybar
from vision.camera import Camera
from vision.face_detector import FacePresenceDetector
from vision.face_recognition import FaceRecognizer
from vision.hand_tracker import HandTracker


WINDOW_NAME = "Tutor"
BLUR_DURATION = 1.5


def main():
    state = TutorState()

    camera = Camera()
    if not camera.is_opened():
        raise RuntimeError("Failed to open camera")

    hand_tracker = HandTracker()
    face_detector = FacePresenceDetector(absence_timeout=0.1)
    face_recognizer = FaceRecognizer()
    actions = DesktopActions()
    mapper = GestureMapper(actions, state)

    blur_start_time = None

    print("[Tutor] Daemon started")

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break

            # --- Vision ---
            gesture = hand_tracker.process(frame)
            mapper.handle(gesture)

            face_absent = face_detector.process(frame)
            identity = face_recognizer.process(frame)
            state.identity = identity or "NONE"

            now = time.time()

            # --- SECURITY (LATCHED) ---
            if not state.lock_triggered:

                # Unknown face → immediate lock
                if state.identity == "UNKNOWN":
                    frame = apply_blur(frame, 45)
                    polybar(frame, state.gesture_enabled, "UNKNOWN")
                    lock_screen()
                    state.lock_triggered = True
                    break

                # Face absent → delayed lock
                if face_absent:
                    if blur_start_time is None:
                        blur_start_time = now

                    elapsed = now - blur_start_time
                    progress = min(elapsed / BLUR_DURATION, 1.0)
                    blur_strength = int(5 + progress * 45)

                    frame = apply_blur(frame, blur_strength)

                    if elapsed >= BLUR_DURATION:
                        lock_screen()
                        state.lock_triggered = True
                        break
                else:
                    blur_start_time = None

            # --- UI (POLYBAR ONLY) ---
            polybar(frame, state.gesture_enabled, state.identity)

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("r"):
                if face_recognizer.register_face(frame):
                    print("[Tutor] Face registered")
                else:
                    print("[Tutor] No face detected")
            elif key == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("[Tutor] Daemon stopped")


if __name__ == "__main__":
    main()
