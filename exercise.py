from constants import WIDTH
from utils import apply_rewards, show_rewards
import random

exercise_events = [

{
    "text": "You beat your personal best today.",
    "confidence": 6,
    "experience": 4
},

{
    "text": "You felt tired but finished the workout.",
    "confidence": 2,
    "energy": -5
},

{
    "text": "Music kept you motivated.",
    "hope": 4,
    "urge": -3
},

{
    "text": "You met someone friendly at the gym.",
    "confidence": 3,
    "hope": 2
},

{
    "text": "Your muscles are sore after today's workout.",
    "energy": -8,
    "experience": 3
}

]


def exercise_header():
    print()
    print()
    print("=" * WIDTH)
    print("EXERCISE 🏃".center(WIDTH))
    print("=" * WIDTH)
    print()

def exercise_intro():

    print("🏃 You decided to exercise today.")
    print()
    print("Even though motivation wasn't always there,")
    print("you showed up.")
    print()
    print("Every workout strengthens both body and mind.")
    print()
    print("Healthy habits replace old ones.")

    return {
            "energy": -12,
            "confidence": 5,
            "hope": 2,
            "urge": -2,
            "experience": 5
        }


def go_to_exercise(player):

    exercise_header()

    base_rewards = exercise_intro()
    apply_rewards(player, base_rewards)

    event = random.choice(exercise_events)

    print()
    print(event["text"])

    apply_rewards(player, event)

    player.level_up()

    show_rewards("Today's workout", base_rewards)
    show_rewards(event["text"], event)

    input("Press Enter to continue...")
