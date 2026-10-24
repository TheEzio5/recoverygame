"""Real-world help. Everything here points to real, free services.
The self-check is NOT a diagnosis, it is a short reflection."""
from constants import WIDTH
from utils import ask_yes_no

#this is help_support.py

LINK_GA_ONLINE = ("Online GA meetings, any time", "https://gamblersinrecovery.com")
LINK_GA_DIRECTORY = ("GA international meeting directory", "https://gamblersanonymous.org/mtgdirTOP.html")
LINK_GA_UK = ("GA England, Wales and Ulster", "https://www.gamblersanonymous.org.uk/find-a-meeting")
LINK_GA_HOME = ("Gamblers Anonymous", "https://gamblersanonymous.org")
LINK_GA_20Q = ("GA's own 20 questions", "https://gamblersanonymous.org/20questions.html")
LINK_THERAPY = ("Gambling Therapy, free online support", "https://gamblingtherapy.org")
LINK_GAM_ANON = ("Gam-Anon, for family and friends", "https://gam-anon.org")

EMERGENCY = ("If you are in danger or thinking about harming yourself,\n"
             "call your local emergency number now (112 in the EU).")

# Plain-language questions based on the nine signs clinicians look at
# (DSM-5, gambling disorder). Our own wording; answered about the last 12 months.
SELF_CHECK_QUESTIONS = [
    "Have you needed to bet more and more money to feel the same excitement?",
    "Have you felt restless or irritable when you tried to cut down or stop gambling?",
    "Have you tried more than once to cut back or stop, and not managed to?",
    "Do thoughts about gambling take up a lot of your mind (reliving bets, planning the next one, finding money)?",
    "Do you often gamble when you feel down, anxious, guilty or helpless?",
    "After losing, do you often go back another day to win it back?",
    "Have you hidden or lied about how much you gamble?",
    "Has gambling put a relationship, job, study or opportunity at risk, or cost you one?",
    "Have you relied on other people to give or lend you money to fix problems gambling caused?",
]


def interpret(yes_count):
    """Returns (title, lines) for the number of 'yes' answers."""
    if yes_count == 0:
        return ("No signs came up", [
            "None of these signs came up. If gambling ever starts to feel",
            "hard to control, this check and the support here will still be here.",
        ])
    if yes_count < 4:
        return ("Some signs came up", [
            f"{yes_count} sign(s) came up. That doesn't mean you have a gambling problem,",
            "but it is worth taking seriously. Talk to someone you trust,",
            "and consider a Gamblers Anonymous meeting or a counselor.",
        ])
    return ("Many signs came up", [
        f"{yes_count} of 9 signs came up. Clinicians start to look closely at gambling",
        "when four or more of these show up within a year.",
        "This is not a diagnosis. Only a professional can do that,",
        "but please talk with a doctor, a counselor or a GA meeting soon.",
        "You are not alone, and people do recover.",
    ])


def _header(title):
    print()
    print("=" * WIDTH)
    print(title.center(WIDTH))
    print("=" * WIDTH)
    print()


def _link(link):
    print(f"{link[0]}: {link[1]}")


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
    print("This is a short reflection, not a diagnosis.")
    print("Think about the last 12 months and answer honestly.")
    print("Nothing is saved or shared.")
    print()

    yes = 0
    total = len(SELF_CHECK_QUESTIONS)
    for number, question in enumerate(SELF_CHECK_QUESTIONS, 1):
        if ask_yes_no(f"Question {number} of {total}: {question}"):
            yes += 1

    title, lines = interpret(yes)
    _header("GAMBLING SELF-CHECK")
    print(f"{title}.")
    print()
    for line in lines:
        print(line)
    print()
    print("Gamblers Anonymous also has its own well-known list of 20 questions:")
    _link(LINK_GA_20Q)
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
        print("3. Take the gambling self-check")
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
