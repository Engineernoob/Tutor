import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .actions import DesktopActions


class GestureMapper:
    """Maps detected gestures to desktop actions with cooldown and edge detection."""

    # Gesture constants
    GESTURES = {
        "NO_HAND": "no_hand",
        "OPEN_PALM": "open_palm",
        "FIST": "fist",
        "POINT": "point",
        "PINCH": "pinch",
        "UNKNOWN": "unknown"
    }

    def __init__(self, actions: "DesktopActions", cooldown: float = 0.8) -> None:
        """
        Initialize gesture mapper.

        Args:
            actions: DesktopActions instance to control
            cooldown: Minimum time between gesture actions (seconds)
        """
        self.actions = actions
        self.prev_gesture = self.GESTURES["NO_HAND"]
        self.cooldown = cooldown
        self.last_action_time = 0.0

    def handle(self, gesture: str) -> None:
        """
        Process gesture input and trigger appropriate actions.

        Uses edge detection (gesture change) with cooldown to prevent spam.
        Control toggle happens on OPEN_PALM gesture.
        Other actions only work when control is enabled.

        Args:
            gesture: Detected gesture name
        """
        now = time.time()

        # Cooldown gate - prevent action spam
        if now - self.last_action_time < self.cooldown:
            self.prev_gesture = gesture
            return

        # Edge detection: only trigger on gesture change
        if gesture != self.prev_gesture:
            self.last_action_time = now

            # Special case: OPEN_PALM toggles control mode
            if gesture == self.GESTURES["OPEN_PALM"]:
                self.actions.toggle_control()
                self.prev_gesture = gesture
                return

            # Regular actions (only when control is enabled)
            if self.actions.control_enabled:
                self._execute_action(gesture)

        self.prev_gesture = gesture

    def _execute_action(self, gesture: str) -> None:
        """Execute the appropriate action for the given gesture."""
        action_map = {
            self.GESTURES["FIST"]: self.actions.play_pause,
            self.GESTURES["POINT"]: self.actions.next_desktop,
            self.GESTURES["PINCH"]: self.actions.volume_up,
        }

        action = action_map.get(gesture)
        if action:
            action()
