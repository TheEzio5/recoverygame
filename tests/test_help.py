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
        for n in (1, 6):
            self.assertEqual(help_support.interpret(n)[0], "Some signs came up")
        for n in (7, 12, 20):
            title, lines = help_support.interpret(n)
            self.assertEqual(title, "Help is there")
            self.assertIn("not a diagnosis", " ".join(lines))
            self.assertIn("reach out today", " ".join(lines))

    def test_threshold_is_the_gamblers_anonymous_seven(self):
        self.assertEqual(help_support.HIGH_THRESHOLD, 7)

    def test_twenty_unique_questions(self):
        qs = help_support.SELF_CHECK_QUESTIONS
        self.assertEqual(len(qs), 20)
        self.assertEqual(len(set(qs)), 20)
        self.assertTrue(all(q.endswith("?") for q in qs))

    def run_check(self, answers, extra=()):
        return feed(help_support.self_check, list(answers) + list(extra))

    def test_all_no(self):
        yes, text = self.run_check(["2"] * 20, [""])
        self.assertEqual(yes, 0)
        self.assertIn("No signs came up", text)

    def test_seven_yes_shows_help_text_and_the_right_next_steps(self):
        yes, text = self.run_check(["1"] * 7 + ["2"] * 13, ["1", "", "2"])
        self.assertEqual(yes, 7)
        self.assertIn("Help is there", text)
        self.assertIn("Go to Gamblers Anonymous: https://gamblersanonymous.org", text)
        self.assertIn("HOW REHAB CAN HELP", text)
        self.assertIn("emergency number", text)

    def test_six_yes_is_below_the_line(self):
        yes, text = self.run_check(["1"] * 6 + ["2"] * 14, [""])
        self.assertEqual(yes, 6)
        self.assertIn("Some signs came up", text)
        self.assertNotIn("HOW REHAB CAN HELP", text)

    def test_official_20_questions_link_is_offered(self):
        _, text = self.run_check(["2"] * 20, [""])
        self.assertIn("https://gamblersanonymous.org/20questions.html", text)

    def test_hopeless_answer_gets_an_immediate_caring_message(self):
        # only the last question answered yes
        yes, text = self.run_check(["2"] * 19 + ["1"], ["", ""])
        self.assertEqual(yes, 1)
        self.assertIn("Please reach out to someone right now", text)
        self.assertIn("988", text)

    def test_nothing_is_saved(self):
        p = Player("T", 5)
        before = dict(vars(p))
        self.run_check(["1"] * 20, ["", "2"])
        self.assertEqual(dict(vars(p)), before)


class TestGamblingSupportPage(unittest.TestCase):
    def test_page_links_and_rehab_info(self):
        _, text = feed(help_support.gambling_support_page, ["1", "", "2"])
        self.assertIn("SUPPORT FOR GAMBLING", text)
        self.assertIn("Go to Gamblers Anonymous: https://gamblersanonymous.org", text)
        self.assertIn("HOW REHAB CAN HELP", text)
        self.assertIn("Therapy", text.title().replace("Talking Therapy", "Therapy"))

    def test_only_when_gambling_is_newly_chosen(self):
        self.assertFalse(help_support.offer_gambling_support([], ["alcohol"]))
        self.assertFalse(help_support.offer_gambling_support(["gambling"], ["gambling", "alcohol"]))
        shown, text = feed(help_support.offer_gambling_support, ["2"], [], ["gambling"])
        self.assertTrue(shown)
        self.assertIn("SUPPORT FOR GAMBLING", text)

    def test_new_game_with_gambling_shows_it(self):
        script = ["1", "T", "5", "0", "0", "1", "5", "2", "8", "4"]
        _, text = feed(recovery_main.main, script)
        self.assertIn("SUPPORT FOR GAMBLING", text)

    def test_new_game_with_alcohol_does_not(self):
        script = ["1", "T", "5", "0", "0", "2", "5", "8", "4"]
        _, text = feed(recovery_main.main, script)
        self.assertNotIn("SUPPORT FOR GAMBLING", text)


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
