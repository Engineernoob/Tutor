import subprocess
import time
import platform
from typing import NoReturn

LOCK_DELAY = 5.0  # seconds


def lock_screen() -> None:
    """
    Lock the screen and put display to sleep.

    Uses platform-specific commands to lock the workstation.
    Includes error handling and fallback options.
    """
    system = platform.system().lower()
    print(f"[Tutor] Locking screen on {system}")

    try:
        if system == "darwin":  # macOS
            # Put display to sleep (locks screen)
            subprocess.run(["pmset", "displaysleepnow"], check=True, timeout=10)

        elif system == "windows":
            # Lock workstation
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True, timeout=10)

        elif system == "linux":
            # Try multiple common lock commands
            lock_commands = [
                ["gnome-screensaver-command", "-l"],
                ["xdg-screensaver", "lock"],
                ["i3lock", "-c", "000000"],  # Simple black screen lock
                ["slock"],  # Simple X lock
            ]

            success = False
            for cmd in lock_commands:
                try:
                    subprocess.run(cmd, check=True, timeout=5)
                    success = True
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            if not success:
                print("[Tutor] Warning: No suitable screen lock command found")

        else:
            print(f"[Tutor] Warning: Screen locking not implemented for {system}")

    except subprocess.TimeoutExpired:
        print("[Tutor] Warning: Screen lock command timed out")
    except subprocess.CalledProcessError as e:
        print(f"[Tutor] Warning: Screen lock failed: {e}")
    except Exception as e:
        print(f"[Tutor] Error during screen lock: {e}")

    # Brief delay to allow lock to take effect
    time.sleep(min(LOCK_DELAY, 2.0))
