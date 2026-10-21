"""Replaces print() and input() so the unchanged terminal game can run inside an app.
No Kivy imports here, so it can be tested anywhere."""
import builtins
import queue
import re

_EMOJI = re.compile(
    "[\U0001F000-\U0001FFFF\u2190-\u21FF\u2300-\u23FF\u2600-\u27BF"
    "\u2B00-\u2BFF\uFE0F\u200D]"
)


def strip_emoji(text):
    lines = []
    for line in text.split("\n"):
        starts_with_emoji = bool(line) and bool(_EMOJI.match(line))
        cleaned = _EMOJI.sub("", line)
        if starts_with_emoji:
            cleaned = cleaned.lstrip()
        lines.append(cleaned.rstrip() if cleaned.strip() == "" else cleaned)
    return "\n".join(lines)


class ConsoleBridge:
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

    def _emit(self, text):
        if self.remove_emoji:
            text = strip_emoji(text)
        self.on_output(text)

    def print(self, *args, sep=" ", end="\n", **kwargs):
        self._emit(sep.join(str(a) for a in args) + end)

    def input(self, prompt=""):
        if prompt:
            self._emit(str(prompt))
        self.on_input_needed()
        answer = self.answers.get()
        self._emit(answer + "\n")
        return answer

    def submit(self, text):
        self.answers.put(text)
