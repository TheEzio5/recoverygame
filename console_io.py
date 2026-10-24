"""Replaces print() and input() so the unchanged terminal game can run inside an app.
No Kivy imports here, so it can be tested anywhere."""
import builtins
import queue
import re

HELP_TOKEN = "\x00help"        # sent by the always-visible Help button

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
    """Collects what the game prints. When the game asks a question, on_input_needed(prompt, block)
    is called from the game thread, where block = everything printed since the last question.
    If the Help button is pressed, help_handler() runs inside the game thread and the
    original question is asked again afterwards."""

    def __init__(self, on_input_needed, remove_emoji=True, help_handler=None):
        self.on_input_needed = on_input_needed
        self.remove_emoji = remove_emoji
        self.help_handler = help_handler
        self.in_help = False
        self.answers = queue.Queue()
        self._buffer = []
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

    def take_buffer(self):
        text = "".join(self._buffer)
        self._buffer = []
        return text

    def print(self, *args, sep=" ", end="\n", **kwargs):
        self._buffer.append(self._clean(sep.join(str(a) for a in args) + end))

    def input(self, prompt=""):
        prompt = self._clean(str(prompt))
        block = self.take_buffer()
        while True:
            self.on_input_needed(prompt, block)
            answer = self.answers.get()
            if answer != HELP_TOKEN:
                return answer
            if self.help_handler is not None and not self.in_help:
                self.in_help = True
                try:
                    self.help_handler()
                finally:
                    self.in_help = False
                    self.take_buffer()          # drop leftovers, then re-ask the same question
            # (help pressed while already in help: just show the same screen again)

    def submit(self, text):
        self.answers.put(text)
