import time

class TutorState:
    def __init__(self):
        self.gesture_enabled = False
        self.quiet_mode = False
        self.identity = "NONE"   # NONE | AUTHORIZED | UNKNOWN
        self.lock_triggered = False
        self.blur_start_time = None
        self.blur_strength = 5

    # --- toggles ---
    def toggle_gesture(self):
        self.gesture_enabled = not self.gesture_enabled

    def toggle_quiet(self):
        self.quiet_mode = not self.quiet_mode

    # --- security ---
    def start_blur(self):
        self.lock_triggered = True

    def reset(self):
        self.lock_triggered = False

    def should_lock(self):
        return self.lock_triggered