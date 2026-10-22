from constants import WIDTH, ADDICTIONS

#this is history.py


def show_history(player):
    print()
    print("=" * WIDTH)
    print("RECOVERY STORY 📖".center(WIDTH))
    print("=" * WIDTH)
    print()
    print(f"Current streak: {player.recovery_days} day(s)")
    print(f"Longest streak: {player.longest_streak} day(s)")
    print(f"Relapses logged: {player.relapses}")
    print(f"Debt created by relapses: €{player.total_relapse_debt}")
    print(f"Debt repaid: €{player.debt_repaid}")
    print(f"Sent to loved ones: €{player.sent_to_loved_ones}")
    print(f"Meetings attended: {player.meetings_attended}")
    print(f"Rehabilitation programs completed: {player.rehabs_completed}")

    if player.milestone_log:
        print()
        print("Milestones")
        for item in player.milestone_log:
            print(f"  {item['days']} days ({item['date']})")

    if player.relapse_history:
        print()
        print("Relapse history")
        for item in player.relapse_history:
            name = ADDICTIONS.get(item["addiction"], item["addiction"])
            print(f"  {item['date']}: {name}, ended a {item['streak_before']}-day streak")

    input("Press Enter to continue...")
