import contextlib
import io
import os
import sys
import tempfile
import threading
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import help_support
import recovery_main
from console_io import ConsoleBridge, HELP_TOKEN
from player import Player
from save import save_game


def feed(func, answers, *args):
    out = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(answers)), \
            contextlib.redirect_stdout(out):
        result = func(*args)
    return result, out.getvalue()


class TestSelfCheck(unittest.TestCase):
    def test_interpretation_tiers(self):
        self.assertEqual(help_support.interpret(0)[0], "No signs came up")
        for n in (1, 3):
            self.assertEqual(help_support.interpret(n)[0], "Some signs came up")
        for n in (4, 7, 9):
            title, lines = help_support.interpret(n)
            self.assertEqual(title, "Many signs came up")
            self.assertIn("not a diagnosis", " ".join(lines))

    def test_nine_questions_original_wording(self):
        self.assertEqual(len(help_support.SELF_CHECK_QUESTIONS), 9)
        self.assertEqual(len(set(help_support.SELF_CHECK_QUESTIONS)), 9)

    def run_check(self, answers):
        return feed(help_support.self_check, answers + [""])

    def test_all_no(self):
        yes, text = self.run_check(["2"] * 9)
        self.assertEqual(yes, 0)
        self.assertIn("No signs came up", text)

    def test_four_yes_points_to_help(self):
        yes, text = self.run_check(["1"] * 4 + ["2"] * 5)
        self.assertEqual(yes, 4)
        self.assertIn("Many signs came up", text)
        self.assertIn("gamblersanonymous.org/20questions.html", text)
        self.assertIn("emergency number", text)

    def test_nothing_is_saved(self):
        p = Player("T", 5)
        before = dict(vars(p))
        self.run_check(["1"] * 9)
        self.assertEqual(dict(vars(p)), before)


class TestHelpMenu(unittest.TestCase):
    def test_meeting_screen_links(self):
        _, text = feed(help_support.help_session, ["2", "", "5"])
        self.assertIn("https://gamblersinrecovery.com", text)
        self.assertIn("https://gamblersanonymous.org/mtgdirTOP.html", text)
        self.assertIn("free", text.lower())

    def test_struggling_screen_has_live_meeting_and_emergency_line(self):
        _, text = feed(help_support.help_session, ["1", "", "5"])
        self.assertIn("gamblersinrecovery.com", text)
        self.assertIn("112", text)

    def test_all_links_are_https_and_known_hosts(self):
        allowed = ("gamblersinrecovery.com", "gamblersanonymous.org",
                   "www.gamblersanonymous.org.uk", "gamblingtherapy.org", "gam-anon.org")
        for name in dir(help_support):
            if name.startswith("LINK_"):
                url = getattr(help_support, name)[1]
                self.assertTrue(url.startswith("https://"), url)
                self.assertTrue(any(url.split("/")[2] == host for host in allowed), url)

    def test_reachable_from_main_and_journey_menus(self):
        _, text = feed(recovery_main.main, ["3", "5", "4"])
        self.assertIn("GET HELP NOW", text)
        self.assertIn("Goodbye", text)
        p = Player("T", 5)
        _, text = feed(recovery_main.journey, ["15", "5", "8"], p)
        self.assertIn("GET HELP NOW", text)
        self.assertIn("Returning to main menu", text)


class TestWelcomeBack(unittest.TestCase):
    def setUp(self):
        self._old = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)

    def tearDown(self):
        os.chdir(self._old)
        self._tmp.cleanup()

    def test_load_shows_name_and_motivation(self):
        save_game(Player("Pero", 40))
        _, text = feed(recovery_main.main, ["2", "", "8", "4"])
        self.assertIn("WELCOME BACK", text)
        self.assertIn("Welcome back, Pero.", text)
        self.assertTrue(any(line in text for line in recovery_main.WELCOME_LINES))
        self.assertIn("Current streak: 40", text)

    def test_new_game_has_no_welcome_back(self):
        _, text = feed(recovery_main.main, ["2", "4"])       # no save file
        self.assertNotIn("WELCOME BACK", text)


class TestBridgeHelpToken(unittest.TestCase):
    def test_help_runs_then_original_question_returns(self):
        shown = []
        helped = []

        def on_input(prompt, block):
            shown.append((prompt, block))

        bridge = ConsoleBridge(on_input, help_handler=lambda: helped.append(True))
        result = []

        def game():
            bridge.print("Menu text")
            result.append(bridge.input("Choose an option: "))

        bridge.submit(HELP_TOKEN)
        bridge.submit("2")
        t = threading.Thread(target=game)
        t.start()
        t.join(5)
        self.assertEqual(result, ["2"])
        self.assertEqual(helped, [True])
        self.assertEqual(len(shown), 2)                       # asked, helped, asked again
        self.assertEqual(shown[0], shown[1])                  # identical screen both times
        self.assertIn("Menu text", shown[1][1])

    def test_help_pressed_inside_help_is_ignored(self):
        calls = []

        def nested():
            calls.append("help")
            bridge.input("inside help: ")

        bridge = ConsoleBridge(lambda p, b: None, help_handler=nested)
        out = []
        bridge.submit(HELP_TOKEN)      # opens help
        bridge.submit(HELP_TOKEN)      # pressed again inside help
        bridge.submit("x")             # answers help's question
        bridge.submit("final")         # answers the original question
        t = threading.Thread(target=lambda: out.append(bridge.input("q: ")))
        t.start()
        t.join(5)
        self.assertEqual(out, ["final"])
        self.assertEqual(calls, ["help"])


if __name__ == "__main__":
    unittest.main()
