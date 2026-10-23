from rehabilitation import rehabilitation
from exercise import go_to_exercise
from player import Player
from save import save_game, load_game
from ga import attend_ga
from menus import show_game_title, show_main_menu, show_journey_menu
from work import go_to_work
from programming import programming
from rest import rest
from addictions import choose_addictions
from day import spend_time, end_day
from finances import finance_menu
from safeguards import safeguards_menu
from relapse import log_relapse
from history import show_history
from utils import ask_int
import rehab_rules

# this is recovery_main.py (your original main.py, wrapped in main() so the app can start it)


def run_activity(player, key, action):
    """Checks the rules first. If an activity isn't allowed it simply does not run."""
    allowed, reason = rehab_rules.can_do(player, key)
    if not allowed:
        print()
        print(f"(locked) {reason}")
        return
    if action(player) is False:       # player backed out, no time passes
        return
    spend_time(player, rehab_rules.DURATION[key])


def handle_journey_choice(player, journey_choice):
    """Runs one menu choice. Returns True when the player leaves the journey."""
    if journey_choice == "1":
        run_activity(player, "ga", attend_ga)

    elif journey_choice == "2":
        if player.in_rehabilitation:
            run_activity(player, "rehab", rehabilitation)
        else:
            rehabilitation(player)

    elif journey_choice == "3":
        run_activity(player, "work", go_to_work)

    elif journey_choice == "4":
        run_activity(player, "exercise", go_to_exercise)

    elif journey_choice == "5":
        run_activity(player, "programming", programming)

    elif journey_choice == "6":
        run_activity(player, "rest", rest)

    elif journey_choice == "7":
        player.show_status()

    elif journey_choice == "8":
        print("Returning to main menu...")
        return True

    elif journey_choice == "9":
        save_game(player)
        print("Game saved.")
        print("Returning to main menu...")
        return True

    elif journey_choice == "10":
        end_day(player)

    elif journey_choice == "11":
        finance_menu(player)

    elif journey_choice == "12":
        safeguards_menu(player)

    elif journey_choice == "13":
        show_history(player)

    elif journey_choice == "14":
        log_relapse(player)

    else:
        print("Invalid option.")

    return False


def journey(player):
    while True:
        show_journey_menu(player)
        journey_choice = input("Choose an option: ").strip()
        try:
            if handle_journey_choice(player, journey_choice):
                break
        except (KeyboardInterrupt, SystemExit, StopIteration, EOFError):
            raise
        except Exception as exc:
            print()
            print(f"Something went wrong in that screen: {exc!r}")
            print("Your game is still running.")


def new_journey():
    player_name = input("What shall we call you on this journey? ")
    print()
    recovery_days = ask_int("How many days have you been in recovery? ")
    money = ask_int("How much money do you currently have? ")
    debt = ask_int("How much debt do you currently have? ")

    player = Player(player_name, recovery_days)
    player.money = money
    player.debt = debt
    player.addictions = choose_addictions([])

    print()
    print(f"Welcome, {player.name}")
    print()
    print("Remember:")
    player.show_recovery_message()
    print()
    print("Your journey continues...")
    player.show_status()
    print("Starting your recovery journey...")
    return player


def main():
    print()
    show_game_title()
    print()
    print("Every journey begins with a single step.")
    print("Today is another chance to move forward.")
    print()

    while True:
        show_main_menu()
        main_choice = input("Choose an option: ").strip()

        if main_choice == "1":
            journey(new_journey())

        elif main_choice == "2":
            try:
                player = load_game()
            except (FileNotFoundError, ValueError, KeyError):
                print("No usable saved journey found. Start a new one first.")
                continue
            journey(player)

        elif main_choice == "3":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
