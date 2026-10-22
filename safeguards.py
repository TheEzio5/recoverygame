from constants import WIDTH
from utils import ask_int
import rehab_rules

#this is safeguards.py


def _on_off(value):
    return "ON" if value else "OFF"


def safeguards_menu(player):
    locked = rehab_rules.in_closed_rehab(player)
    sg = player.safeguards

    while True:
        limit = sg["daily_limit"]
        print()
        print("=" * WIDTH)
        print("SAFEGUARDS 🛡️".center(WIDTH))
        print("=" * WIDTH)
        print(f"1. Gambling exclusion / blocking tools: {_on_off(sg['gambling_exclusion'])}")
        print(f"2. Banking apps restricted: {_on_off(sg['banking_restricted'])}")
        print(f"3. Daily spending limit: {'€' + str(limit) if limit is not None else 'none'}")
        print("4. Back")
        if locked:
            print("🔒 Your closed program keeps protections in place.")
            print("   You can add more, but not turn any off.")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            if sg["gambling_exclusion"] and locked:
                print("This can't be turned off during closed rehabilitation.")
            else:
                sg["gambling_exclusion"] = not sg["gambling_exclusion"]
                print(f"Gambling exclusion is now {_on_off(sg['gambling_exclusion'])}.")

        elif choice == "2":
            if sg["banking_restricted"] and locked:
                print("This can't be turned off during closed rehabilitation.")
            else:
                sg["banking_restricted"] = not sg["banking_restricted"]
                print(f"Banking restriction is now {_on_off(sg['banking_restricted'])}.")

        elif choice == "3":
            amount = ask_int("Daily limit in € (0 = no limit): ")
            if amount == 0:
                if locked and limit is not None:
                    print("The limit can't be removed during closed rehabilitation.")
                else:
                    sg["daily_limit"] = None
                    print("No daily limit.")
            elif locked and limit is not None and amount > limit:
                print("During closed rehabilitation you can only lower the limit.")
            else:
                sg["daily_limit"] = amount
                print(f"Daily limit set to €{amount}.")

        elif choice == "4":
            return
        else:
            print("Invalid option.")
