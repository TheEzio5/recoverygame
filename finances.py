from constants import WIDTH
from utils import ask_int, apply_rewards, show_rewards

#this is finances.py

EXPENSES = [
    ("Groceries and essentials", 10, {"energy": 5}),
    ("Therapy session", 25, {"hope": 5, "urge": -4, "confidence": 2}),
]


def check_spend(player, amount):
    """The one place that decides if a payment is possible."""
    if amount > player.money:
        return False, "You don't have enough money for this payment."
    limit = player.safeguards.get("daily_limit")
    if limit is not None and player.spent_today + amount > limit:
        left = max(0, limit - player.spent_today)
        return False, (f"That is over your daily spending limit of €{limit}. "
                       f"You can still spend €{left} today.")
    return True, ""


def _banking_blocked(player):
    if player.safeguards.get("banking_restricted"):
        print("Banking apps are restricted by your safeguards.")
        return True
    return False


def pay_debt(player):
    if _banking_blocked(player):
        return
    if player.debt <= 0:
        print("You have no debt to pay. 🎉")
        return
    amount = ask_int(f"How much do you want to pay? (debt €{player.debt}, 0 = cancel): ")
    if amount == 0:
        return
    amount = min(amount, player.debt)          # never pay more than you owe
    ok, reason = check_spend(player, amount)
    if not ok:
        print(reason)
        return
    player.money -= amount
    player.spent_today += amount
    player.debt -= amount
    player.debt_repaid += amount
    print(f"You paid €{amount}. Remaining debt: €{player.debt}.")


def send_money(player):
    if _banking_blocked(player):
        return
    amount = ask_int("How much do you want to send to a loved one? (0 = cancel): ")
    if amount == 0:
        return
    ok, reason = check_spend(player, amount)
    if not ok:
        print(reason)
        return
    player.money -= amount
    player.spent_today += amount
    player.sent_to_loved_ones += amount
    player.hope += 3
    player.clamp_stats()
    print(f"You sent €{amount}. It felt good to give. 🌅 Hope +3")


def pay_expense(player):
    print()
    for i, (name, cost, _) in enumerate(EXPENSES, 1):
        print(f"{i}. {name} (€{cost})")
    print(f"{len(EXPENSES) + 1}. Back")
    choice = input("Choose an option: ").strip()
    if not (choice.isdigit() and 1 <= int(choice) <= len(EXPENSES)):
        return
    name, cost, rewards = EXPENSES[int(choice) - 1]
    ok, reason = check_spend(player, cost)
    if not ok:
        print(reason)
        return
    player.money -= cost
    player.spent_today += cost
    apply_rewards(player, rewards)
    print(f"You paid €{cost} for: {name}.")
    show_rewards(name, rewards)


def finance_menu(player):
    while True:
        print()
        print("=" * WIDTH)
        print("FINANCES 💶".center(WIDTH))
        print("=" * WIDTH)
        print(f"💰 Money: €{player.money}    💳 Debt: €{player.debt}")
        limit = player.safeguards.get("daily_limit")
        if limit is not None:
            print(f"Spent today: €{player.spent_today} of €{limit}")
        print(f"Debt repaid so far: €{player.debt_repaid}")
        print()
        print("1. Pay towards debt")
        print("2. Send money to a loved one")
        print("3. Everyday and recovery expenses")
        print("4. Back")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            pay_debt(player)
        elif choice == "2":
            send_money(player)
        elif choice == "3":
            pay_expense(player)
        elif choice == "4":
            return
        else:
            print("Invalid option.")
