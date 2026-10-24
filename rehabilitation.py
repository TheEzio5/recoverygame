import random

from constants import WIDTH, ADDICTIONS, REHAB_DURATIONS, PROTECTED_DAILY_LIMIT
from addictions import choose_addictions
from help_support import offer_gambling_support
from utils import apply_rewards, show_rewards, ask_yes_no

#this is rehabilitation.py

SESSIONS = {
    "1": ("Individual therapy", "You talked openly with your therapist.",
          {"hope": 4, "confidence": 3, "urge": -4, "energy": -6, "experience": 6}),
    "2": ("Group session", "You listened to others and shared a little of your own story.",
          {"hope": 3, "willpower": 4, "urge": -3, "energy": -5, "experience": 5}),
    "3": ("Workshop", "You learned a new way to handle difficult moments.",
          {"confidence": 4, "hope": 2, "energy": -6, "experience": 7}),
    "4": ("Quiet reflection", "You sat quietly and wrote down what matters to you.",
          {"hope": 3, "willpower": 2, "urge": -3, "energy": -2, "experience": 3}),
}


def rehab_header():
    print()
    print("=" * WIDTH)
    print("REHABILITATION 🏥".center(WIDTH))
    print("=" * WIDTH)
    print()


def rehabilitation(player):
    """Journey menu entry. Returns False if the player did nothing that costs time."""
    rehab_header()
    if player.in_rehabilitation:
        return rehab_session(player)
    setup_rehabilitation(player)
    return False          # entering takes no in-game time


def setup_rehabilitation(player):
    print("You entered rehabilitation.")
    print()
    print("Recovery sometimes requires stepping away")
    print("from everyday life and focusing on yourself.")

    # 1) addictions
    if player.addictions:
        print()
        print(f"You are recovering from: {player.addiction_names()}")
        if not ask_yes_no("Keep this list?"):
            previous = list(player.addictions)
            player.addictions = choose_addictions(player.addictions)
            offer_gambling_support(previous, player.addictions)
    else:
        player.addictions = choose_addictions([])
        offer_gambling_support([], player.addictions)

    # 2) section
    print()
    print("Which rehabilitation section?")
    print("1. Open   - more freedom, more exposure to triggers")
    print("2. Closed - strict structure, no work, laptop and outing hours")
    while True:
        section_choice = input("Choose an option: ").strip()
        if section_choice in ("1", "2"):
            break
        print("Invalid option.")
    section = "open" if section_choice == "1" else "closed"

    # 3) duration
    print()
    print("How long will you stay?")
    print("1. 7 days")
    print("2. 14 days")
    print("3. 1 month (30 days)")
    print("4. 3 months (90 days)")
    while True:
        duration_choice = input("Enter your choice: ").strip()
        if duration_choice in REHAB_DURATIONS:
            break
        print("Invalid choice.")
    days = REHAB_DURATIONS[duration_choice]

    # 4) safeguards (always the player's own explicit choice)
    if "gambling" in player.addictions:
        print()
        if not player.safeguards["gambling_exclusion"]:
            if ask_yes_no("Register gambling self-exclusion / blocking tools?"):
                player.safeguards["gambling_exclusion"] = True
                print("Recorded: gambling exclusion is ON.")
        if section == "closed":
            print()
            print("Protected money rule: no banking apps and")
            print(f"a maximum of €{PROTECTED_DAILY_LIMIT} spending per day.")
            if ask_yes_no("Use this rule during your stay?"):
                player.safeguards["banking_restricted"] = True
                player.safeguards["daily_limit"] = PROTECTED_DAILY_LIMIT
                print("Recorded: banking restricted, daily limit set.")

    # 5) enter
    player.in_rehabilitation = True
    player.rehab_program = "standard"
    player.rehab_section = section
    player.rehab_days_remaining = days

    print()
    print(f"You have entered {section.upper()} rehabilitation.")
    print(f"Your rehabilitation will last {days} days.")
    if section == "closed":
        print("Work is unavailable. Your laptop is available 09:00-21:00.")
    else:
        print("You have more freedom here. Stay mindful of your triggers.")
    input("Press Enter to continue...")


def rehab_session(player):
    print(f"{player.rehab_section.capitalize()} section, "
          f"{player.rehab_days_remaining} day(s) remaining.")
    print()
    print("Which activity today?")
    for number, (name, _, _) in SESSIONS.items():
        print(f"{number}. {name}")
    print("5. Back")

    choice = input("Choose an option: ").strip()
    if choice not in SESSIONS:
        if choice != "5":
            print("Invalid option.")
        return False

    name, text, rewards = SESSIONS[choice]
    print()
    print(f"{name} 🏥")
    print(text)
    apply_rewards(player, rewards)
    show_rewards(name, rewards)
    input("Press Enter to continue...")
    return True


def complete_rehabilitation(player):
    print()
    print("🏥 You completed your rehabilitation program!")
    print("The staff say goodbye. You leave with new tools,")
    print("and the freedom to make your own choices again.")

    rewards = {"hope": 10, "confidence": 8, "willpower": 5,
               "experience": 30, "urge": -10}
    apply_rewards(player, rewards)
    show_rewards("Program completed", rewards)

    player.rehabs_completed += 1
    player.in_rehabilitation = False
    player.rehab_program = None
    player.rehab_section = None
    player.rehab_days_remaining = 0
    print()
    print("Your safeguards stay on until you change them.")
