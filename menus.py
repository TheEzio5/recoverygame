from constants import WIDTH
import rehab_rules

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


def _locked(player, key):
    ok, _ = rehab_rules.can_do(player, key)
    return "" if ok else "  (locked)"


def show_journey_menu(player):
    print()
    print()
    print("=" * WIDTH)
    print("YOUR JOURNEY".center(WIDTH))
    print("=" * WIDTH)
    print()
    print(f"📅 Your real Recovery Days: {player.recovery_days}")
    print(f"🗺️ Your ingame Journey Days: {player.journey_days}")
    print(f"🕒 {player.weekday_name}, {player.clock_text}")
    if player.in_rehabilitation:
        print(f"🏥 {player.rehab_section.capitalize()} rehabilitation: "
              f"{player.rehab_days_remaining} day(s) left")
    print()
    print(f"1. Attend G.A. Meeting 🤝{_locked(player, 'ga')}")
    if player.in_rehabilitation:
        print(f"2. Rehabilitation activity 🏥{_locked(player, 'rehab')}")
    else:
        print("2. Go to Rehabilitation 🏥")
    print(f"3. Go to Work 💼{_locked(player, 'work')}")
    print(f"4. Exercise 🏃{_locked(player, 'exercise')}")
    print(f"5. Practice programming 💻{_locked(player, 'programming')}")
    print(f"6. Rest 😴{_locked(player, 'rest')}")
    print("7. Check Status 📊")
    print("8. Return to Main Menu ↩️")
    print("9. Save Game")
    print("10. End the day 🌙")
    print("11. Finances 💶")
    print("12. Safeguards 🛡️")
    print("13. Recovery story 📖")
    print("14. I relapsed today")
