from constants import WIDTH

#this is utils.py

def apply_rewards(player, rewards):

    player.confidence += rewards.get("confidence", 0)
    player.energy += rewards.get("energy", 0)
    player.experience += rewards.get("experience", 0)
    player.hope += rewards.get("hope", 0)
    player.urge += rewards.get("urge", 0)

    player.level_up()

    player.clamp_stats()

    return player


def show_rewards(title,rewards):
    print()
    print(title)
    print("-" * WIDTH)

    for stat, value in rewards.items():
        if stat == "energy":
            print(f"⚡ Energy {value}")
        elif stat == "confidence":
            print(f"💪 Confidence {value:+}")
        elif stat == "experience":
            print(f"📚 Experience {value:+}")
        elif stat == "hope":
            print(f"🌅 Hope {value:+}")
        elif stat == "urge":
            print(f"🔥 Urge {value:+}")

    print()
    print("You earned your progress through honest work.")
