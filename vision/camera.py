import cv2


class Camera:
    def __init__(self, width=1280, height=720):
        """
        macOS camera selection strategy:
        - Ignore Continuity Camera (usually index 0)
        - Prefer built-in webcam (usually index 1)
        """
        self.cap = None
        self.index = self._select_camera()

        if self.index is None:
            raise RuntimeError("No usable camera found")

        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera index {self.index}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        print(f"[Tutor] Using camera index {self.index}")

    def _select_camera(self):
        available = []

        # Probe first few indices safely
        for i in range(3):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()

        if not available:
            return None

        # Prefer index 1 (built-in webcam) if present
        if 1 in available:
            return 1

        # Otherwise fall back to first available
        return available[0]

    def read(self):
        return self.cap.read()

    def release(self):
        if self.cap:
            self.cap.release()

    def is_opened(self):
        return self.cap is not None and self.cap.isOpened()
