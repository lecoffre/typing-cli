"""Typing area widget — renders the target text with per-character coloring."""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget
from textual.reactive import reactive

from typingtest.core.tracker import Match, Tracker


class TypingArea(Widget):
    """Displays target text with live character-by-character coloring.

    Supports letter_spacing to visually "zoom" by inserting spaces between chars.
    """

    DEFAULT_CSS = """
    TypingArea {
        width: 100%;
        height: auto;
        min-height: 5;
        padding: 1 2;
        content-align: left middle;
    }
    """

    target_text: reactive[str] = reactive("", layout=True)
    letter_spacing: reactive[int] = reactive(0)

    def __init__(self, target: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.target_text = target
        self.tracker = Tracker(target)

    def reset(self, target: str) -> None:
        """Reset with a new target paragraph."""
        self.target_text = target
        self.tracker = Tracker(target)
        self.refresh()

    def render(self) -> Text:
        text = Text()
        theme = self.app.theme_colors  # type: ignore[attr-defined]
        spacer = " " * self.letter_spacing  # extra spaces between characters

        for i, char in enumerate(self.target_text):
            # determine style for this character
            if i < self.tracker.cursor:
                match self.tracker.results[i]:
                    case Match.CORRECT:
                        style = theme["correct"]
                        if char == " ":
                            display = " "
                        elif char == "\n":
                            display = "↵\n"
                        elif char == "\t":
                            display = "→   "
                        else:
                            display = char
                    case Match.INCORRECT:
                        if char == " ":
                            display = "·"
                        elif char == "\n":
                            display = "↵\n"
                        elif char == "\t":
                            display = "→   "
                        else:
                            display = char
                        style = theme["incorrect"]
                    case _:
                        style = theme["pending"]
                        display = char
            elif i == self.tracker.cursor:
                style = theme["cursor"]
                if char == " ":
                    display = " "
                elif char == "\n":
                    display = "↵\n"
                elif char == "\t":
                    display = "→   "
                else:
                    display = char
            else:
                style = theme["pending"]
                if char == "\n":
                    display = "↵\n"
                elif char == "\t":
                    display = "→   "
                else:
                    display = char

            text.append(display, style=style)

            # add spacing after each char (but not after the last one)
            # skip spacing for newlines and tabs (already handled above)
            if spacer and i < len(self.target_text) - 1 and char not in ("\n", "\t"):
                if char == " ":
                    text.append(spacer, style=theme["pending"])
                else:
                    text.append(spacer, style="")

        return text
