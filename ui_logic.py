"""Turns the game's text into touch-screen pieces (buttons, pictures).
Pure Python (no Kivy) so it is easy to test. The game itself is not changed:
we read what it printed, find its numbered menus, and show them as tiles."""
import re

from rehab_rules import DURATION

OPTION_RE = re.compile(r"^\s*(\d{1,2})\.\s+(.+?)\s*$")
YESNO_RE = re.compile(r"\(1\s*=\s*yes,\s*2\s*=\s*no\)", re.I)
NUMBER_PROMPT_RE = re.compile(r"how many|how much|limit in", re.I)
LINK_RE = re.compile(r"^\s*(?:(.+?)\s*:\s*)?(https?://\S+?)\s*$")

# header text printed by the game -> banner picture
TITLE_BANNERS = {
    "RECOVERY QUEST": "title",
    "MAIN MENU": "title",
    "G.A. MEETING": "ga",
    "WORK": "work",
    "EXERCISE": "exercise",
    "PROGRAMMING": "programming",
    "REST": "rest",
    "REHABILITATION": "rehab",
    "END OF DAY": "endday",
    "FINANCES": "finances",
    "SAFEGUARDS": "safeguards",
    "RECOVERY STORY": "story",
    "PLAYER STATUS": "status",
    "I RELAPSED TODAY": "relapse",
    "WELCOME BACK": "welcome",
    "GET HELP NOW": "help",
    "GAMBLING SELF-CHECK": "test",
    "FIND A MEETING": "ga",
    "SUPPORT FOR GAMBLING": "help",
    "HOW REHAB CAN HELP": "rehab",
}
# headers that are only decoration (the banner already shows them)
DROP_TITLES = set(TITLE_BANNERS) | {"YOUR JOURNEY"}

# keyword in a menu label -> icon picture (first match wins)
ICON_RULES = [
    ("get help", "help"),
    ("struggling", "help"),
    ("other places", "help"),
    ("self-check", "test"),
    ("gamblers anonymous", "ga"),
    ("g.a.", "ga"),
    ("rehabilitation", "rehab"),
    ("rehab", "rehab"),
    ("work", "work"),
    ("exercise", "exercise"),
    ("programming", "programming"),
    ("rest", "rest"),
    ("status", "status"),
    ("return", "back"),
    ("back", "back"),
    ("save", "save"),
    ("end the day", "endday"),
    ("finances", "finances"),
    ("safeguards", "safeguards"),
    ("recovery story", "story"),
    ("relapsed", "relapse"),
    ("start journey", "start"),
    ("load journey", "load"),
    ("exit", "exit"),
]


class Option:
    def __init__(self, number, label, locked=False, checked=False, hint=""):
        self.number = number
        self.label = label
        self.locked = locked
        self.checked = checked
        self.hint = hint            # e.g. "8 h": how much game time it takes

    def __repr__(self):
        return f"Option({self.number!r}, {self.label!r}, locked={self.locked}, checked={self.checked})"


class Screen:
    """Everything the UI needs for one question from the game."""

    def __init__(self, lines, options, banner, mode, prompt, links=None):
        self.links = links or []    # [(label, url)] -> tiles that open the browser
        self.lines = lines          # text to show in the log area
        self.options = options      # list[Option] -> tiles
        self.banner = banner        # picture key or None (keep current)
        self.mode = mode            # buttons | continue | yesno | number | text
        self.prompt = prompt

    @property
    def text(self):
        return "\n".join(self.lines)


def icon_for(label):
    low = label.lower()
    for word, key in ICON_RULES:
        if word in low:
            return key
    return None


def time_hint(label):
    """How much in-game time a journey menu choice costs."""
    low = label.lower()
    if low.startswith("go to rehabilitation"):
        return ""
    if low.startswith("rehabilitation activity"):
        return f"{DURATION['rehab']} h"
    if "end the day" in low:
        return "until morning"
    key = {"ga": "ga", "work": "work", "exercise": "exercise",
           "programming": "programming", "rest": "rest"}.get(icon_for(label))
    return f"{DURATION[key]} h" if key else ""


