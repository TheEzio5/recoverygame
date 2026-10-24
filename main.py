"""Touch interface for Recovery Quest (Kivy).
The game itself is unchanged: this file shows what it prints and turns its numbered
menus into tappable picture tiles (see ui_logic.py)."""
import os
import threading
from datetime import datetime

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
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

try:
    from kivy.core.clipboard import Clipboard
except Exception:          # no clipboard on this platform
    Clipboard = None

import recovery_main
import help_support
from console_io import ConsoleBridge, HELP_TOKEN
from constants import DAY_START_HOUR, DAY_END_HOUR
from ui_logic import Option, Screen, build_screen, icon_for

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
MAX_LINES = 120          # a Label is one texture; keep it far below GPU limits
BANNER_RATIO = 420 / 1080

# what each number means (shown on the Status card)
STAT_INFO = [
    ("Willpower", "willpower", "Your strength to resist urges."),
    ("Hope", "hope", "Belief that things can get better."),
    ("Energy", "energy", "Fuel for activities. Rest and sleep restore it."),
    ("Confidence", "confidence", "Trust in yourself. Grows with honest effort."),
    ("Urge", "urge", "The pull toward old habits. Lower is better."),
]

BG = (0.07, 0.08, 0.11, 1)
TILE = (0.16, 0.18, 0.25, 1)
TILE_DOWN = (0.26, 0.30, 0.42, 1)
TILE_LOCKED = (0.13, 0.14, 0.18, 1)
TILE_ON = (0.17, 0.38, 0.28, 1)
TILE_LINK = (0.12, 0.30, 0.52, 1)
HELP_RED = (0.75, 0.31, 0.30, 1)
TEXT = (0.93, 0.95, 0.93, 1)
TEXT_DIM = (0.55, 0.58, 0.62, 1)


def asset(*parts):
    path = os.path.join(ASSETS, *parts)
    return path if os.path.exists(path) else ""


