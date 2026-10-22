from constants import WIDTH
import random

#this is ga.py

meeting_names = [
    "HopefulOne",
    "Phoenix",
    "StillFighting",
    "OneDayAtATime",
    "RecoveryJourney",
    "KeepComingBack",
    "GratefulToday",
    "FaithOverFear",
    "NeverAlone",
    "StepByStep",
]

group_replies = [
    "Hi, {}.",
    "Welcome, {}.",
    "Glad you're here, {}.",
    "Keep coming back, {}.",
]


def ga_meeting(meeting_choice):
    print()
    print()
    print("=" * WIDTH)
    print("G.A. MEETING".center(WIDTH))
    print("=" * WIDTH)
    print()
    print("You attended today's G.A. meeting.")
    print()
    if meeting_choice == "listen":
        print("You listened carefully.")
        print("You took home a few ideas to think about.")
    else:
        print("You shared honestly.")
        print("The group thanked you for your courage.")

    print()
    print("You leave today's meeting feeling stronger.")


def ga_intro(player):
    member_names = random.sample(meeting_names, 2)

    member1_days = random.randint(1, 365)
    member2_days = random.randint(1, 365)

    print("=" * WIDTH)
    print("YOUR JOURNEY".center(WIDTH))
    print("=" * WIDTH)
    print()
    print("You join today's meeting.")
    print("📖 The G.A. Preamble is read.")
    print()
    print("🔒 A reminder is given about\nsafety, respect and anonymity.")
    print()
    print(f'"My name is {member_names[0]}, and today I have {member1_days} days without gambling."')
    print()
    print(f'"My name is {member_names[1]}, and today I have {member2_days} days without gambling."')
    print()
    print(f'"My name is {player.name}, and today I have {player.recovery_days} days without gambling."')
    print()
    print(random.choice(group_replies).format(player.name))
    print()
    print("--------------------------------")


def ga_story_listen():
    story = random.choice([
        ga_story_gratitude,
        ga_story_newcomer,
        ga_story_listening,
    ])
    reward_ranges = story()

    return reward_ranges



def ga_story_share():
    story = random.choice([
        ga_story_honesty,
        ga_story_relapse,
    ])
    reward_ranges = story()

    return reward_ranges

def ga_story_gratitude():

    print("Today's topic was Gratitude...")
    print()
    print("One member shared how recovery helped rebuild trust with their family.")
    print()
    print("You left thinking about the people who still believe in you.")
    return {
        "willpower": (3, 6),
        "hope": (7, 10),
        "confidence": (0, 2),
        "experience": (2, 4),
        "urge": (-5, -2)

    }

def ga_story_honesty():

    print("Today's topic was Honesty...")
    print()
    print("You shared something that had been on your mind all week.")
    print()
    print("It wasn't easy.")
    print()
    print("After the meeting, you felt lighter.")

    return {
        "willpower": (7, 10),
        "hope": (4, 7),
        "confidence": (4, 7),
        "experience": (5, 8),
        "urge": (-5, -2)

    }

def ga_story_newcomer():

    print("A newcomer joined today's meeting.")
    print()
    print("You remembered how difficult your own first meeting felt.")
    print()
    print("You welcomed them with a ❤️ reaction.")

    return {
        "willpower": (4, 6),
        "hope": (5, 8),
        "confidence": (1, 3),
        "experience": (3, 5),
        "urge": (-5, -2)
    }

def ga_story_listening():

    print("Today you weren't feeling your best.")
    print()
    print("You decided not to share.")
    print()
    print("Instead, you listened carefully.")
    print()
    print("Sometimes listening is enough.")
    print()
    print("You left with new hope.")

    return {
        "willpower": (2, 4),
        "hope": (2, 5),
        "confidence": (0, 1),
        "experience": (1, 3),
        "urge": (-5, -2)

    }


def ga_story_relapse():
    print("Today you shared that you had relapsed.")
    print()
    print("It wasn't easy to say out loud.")
    print()
    print("Nobody judged you.")
    print()
    print("The group listened.")
    print()
    print("They were supportive and u got a lot ❤️ ❤️ ❤️ 🤝 ❤️ 🙏 ❤️")
    print("They reminded you that recovery isn't about perfection.")
    print()
    print("It's about coming back.")
    print()
    print("You left determined to begin again.")
    print()

    return {
        "willpower": (5, 8),
        "hope": (6, 10),
        "confidence": (-2, 2),
        "experience": (8, 12),
        "urge": (-5, -2)
    }


def ga_meeting_choice():

    print()
    print("Today's meeting begins...")
    print()
    print("1. Listen today 👂")
    print("2. Share today 🗣️")
    print()

    meeting_choice = input("Choose an option: ")

    if meeting_choice == "1":
        print()
        print("You decided to listen today.")
        return "listen"

    elif meeting_choice == "2":
        print()
        print("You decided to share today.")
        return "share"

    else:
        print("You stayed quiet.")
        return "listen"






def ga_rewards(player, rewards):

    willpower_gain = random.randint(
        rewards["willpower"][0],
        rewards["willpower"][1]
    )
    hope_gain = random.randint(
        rewards["hope"][0],
        rewards["hope"][1]
    )
    confidence_gain = random.randint(
        rewards["confidence"][0],
        rewards["confidence"][1]
    )
    experience_gain = random.randint(
        rewards["experience"][0],
        rewards["experience"][1]
    )

    urge_gain = random.randint(
        rewards["urge"][0],
        rewards["urge"][1]
    )


    energy_gain = -5

    player.willpower += willpower_gain
    player.hope += hope_gain
    player.urge += urge_gain
    player.confidence += confidence_gain
    player.experience += experience_gain
    player.energy += energy_gain
    player.clamp_stats()

    print()
    print("Reflection")
    print("-" * WIDTH)
    print(f"❤️ Willpower +{willpower_gain}")
    print(f"🌅 Hope +{hope_gain}")
    print(f"💪 Confidence +{confidence_gain}")
    print(f"🔥 Urge {urge_gain}")
    print(f"📚 Experience +{experience_gain}")
    print(f"⚡ Energy {energy_gain}")

    input("Press Enter to continue...")

def attend_ga(player):
    player.meetings_attended += 1
    ga_intro(player)

    meeting_choice = ga_meeting_choice()

    if meeting_choice == "listen":
        rewards = ga_story_listen()
    else:
        rewards = ga_story_share()

    ga_meeting(meeting_choice)
    ga_rewards(player, rewards)

    player.level_up()