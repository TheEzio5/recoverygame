"""Run from the project folder:  python -m unittest discover -s tests -v"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import day
import finances
import rehab_rules
import recovery_main
from addictions import choose_addictions
from player import Player
from relapse import log_relapse
from safeguards import safeguards_menu
from save import save_game, load_game


def feed(func, answers, *args):
    """Run func with scripted input(); returns (result, printed text)."""
    out = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(answers)), \
            contextlib.redirect_stdout(out):
        result = func(*args)
    return result, out.getvalue()


def read_save():
    with open("player_save.json") as f:
        return json.load(f)


def write_save(data):
    with open("player_save.json", "w") as f:
        json.dump(data, f)


class InTempDir(unittest.TestCase):
    def setUp(self):
        self._old = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)

    def tearDown(self):
        os.chdir(self._old)
        self._tmp.cleanup()


class TestAddictions(unittest.TestCase):
    def test_multiple_selection_and_toggle(self):
        result, _ = feed(choose_addictions, ["1", "3", "5"])
        self.assertEqual(result, ["gambling", "substances"])
        result, _ = feed(choose_addictions, ["1", "2", "2", "5"])
        self.assertEqual(result, ["gambling"])

    def test_done_needs_a_choice(self):
        result, text = feed(choose_addictions, ["5", "4", "5"])
        self.assertEqual(result, ["internet_games"])
        self.assertIn("at least one", text)


class TestRules(unittest.TestCase):
    def closed(self):
        p = Player("T", 10)
        p.in_rehabilitation, p.rehab_section, p.rehab_days_remaining = True, "closed", 14
        return p

    def test_closed_blocks_work_open_allows_it(self):
        p = self.closed()
        self.assertFalse(rehab_rules.can_do(p, "work")[0])
        p.rehab_section = "open"
        self.assertTrue(rehab_rules.can_do(p, "work")[0])

    def test_laptop_hours_in_closed(self):
        p = self.closed()
        p.hour = 8
        self.assertFalse(rehab_rules.can_do(p, "programming")[0])
        p.hour = 9
        self.assertTrue(rehab_rules.can_do(p, "programming")[0])
        p.hour = 19   # 19 + 3h would run past 21:00
        self.assertFalse(rehab_rules.can_do(p, "programming")[0])

    def test_outing_windows(self):
        self.assertTrue(rehab_rules.is_outing_time(0, 18))     # Monday
        self.assertFalse(rehab_rules.is_outing_time(0, 10))
        self.assertTrue(rehab_rules.is_outing_time(5, 10))     # Saturday
        self.assertTrue(rehab_rules.is_outing_time(6, 19))
        self.assertFalse(rehab_rules.is_outing_time(6, 14))

    def test_energy_and_time_left(self):
        p = Player("T", 1)
        p.energy = 5
        self.assertFalse(rehab_rules.can_do(p, "work")[0])
        p.energy, p.hour = 80, 20
        self.assertFalse(rehab_rules.can_do(p, "work")[0])     # 8h won't fit


class TestDayAndRehab(InTempDir):
    def test_countdown_and_completion(self):
        p = Player("T", 10)
        p.in_rehabilitation, p.rehab_section, p.rehab_days_remaining = True, "closed", 2
        p.journey_days = 1
        feed(day.end_day, [""], p)
        self.assertEqual((p.journey_days, p.rehab_days_remaining), (2, 1))
        self.assertTrue(p.in_rehabilitation)
        feed(day.end_day, [""], p)
        self.assertFalse(p.in_rehabilitation)
        self.assertEqual(p.rehabs_completed, 1)
        self.assertIsNone(p.rehab_section)
        self.assertEqual(p.hour, 8)

    def test_activity_pushing_past_midnight_ends_day(self):
        p = Player("T", 10)
        p.hour = 22
        feed(day.spend_time, [""], p, 2)
        self.assertEqual((p.journey_days, p.hour), (2, 8))

    def test_new_day_resets_spending(self):
        p = Player("T", 10)
        p.spent_today = 4
        feed(day.end_day, [""], p)
        self.assertEqual(p.spent_today, 0)


class TestFinances(unittest.TestCase):
    def test_debt_payment_caps_and_tracks(self):
        p = Player("T", 10)
        p.money, p.debt = 500, 120
        feed(finances.pay_debt, ["300"], p)      # more than owed -> capped at 120
        self.assertEqual((p.money, p.debt, p.debt_repaid), (380, 0, 120))

    def test_not_enough_money(self):
        p = Player("T", 10)
        p.money, p.debt = 20, 100
        _, text = feed(finances.pay_debt, ["50"], p)
        self.assertEqual((p.money, p.debt), (20, 100))
        self.assertIn("enough money", text)

    def test_banking_restriction_blocks_payments(self):
        p = Player("T", 10)
        p.money, p.debt = 100, 100
        p.safeguards["banking_restricted"] = True
        _, text = feed(finances.pay_debt, [], p)
        self.assertEqual((p.money, p.debt), (100, 100))
        self.assertIn("restricted", text)
        feed(finances.send_money, [], p)
        self.assertEqual(p.money, 100)

    def test_daily_limit(self):
        p = Player("T", 10)
        p.money = 100
        p.safeguards["daily_limit"] = 4
        _, text = feed(finances.pay_expense, ["1"], p)   # groceries cost 10
        self.assertEqual(p.money, 100)
        self.assertIn("daily spending limit", text)


class TestSafeguardsLock(unittest.TestCase):
    def test_cannot_switch_off_in_closed_rehab(self):
        p = Player("T", 10)
        p.in_rehabilitation, p.rehab_section = True, "closed"
        p.safeguards.update(gambling_exclusion=True, banking_restricted=True, daily_limit=4)
        feed(safeguards_menu, ["1", "2", "3", "0", "3", "9", "4"], p)
        self.assertTrue(p.safeguards["gambling_exclusion"])
        self.assertTrue(p.safeguards["banking_restricted"])
        self.assertEqual(p.safeguards["daily_limit"], 4)

    def test_free_toggle_outside_rehab(self):
        p = Player("T", 10)
        feed(safeguards_menu, ["1", "3", "20", "4"], p)
        self.assertTrue(p.safeguards["gambling_exclusion"])
        self.assertEqual(p.safeguards["daily_limit"], 20)


class TestRelapse(unittest.TestCase):
    def test_relapse_resets_streak_keeps_journey(self):
        p = Player("T", 40)
        p.journey_days, p.debt = 12, 1000
        p.addictions = ["gambling"]
        feed(log_relapse, ["1", "1", "250", ""], p)
        self.assertEqual(p.recovery_days, 0)
        self.assertEqual(p.longest_streak, 40)
        self.assertEqual(p.journey_days, 12)
        self.assertEqual((p.debt, p.total_relapse_debt, p.relapses), (1250, 250, 1))
        self.assertEqual(p.relapse_history[0]["streak_before"], 40)

    def test_declining_changes_nothing(self):
        p = Player("T", 40)
        feed(log_relapse, ["2"], p)
        self.assertEqual((p.recovery_days, p.relapses), (40, 0))

    def test_no_debt_question_for_alcohol(self):
        p = Player("T", 5)
        p.addictions = ["alcohol"]
        feed(log_relapse, ["1", "1", ""], p)          # no debt prompt consumed
        self.assertEqual((p.debt, p.relapses), (0, 1))


class TestSaveLoad(InTempDir):
    def test_roundtrip_all_new_fields(self):
        p = Player("T", 30)
        p.addictions = ["gambling", "alcohol"]
        p.in_rehabilitation, p.rehab_section, p.rehab_days_remaining = True, "closed", 9
        p.safeguards.update(banking_restricted=True, daily_limit=4)
        p.hour, p.money, p.debt, p.relapses = 15, 55, 900, 2
        save_game(p)
        q = load_game()
        for field in ("addictions", "in_rehabilitation", "rehab_section",
                      "rehab_days_remaining", "safeguards", "hour", "money",
                      "debt", "relapses", "next_level", "start_weekday"):
            self.assertEqual(getattr(q, field), getattr(p, field), field)

    def test_same_day_loads_do_not_advance(self):
        p = Player("T", 30)
        p.journey_days = 5
        save_game(p)
        for _ in range(3):
            q = load_game()
            save_game(q)
        self.assertEqual((q.recovery_days, q.journey_days), (30, 5))

    def test_real_days_only_advance_recovery(self):
        p = Player("T", 6)
        p.journey_days = 5
        save_game(p)
        data = read_save()
        data["last_played"] = str(date.today() - timedelta(days=2))
        write_save(data)
        q, text = feed(load_game, [])
        self.assertEqual((q.recovery_days, q.journey_days), (8, 5))
        self.assertIn("Milestone reached: 7", text)
        self.assertIn("2 real days", text)
        # loading again right away adds nothing more
        q2, _ = feed(load_game, [])
        self.assertEqual(q2.recovery_days, 8)

    def test_clock_set_backwards_is_handled(self):
        p = Player("T", 30)
        save_game(p)
        data = read_save()
        data["last_played"] = str(date.today() + timedelta(days=3))
        write_save(data)
        q, text = feed(load_game, [])
        self.assertEqual(q.recovery_days, 30)
        self.assertIn("earlier than your last save", text)

    def test_old_save_file_without_new_fields(self):
        old = {"name": "Test", "recovery_days": 106, "level": 3, "willpower": 50,
               "hope": 50, "energy": 50, "confidence": 50, "urge": 50,
               "experience": 0, "journey_days": 8, "last_played": str(date.today()),
               "money": 100, "debt": 1300}
        write_save(old)
        q = load_game()
        self.assertEqual((q.name, q.debt, q.addictions, q.next_level), ("Test", 1300, [], 300))
        self.assertEqual(q.safeguards["daily_limit"], None)
        self.assertEqual(q.longest_streak, 106)
        self.assertIn(90, q.current_milestones)


class TestPlaythrough(InTempDir):
    def test_full_game_with_rehab_and_rules(self):
        script = [
            "1", "Pero", "x", "106", "100", "1300",      # new game (bad number first)
            "1", "3", "5",                                 # gambling + substances
            "2",                                           # Go to Rehabilitation
            "1",                                           # keep list? yes
            "2", "2",                                      # closed, 14 days
            "1",                                           # register exclusion
            "1",                                           # protected money rule
            "",                                            # enter
            "3",                                           # try Work -> refused
            "5",                                           # programming at 08:00 -> refused
            "10", "",                                      # end day -> 09:00
            "5", "", "",                                   # programming ok (+Enter after)
            "2", "1", "",                                  # rehab therapy session
            "11", "1", "50", "4",                          # finances: banking blocked
            "9",                                           # save + return
            "3",                                           # exit
        ]
        # wrap: 'keep this list?' is yes -> "1", so script above is consistent
        result, text = feed(recovery_main.main, script)
        self.assertIn("CLOSED rehabilitation", text)
        self.assertIn("can't go to work", text)
        self.assertIn("laptop is handed in", text)
        self.assertIn("Banking apps are restricted", text)
        self.assertIn("Game saved", text)
        q = load_game()
        self.assertTrue(q.in_rehabilitation)
        self.assertEqual(q.rehab_days_remaining, 13)
        self.assertEqual(q.addictions, ["gambling", "substances"])
        self.assertEqual(q.safeguards["daily_limit"], 4)
        self.assertEqual(q.money, 100)          # work never ran, so no pay


class TestScreenCrashIsContained(unittest.TestCase):
    def test_broken_screen_does_not_end_the_game(self):
        p = Player("T", 10)
        with mock.patch.object(recovery_main, "show_history",
                               side_effect=RuntimeError("boom")):
            _, text = feed(recovery_main.journey, ["13", "8"], p)
        self.assertIn("Something went wrong", text)
        self.assertIn("Returning to main menu", text)


class TestWorkPays(unittest.TestCase):
    def test_work_adds_money_in_open_life(self):
        p = Player("T", 10)
        p.money = 0
        feed(recovery_main.run_activity, [""], p, "work", recovery_main.go_to_work)
        self.assertGreaterEqual(p.money, 60)
        self.assertEqual(p.hour, 16)             # 8 hours passed


if __name__ == "__main__":
    unittest.main()
