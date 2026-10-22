from constants import WIDTH

#this is utils.py


def ask_int(prompt, minimum=0):
    """Keep asking until the player types a whole number >= minimum."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a number.")
            continue
        if value < minimum:
            print(f"Please enter {minimum} or higher.")
            continue
        return value


def ask_yes_no(question):
    while True:
        answer = input(f"{question} (1 = yes, 2 = no): ").strip()
        if answer == "1":
            return True
        if answer == "2":
            return False
        print("Please choose 1 or 2.")


def apply_rewards(player, rewards):

    player.confidence += rewards.get("confidence", 0)
    player.energy += rewards.get("energy", 0)
    player.experience += rewards.get("experience", 0)
    player.hope += rewards.get("hope", 0)
    player.urge += rewards.get("urge", 0)
    player.willpower += rewards.get("willpower", 0)
    player.money += rewards.get("money", 0)

    player.level_up()

    player.clamp_stats()

    return player


def show_rewards(title, rewards):
    print()
    print(title)
    print("-" * WIDTH)

    for stat, value in rewards.items():
        if stat == "energy":
            print(f"⚡ Energy {value:+}")
        elif stat == "confidence":
            print(f"💪 Confidence {value:+}")
        elif stat == "experience":
            print(f"📚 Experience {value:+}")
        elif stat == "hope":
            print(f"🌅 Hope {value:+}")
        elif stat == "urge":
            print(f"🔥 Urge {value:+}")
        elif stat == "willpower":
            print(f"❤️ Willpower {value:+}")
        elif stat == "money":
            print(f"💰 Money {value:+} €")
