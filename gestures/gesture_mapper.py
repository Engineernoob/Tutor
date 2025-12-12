import time


class GestureMapper:
    """
    Maps stabilized gestures to desktop actions.
    Obeys core state (gesture_enabled, quiet_mode).
    """

    def __init__(self, actions, state):
        self.actions = actions
        self.state = state

        self.prev_gesture = "NO_HAND"
        self.cooldown = 0.7  # seconds
        self.last_time = 0

    def handle(self, gesture):
        """
        Edge-triggered gesture handling.
        A gesture only fires when it CHANGES.
        """
        now = time.time()

        # Ignore everything if system already locked
        if self.state.lock_triggered:
            return

        # Cooldown gate
        if now - self.last_time < self.cooldown:
            self.prev_gesture = gesture
            return

        # Edge detection: gesture transition
        if gesture != self.prev_gesture:
            self.last_time = now

            # --- GLOBAL TOGGLES (allowed anytime) ---

            # Open palm toggles gesture control
            if gesture == "OPEN_PALM":
                self.state.toggle_gesture()
                self.prev_gesture = gesture
                return

            # If gestures are disabled, stop here
            if not self.state.gesture_enabled:
                self.prev_gesture = gesture
                return

            # --- ACTION MAPPINGS (only when enabled) ---

            if gesture == "FIST":
                self.actions.play_pause()

            elif gesture == "POINT":
                self.actions.next_desktop()

            elif gesture == "PINCH":
                self.actions.volume_up()

        self.prev_gesture = gesture
