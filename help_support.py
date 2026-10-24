"""Real-world help. Everything here points to real, free services.
The self-check is NOT a diagnosis, it is a short reflection."""
from constants import WIDTH
from utils import ask_yes_no

#this is help_support.py

LINK_GA_ONLINE = ("Online GA meetings, any time", "https://gamblersinrecovery.com")
LINK_GA_DIRECTORY = ("GA international meeting directory", "https://gamblersanonymous.org/mtgdirTOP.html")
LINK_GA_UK = ("GA England, Wales and Ulster", "https://www.gamblersanonymous.org.uk/find-a-meeting")
LINK_GA_HOME = ("Gamblers Anonymous", "https://gamblersanonymous.org")
LINK_GO_GA = ("Go to Gamblers Anonymous", "https://gamblersanonymous.org")
LINK_GA_20Q = ("GA's official 20 questions", "https://gamblersanonymous.org/20questions.html")
LINK_THERAPY = ("Gambling Therapy, free online support", "https://gamblingtherapy.org")
LINK_GAM_ANON = ("Gam-Anon, for family and friends", "https://gam-anon.org")

EMERGENCY = ("If you are in danger or thinking about harming yourself,\n"
             "call your local emergency number now (112 in the EU, 988 in the US).")

HIGH_THRESHOLD = 7      # Gamblers Anonymous: most compulsive gamblers answer yes to 7 or more

# Our own 20 questions (we cannot copy Gamblers Anonymous's wording, which is theirs).
# They cover the same kinds of harm. Answer about your own gambling.
SELF_CHECK_QUESTIONS = [
    # control and craving
    "Have you gambled for longer, or with more money, than you meant to?",
    "Have you tried to cut down or stop gambling and found you couldn't?",
    "Do you feel restless, irritable or on edge when you try to cut down?",
    "Do thoughts about gambling (past bets, the next bet, finding money) take up a lot of your day?",
    "Have you needed bigger bets to get the same thrill?",
    # feelings and triggers
    "Do you gamble to escape stress, boredom, loneliness or a low mood?",
    "After a loss, have you felt you had to go back soon to win it back?",
    "Do you feel guilty, ashamed or anxious after gambling?",
    "Do arguments or bad days make you want to gamble?",
    # money
    "Have you gambled money that was meant for bills, food or rent?",
    "Have you borrowed money, used credit or sold things to gamble?",
    "Have you asked someone to bail you out of money trouble caused by gambling?",
    "Do you keep gambling even though your debts are growing?",
    # honesty and relationships
    "Have you hidden or lied about how much you gamble?",
    "Has gambling caused arguments or distance with family, a partner or friends?",
    "Has gambling hurt your work, your studies or your reputation?",
    # wellbeing and life
    "Has gambling disturbed your sleep, appetite or health?",
    "Have you given up hobbies, plans or time with people so you could gamble?",
    "Have you done, or considered doing, something illegal to get money for gambling?",
    "Has gambling ever left you so hopeless that you thought about ending your life?",
]
LAST_QUESTION_IS_CRISIS = True


def interpret(yes_count):
    """Returns (title, lines) for the number of 'yes' answers."""
    if yes_count == 0:
        return ("No signs came up", [
            "None of these signs came up. If gambling ever starts to feel",
            "hard to control, this check and the support here will still be here.",
        ])
    if yes_count < HIGH_THRESHOLD:
        return ("Some signs came up", [
            f"{yes_count} of {len(SELF_CHECK_QUESTIONS)} signs came up. That is not a diagnosis,",
            "but it is worth taking seriously. Talk to someone you trust,",
            "and consider a Gamblers Anonymous meeting or a counselor.",
        ])
    return ("Help is there", [
        f"{yes_count} of {len(SELF_CHECK_QUESTIONS)} answers were yes. Gamblers Anonymous says most people",
        f"with a gambling problem answer yes to {HIGH_THRESHOLD} or more questions like these.",
        "",
        "This is not a diagnosis, but it is a strong sign that gambling is",
        "hurting you. You are not alone, and people really do recover.",
        "",
        "Help is there. The right step is to reach out today.",
    ])


def _header(title):
    print()
    print("=" * WIDTH)
    print(title.center(WIDTH))
    print("=" * WIDTH)
    print()


def _link(link):
    print(f"{link[0]}: {link[1]}")


def rehab_info():
    _header("HOW REHAB CAN HELP")
    print("Rehab (treatment) is structured help for addiction.")
    print("It can be a stay at a facility, a day program, or regular visits")
    print("while you live at home. What is offered depends on where you live.")
    print()
    print("How it can help people with gambling addiction:")
    print("- A safe, structured space away from betting and triggers.")
    print("- Talking therapy (often CBT) to change the thoughts and habits")
    print("  that keep the gambling going.")
    print("- Support from counselors and from others who understand.")
    print("- Practical help with debt, money and repairing relationships.")
    print("- A plan for staying well once treatment ends.")
    print()
    print("It works well together with Gamblers Anonymous meetings.")
    print("Your doctor or a counselor can tell you what is available near you.")
    print("In this game you can try it from the journey menu: Go to Rehabilitation.")
    print()
    _link(LINK_GO_GA)
    _link(LINK_THERAPY)
    input("Press Enter to continue...")


