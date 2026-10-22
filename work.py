from constants import WIDTH
import random
from utils import apply_rewards, show_rewards

#this is work.py

def work_header():
    print()
    print()
    print("=" * WIDTH)
    print("WORK".center(WIDTH))
    print("=" * WIDTH)
    print()

work_events = [

    {
        "text": "You had a peaceful day at work.",
        "energy": -2,
        "confidence": 1
    },

    {
        "text": "A customer thanked you and left a tip.",
        "confidence": 5,
        "experience": 2,
        "money": 10
    },

    {
        "text": "You had a stressful day.",
        "urge": 2,
        "experience": 8
    },

    {
        "text": "Boss praised you and gave you a small bonus.",
        "confidence": 8,
        "money": 15
    },

    {
        "text": "You had a very long shift and got paid overtime.",
        "energy": -20,
        "hope": 3,
        "money": 25
    }

]


def work_intro():

    print("💼 You went to work today.")
    print()
    print("It wasn't always easy,")
    print("but you stayed honest.")
    print()
    print("You earned money through hard work.")
    print()
    print("Another day away from gambling.")

    return {
        "energy": -15,
        "confidence": 4,
        "experience": 6,
        "money": random.randint(60, 100),
    }


def go_to_work(player):

    work_header()

    base_rewards = work_intro()
    apply_rewards(player, base_rewards)

    event = random.choice(work_events)
    print()
    print(event["text"])
    apply_rewards(player, event)

    show_rewards("Today's Work Summary", base_rewards)
    show_rewards(event["text"], event)
    print()
    print("You earned your progress through honest work.")
    input("Press Enter to continue...")