def find_links(lines):
    """Lines like 'Label: https://example.org' become tappable link tiles."""
    found, seen = [], set()
    for line in lines:
        m = LINK_RE.match(line)
        if not m:
            continue
        label, url = m.group(1), m.group(2)
        if url in seen:
            continue
        seen.add(url)
        if not label:
            label = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        found.append((label.strip(), url))
    return found


def _clean_label(label):
    locked = "(locked)" in label
    checked = "[x]" in label
    label = label.replace("(locked)", "").replace("[x]", "").strip()
    return label, locked, checked


def _find_menu(lines):
    """The last run of consecutive numbered lines (2+ long, counting up)."""
    best = None
    i = 0
    while i < len(lines):
        m = OPTION_RE.match(lines[i])
        if not m:
            i += 1
            continue
        j, expected = i, int(m.group(1))
        while j < len(lines):
            mj = OPTION_RE.match(lines[j])
            if not mj or int(mj.group(1)) != expected:
                break
            expected += 1
            j += 1
        if j - i >= 2:
            best = (i, j)
        i = max(j, i + 1)
    return best


def _tidy(lines):
    out = []
    for line in lines:
        s = line.strip()
        if s and set(s) <= set("=-"):
            continue                       # decoration lines
        if s.upper() in DROP_TITLES:
            continue                       # shown as a picture instead
        if not s and (not out or not out[-1]):
            continue                       # no double blank lines
        out.append(s)
    while out and not out[-1]:
        out.pop()
    return out


def build_screen(text, prompt):
    """text = everything printed since the last question, prompt = the question."""
    raw = text.split("\n")
    banner = None
    for line in raw:
        key = TITLE_BANNERS.get(line.strip().upper())
        if key:
            banner = key

    menu = _find_menu([l for l in raw])
    options = []
    rest = raw
    if menu:
        start, end = menu
        for line in raw[start:end]:
            m = OPTION_RE.match(line)
            label, locked, checked = _clean_label(m.group(2))
            options.append(Option(m.group(1), label, locked, checked))
        rest = raw[:start] + raw[end:]
        labels = " ".join(o.label for o in options)
        if "Attend G.A. Meeting" in labels:          # the journey menu
            for o in options:
                o.hint = time_hint(o.label)
        if banner is None:
            if "Attend G.A. Meeting" in labels:
                banner = "journey"
            elif "Start Journey" in labels:
                banner = "title"

    lines = _tidy(rest)
    low = prompt.lower()

    if "press enter" in low:
        mode = "continue"
    elif YESNO_RE.search(prompt):
        mode = "yesno"
    elif options:
        mode = "buttons"
    elif NUMBER_PROMPT_RE.search(prompt):
        mode = "number"
    else:
        mode = "text"

    # a typed question is part of the screen, a "Choose an option:" is not
    if mode in ("yesno", "number", "text") and prompt.strip():
        shown = YESNO_RE.sub("", prompt).strip().rstrip(":").strip() if mode == "yesno" else prompt.strip()
        if lines and lines[-1]:
            lines.append("")
        lines.append(shown)

    return Screen(lines, options, banner, mode, prompt, find_links(raw))


STAT_INFO = [
    ("Willpower", "willpower", "Your strength to resist urges."),
    ("Hope", "hope", "Belief that things can get better."),
    ("Energy", "energy", "Fuel for activities. Rest and sleep restore it."),
    ("Confidence", "confidence", "Trust in yourself. Grows with honest effort."),
    ("Urge", "urge", "The pull toward old habits. Lower is better."),
]


def status_text(player):
    """The whole status as plain text (used as a fallback and for tests)."""
    lines = [
        f"{player.name}  -  Level {player.level}",
        f"Recovery days: {player.recovery_days}   Journey days: {player.journey_days}",
        f"Money: €{player.money}   Debt: €{player.debt}",
        f"Recovering from: {player.addiction_names()}",
    ]
    if player.in_rehabilitation:
        lines.append(f"{player.rehab_section.capitalize()} rehabilitation, "
                     f"{player.rehab_days_remaining} day(s) left")
    lines.append("")
    for label, attr, meaning in STAT_INFO:
        lines.append(f"{label}: {getattr(player, attr)} / 100")
        lines.append(meaning)
    lines.append(f"Experience: {player.experience} / {player.next_level}")
    lines.append("Fills up to raise your level.")
    return "\n".join(lines)
