from constants import WIDTH

#this is menus.py

def show_game_title():
    print("=" * WIDTH)
    print("RECOVERY QUEST".center(WIDTH))
    print("=" * WIDTH)


def show_main_menu():
    print()
    print()
    print("=" * WIDTH)
    print("MAIN MENU".center(WIDTH))
    print("=" * WIDTH)

    print("1. Start Journey 🌅")
    print("2. Load Journey 💾")
    print("3. Exit 🚪")
    print()

def show_journey_menu(player):
    print()
    print()
    print("=" * WIDTH)
    print("YOUR JOURNEY".center(WIDTH))
    print("=" * WIDTH)
    print()
    print(f"📅 Your real Recovery Days: {player.recovery_days}")
    print(f"🗺️ Your ingame Journey Days: {player.journey_days}")
    print()
    print("1. Attend G.A. Meeting 🤝")
    print("2. Go to Rehabilitation 🏥")
    print("3. Go to Work 💼")
    print("4. Exercise 🏃")
    print("5. Practice programming ")
    print("6. Rest 😴")
    print("7. Check Status 📊")
    print("8. Return to Main Menu ↩️")
    print("9. Save Game")

