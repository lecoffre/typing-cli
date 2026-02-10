"""Keypress tracker — tracks every keystroke against the target text."""

from __future__ import annotations

from enum import Enum, auto


class Match(Enum):
    PENDING = auto()    # not yet typed
    CORRECT = auto()    # matches target
    INCORRECT = auto()  # does not match


class Tracker:
    """Compares each typed character against the target text, character by character."""

    def __init__(self, target: str) -> None:
        self.target = target
        self.results: list[Match] = [Match.PENDING] * len(target)
        self.cursor: int = 0  # current position in target
        self.total_correct: int = 0
        self.total_incorrect: int = 0
        self.total_keystrokes: int = 0

        # ── Streak / combo tracking ──
        self.streak: int = 0           # current consecutive correct
        self.best_streak: int = 0      # best streak in this session
        self._last_was_correct: bool = False

    # ── public API ────────────────────────────────────────────────────

    def keypress(self, char: str) -> None:
        """Register a single printable character."""
        if self.cursor >= len(self.target):
            return  # test already complete

        self.total_keystrokes += 1
        if char == self.target[self.cursor]:
            self.results[self.cursor] = Match.CORRECT
            self.total_correct += 1
            self.streak += 1
            self._last_was_correct = True
            if self.streak > self.best_streak:
                self.best_streak = self.streak
        else:
            self.results[self.cursor] = Match.INCORRECT
            self.total_incorrect += 1
            self.streak = 0
            self._last_was_correct = False
        self.cursor += 1

    def backspace(self) -> None:
        """Delete the last typed character."""
        if self.cursor <= 0:
            return
        self.cursor -= 1
        prev = self.results[self.cursor]
        if prev == Match.CORRECT:
            self.total_correct -= 1
        elif prev == Match.INCORRECT:
            self.total_incorrect -= 1
        self.results[self.cursor] = Match.PENDING
        # recalculate streak from current position backwards
        self.streak = 0
        for i in range(self.cursor - 1, -1, -1):
            if self.results[i] == Match.CORRECT:
                self.streak += 1
            else:
                break

    def ctrl_backspace(self) -> None:
        """Delete the last typed word (back to previous space or start)."""
        if self.cursor <= 0:
            return
        # skip trailing spaces
        while self.cursor > 0 and self.target[self.cursor - 1] == " ":
            self.backspace()
        # delete word chars
        while self.cursor > 0 and self.target[self.cursor - 1] != " ":
            self.backspace()

    @property
    def finished(self) -> bool:
        return self.cursor >= len(self.target)

    @property
    def accuracy(self) -> float:
        total = self.total_correct + self.total_incorrect
        return (self.total_correct / total * 100) if total > 0 else 100.0

    @property
    def progress(self) -> float:
        return self.cursor / len(self.target) * 100 if self.target else 0

    @property
    def streak_label(self) -> str:
        """Visual flame indicator based on streak length."""
        if self.streak >= 50:
            return "🔥🔥🔥"
        elif self.streak >= 30:
            return "🔥🔥"
        elif self.streak >= 15:
            return "🔥"
        elif self.streak >= 5:
            return "✦"
        return ""
