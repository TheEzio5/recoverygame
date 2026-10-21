import json

from datetime import date
from player import Player

def save_game(player):
    save_file = "player_save.json"
    data = {
        "name": player.name,
        "recovery_days": player.recovery_days,
        "level": player.level,
        "willpower": player.willpower,
        "hope": player.hope,
        "energy": player.energy,
        "confidence": player.confidence,
        "urge": player.urge,
        "experience": player.experience,
        "journey_days": player.journey_days,
        "last_played": str(date.today()),
        "money": player.money,
        "debt": player.debt
    }

    with open(save_file, "w") as file:
        json.dump(data, file, indent=4)


def load_game():

    save_file = "player_save.json"

    with open(save_file, "r") as file:
        data = json.load(file)

    player = Player(
        data["name"],
        data["recovery_days"]
    )

    player.level = data["level"]
    player.journey_days = data["journey_days"]
    player.willpower = data["willpower"]
    player.hope = data["hope"]
    player.energy = data["energy"]
    player.confidence = data["confidence"]
    player.urge = data["urge"]
    player.experience = data["experience"]
    player.money = data["money"]
    player.debt = data["debt"]


    today = date.today()
    last_played = date.fromisoformat(data["last_played"])

    days_passed = (today - last_played).days

    #print(today)
    #print(last_played)
    #print(days_passed)

    if days_passed > 0:
        print()
        print(f"Welcome back, {player.name}!")
        print()
        print(f"{days_passed} real day{'s' if days_passed != 1 else ''} have passed.")
        print("Your recovery continues.")
        print()
        player.recovery_days += days_passed
        player.journey_days += days_passed
        save_game(player)


    return player