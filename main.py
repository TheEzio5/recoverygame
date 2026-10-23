"""Touch interface for Recovery Quest (Kivy).
The game itself is unchanged: this file shows what it prints and turns its numbered
menus into tappable picture tiles (see ui_logic.py)."""
import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from console_io import ConsoleBridge
from ui_logic import Screen, build_screen, icon_for

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
MAX_LINES = 120          # a Label is one texture; keep it far below GPU limits
BANNER_RATIO = 420 / 1080

BG = (0.07, 0.08, 0.11, 1)
TILE = (0.16, 0.18, 0.25, 1)
TILE_DOWN = (0.26, 0.30, 0.42, 1)
TILE_LOCKED = (0.13, 0.14, 0.18, 1)
TILE_ON = (0.17, 0.38, 0.28, 1)
TEXT = (0.93, 0.95, 0.93, 1)
TEXT_DIM = (0.55, 0.58, 0.62, 1)


def asset(*parts):
    path = os.path.join(ASSETS, *parts)
    return path if os.path.exists(path) else ""


class Tile(ButtonBehavior, BoxLayout):
    """A rounded, tappable row: picture on the left, text on the right."""

    def __init__(self, label, icon="", locked=False, checked=False, **kwargs):
        super().__init__(orientation="horizontal", padding=dp(8), spacing=dp(10),
                         size_hint_y=None, height=dp(72), **kwargs)
        self.locked = locked
        self.checked = checked
        with self.canvas.before:
            self._color = Color(*self._idle_color())
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._sync, size=self._sync, state=self._recolor)

        if icon:
            self.add_widget(Image(source=icon, size_hint=(None, 1), width=dp(52)))
        text = ("[x] " if checked else "") + label
        lbl = Label(text=text, halign="left", valign="middle", font_size="16sp",
                    color=TEXT_DIM if locked else TEXT)
        lbl.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.add_widget(lbl)

    def _idle_color(self):
        if self.locked:
            return TILE_LOCKED
        return TILE_ON if self.checked else TILE

    def _sync(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _recolor(self, *_):
        self._color.rgba = TILE_DOWN if self.state == "down" else self._idle_color()


class RecoveryQuestApp(App):
    title = "Recovery Quest"

    # ------------------------------------------------------------ layout
    def build(self):
        try:
            Window.softinput_mode = "below_target"
        except Exception:
            pass
        Window.clearcolor = BG
        self.pending = []
        self.screen = None
        self.screen_count = 0

        root = BoxLayout(orientation="vertical", spacing=dp(6))

        self.banner = Image(source=asset("banners", "title.png"), size_hint_y=None,
                            height=dp(140))
        self.banner.bind(width=lambda img, w: setattr(img, "height", w * BANNER_RATIO))
        root.add_widget(self.banner)

        self.scroll = ScrollView(do_scroll_x=False)
        self.log = Label(text="", size_hint_y=None, halign="left", valign="top",
                         font_size="16sp", color=TEXT, padding=(dp(14), dp(8)))
        self.log.bind(
            width=lambda inst, w: setattr(inst, "text_size", (w, None)),
            texture_size=lambda inst, size: setattr(inst, "height", size[1]),
        )
        self.scroll.add_widget(self.log)
        root.add_widget(self.scroll)

        self.controls = BoxLayout(orientation="vertical", size_hint_y=None,
                                  height=dp(10), padding=dp(8), spacing=dp(8))
        root.add_widget(self.controls)
        return root

    # ------------------------------------------------------------ game thread
    def on_start(self):
        # Android/iOS only allow writing inside the app's own folder
        os.chdir(self.user_data_dir)
        self.bridge = ConsoleBridge(self.on_output, self.on_input_needed)
        self.bridge.install()
        threading.Thread(target=self.run_game, daemon=True).start()

    def run_game(self):
        try:
            import recovery_main
            recovery_main.main()
        except Exception as exc:
            self.bridge.print(f"\nSomething went wrong: {exc!r}")
        self.bridge.print("\nGame closed. You can close the app now.")
        text = "".join(self.pending)
        self.pending = []
        screen = build_screen(text, "")
        screen.mode = "end"
        Clock.schedule_once(lambda dt: self.present(screen))

    def on_output(self, text):                    # game thread
        self.pending.append(text)

    def on_input_needed(self, prompt):            # game thread
        text = "".join(self.pending)
        self.pending = []
        screen = build_screen(text, prompt)
        Clock.schedule_once(lambda dt: self.present(screen))

    # ------------------------------------------------------------ UI thread
    def set_banner(self, key):
        path = asset("banners", f"{key}.png")
        if path:
            self.banner.source = path

    def present(self, screen):
        self.screen = screen
        self.screen_count += 1
        if screen.banner:
            self.set_banner(screen.banner)

        self.log.text = "\n".join(screen.lines[-MAX_LINES:])
        self.scroll.scroll_y = 1
        self.controls.clear_widgets()

        if screen.mode == "buttons":
            self._show_tiles(screen)
        elif screen.mode == "continue":
            self._show_continue()
        elif screen.mode == "yesno":
            self._show_yesno()
        elif screen.mode in ("text", "number"):
            self._show_entry(screen)
        else:                                      # "end"
            self.controls.height = dp(10)

    def _show_tiles(self, screen):
        cols = 2 if len(screen.options) >= 8 else 1
        grid = GridLayout(cols=cols, spacing=dp(8), padding=(0, 0, 0, dp(8)),
                          size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for opt in screen.options:
            tile = Tile(opt.label, asset("icons", f"{icon_for(opt.label)}.png")
                        if icon_for(opt.label) else "",
                        locked=opt.locked, checked=opt.checked)
            tile.bind(on_release=lambda _w, n=opt.number: self.choose(n))
            grid.add_widget(tile)
        sv = ScrollView(do_scroll_x=False)
        sv.add_widget(grid)
        self.controls.height = Window.height * 0.46
        self.controls.add_widget(sv)

    def _show_continue(self):
        btn = Button(text="Continue", font_size="18sp", background_normal="",
                     background_color=TILE_ON)
        btn.bind(on_release=lambda _w: self.choose(""))
        self.controls.height = dp(72)
        self.controls.add_widget(btn)

    def _show_yesno(self):
        row = BoxLayout(spacing=dp(10))
        for text, value, color in (("Yes", "1", TILE_ON), ("No", "2", TILE)):
            btn = Button(text=text, font_size="18sp", background_normal="",
                         background_color=color)
            btn.bind(on_release=lambda _w, v=value: self.choose(v))
            row.add_widget(btn)
        self.controls.height = dp(72)
        self.controls.add_widget(row)

    def _show_entry(self, screen):
        row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(56))
        self.entry = TextInput(multiline=False, font_size="18sp",
                               hint_text="Type here",
                               input_filter="int" if screen.mode == "number" else None)
        self.entry.bind(on_text_validate=lambda _w: self.send_entry())
        send = Button(text="Send", size_hint_x=None, width=dp(90))
        send.bind(on_release=lambda _w: self.send_entry())
        row.add_widget(self.entry)
        row.add_widget(send)
        self.controls.height = dp(72)
        self.controls.add_widget(row)
        Clock.schedule_once(lambda dt: setattr(self.entry, "focus", True), 0.1)

    def send_entry(self):
        self.choose(self.entry.text)

    def choose(self, value):
        self.controls.clear_widgets()
        self.bridge.submit(value)


if __name__ == "__main__":
    RecoveryQuestApp().run()
