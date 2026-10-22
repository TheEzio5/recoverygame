WIDTH = 33

# --- addictions the player can recover from (key -> label) ---
ADDICTIONS = {
    "gambling": "Gambling",
    "alcohol": "Alcohol",
    "substances": "Substances",
    "internet_games": "Internet and games",
}

# --- in-game day ---
DAY_START_HOUR = 8
DAY_END_HOUR = 24
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]

# --- rehabilitation rules (the game's own simulation rules) ---
REHAB_DURATIONS = {"1": 7, "2": 14, "3": 30, "4": 90}
LAPTOP_FROM = 9      # closed section: laptop returned at 09:00
LAPTOP_UNTIL = 21    # ...and handed in at 21:00
PROTECTED_DAILY_LIMIT = 4   # euro, only if the player chooses the rule

# --- recovery milestones (days) ---
MILESTONES = [1, 7, 30, 60, 90, 180, 365, 730]
