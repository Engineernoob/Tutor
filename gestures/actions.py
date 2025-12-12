import platform
from typing import Optional
import pyautogui
from pynput.keyboard import Key, Controller

keyboard = Controller()


class DesktopActions:
    """Handles desktop control actions via keyboard and mouse simulation."""

    def __init__(self) -> None:
        self.control_enabled = False
        self.last_action: Optional[str] = None
        self.system = platform.system().lower()

    def toggle_control(self) -> None:
        """Toggle gesture control on/off."""
        self.control_enabled = not self.control_enabled
        status = "ENABLED" if self.control_enabled else "DISABLED"
        print(f"[Tutor] Control mode: {status}")

    def play_pause(self) -> None:
        """Toggle play/pause for media playback."""
        keyboard.press(Key.media_play_pause)
        keyboard.release(Key.media_play_pause)
        self.last_action = "play_pause"

    def next_desktop(self) -> None:
        """Switch to next virtual desktop/workspace."""
        if self.system == "darwin":  # macOS
            pyautogui.hotkey("ctrl", "right")
        elif self.system == "windows":
            pyautogui.hotkey("win", "ctrl", "right")
        elif self.system == "linux":
            pyautogui.hotkey("ctrl", "alt", "right")
        self.last_action = "next_desktop"

    def volume_up(self) -> None:
        """Increase system volume."""
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        self.last_action = "volume_up"

    def volume_down(self) -> None:
        """Decrease system volume."""
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)
        self.last_action = "volume_down"

    def mute(self) -> None:
        """Mute/unmute system volume."""
        keyboard.press(Key.media_volume_mute)
        keyboard.release(Key.media_volume_mute)
        self.last_action = "mute"

    def unmute(self) -> None:
        """Unmute system volume (press volume up as alternative)."""
        # Note: Some systems don't have a dedicated unmute key
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        self.last_action = "unmute"

    def increase_brightness(self) -> None:
        """Increase screen brightness."""
        keyboard.press(Key.media_brightness_up)
        keyboard.release(Key.media_brightness_up)
        self.last_action = "brightness_up"

    def decrease_brightness(self) -> None:
        """Decrease screen brightness."""
        keyboard.press(Key.media_brightness_down)
        keyboard.release(Key.media_brightness_down)
        self.last_action = "brightness_down"
