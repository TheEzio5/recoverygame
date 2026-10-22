from constants import WIDTH, ADDICTIONS
from utils import ask_int

#this is relapse.py


def log_relapse(player):
    print()
    print("=" * WIDTH)
    print("I RELAPSED TODAY".center(WIDTH))
    print("=" * WIDTH)
    print()
    print("Thank you for being honest. That takes courage.")
    print("This only resets your current streak.")
    print("Your journey days and history stay.")
    print()

    answer = input("Do you want to log a relapse? (1 = yes, 2 = no): ").strip()
    if answer != "1":
        print("Nothing was changed.")
        return False

    keys = player.addictions or list(ADDICTIONS)
    print()
    print("Which addiction was it?")
    for i, key in enumerate(keys, 1):
        print(f"{i}. {ADDICTIONS[key]}")
    while True:
        pick = input("Choose an option: ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(keys):
            addiction = keys[int(pick) - 1]
            break
        print("Invalid option.")

    new_debt = 0
    if addiction == "gambling":
        new_debt = ask_int("How much additional debt did it create? (0 if none): ")

    streak_before = player.record_relapse(addiction, new_debt)

    print()
    print("Recovery isn't about perfection. It's about coming back.")
    print(f"Your streak of {streak_before} day(s) is saved in your history.")
    print(f"Current streak: {player.recovery_days} days. "
          f"Longest streak: {player.longest_streak}.")
    if new_debt:
        print(f"€{new_debt} was added to your debt. Total debt: €{player.debt}.")
    print("Consider telling someone you trust, or going to a meeting.")
    input("Press Enter to continue...")
    return False
