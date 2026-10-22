from constants import WIDTH, DAY_START_HOUR, DAY_END_HOUR
import rehab_rules
from rehabilitation import complete_rehabilitation

#this is day.py


def spend_time(player, hours):
    player.hour += hours
    if player.hour >= DAY_END_HOUR:
        end_day(player, automatic=True)


def end_day(player, automatic=False):
    print()
    print()
    print("=" * WIDTH)
    print("END OF DAY 🌙".center(WIDTH))
    print("=" * WIDTH)
    print()
    print("It's midnight. You head to bed." if automatic else "You head to bed.")

    player.energy += 30
    note = rehab_rules.end_of_day_urge(player)
    player.clamp_stats()
    print("⚡ Energy +30 after a night's sleep")
    if note:
        print(note)
    if player.urge >= 80:
        print("Your urges are high. Tomorrow, consider a meeting,")
        print("calling someone you trust, or resting first.")

    player.journey_days += 1
    player.hour = DAY_START_HOUR
    player.spent_today = 0

    if player.in_rehabilitation:
        player.rehab_days_remaining -= 1
        if player.rehab_days_remaining > 0:
            print(f"🏥 Rehabilitation: {player.rehab_days_remaining} day(s) remaining.")
        else:
            complete_rehabilitation(player)

    print()
    print(f"Day {player.journey_days} begins. It's {player.weekday_name}, "
          f"{player.clock_text}.")
    input("Press Enter to continue...")
