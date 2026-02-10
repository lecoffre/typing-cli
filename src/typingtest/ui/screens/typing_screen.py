"""Typing screen — the main typing test experience."""

from __future__ import annotations

from datetime import datetime

from textual import events, work
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Center, Vertical, Middle
from textual.widgets import Static, Footer

from typingtest.core.config import (
    LANGUAGES, THEMES, MODES, ZOOM_PRESETS, cycle_option, load_config,
    save_config, load_history, zoom_in, zoom_out,
)
from typingtest.core.generator import generate_paragraph, generate_code_snippet, CODE_LANGUAGES
from typingtest.core.stats import Stats
from typingtest.core.tracker import Tracker
from typingtest.ui.widgets.typing_area import TypingArea
from typingtest.ui.widgets.stats_bar import StatsBar
from typingtest.ui.widgets.character import CharacterWidget


# ── WPM milestones ────────────────────────────────────────────────────
# (threshold, emoji, label) — triggers once each when WPM crosses upward

_MILESTONES = [
    (30,  "⚡",  "Getting started!"),
    (50,  "🔥",  "On fire!"),
    (70,  "💫",  "Impressive!"),
    (80,  "⚡⚡", "Lightning fast!"),
    (100, "🚀",  "Rocket speed!"),
    (120, "👑",  "Legendary!"),
]

_STREAK_MILESTONES = [
    (25,  "✦",  "25 streak!"),
    (50,  "🔥",  "50 combo!"),
    (100, "💎",  "100 combo! Unstoppable!"),
]


