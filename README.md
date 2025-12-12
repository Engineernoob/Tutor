🛡️ Tutor

Gesture-Controlled, Privacy-First Desktop Guardian (macOS)

Tutor is a local-only computer vision system that enables gesture-based desktop control and automatically secures a workstation using presence and identity awareness — without sending data to the cloud.

✨ Why Tutor Exists

Most “computer vision projects” stop at detection demos.
Tutor treats vision as input + security, not novelty.

It answers a real question:

How can a computer understand human intent and protect itself without violating privacy?

🔐 Core Features
🖐️ Gesture-Controlled Desktop

Hands act as an input device.

Gesture Action
Open Palm Toggle control mode
Fist Play / Pause media
Point Switch macOS desktops
Pinch Volume control

Gestures are:

Edge-triggered (no flicker)

Debounced

Intentional

👁️ Presence-Based Security

If no face is detected → system initiates lock

Includes a grace period + blur UX

Prevents accidental lockouts

🧠 Identity Awareness (Local Only)

User registers their face once

If an unknown face appears → immediate blur + lock

No auto-unlock

No cloud

No biometric uploads

🌫️ Blur-Before-Lock UX

Instead of instantly locking:

Screen progressively blurs

User is visually informed

Lock triggers cleanly

This avoids jump-scare UX and builds trust.

🧱 Architecture Overview
Tutor/
├── vision/
│ ├── hand_tracker.py # MediaPipe hands + gesture classification
│ ├── face_detector.py # Face presence detection
│ └── face_recognition.py # Local face embeddings + distance check
│
├── gestures/
│ ├── actions.py # macOS system actions
│ └── gesture_mapper.py # Edge-triggered gesture logic
│
├── security/
│ └── lock_screen.py # OS-level screen lock
│
├── utils/
│ └── blur.py # Progressive blur utility
│
├── main.py
└── README.md

Key design rule:
Vision ≠ Actions ≠ Security
Each concern is isolated.

🧠 Design Decisions (Interview Gold)

Edge-triggered gestures instead of state-based
→ prevents repeated actions and flicker

Presence before identity
→ reduces false positives and attack surface

No auto-unlock
→ security systems should fail closed

Local embeddings only
→ privacy by design, not by policy

OS-level display sleep for locking
→ reliable, permission-safe, future-proof

🛠️ Tech Stack

Python 3.10+

OpenCV

MediaPipe (Hands + Face Mesh)

NumPy

PyAutoGUI / pynput

macOS system utilities

🚀 How to Run
python main.py

Controls

Press R → register your face

Press Q → quit

## Architecture Notes

Tutor is intentionally modular. Each subsystem owns exactly one responsibility.

- `camera.py` abstracts hardware access and frame acquisition
- Vision modules consume frames but do not control the OS
- Gesture logic is edge-triggered and state-aware
- Security actions are latched and one-shot
- All identity data remains local

This separation prevents cascading failures and simplifies reasoning
about security-critical behavior.
