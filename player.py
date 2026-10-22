from datetime import date

from constants import (WIDTH, ADDICTIONS, DAY_START_HOUR, WEEKDAYS, MILESTONES)

#this is player.py


class Player:
    def __init__(self, name, recovery_days):
        self.name = name
        self.level = 1
        self.journey_days = 1
        self.recovery_days = recovery_days
        self.willpower = 50
        self.hope = 50
        self.energy = 50
        self.confidence = 50
        self.experience = 0
        self.urge = 50
        self.next_level = 100
        self.money = 0
        self.debt = 0

        # in-game clock
        self.hour = DAY_START_HOUR
        self.start_weekday = date.today().weekday()

        # addictions (one or more) and rehabilitation state
        self.addictions = []
        self.in_rehabilitation = False
        self.rehab_program = None
        self.rehab_section = None          # "open" / "closed"
        self.rehab_days_remaining = 0

        # safeguards the player has chosen (they really change gameplay)
        self.safeguards = {
            "gambling_exclusion": False,
            "banking_restricted": False,
            "daily_limit": None,           # euro per in-game day, or None
        }
        self.spent_today = 0

        # recovery history
        self.longest_streak = recovery_days
        self.relapses = 0
        self.relapse_history = []
        self.total_relapse_debt = 0
        self.debt_repaid = 0
        self.sent_to_loved_ones = 0
        self.meetings_attended = 0
        self.rehabs_completed = 0
        self.milestone_log = []
        self.current_milestones = [m for m in MILESTONES if m <= recovery_days]

    # ---------- clock ----------
    @property
    def weekday(self):
        """0 = Monday ... 6 = Sunday, follows the in-game journey day."""
        return (self.start_weekday + self.journey_days - 1) % 7

    @property
    def weekday_name(self):
        return WEEKDAYS[self.weekday]

    @property
    def clock_text(self):
        return f"{self.hour:02d}:00"

    def addiction_names(self):
        return ", ".join(ADDICTIONS.get(a, a) for a in self.addictions) or "none chosen"

    # ---------- display ----------
    def show_status(self):
        print()
        print()

        print("=" * WIDTH)
        print("PLAYER STATUS".center(WIDTH))
        print("=" * WIDTH)
        print()

        print(f"👤 Name: {self.name}")
        print(f"⭐ Level: {self.level}")
        print(f"📅 Your real Recovery Days: {self.recovery_days}")
        print(f"🗺️ Your ingame Journey Days: {self.journey_days}")
        print(f"🕒 {self.weekday_name}, {self.clock_text}")
        print(f"💰 Money: €{self.money}")
        print(f"💳 Debt: €{self.debt}")
        print(f"🧩 Recovering from: {self.addiction_names()}")
        if self.in_rehabilitation:
            print(f"🏥 {self.rehab_section.capitalize()} rehabilitation, "
                  f"{self.rehab_days_remaining} day(s) left")

        print()
        print(f"❤️ Willpower: {self.willpower}")
        print(f"🌅 Hope: {self.hope}")
        print(f"⚡ Energy: {self.energy}")
        print(f"💪 Confidence: {self.confidence}")
        print(f"📚 Experience: {self.experience}/{self.next_level}")
        print(f"🔥 Urge: {self.urge}")

        print()
        print()
        print("=" * WIDTH)

    def show_recovery_message(self):

        if self.recovery_days < 30:
            print("Every day matters.")
            print("Stay close to your recovery.")

        elif self.recovery_days < 90:
            print("You're building a strong foundation.")
            print("Keep coming back.")

        elif self.recovery_days < 365:
            print("Recovery is becoming a way of life.")
            print("One day at a time.")
        else:
            print("One year or more.")
            print("Your journey can inspire someone else today.")

    # ---------- stats ----------
    def level_up(self):

        while self.experience >= self.next_level:
            self.experience -= self.next_level
            self.level += 1

            self.willpower += 5
            self.energy += 5
            self.confidence += 3

            self.next_level += 100

            print()
            print("⭐ LEVEL UP!")
            print(f"You reached Level {self.level}!")
            print("You feel stronger.")
            print()

        self.clamp_stats()

    def clamp_stats(self):
        self.energy = max(0, min(100, self.energy))
        self.willpower = max(0, min(100, self.willpower))
        self.confidence = max(0, min(100, self.confidence))
        self.hope = max(0, min(100, self.hope))
        self.urge = max(0, min(100, self.urge))
        self.experience = max(0, self.experience)
        self.money = max(0, self.money)
        self.debt = max(0, self.debt)

    # ---------- recovery days, milestones, relapse ----------
    def add_recovery_days(self, days):
        """Real calendar days passed. Updates streak and announces milestones."""
        self.recovery_days += days
        self.longest_streak = max(self.longest_streak, self.recovery_days)

        for milestone in MILESTONES:
            if milestone <= self.recovery_days and milestone not in self.current_milestones:
                self.current_milestones.append(milestone)
                self.milestone_log.append(
                    {"days": milestone, "date": str(date.today())})
                print()
                print(f"🏅 Milestone reached: {milestone} day(s) in recovery!")

    def record_relapse(self, addiction, new_debt=0):
        """Resets the CURRENT streak only. Journey days and history are kept."""
        self.longest_streak = max(self.longest_streak, self.recovery_days)
        streak_before = self.recovery_days

        self.relapses += 1
        self.relapse_history.append({
            "date": str(date.today()),
            "journey_day": self.journey_days,
            "addiction": addiction,
            "new_debt": new_debt,
            "streak_before": streak_before,
        })

        self.total_relapse_debt += new_debt
        self.debt += new_debt          # added to existing debt, never replaced

        self.recovery_days = 0
        self.current_milestones = []

        self.hope -= 5
        self.confidence -= 5
        self.urge += 10
        self.clamp_stats()
        return streak_before