class TypingScreen(Screen):
    """Main typing test screen."""

    BINDINGS = [
        Binding("tab", "restart_tab", "Restart", show=True),
        Binding("ctrl+r", "restart_ctrlr", "Restart", show=True),
        Binding("escape", "go_back", "Back", show=True),
        Binding("ctrl+t", "cycle_theme", "Theme", show=True),
        Binding("ctrl+l", "cycle_language", "Language", show=True),
        Binding("ctrl+g", "cycle_mode", "Mode", show=True),
        Binding("ctrl+k", "cycle_code_lang", "Code lang", show=True),
        Binding("ctrl+h", "show_history", "History", show=True),
        Binding("ctrl+equal", "zoom_in", "Zoom+", show=True),
        Binding("ctrl+plus", "zoom_in", "Zoom+", show=False),
        Binding("ctrl+minus", "zoom_out", "Zoom-", show=True),
        Binding("ctrl+q", "quit_app", "Quit", show=True),
    ]

    DEFAULT_CSS = """
    TypingScreen {
        align: center middle;
    }
    TypingScreen #typing-container {
        width: 80;
        max-width: 90%;
        height: auto;
        padding: 1 0;
    }
    TypingScreen #info-bar {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-align: center;
        margin-bottom: 1;
        color: $text-disabled;
    }
    TypingScreen #milestone-bar {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-align: center;
        margin-bottom: 1;
    }
    TypingScreen #char-row {
        width: 100%;
        height: auto;
        align: center middle;
        content-align: center middle;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg = load_config()
        self.stats = Stats()
        self._timer_handle = None
        self._reached_milestones: set[int] = set()
        self._reached_streak_milestones: set[int] = set()
        self._personal_best: float = self._load_personal_best()
        self._milestone_clear_handle = None

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Dynamically show/hide bindings based on current mode."""
        is_code = self.cfg.get("mode", "words") == "code"
        if action == "restart_tab":
            return not is_code          # hide in code mode
        if action == "restart_ctrlr":
            return is_code              # hide in words mode
        if action == "cycle_language":
            return not is_code          # hide in code mode
        if action == "cycle_code_lang":
            return is_code              # hide in words mode
        return True

    def _load_personal_best(self) -> float:
        """Get the user's all-time best WPM from history."""
        history = load_history()
        if not history:
            return 0.0
        return max(entry.get("wpm", 0) for entry in history)

    def compose(self):
        with Middle():
            with Vertical(id="typing-container"):
                yield Static(self._info_text(), id="info-bar")
                yield Static("", id="milestone-bar")
                with Center(id="char-row"):
                    yield CharacterWidget(id="character")
                yield StatsBar(id="stats-bar")
                yield TypingArea(id="typing-area")
        yield Footer()

    def on_mount(self) -> None:
        self._new_test()

    # ── Test lifecycle ────────────────────────────────────────────────

    def _info_text(self) -> str:
        mode = self.cfg.get("mode", "words")
        theme = self.cfg.get("theme", "midnight")
        zoom = self.cfg.get("zoom", 1)
        zoom_label = ZOOM_PRESETS.get(zoom, ZOOM_PRESETS[1])["label"]

        if mode == "code":
            code_lang = self.cfg.get("code_language", "python")
            return f"  {code_lang}  •  code mode  •  {theme}  •  {zoom_label}  "
        else:
            lang = self.cfg.get("language", "english")
            wc = self.cfg.get("word_count", 30)
            return f"  {lang}  •  {theme}  •  {wc} words  •  {zoom_label}  "

    def _apply_zoom(self) -> None:
        """Apply current zoom preset to the typing container and area."""
        zoom = self.cfg.get("zoom", 1)
        preset = ZOOM_PRESETS.get(zoom, ZOOM_PRESETS[1])

        container = self.query_one("#typing-container")
        container.styles.width = preset["width"]
        container.styles.padding = (preset["padding_y"], preset["padding_x"])

        area = self.query_one("#typing-area", TypingArea)
        area.letter_spacing = preset["letter_spacing"]
        area.styles.padding = (preset["line_height"], preset["padding_x"])
        area.refresh(layout=True)

    def _new_test(self) -> None:
        mode = self.cfg.get("mode", "words")

        if mode == "code":
            code_lang = self.cfg.get("code_language", "python")
            paragraph = generate_code_snippet(code_lang)
        else:
            lang = self.cfg.get("language", "english")
            wc = self.cfg.get("word_count", 30)
            paragraph = generate_paragraph(lang, wc)

        self.stats = Stats()
        self._reached_milestones = set()
        self._reached_streak_milestones = set()
        self._personal_best = self._load_personal_best()

        # clear milestone display
        if self._milestone_clear_handle is not None:
            self._milestone_clear_handle.stop()
            self._milestone_clear_handle = None
        try:
            self.query_one("#milestone-bar", Static).update("")
        except Exception:
            pass

        area = self.query_one("#typing-area", TypingArea)
        area.reset(paragraph)

        bar = self.query_one("#stats-bar", StatsBar)
        bar.update_refs(area.tracker, self.stats)
        bar.refresh()

        info = self.query_one("#info-bar", Static)
        info.update(self._info_text())

        # reset character animation
        try:
            self.query_one("#character", CharacterWidget).reset()
        except Exception:
            pass

        self._apply_zoom()

        # stop any existing timer
        if self._timer_handle is not None:
            self._timer_handle.stop()
            self._timer_handle = None

    @work(thread=False)
    async def _finish_test(self) -> None:
        """Called when the user finishes typing all words."""
        self.stats.stop()
        if self._timer_handle is not None:
            self._timer_handle.stop()
            self._timer_handle = None

        area = self.query_one("#typing-area", TypingArea)
        tracker = area.tracker

        from typingtest.core.config import save_score

        net_wpm = self.stats.net_wpm(tracker.cursor, tracker.accuracy)
        is_pb = net_wpm > self._personal_best and self._personal_best > 0

        mode = self.cfg.get("mode", "words")
        if mode == "code":
            lang_label = self.cfg.get("code_language", "python") + " (code)"
        else:
            lang_label = self.cfg.get("language", "english")

        score = {
            "date": datetime.now().isoformat(timespec="seconds"),
            "wpm": net_wpm,
            "raw_wpm": self.stats.raw_wpm(tracker.cursor),
            "accuracy": round(tracker.accuracy, 1),
            "time": round(self.stats.elapsed, 1),
            "language": lang_label,
            "words": self.cfg.get("word_count", 30) if mode == "words" else 0,
            "best_streak": tracker.best_streak,
            "is_personal_best": is_pb,
        }
        save_score(score)

        self.app.push_screen("result", callback=lambda _: None)

    # ── Milestone display ────────────────────────────────────────────

    def _show_milestone(self, message: str) -> None:
        """Show a milestone in the inline bar (replaces previous) and auto-clear."""
        try:
            bar = self.query_one("#milestone-bar", Static)
            bar.update(message)
        except Exception:
            return

        # cancel any pending clear
        if self._milestone_clear_handle is not None:
            self._milestone_clear_handle.stop()
        # auto-clear after 2.5 seconds
        self._milestone_clear_handle = self.set_timer(
            2.5, self._clear_milestone
        )

    def _clear_milestone(self) -> None:
        try:
            bar = self.query_one("#milestone-bar", Static)
            bar.update("")
        except Exception:
            pass
        self._milestone_clear_handle = None

    def _check_milestones(self, wpm: int, tracker: Tracker) -> None:
        """Fire inline notifications when the user crosses WPM / streak thresholds."""
        for threshold, emoji, label in _MILESTONES:
            if wpm >= threshold and threshold not in self._reached_milestones:
                self._reached_milestones.add(threshold)
                self._show_milestone(
                    f"[bold bright_yellow]{emoji}  {threshold} WPM — {label}[/]"
                )

        streak = tracker.streak
        for threshold, emoji, label in _STREAK_MILESTONES:
            if streak >= threshold and threshold not in self._reached_streak_milestones:
                self._reached_streak_milestones.add(threshold)
                self._show_milestone(
                    f"[bold bright_cyan]{emoji}  {label}[/]"
                )

    # ── Key handling ──────────────────────────────────────────────────

    def on_key(self, event: events.Key) -> None:
        mode = self.cfg.get("mode", "words")
        is_code = mode == "code"

        # Keys that always bypass to Textual's binding system
        bypass_keys = {
            "escape", "ctrl+t", "ctrl+l", "ctrl+h", "ctrl+q",
            "ctrl+plus", "ctrl+equal", "ctrl+minus", "ctrl+g", "ctrl+k",
            "ctrl+r", "tab",
        }

        area = self.query_one("#typing-area", TypingArea)
        tracker = area.tracker

        # In code mode, capture tab for whitespace typing (unless test is done)
        if is_code and not tracker.finished:
            bypass_keys.discard("tab")

        if event.key in bypass_keys:
            return

        event.stop()

        if tracker.finished:
            return

        # start timer on first keypress
        self.stats.start()
        self.stats.record_keypress()
        if self._timer_handle is None:
            self._timer_handle = self.set_interval(0.1, self._tick_stats)

        if event.key == "backspace":
            tracker.backspace()
        elif event.key == "ctrl+w" or event.key == "ctrl+backspace":
            tracker.ctrl_backspace()
        elif is_code and event.key == "tab":
            # In code mode, Tab auto-types the next whitespace block (spaces/tab)
            while not tracker.finished and tracker.target[tracker.cursor] in (" ", "\t"):
                tracker.keypress(tracker.target[tracker.cursor])
            area.refresh()
        elif is_code and event.key == "enter":
            # In code mode, Enter auto-types newline + leading indentation
            if not tracker.finished and tracker.target[tracker.cursor] == "\n":
                tracker.keypress("\n")
                # auto-type leading whitespace on the next line
                while not tracker.finished and tracker.target[tracker.cursor] in (" ", "\t"):
                    tracker.keypress(tracker.target[tracker.cursor])
            area.refresh()
        elif event.character and event.is_printable:
            tracker.keypress(event.character)
        else:
            return  # ignore unknown keys

        area.refresh()

        # flash hurt on error
        if tracker.cursor > 0 and tracker.results[tracker.cursor - 1].name == "INCORRECT":
            try:
                self.query_one("#character", CharacterWidget).flash_hurt()
            except Exception:
                pass

        # check for milestone achievements
        if self.stats.started and self.stats.elapsed > 1:
            wpm = self.stats.wpm(tracker.cursor)
            self._check_milestones(wpm, tracker)

        if tracker.finished:
            self._finish_test()

    def _tick_stats(self) -> None:
        """Periodic refresh of the stats bar + character animation."""
        try:
            self.stats.tick()
            bar = self.query_one("#stats-bar", StatsBar)
            bar.refresh()

            # update character tier
            area = self.query_one("#typing-area", TypingArea)
            if self.stats.started and self.stats.elapsed > 0.5:
                wpm = self.stats.wpm(area.tracker.cursor)
                self.query_one("#character", CharacterWidget).set_performance(wpm)
        except Exception:
            pass

    # ── Actions ───────────────────────────────────────────────────────

    def action_restart_tab(self) -> None:
        self._new_test()

    def action_restart_ctrlr(self) -> None:
        self._new_test()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_cycle_theme(self) -> None:
        new_theme = cycle_option(self.cfg, "theme", THEMES)
        self.app.apply_theme(new_theme)  # type: ignore[attr-defined]
        info = self.query_one("#info-bar", Static)
        info.update(self._info_text())

    def action_cycle_language(self) -> None:
        cycle_option(self.cfg, "language", LANGUAGES)
        self._new_test()

    def action_cycle_mode(self) -> None:
        cycle_option(self.cfg, "mode", MODES)
        self.refresh_bindings()
        self._new_test()

    def action_cycle_code_lang(self) -> None:
        cycle_option(self.cfg, "code_language", CODE_LANGUAGES)
        if self.cfg.get("mode") == "code":
            self._new_test()
        else:
            # switch to code mode automatically
            self.cfg["mode"] = "code"
            save_config(self.cfg)
            self.refresh_bindings()
            self._new_test()

    def action_show_history(self) -> None:
        self.app.push_screen("history")

    def action_zoom_in(self) -> None:
        zoom_in(self.cfg)
        self._apply_zoom()
        info = self.query_one("#info-bar", Static)
        info.update(self._info_text())

    def action_zoom_out(self) -> None:
        zoom_out(self.cfg)
        self._apply_zoom()
        info = self.query_one("#info-bar", Static)
        info.update(self._info_text())

    def action_quit_app(self) -> None:
        self.app.exit()
