"""Live stats bar — shows WPM, accuracy, progress, streak in real time."""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

from typingtest.core.stats import Stats
from typingtest.core.tracker import Tracker


# ── WPM color tiers ───────────────────────────────────────────────────
# Maps a WPM value to a color for instant speed feedback.

def _wpm_color(wpm: int) -> str:
    if wpm >= 100:
        return "bold bright_cyan"
    elif wpm >= 80:
        return "bold cyan"
    elif wpm >= 60:
        return "bold green"
    elif wpm >= 40:
        return "bold yellow"
    elif wpm >= 20:
        return "bold dark_orange"
    return "bold red"


def _accuracy_color(acc: float) -> str:
    if acc >= 98:
        return "bold bright_cyan"
    elif acc >= 95:
        return "bold green"
    elif acc >= 90:
        return "bold yellow"
    return "bold red"


def _progress_bar(pct: float, width: int = 16) -> Text:
    """Render a compact text-based progress bar."""
    filled = int(pct / 100 * width)
    bar = Text()
    bar.append("▓" * filled, style="bold green")
    bar.append("░" * (width - filled), style="dim")
    bar.append(f" {pct:.0f}%", style="bold white")
    return bar


class StatsBar(Widget):
    """A compact bar showing live typing stats with dynamic colors."""

    DEFAULT_CSS = """
    StatsBar {
        width: 100%;
        height: 1;
        padding: 0 2;
        content-align: center middle;
    }
    """

    def __init__(self, tracker: Tracker | None = None, stats: Stats | None = None, **kwargs):
        super().__init__(**kwargs)
        self.tracker = tracker
        self.stats = stats

    def update_refs(self, tracker: Tracker, stats: Stats) -> None:
        self.tracker = tracker
        self.stats = stats

    def render(self) -> Text:
        if not self.tracker or not self.stats:
            return Text("")

        theme = self.app.theme_colors  # type: ignore[attr-defined]

        # Before the first keypress, show a prompt instead of fake stats
        if not self.stats.started:
            text = Text()
            text.append("  ▸ ", style=theme["accent"])
            text.append("start typing to begin", style=f"italic {theme['dim']}")
            text.append("  ", style=theme["dim"])
            return text

        wpm = self.stats.wpm(self.tracker.cursor)
        acc = self.tracker.accuracy
        elapsed = self.stats.elapsed_display
        paused = self.stats.is_paused
        streak = self.tracker.streak
        streak_label = self.tracker.streak_label
        progress = self.tracker.progress

        text = Text()

        # ── WPM with dynamic color ──
        text.append("  ⌨ ", style=theme["accent"])
        text.append(f"{wpm}", style=_wpm_color(wpm))
        text.append(" wpm", style=theme["dim"])

        # ── Accuracy with dynamic color ──
        text.append("   ◎ ", style=theme["accent"])
        text.append(f"{acc:.0f}", style=_accuracy_color(acc))
        text.append("%", style=theme["dim"])

        # ── Timer ──
        text.append("   ⏱ ", style=theme["accent"])
        text.append(elapsed, style=f"bold {theme['accent']}")

        # ── Streak / combo ──
        if streak >= 5:
            text.append(f"   {streak_label} ", style="bold bright_yellow")
            text.append(f"x{streak}", style="bold bright_yellow")

        # ── Pause indicator ──
        if paused:
            text.append("   ⏸ ", style="bold yellow")
            text.append("paused", style="italic yellow")

        # ── Progress bar ──
        text.append("   ")
        text.append_text(_progress_bar(progress))

        text.append("  ", style=theme["dim"])

        return text
