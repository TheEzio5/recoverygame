"""UI tests. ui_logic is pure Python. For main.py we install tiny stand-ins for Kivy,
so the real game runs through the real tile logic (only the drawing is faked)."""
import os
import sys
import tempfile
import threading
import time
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ui_logic import build_screen, icon_for
from console_io import strip_emoji


class TestBuildScreen(unittest.TestCase):
    def journey_text(self):
        labels = ["Attend G.A. Meeting", "Go to Rehabilitation", "Go to Work  (locked)",
                  "Exercise", "Practice programming", "Rest", "Check Status",
                  "Return to Main Menu", "Save Game", "End the day", "Finances",
                  "Safeguards", "Recovery story", "I relapsed today"]
        menu = "\n".join(f"{i}. {l}" for i, l in enumerate(labels, 1))
        return ("\n\n=================================\n"
                "          YOUR JOURNEY\n"
                "=================================\n\n"
                "Your real Recovery Days: 106\nThursday, 08:00\n\n" + menu + "\n")

    def test_journey_menu_becomes_tiles(self):
        s = build_screen(self.journey_text(), "Choose an option: ")
        self.assertEqual(s.mode, "buttons")
        self.assertEqual(len(s.options), 14)
        self.assertEqual(s.banner, "journey")
        self.assertTrue(s.options[2].locked)
        self.assertEqual(s.options[2].label, "Go to Work")
        self.assertEqual(s.lines, ["Your real Recovery Days: 106", "Thursday, 08:00"])

    def test_header_picks_banner_and_is_hidden_from_log(self):
        s = build_screen("\n\n=====\n          WORK\n=====\n\nYou went to work today.\n",
                         "Press Enter to continue...")
        self.assertEqual((s.mode, s.banner), ("continue", "work"))
        self.assertEqual(s.lines, ["You went to work today."])

    def test_yes_no(self):
        s = build_screen("You are recovering from: Gambling\n", "Keep this list? (1 = yes, 2 = no): ")
        self.assertEqual(s.mode, "yesno")
        self.assertIn("Keep this list?", s.lines[-1])

    def test_number_and_text(self):
        self.assertEqual(build_screen("", "How much money do you currently have? ").mode, "number")
        self.assertEqual(build_screen("", "Daily limit in € (0 = no limit): ").mode, "number")
        self.assertEqual(build_screen("", "What shall we call you on this journey? ").mode, "text")

    def test_multiselect_checks(self):
        text = ("\nWhich addictions are you recovering from?\n"
                "1. Gambling [x]\n2. Alcohol   \n3. Substances [x]\n4. Internet and games   \n5. Done\n")
        s = build_screen(strip_emoji(text.replace("[x]", "✅")), "Choose an option: ")
        self.assertEqual([o.checked for o in s.options], [True, False, True, False, False])
        self.assertEqual(s.options[0].label, "Gambling")

    def test_emoji_stand_ins(self):
        self.assertIn("[x]", strip_emoji("Gambling ✅"))
        self.assertIn("(locked)", strip_emoji("Work 🔒"))

    def test_icon_lookup(self):
        for label, key in [("Attend G.A. Meeting", "ga"), ("Go to Work", "work"),
                           ("Practice programming", "programming"), ("Return to Main Menu", "back"),
                           ("End the day", "endday"), ("I relapsed today", "relapse"),
                           ("Load Journey", "load"), ("Groceries and essentials (€10)", None)]:
            self.assertEqual(icon_for(label), key, label)
        for key in {icon_for(l) for l in ["Attend G.A. Meeting", "Go to Work", "Exit", "Save Game"]}:
            self.assertTrue(os.path.exists(os.path.join(ROOT, "assets", "icons", f"{key}.png")), key)

    def test_all_banners_and_icons_exist(self):
        from ui_logic import TITLE_BANNERS, ICON_RULES
        for key in set(TITLE_BANNERS.values()) | {"journey"}:
            self.assertTrue(os.path.exists(os.path.join(ROOT, "assets", "banners", f"{key}.png")), key)
        for _, key in ICON_RULES:
            self.assertTrue(os.path.exists(os.path.join(ROOT, "assets", "icons", f"{key}.png")), key)


