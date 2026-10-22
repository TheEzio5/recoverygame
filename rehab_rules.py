"""All restrictions live here, so main.py never needs scattered if-statements.
These are the GAME's simulation rules, not universal medical rules."""
import random

from constants import (DAY_END_HOUR, LAPTOP_FROM, LAPTOP_UNTIL, ADDICTIONS)

#this is rehab_rules.py

# hours each activity takes
DURATION = {
    "ga": 2,
    "rehab": 2,
    "work": 8,
    "exercise": 2,
    "programming": 3,
    "rest": 3,
}

# energy needed to start
MIN_ENERGY = {"work": 15, "exercise": 10, "programming": 10}


def in_closed_rehab(player):
    return player.in_rehabilitation and player.rehab_section == "closed"


def laptop_available(hour):
    return LAPTOP_FROM <= hour < LAPTOP_UNTIL


def is_outing_time(weekday, hour):
    """Closed section: weekdays 18-20, weekends 10-12 and 18-20."""
    if weekday < 5:
        return 18 <= hour < 20
    return 10 <= hour < 12 or 18 <= hour < 20


def can_do(player, key):
    """Returns (allowed, reason). The journey menu REFUSES when not allowed."""
    if key == "rehab" and not player.in_rehabilitation:
        return False, "You are not in a rehabilitation program."

    if in_closed_rehab(player):
        if key == "work":
            return False, "You can't go to work while you are in closed rehabilitation."
        if key == "programming":
            end = player.hour + DURATION["programming"]
            if not laptop_available(player.hour) or end > LAPTOP_UNTIL:
                return False, (f"Your laptop is handed in at {LAPTOP_UNTIL}:00 and returned "
                               f"at {LAPTOP_FROM:02d}:00. It's {player.clock_text} now, "
                               "and a session needs 3 hours with the laptop.")

    if player.hour + DURATION[key] > DAY_END_HOUR:
        return False, "There isn't enough of the day left for that. Maybe it's time to end the day."

    needed = MIN_ENERGY.get(key)
    if needed and player.energy < needed:
        return False, "You're too tired for that. Try resting or ending the day to sleep."

    return True, ""


def end_of_day_urge(player):
    """Urge drift overnight. Closed section calms it; exposure raises it."""
    if in_closed_rehab(player):
        player.urge -= 2
        return "The structure of the program keeps you steady. 🔥 Urge -2"

    total = 0
    for addiction in player.addictions:
        chance = 0.4
        if addiction == "gambling" and player.safeguards.get("gambling_exclusion"):
            chance = 0.15      # protections help, they don't make it impossible
        if random.random() < chance:
            total += random.randint(1, 3)

    player.urge += total
    if total:
        return f"Triggers are around in everyday life. 🔥 Urge +{total}"
    return ""
