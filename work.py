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

"text": "A customer thanked you.",

"confidence": 5,

"experience": 2

},

{

"text": "You had a stressful day.",

"urge": 2,

"experience": 8

},

{

"text": "Boss praised you.",

"confidence": 8,

},

{

"text": "You had a very long shift",

"energy": -20,

"hope": 3

}

]



def go_to_work(player):

    work_header()

    base_rewards = work_intro()
    apply_rewards(player, base_rewards)

    event = random.choice(work_events)
    print()
    print(event["text"])
    apply_rewards(player, event)

    player.level_up()

    show_rewards("Today's Work Summary",base_rewards)
    show_rewards(event["text"],event)
    input("Press Enter to continue...")

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
        "energy" : -15,
        "confidence" : 4,
        "experience" : 6,
    }



