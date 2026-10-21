
from constants import WIDTH

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
        self.experience =  0
        self.urge = 50
        self.next_level = 100
        self.money = 0
        self.debt = 0
        self.in_rehabilitation = False
        self.rehab_program = None
        self.rehab_section = None
        self.rehab_days_remaining = 0
        self.addictions = []


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
        print(f"💰 Money: €{self.money}")
        print(f"💳 Debt: €{self.debt}")

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

    def clamp_stats(self):
        self.energy =max(0, min(100, self.energy))
        self.willpower =max(0, min(100, self.willpower))
        self.confidence = max(0, min(100, self.confidence))
        self.hope = max(0, min(100, self.hope))
        self.urge = max(0, min(100, self.urge))
