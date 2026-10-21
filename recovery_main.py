from rehabilitation import rehabilitation
from exercise import go_to_exercise
from player import Player
from save import save_game, load_game
from ga import attend_ga
from menus import show_game_title, show_main_menu, show_journey_menu
from work import go_to_work
from programming import programming
from rest import rest

# this is recovery_main.py (your original main.py, wrapped in main() so the app can start it)


def ask_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a number.")


def journey(player):
    while True:
        show_journey_menu(player)
        journey_choice = input("Choose an option: ")

        if journey_choice == "1":
            attend_ga(player)
        elif journey_choice == "2":
            rehabilitation(player)
        elif journey_choice == "3":
            go_to_work(player)
        elif journey_choice == "4":
            go_to_exercise(player)
        elif journey_choice == "5":
            programming(player)
        elif journey_choice == "6":
            rest(player)
        elif journey_choice == "7":
            player.show_status()
        elif journey_choice == "8":
            print("Returning to main menu...")
            break
        elif journey_choice == "9":
            save_game(player)
            print("Game saved.")
            print("Returning to main menu...")
            break
        else:
            print("Invalid option.")


def main():
    print()
    show_game_title()
    print()
    print("Every journey begins with a single step.")
    print("Today is another chance to move forward.")
    print()

    while True:
        show_main_menu()
        main_choice = input("Choose an option: ")

        if main_choice == "1":
            player_name = input("What shall we call you on this journey? ")
            print()
            recovery_days = ask_int("How many days have you been in recovery? ")
            money = ask_int("How much money do you currently have? ")
            debt = ask_int("How much debt do you currently have? ")

            player = Player(player_name, recovery_days)
            player.money = money
            player.debt = debt

            print(f"Welcome back, {player.name}")
            print()
            print("Remember:")
            player.show_recovery_message()
            print()
            print("Your journey continues...")
            player.show_status()
            print("Starting your recovery journey...")
            journey(player)

        elif main_choice == "2":
            try:
                player = load_game()
            except FileNotFoundError:
                print("No saved journey found. Start a new one first.")
                continue
            journey(player)

        elif main_choice == "3":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