# ---------------------------------------------------------------- fake Kivy
class Stub:
    def __init__(self, *a, **k):
        self.children = []
        self.kw = k
        for key, val in k.items():
            try:
                object.__setattr__(self, key, val)
            except Exception:
                pass
        self.width = 400
        self.height = 800
        self.state = "normal"

    def add_widget(self, w):
        self.children.append(w)

    def clear_widgets(self):
        self.children = []

    def bind(self, **k):
        self.bound = getattr(self, "bound", {})
        self.bound.update(k)

    def setter(self, name):
        return lambda *a: None

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return Stub()

    def __call__(self, *a, **k):
        return Stub()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def install_kivy_stubs():
    names = ["kivy", "kivy.app", "kivy.clock", "kivy.core", "kivy.core.window",
             "kivy.graphics", "kivy.metrics", "kivy.uix", "kivy.uix.behaviors",
             "kivy.uix.boxlayout", "kivy.uix.button", "kivy.uix.gridlayout",
             "kivy.uix.image", "kivy.uix.label", "kivy.uix.scrollview",
             "kivy.uix.textinput"]
    for n in names:
        sys.modules[n] = types.ModuleType(n)

    class App(Stub):
        def run(self):
            pass

    class Clock:
        @staticmethod
        def schedule_once(fn, timeout=0):
            fn(0)

    win = Stub()
    win.height = 800
    sys.modules["kivy.app"].App = App
    sys.modules["kivy.clock"].Clock = Clock
    sys.modules["kivy.core.window"].Window = win
    sys.modules["kivy.graphics"].Color = Stub
    sys.modules["kivy.graphics"].RoundedRectangle = Stub
    sys.modules["kivy.metrics"].dp = lambda v: v
    sys.modules["kivy.uix.behaviors"].ButtonBehavior = type("ButtonBehavior", (), {})
    for mod, cls in [("boxlayout", "BoxLayout"), ("button", "Button"), ("gridlayout", "GridLayout"),
                     ("image", "Image"), ("label", "Label"), ("scrollview", "ScrollView"),
                     ("textinput", "TextInput")]:
        setattr(sys.modules[f"kivy.uix.{mod}"], cls, type(cls, (Stub,), {}))


class TestAppThroughUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        install_kivy_stubs()
        sys.modules.pop("main", None)
        import main
        cls.main = main

    def setUp(self):
        self._old = os.getcwd()
        self.tmp = tempfile.mkdtemp()
        self.app = self.main.RecoveryQuestApp()
        self.app.user_data_dir = self.tmp
        self.app.build()
        self.app.on_start()

    def tearDown(self):
        self.app.bridge.uninstall()
        os.chdir(self._old)

    def wait_for_screen(self, after):
        for _ in range(400):
            if self.app.screen_count > after:
                return self.app.screen
            time.sleep(0.01)
        self.fail("the game never asked anything new")

    def step(self, value):
        before = self.app.screen_count
        self.app.choose(value)
        return self.wait_for_screen(before)

    def tap(self, text):
        for opt in self.app.screen.options:
            if text.lower() in opt.label.lower():
                return self.step(opt.number)
        self.fail(f"no tile containing {text!r}: {self.app.screen.options}")

    def start_new_game(self, addiction="Gambling"):
        self.wait_for_screen(0)
        self.tap("Start Journey")
        self.step("Pero"); self.step("10"); self.step("100"); self.step("0")
        self.tap(addiction)
        s = self.tap("Done")
        while s.mode == "continue":
            s = self.step("")
        return s

    def money(self):
        s = self.tap("Check Status")
        line = [l for l in s.lines if l.startswith("Money")][0]
        return int(line.split("€")[1])

    def test_play_through_touch_only(self):
        s = self.wait_for_screen(0)
        self.assertEqual((s.mode, s.banner), ("buttons", "title"))
        self.assertEqual([o.label for o in s.options][:2], ["Start Journey", "Load Journey"])
        s = self.tap("Start Journey")
        self.assertEqual(s.mode, "text")                          # name
        s = self.step("Pero")
        self.assertEqual(s.mode, "number")                        # recovery days
        self.step("106"); self.step("100"); s = self.step("1300")
        self.assertEqual(s.mode, "buttons")                       # pick addictions
        s = self.tap("Gambling")
        self.assertTrue(s.options[0].checked)
        s = self.tap("Done")
        self.assertEqual((s.mode, s.banner, len(s.options)), ("buttons", "status", 14))
        s = self.tap("Rest")                                      # a picture screen
        self.assertEqual((s.mode, s.banner), ("continue", "rest"))
        s = self.step("")
        self.assertEqual(s.banner, "journey")

    def test_work_tile_pays_money_and_shows_banner(self):
        self.start_new_game("Alcohol")
        before = self.money()
        s = self.tap("Go to Work")
        self.assertEqual((s.mode, s.banner), ("continue", "work"))
        self.step("")
        self.assertGreaterEqual(self.money() - before, 60)

    def test_locked_tile_is_marked_and_refused(self):
        self.start_new_game("Gambling")
        # enter closed rehab: keep list, closed, 7 days, exclusion no, protected rule no
        s = self.tap("Go to Rehabilitation")
        self.assertEqual(s.mode, "yesno")
        s = self.step("1")
        s = self.tap("Closed")
        s = self.tap("7 days")
        self.assertEqual(s.mode, "yesno")                        # exclusion?
        s = self.step("2")
        self.assertEqual(s.mode, "yesno")                        # protected money rule?
        s = self.step("2")
        self.assertEqual(s.mode, "continue")
        s = self.step("")
        work = [o for o in s.options if o.label == "Go to Work"][0]
        self.assertTrue(work.locked)
        s = self.tap("Go to Work")                               # refused, game keeps going
        self.assertIn("closed rehabilitation", s.text.lower())
        self.assertEqual(s.mode, "buttons")


if __name__ == "__main__":
    unittest.main()
