from constants import WIDTH



import random



from utils import apply_rewards, show_rewards



rest_events = [



{

    "text": "You slept deeply and woke up refreshed.",

    "energy": 10,

    "confidence": 2

},



{

    "text": "You dreamed about your future instead of your past.",

    "hope": 5,

    "confidence": 2

},



{

    "text": "You had a nightmare about gambling.",

    "urge": 5,

    "energy": -3

},



{

    "text": "You spent some quiet time doing something you enjoy.",

    "hope": 4,

    "urge": -2

},



{

    "text": "You called someone you care about.",

    "confidence": 3,

    "hope": 4

},



{

    "text": "You slept longer than planned.",

    "energy": 8,

    "experience": -1

},



{

    "text": "You spent a few quiet minutes in prayer.",

    "hope": 6,

    "confidence": 2,

    "urge": -3

},



{

    "text": "You dreamed about your family waiting for you.",

    "hope": 7,

    "urge": -2

}



]







def rest_header():

    print()

    print()

    print("=" * WIDTH)

    print("REST 😴".center(WIDTH))

    print("=" * WIDTH)

    print()



def rest_intro():



    print("😴 You decided to rest today.")

    print()

    print("Recovery isn't only about working harder.")

    print()

    print("Sometimes the strongest decision")

    print("is allowing yourself to slow down.")

    print()

    print("Tomorrow is another chance.")



    return {

            "energy": 20,

            "hope": 2,

            "urge": -1

        }





def rest(player):

    rest_header()



    base_rewards = rest_intro()

    apply_rewards(player, base_rewards)



    event = random.choice(rest_events)



    print()

    print(event["text"])



    apply_rewards(player, event)


    show_rewards("Today's Rest", base_rewards)

    show_rewards(event["text"], event)



    input("Press Enter to continue...")


