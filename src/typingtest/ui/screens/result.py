"""Result screen — displayed after completing a test with animated score reveal."""

from __future__ import annotations

from textual import events, work
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Center, Middle, Vertical
from textual.widgets import Static, Footer
from rich.text import Text

from typingtest.core.config import load_history


# ── Rank system ───────────────────────────────────────────────────────

def _compute_rank(wpm: float, accuracy: float) -> tuple[str, str, str]:
    """Return (rank_letter, rank_label, rank_color) based on WPM & accuracy."""
    score = wpm * (accuracy / 100)

    if score >= 110:
        return "S+", "Transcendent", "bold bright_magenta"
    elif score >= 95:
        return "S", "Master", "bold bright_cyan"
    elif score >= 80:
        return "A", "Expert", "bold cyan"
    elif score >= 65:
        return "B", "Advanced", "bold green"
    elif score >= 50:
        return "C", "Intermediate", "bold yellow"
    elif score >= 35:
        return "D", "Beginner", "bold dark_orange"
    else:
        return "E", "Novice", "bold red"


# ── Score breakdown ───────────────────────────────────────────────────

def _compute_score_breakdown(wpm: int, accuracy: float, best_streak: int, time_s: float) -> list[tuple[str, int, str]]:
    """Return list of (label, points, color) for the animated score reveal."""
    breakdown = []

    wpm_pts = wpm * 10
    breakdown.append(("Speed", wpm_pts, "bold bright_cyan"))

    if accuracy >= 100:
        acc_pts = 500
    elif accuracy >= 95:
        acc_pts = int((accuracy - 90) * 50)
    elif accuracy >= 80:
        acc_pts = int((accuracy - 80) * 10)
    else:
        acc_pts = 0
    breakdown.append(("Accuracy", acc_pts, "bold green"))

    streak_pts = best_streak * 2
    breakdown.append(("Streak", streak_pts, "bold bright_yellow"))

    if wpm >= 100:
        breakdown.append(("Bonus", 300, "bold bright_magenta"))
    elif wpm >= 80:
        breakdown.append(("Bonus", 150, "bold cyan"))
    elif wpm >= 60:
        breakdown.append(("Bonus", 50, "bold yellow"))

    if accuracy >= 100:
        breakdown.append(("Perfect!", 200, "bold bright_magenta"))
    elif accuracy >= 98:
        breakdown.append(("Flawless", 100, "bold bright_cyan"))

    return breakdown