class Tile(ButtonBehavior, BoxLayout):
    """A rounded, tappable row: picture on the left, text on the right."""

    def __init__(self, label, icon="", locked=False, checked=False, hint="", link=False,
                 **kwargs):
        super().__init__(orientation="horizontal", padding=dp(8), spacing=dp(10),
                         size_hint_y=None, height=dp(72), **kwargs)
        self.locked = locked
        self.checked = checked
        self.link = link
        with self.canvas.before:
            self._color = Color(*self._idle_color())
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._sync, size=self._sync, state=self._recolor)

        if icon:
            self.add_widget(Image(source=icon, size_hint=(None, 1), width=dp(52)))
        text = ("[x] " if checked else "") + label
        box = BoxLayout(orientation="vertical")
        lbl = Label(text=text, halign="left", valign="middle", font_size="16sp",
                    color=TEXT_DIM if locked else TEXT)
        lbl.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        box.add_widget(lbl)
        if hint:
            sub = Label(text=hint, halign="left", valign="middle", font_size="12sp",
                        color=TEXT_DIM, size_hint_y=None, height=dp(18))
            sub.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            box.add_widget(sub)
        self.add_widget(box)

    def _idle_color(self):
        if self.locked:
            return TILE_LOCKED
        if self.link:
            return TILE_LINK
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
        self.screen = None
        self.screen_count = 0

        root = BoxLayout(orientation="vertical", spacing=dp(6))

        self.banner = Image(source=asset("banners", "title.png"), size_hint_y=None,
                            height=dp(140))
        self.banner.bind(width=lambda img, w: setattr(img, "height", w * BANNER_RATIO))
        root.add_widget(self.banner)

        # always-visible strip: clocks on the left, a Help button on every screen
        self.hud = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(70),
                             padding=(dp(14), dp(4), dp(10), dp(4)), spacing=dp(10))
        clocks = BoxLayout(orientation="vertical", spacing=dp(2))
        self.hud_real = Label(text="", font_size="13sp", color=TEXT_DIM,
                              halign="left", valign="middle")
        self.hud_game = Label(text="", font_size="16sp", color=TEXT,
                              halign="left", valign="middle")
        for lab in (self.hud_real, self.hud_game):
            lab.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.hud_bar = ProgressBar(max=DAY_END_HOUR - DAY_START_HOUR, value=0,
                                   size_hint_y=None, height=dp(8))
        clocks.add_widget(self.hud_real)
        clocks.add_widget(self.hud_game)
        clocks.add_widget(self.hud_bar)
        self.hud.add_widget(clocks)
        self.help_button = Button(text="Help", font_size="16sp", size_hint=(None, 1),
                                  width=dp(84), background_normal="",
                                  background_color=HELP_RED)
        self.help_button.bind(on_release=lambda _w: self.request_help())
        self.hud.add_widget(self.help_button)
        root.add_widget(self.hud)
        Clock.schedule_interval(lambda dt: self.update_hud(), 1)

        self.scroll = ScrollView(do_scroll_x=False)
        self.log = Label(text="", size_hint_y=None, halign="left", valign="top",
                         font_size="16sp", color=TEXT, padding=(dp(14), dp(8)))
        self.log.bind(
            width=lambda inst, w: setattr(inst, "text_size", (w, None)),
            texture_size=lambda inst, size: setattr(inst, "height", size[1]),
        )
        self.scroll.add_widget(self.log)
        self.body = self.log
        self.status_cards_shown = 0
        self.last_tapped = None
        self.quit_requested = False
        self.opened_links = []
        root.add_widget(self.scroll)
        self.update_hud()

        self.controls = BoxLayout(orientation="vertical", size_hint_y=None,
                                  height=dp(10), padding=dp(8), spacing=dp(8))
        root.add_widget(self.controls)
        return root

    # ------------------------------------------------------------ game thread
    def on_start(self):
        # Android/iOS only allow writing inside the app's own folder
        os.chdir(self.user_data_dir)
        self.bridge = ConsoleBridge(self.on_input_needed,
                                    help_handler=help_support.help_session)
        self.bridge.install()
        threading.Thread(target=self.run_game, daemon=True).start()

    def run_game(self):
        failed = False
        try:
            recovery_main.main()
        except Exception as exc:
            failed = True
            self.bridge.print(f"\nSomething went wrong: {exc!r}")
        screen = build_screen(self.bridge.take_buffer(), "")
        screen.mode = "error" if failed else "end"
        Clock.schedule_once(lambda dt: self.present(screen))
        if not failed:                              # Exit was chosen: close the app
            Clock.schedule_once(lambda dt: self.quit_app(), 1.6)

    def quit_app(self):
        self.quit_requested = True
        try:
            self.stop()
        except Exception:
            pass
        Clock.schedule_once(lambda dt: self._hard_exit(), 0.4)

    def _hard_exit(self):
        # iOS never closes an app by itself after stop(), so end the process.
        os._exit(0)

    def on_input_needed(self, prompt, block):     # game thread
        screen = build_screen(block, prompt)
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

        self.update_hud()
        self.log.text = "\n".join(screen.lines[-MAX_LINES:])
        self.controls.clear_widgets()

        tapped, self.last_tapped = self.last_tapped, None
        player = recovery_main.current_player
        if tapped and icon_for(tapped) == "status" and player is not None:
            self._set_body(self._status_card(player))
            self.status_cards_shown += 1
        else:
            self._set_body(self.log)
        self.scroll.scroll_y = 1

        if screen.mode == "buttons":
            self._show_tiles(screen.options, screen.links)
        elif screen.mode == "continue":
            if screen.links:
                self._show_tiles([Option("", "Continue")], screen.links)
            else:
                self._show_continue()
        elif screen.mode == "yesno":
            if screen.links:
                self._show_tiles([Option("1", "Yes"), Option("2", "No")], screen.links)
            else:
                self._show_yesno()
        elif screen.mode in ("text", "number"):
            self._show_entry(screen)
        elif screen.mode == "error":
            btn = Button(text="Close app", font_size="18sp", background_normal="",
                         background_color=TILE)
            btn.bind(on_release=lambda _w: self.quit_app())
            self.controls.height = dp(72)
            self.controls.add_widget(btn)
        else:                                      # "end": the app closes by itself
            self.controls.height = dp(10)

    def _show_tiles(self, options, links=()):
        cols = 2 if len(options) >= 8 and not links else 1
        grid = GridLayout(cols=cols, spacing=dp(8), padding=(0, 0, 0, dp(8)),
                          size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for label, url in links:                   # real-world links first
            tile = Tile(f"Open: {label}", asset("icons", "link.png"), link=True)
            tile.bind(on_release=lambda _w, u=url: self.open_link(u))
            grid.add_widget(tile)
        for opt in options:
            key = icon_for(opt.label)
            tile = Tile(opt.label, asset("icons", f"{key}.png") if key else "",
                        locked=opt.locked, checked=opt.checked, hint=opt.hint)
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

    def request_help(self):
        bridge = getattr(self, "bridge", None)
        if bridge is not None:
            bridge.submit(HELP_TOKEN)

    def open_link(self, url):
        self.opened_links.append(url)
        opened = False
        try:
            import webbrowser
            opened = bool(webbrowser.open(url))
        except Exception:
            opened = False
        copied = False
        if Clipboard is not None:
            try:
                Clipboard.copy(url)
                copied = True
            except Exception:
                copied = False
        note = "Opening the link..." if opened else "Couldn't open the browser here."
        if copied:
            note += " The link was copied: paste it into your browser."
        self._set_body(self.log)
        self.log.text = self.log.text + "\n\n" + note

    def send_entry(self):
        self.choose(self.entry.text)

    def choose(self, value):
        self.last_tapped = None
        if self.screen is not None and self.screen.mode == "buttons":
            for opt in self.screen.options:
                if opt.number == value:
                    self.last_tapped = opt.label
        self.controls.clear_widgets()
        self.bridge.submit(value)

    # ------------------------------------------------------------ clocks + status
    def update_hud(self):
        now = datetime.now()
        self.hud_real.text = now.strftime("Real time: %a %d %b %Y, %H:%M:%S")
        player = recovery_main.current_player
        if player is None:
            self.hud_game.text = "Game time: --"
            self.hud_bar.value = 0
            return
        self.hud_game.text = (f"Game: Day {player.journey_days}, {player.weekday_name} "
                              f"{player.clock_text}   Energy {player.energy}   "
                              f"Money €{player.money}")
        self.hud_bar.value = max(0, min(DAY_END_HOUR - DAY_START_HOUR,
                                        player.hour - DAY_START_HOUR))

    def _set_body(self, widget):
        if self.body is not widget:
            self.scroll.clear_widgets()
            self.scroll.add_widget(widget)
            self.body = widget

    def _status_card(self, player):
        card = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6),
                         padding=(dp(14), dp(8)))
        card.bind(minimum_height=card.setter("height"))

        def line(text, size="15sp", color=TEXT, height=dp(24)):
            lab = Label(text=text, font_size=size, color=color, halign="left",
                        valign="middle", size_hint_y=None, height=height)
            lab.bind(size=lambda inst, s: setattr(inst, "text_size", s))
            card.add_widget(lab)

        line(f"{player.name}  -  Level {player.level}", "20sp", TEXT, dp(32))
        line(f"Recovery days: {player.recovery_days}   Journey days: {player.journey_days}")
        line(f"Money: €{player.money}   Debt: €{player.debt}")
        line(f"Recovering from: {player.addiction_names()}")
        if player.in_rehabilitation:
            line(f"{player.rehab_section.capitalize()} rehabilitation, "
                 f"{player.rehab_days_remaining} day(s) left")
        line("")

        for label, attr, meaning in STAT_INFO:
            line(f"{label}: {getattr(player, attr)} / 100", "16sp", TEXT, dp(24))
            card.add_widget(ProgressBar(max=100, value=getattr(player, attr),
                                        size_hint_y=None, height=dp(10)))
            line(meaning, "12sp", TEXT_DIM, dp(20))
        line(f"Experience: {player.experience} / {player.next_level}", "16sp", TEXT, dp(24))
        card.add_widget(ProgressBar(max=player.next_level, value=player.experience,
                                    size_hint_y=None, height=dp(10)))
        line("Fills up to raise your level.", "12sp", TEXT_DIM, dp(20))
        return card


if __name__ == "__main__":
    RecoveryQuestApp().run()
