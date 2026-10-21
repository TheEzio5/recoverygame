from constants import WIDTH
from utils import apply_rewards, show_rewards
import random

programming_events = [

{
    "text": "You finally fixed a bug that had been bothering you.",
    "confidence": 8,
    "experience": 6
},

{
    "text": "You learned something completely new today.",
    "experience": 10,
    "hope": 2
},

{
    "text": "Stack Overflow saved your day.",
    "experience": 4
},

{
    "text": "Your code worked on the first try.",
    "confidence": 10,
    "hope": 3
},

{
    "text": "You spent an hour debugging a missing comma.",
    "energy": -8,
    "experience": 8
},

{
    "text": "You pushed another project to GitHub.",
    "confidence": 7,
    "experience": 6
},

{
    "text": "You completed another Python lesson.",
    "experience": 7,
    "hope": 2
},

{
    "text": "You committed your work with a meaningful Git message.",
    "confidence": 5,
    "experience": 5
},

{
    "text": "You solved a coding challenge on your own.",
    "confidence": 6,
    "experience": 6
}

]



def programming_header():
    print()
    print()
    print("=" * WIDTH)
    print("PROGRAMMING 🧑‍💻🐍 ".center(WIDTH))
    print("=" * WIDTH)
    print()


def programming_intro():

    print("💻 You opened your laptop.")
    print()
    print("One line of code at a time...")
    print()
    print("You're building a future where")
    print("you can work from anywhere.")
    print()
    print("Today's effort brings that dream closer.")

    return {
        "energy": -10,
        "confidence": 5,
        "experience": 8,
        "hope": 3,
        "urge": -2
    }




def programming(player):

    programming_header()

    base_rewards = programming_intro()
    apply_rewards(player, base_rewards)

    player.level_up()

    event = random.choice(programming_events)

    print()
    print(event["text"])

    apply_rewards(player, event)

    show_rewards("Today's Coding Session", base_rewards)
    show_rewards(event["text"], event)

    input("Press Enter to continue...")