def gambling_support_page():
    """Shown when someone says gambling is one of their addictions."""
    while True:
        _header("SUPPORT FOR GAMBLING")
        print("You chose gambling. Thank you for being honest about it.")
        print("You don't have to do this alone. Real help is free and available now:")
        print()
        _link(LINK_GO_GA)
        _link(LINK_GA_ONLINE)
        print()
        print("1. How rehab can help people with gambling addiction")
        print("2. Continue my journey")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            rehab_info()
        elif choice == "2":
            return
        else:
            print("Invalid option.")


def offer_gambling_support(previous, current):
    """Show the support page the moment gambling is newly chosen."""
    if "gambling" in current and "gambling" not in previous:
        gambling_support_page()
        return True
    return False


def struggling_now():
    _header("GET HELP NOW")
    print("Take a slow breath. The urge will pass, even when it doesn't feel like it.")
    print()
    print("Right now you can:")
    print("- Put distance between you and gambling: close betting apps,")
    print("  hand your phone or cards to someone you trust.")
    print("- Tell one person how you feel. Call or message them.")
    print("- Join a live online Gamblers Anonymous meeting. It's free and anonymous.")
    print()
    _link(LINK_GA_ONLINE)
    print()
    print(EMERGENCY)
    input("Press Enter to continue...")


def find_meeting():
    _header("FIND A MEETING")
    print("Gamblers Anonymous is a free fellowship of people who help each other")
    print("stop gambling. The only requirement is a wish to stop.")
    print("You never have to speak, and you can use just a first name.")
    print()
    _link(LINK_GA_ONLINE)
    _link(LINK_GA_DIRECTORY)
    _link(LINK_GA_UK)
    print()
    print("Family and friends can find support too:")
    _link(LINK_GAM_ANON)
    input("Press Enter to continue...")


def other_support():
    _header("GET HELP NOW")
    print("More places to turn to:")
    print()
    _link(LINK_THERAPY)
    _link(LINK_GA_HOME)
    print()
    print("In the US you can call 1-800-GAMBLER.")
    print("Your doctor or a counselor can also help, and you can ask them")
    print("about treatment for gambling.")
    print()
    print(EMERGENCY)
    input("Press Enter to continue...")


def self_check():
    _header("GAMBLING SELF-CHECK")
    total = len(SELF_CHECK_QUESTIONS)
    print(f"{total} short yes/no questions about your gambling.")
    print("This is a reflection, not a diagnosis. Answer honestly.")
    print("Nothing is saved or shared.")
    print()
    print("Gamblers Anonymous has its own version too:")
    _link(LINK_GA_20Q)
    print()

    yes = 0
    for number, question in enumerate(SELF_CHECK_QUESTIONS, 1):
        said_yes = ask_yes_no(f"Question {number} of {total}: {question}")
        if said_yes:
            yes += 1
        if said_yes and LAST_QUESTION_IS_CRISIS and number == total:
            print()
            print("Thank you for telling the truth. That matters.")
            print("Please reach out to someone right now.")
            print(EMERGENCY)
            input("Press Enter to continue...")

    title, lines = interpret(yes)
    _header("GAMBLING SELF-CHECK")
    print(f"{title}.")
    print()
    for line in lines:
        print(line)
    print()

    if yes >= HIGH_THRESHOLD:
        _link(LINK_GO_GA)
        _link(LINK_GA_ONLINE)
        print()
        print(EMERGENCY)
        while True:
            print()
            print("1. How rehab can help people with gambling addiction")
            print("2. Back")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                rehab_info()
            elif choice == "2":
                break
            else:
                print("Invalid option.")
        return yes

    if yes > 0:
        _link(LINK_GO_GA)
        _link(LINK_GA_ONLINE)
        print()
    print(EMERGENCY)
    input("Press Enter to continue...")
    return yes


def help_session():
    """The 'Get help now' menu. Can be opened from the main menu, the journey menu,
    or the Help button that is visible on every screen of the app."""
    while True:
        _header("GET HELP NOW")
        print("You are not alone, and reaching out is a strong thing to do.")
        print("These are real people and real services.")
        print()
        print("1. I'm struggling right now")
        print("2. Find a real Gamblers Anonymous meeting")
        print("3. Take the gambling self-check (20 questions)")
        print("4. Other places to get support")
        print("5. Back to the game")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            struggling_now()
        elif choice == "2":
            find_meeting()
        elif choice == "3":
            self_check()
        elif choice == "4":
            other_support()
        elif choice == "5":
            return
        else:
            print("Invalid option.")
