"""Replaces print() and input() so the unchanged terminal game can run inside an app.
No Kivy imports here, so it can be tested anywhere."""
import builtins
import queue
import re

_EMOJI = re.compile(
    "[\U0001F000-\U0001FFFF\u2190-\u21FF\u2300-\u23FF\u2600-\u27BF"
    "\u2B00-\u2BFF\uFE0F\u200D]"
)

# emoji that carry meaning get a text stand-in before the rest are removed
_KEEP = {"✅": "[x]", "🔒": "(locked)"}


def strip_emoji(text):
    for emoji, stand_in in _KEEP.items():
        text = text.replace(emoji, stand_in)
    lines = []
    for line in text.split("\n"):
        starts_with_emoji = bool(line) and bool(_EMOJI.match(line))
        cleaned = _EMOJI.sub("", line)
        if starts_with_emoji:
            cleaned = cleaned.lstrip()
        lines.append(cleaned.rstrip() if cleaned.strip() == "" else cleaned)
    return "\n".join(lines)


class ConsoleBridge:
    """on_output(text): called for everything the game prints.
    on_input_needed(prompt): called (from the game thread) when the game asks a question."""

    def __init__(self, on_output, on_input_needed, remove_emoji=True):
        self.on_output = on_output
        self.on_input_needed = on_input_needed
        self.remove_emoji = remove_emoji
        self.answers = queue.Queue()
        self._real_print = builtins.print
        self._real_input = builtins.input

    def install(self):
        builtins.print = self.print
        builtins.input = self.input

    def uninstall(self):
        builtins.print = self._real_print
        builtins.input = self._real_input

    def _clean(self, text):
        return strip_emoji(text) if self.remove_emoji else text

    def print(self, *args, sep=" ", end="\n", **kwargs):
        self.on_output(self._clean(sep.join(str(a) for a in args) + end))

    def input(self, prompt=""):
        self.on_input_needed(self._clean(str(prompt)))
        return self.answers.get()

    def submit(self, text):
        self.answers.put(text)
