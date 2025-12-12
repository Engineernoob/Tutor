import cv2
import numpy as np
from typing import Union


def apply_blur(frame: np.ndarray, intensity: Union[int, float] = 15) -> np.ndarray:
    """
    Apply Gaussian blur to frame for privacy protection.

    Args:
        frame: Input image/frame to blur
        intensity: Blur intensity (higher = more blur).
                  Will be made odd and clamped to valid range.

    Returns:
        Blurred frame as numpy array

    Note:
        Gaussian blur kernel size must be odd and positive.
        Intensity is automatically adjusted to valid range.
    """
    if not isinstance(frame, np.ndarray):
        raise TypeError("Frame must be a numpy array")

    if frame.size == 0:
        raise ValueError("Frame cannot be empty")

    # Ensure intensity is valid for Gaussian blur
    intensity = max(1, int(intensity))

    # Make kernel size odd (required for Gaussian blur)
    kernel_size = intensity | 1  # Bitwise OR with 1 makes it odd

    # Clamp to reasonable range to prevent excessive computation
    kernel_size = min(kernel_size, 99)  # Max reasonable kernel size

    try:
        return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    except cv2.error as e:
        print(f"[Tutor] Blur error: {e}")
        return frame  # Return original frame on error
