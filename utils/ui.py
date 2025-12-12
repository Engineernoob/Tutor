import cv2

# --- Gruvbox (BGR) ---
FG = (178, 219, 235)
MUTED = (132, 153, 168)
GREEN = (38, 187, 184)
YELLOW = (47, 189, 250)
RED = (52, 73, 251)
AQUA = (152, 165, 131)


def polybar(frame, gesture_on, identity):
    x = 15
    y = 30
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.55
    thickness = 2

    def draw(text, color):
        nonlocal x
        cv2.putText(frame, text, (x, y), font, scale, color, thickness)
        x += int(len(text) * 11)

    # Tutor label
    draw("TUTOR", GREEN)
    draw(" │ ", GREEN)

    # Gesture state
    draw("G:ON" if gesture_on else "G:OFF", YELLOW)

    draw(" │ ", MUTED)

    # Identity state
    if identity == "AUTHORIZED":
        draw("ID:OK", GREEN)
    elif identity == "UNKNOWN":
        draw("ID:UNK", RED)
    else:
        draw("ID:NONE", MUTED)
