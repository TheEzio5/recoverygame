import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy import kivy_data_dir

from console_io import ConsoleBridge

MAX_CHARS = 30000
MONO = os.path.join(kivy_data_dir, "fonts", "RobotoMono-Regular.ttf")


class RecoveryQuestApp(App):
    title = "Recovery Quest"

    def build(self):
        Window.clearcolor = (0.07, 0.08, 0.10, 1)
        self.text = ""

        root = BoxLayout(orientation="vertical", padding=8, spacing=8)

        self.scroll = ScrollView(do_scroll_x=False)
        self.log = Label(
            text="", font_name=MONO, font_size="14sp", markup=False,
            size_hint_y=None, halign="left", valign="top",
            color=(0.9, 0.95, 0.9, 1),
        )
        self.log.bind(
            width=lambda *_: setattr(self.log, "text_size", (self.log.width, None)),
            texture_size=lambda *_: setattr(self.log, "height", self.log.texture_size[1]),
        )
        self.scroll.add_widget(self.log)
        root.add_widget(self.scroll)

        row = BoxLayout(size_hint_y=None, height="52dp", spacing=8)
        self.entry = TextInput(
            multiline=False, font_size="16sp", hint_text="Type here, then Send",
        )
        self.entry.bind(on_text_validate=self.send)
        send = Button(text="Send", size_hint_x=None, width="90dp")
        send.bind(on_release=self.send)
        row.add_widget(self.entry)
        row.add_widget(send)
        root.add_widget(row)
        return root

    def on_start(self):
        # Android only lets the app write inside its own folder
        os.chdir(self.user_data_dir)
        self.bridge = ConsoleBridge(self.write, self.focus_entry)
        self.bridge.install()
        threading.Thread(target=self.run_game, daemon=True).start()

    def run_game(self):
        try:
            import recovery_main
            recovery_main.main()
        except Exception as exc:
            self.bridge.print(f"\nSomething went wrong: {exc!r}")
        self.bridge.print("\nGame closed. You can close the app now.")

    # called from the game thread -> hop to the UI thread
    def write(self, text):
        Clock.schedule_once(lambda dt: self._append(text))

    def focus_entry(self):
        Clock.schedule_once(lambda dt: setattr(self.entry, "focus", True))

    def _append(self, text):
        self.text = (self.text + text)[-MAX_CHARS:]
        self.log.text = self.text
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0), 0.05)

    def send(self, *_):
        answer = self.entry.text
        self.entry.text = ""
        self.bridge.submit(answer)
        self.entry.focus = True


if __name__ == "__main__":
    RecoveryQuestApp().run()
