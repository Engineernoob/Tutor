import cv2

# --- Gruvbox Colors (BGR for OpenCV) ---
BG = (40, 40, 40)
FG = (178, 219, 235)

GREEN = (38, 187, 184)
YELLOW = (47, 189, 250)
RED = (52, 73, 251)
AQUA = (152, 165, 131)
MUTED = (132, 153, 168)


def panel(frame, x, y, w, h):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), BG, -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)


def label(frame, text, x, y, color=FG, scale=0.6):
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        2
    )
