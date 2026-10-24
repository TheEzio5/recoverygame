import json

from datetime import date
from player import Player
from constants import MILESTONES

#this is save.py

SAVE_FILE = "player_save.json"

# every simple field that is stored as-is
FIELDS = [
    "level", "journey_days", "willpower", "hope", "energy", "confidence",
    "urge", "experience", "next_level", "money", "debt",
    "hour", "start_weekday", "spent_today",
    "addictions", "in_rehabilitation", "rehab_program", "rehab_section",
    "rehab_days_remaining", "safeguards",
    "longest_streak", "relapses", "relapse_history", "total_relapse_debt",
    "debt_repaid", "sent_to_loved_ones", "meetings_attended",
    "rehabs_completed", "milestone_log", "current_milestones",
]


def save_game(player):
    data = {
        "name": player.name,
        "recovery_days": player.recovery_days,
        "last_played": str(date.today()),
    }
    for field in FIELDS:
        data[field] = getattr(player, field)

    with open(SAVE_FILE, "w") as file:
        json.dump(data, file, indent=4)


def load_game():

    with open(SAVE_FILE, "r") as file:
        data = json.load(file)

    player = Player(data["name"], data["recovery_days"])

    # Older saves miss new fields: keep the Player() defaults for those.
    for field in FIELDS:
        if field in data:
            if field == "safeguards":
                player.safeguards.update(data[field])
            else:
                setattr(player, field, data[field])

    if "next_level" not in data:
        player.next_level = 100 * player.level
    if "start_weekday" not in data:
        player.start_weekday = (date.today().weekday() - (player.journey_days - 1)) % 7
    if "current_milestones" not in data:
        player.current_milestones = [m for m in MILESTONES if m <= player.recovery_days]
    if "longest_streak" not in data:
        player.longest_streak = player.recovery_days
    player.longest_streak = max(player.longest_streak, player.recovery_days)

    today = date.today()
    try:
        last_played = date.fromisoformat(data["last_played"])
    except (KeyError, ValueError):
        last_played = today

    days_passed = (today - last_played).days

    if days_passed > 0:
        # Real days advance the recovery streak only. In-game journey days
        # advance when you actually play through a day.
        print()
        print(f"{days_passed} real day{'s' if days_passed != 1 else ''} have passed.")
        print("Your recovery continues.")
        player.add_recovery_days(days_passed)
        print()
        save_game(player)

    elif days_passed < 0:
        print()
        print("Your device date is earlier than your last save.")
        print("No days were added. Please check your date settings.")

    return player
