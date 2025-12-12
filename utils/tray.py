import rumps

class TutorTray(rumps.App):
    def __init__(self):
        super().__init__("TUTOR", quit_button=None)
        self.menu = [
            rumps.MenuItem("Gesture Control", callback=self.toggle_gesture),
            rumps.MenuItem("Quiet Mode", callback=self.toggle_quiet),
            None,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]

        self.gesture_on = False
        self.quiet_mode = False
        self.update_icon("idle")

    def toggle_gesture(self, _):
        self.gesture_on = not self.gesture_on
        self.update_icon("armed" if self.gesture_on else "idle")

    def toggle_quiet(self, _):
        self.quiet_mode = not self.quiet_mode
        self.update_icon("quiet" if self.quiet_mode else "idle")

    def update_icon(self, state):
        if state == "armed":
            self.icon = "assets/tutor_icon.png"
        elif state == "quiet":
            self.icon = "assets/tutor_icon_muted.png"
        else:
            self.icon = "assets/tutor_icon_fg.png"


if __name__ == "__main__":
    TutorTray().run()