class ResultScreen(Screen):
    """Shows animated score reveal with progressive point tallying."""

    BINDINGS = [
        Binding("tab", "retry", "New test", show=True),
        Binding("escape", "go_back", "Back", show=True),
        Binding("ctrl+h", "show_history", "History", show=True),
        Binding("ctrl+q", "quit_app", "Quit", show=True),
    ]

    DEFAULT_CSS = """
    ResultScreen {
        align: center middle;
    }
    ResultScreen #result-box {
        width: 50;
        height: auto;
        padding: 1 3;
        border: round $accent;
        content-align: center middle;
        text-align: center;
    }
    ResultScreen #result-header {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-align: center;
    }
    ResultScreen #result-stats {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-align: center;
    }
    ResultScreen #score-breakdown {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-align: center;
    }
    ResultScreen #score-total {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-align: center;
    }
    ResultScreen #result-hint {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-align: center;
        color: $text-disabled;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._anim_step: int = 0
        self._anim_timer = None
        self._score_data: dict = {}
        self._breakdown: list[tuple[str, int, str]] = []
        self._displayed_total: int = 0
        self._target_total: int = 0
        self._counting_up: bool = False
        self._count_timer = None

    def compose(self):
        history = load_history()
        last = history[-1] if history else {}
        self._score_data = last

        wpm = last.get("wpm", 0)
        raw = last.get("raw_wpm", 0)
        acc = last.get("accuracy", 0)
        time_s = last.get("time", 0)
        lang = last.get("language", "---")
        best_streak = last.get("best_streak", 0)
        is_pb = last.get("is_personal_best", False)

        rank_letter, rank_label, rank_color = _compute_rank(wpm, acc)
        self._breakdown = _compute_score_breakdown(wpm, acc, best_streak, time_s)
        self._target_total = sum(pts for _, pts, _ in self._breakdown)

        # Build compact header: rank + label on one line
        header_parts = f"[{rank_color}][ {rank_letter} ][/]  [{rank_color}]{rank_label}[/]"
        if is_pb:
            header_parts += "  [bold bright_yellow]🏆 PB![/]"

        # Build compact stats: all on 2 lines
        streak_bit = ""
        if best_streak > 0:
            si = "🔥" if best_streak >= 15 else "✦"
            streak_bit = f"  {si} {best_streak}"

        stats_text = (
            f"⌨ {wpm} wpm (raw {raw})  ◎ {acc}%{streak_bit}\n"
            f"⏱ {time_s}s  •  {lang}"
        )

        with Middle():
            with Center():
                with Vertical(id="result-box"):
                    yield Static(header_parts, id="result-header")
                    yield Static(stats_text, id="result-stats")
                    yield Static("", id="score-breakdown")
                    yield Static("", id="score-total")
                    yield Static("Tab → new  •  Esc → back", id="result-hint")
        yield Footer()

    def on_mount(self) -> None:
        self._anim_step = 0
        self._displayed_total = 0
        self._anim_timer = self.set_timer(0.3, self._reveal_next_line)

    def _reveal_next_line(self) -> None:
        if self._anim_step >= len(self._breakdown):
            self._start_count_up()
            return

        # Compact: show breakdown as "label +pts" segments on fewer lines
        parts = []
        for i in range(self._anim_step + 1):
            label, pts, color = self._breakdown[i]
            parts.append(f"[{color}]{label}[/] [bold white]+{pts}[/]")

        # Join with separator, wrapping every 3 items
        lines = []
        for j in range(0, len(parts), 3):
            lines.append("  ".join(parts[j:j+3]))

        try:
            bd = self.query_one("#score-breakdown", Static)
            bd.update("\n".join(lines))
        except Exception:
            return

        self._anim_step += 1
        self._anim_timer = self.set_timer(0.3, self._reveal_next_line)

    def _start_count_up(self) -> None:
        self._displayed_total = 0
        self._counting_up = True
        self._count_timer = self.set_interval(0.02, self._tick_count)

    def _tick_count(self) -> None:
        if self._displayed_total >= self._target_total:
            self._displayed_total = self._target_total
            self._counting_up = False
            if self._count_timer is not None:
                self._count_timer.stop()
                self._count_timer = None
            self._update_total_display()
            return

        step = max(1, self._target_total // 40)
        self._displayed_total = min(self._displayed_total + step, self._target_total)
        self._update_total_display()

    def _update_total_display(self) -> None:
        try:
            tw = self.query_one("#score-total", Static)
            if self._displayed_total >= self._target_total:
                tw.update(
                    f"[bold bright_yellow]━━━  TOTAL {self._target_total:,} pts  ━━━[/]"
                )
            else:
                tw.update(
                    f"[bold white]━━━  TOTAL {self._displayed_total:,} pts  ━━━[/]"
                )
        except Exception:
            pass

    def action_retry(self) -> None:
        self._cleanup_timers()
        self.app.pop_screen()
        typing_screen = self.app.screen
        if hasattr(typing_screen, "_new_test"):
            typing_screen._new_test()  # type: ignore[attr-defined]

    def action_go_back(self) -> None:
        self._cleanup_timers()
        self.app.pop_screen()

    def action_show_history(self) -> None:
        self.app.push_screen("history")

    def action_quit_app(self) -> None:
        self._cleanup_timers()
        self.app.exit()

    def _cleanup_timers(self) -> None:
        if self._anim_timer is not None:
            try:
                self._anim_timer.stop()
            except Exception:
                pass
            self._anim_timer = None
        if self._count_timer is not None:
            try:
                self._count_timer.stop()
            except Exception:
                pass
            self._count_timer = None
