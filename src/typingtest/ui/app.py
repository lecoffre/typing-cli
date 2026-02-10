"""Main Textual application — orchestrates screens and themes."""

from __future__ import annotations

from textual.app import App
from textual.theme import Theme

from typingtest.core.config import load_config

# ── Theme color palettes for per-character styling ────────────────────
# These are Rich style strings used by TypingArea / StatsBar widgets.
# They drive character-level text coloring (not Textual CSS).

THEME_COLORS: dict[str, dict[str, str]] = {
    "midnight": {
        "pending":   "grey42",
        "correct":   "#c3e88d",
        "incorrect": "bold #ff5370 on #3b1a1a",
        "cursor":    "bold #1e1e2e on #82aaff",
        "accent":    "#82aaff",
        "dim":       "grey50",
    },
    "forest": {
        "pending":   "grey42",
        "correct":   "#a3be8c",
        "incorrect": "bold #bf616a on #2e1a1a",
        "cursor":    "bold #2b303b on #a3be8c",
        "accent":    "#a3be8c",
        "dim":       "grey50",
    },
    "sunset": {
        "pending":   "grey42",
        "correct":   "#fab387",
        "incorrect": "bold #f38ba8 on #3b1a25",
        "cursor":    "bold #1e1e2e on #f9e2af",
        "accent":    "#fab387",
        "dim":       "grey50",
    },
    "ocean": {
        "pending":   "grey42",
        "correct":   "#89dceb",
        "incorrect": "bold #f38ba8 on #2e1a25",
        "cursor":    "bold #1e1e2e on #74c7ec",
        "accent":    "#74c7ec",
        "dim":       "grey50",
    },
    "mono": {
        "pending":   "grey35",
        "correct":   "grey85",
        "incorrect": "bold #ff6b6b on #2a1a1a",
        "cursor":    "bold #1a1a1a on white",
        "accent":    "grey70",
        "dim":       "grey42",
    },
}

# ── Textual Theme definitions ────────────────────────────────────────
# Control the overall look of the TUI (background, accent, footer, etc.)

TEXTUAL_THEMES: dict[str, Theme] = {
    "midnight": Theme(
        name="midnight",
        primary="#82aaff",
        dark=True,
        accent="#82aaff",
        background="#1e1e2e",
        surface="#181825",
        panel="#313244",
        foreground="#cdd6f4",
        secondary="#89b4fa",
        success="#c3e88d",
        warning="#fab387",
        error="#ff5370",
    ),
    "forest": Theme(
        name="forest",
        primary="#a3be8c",
        dark=True,
        accent="#a3be8c",
        background="#2b303b",
        surface="#232830",
        panel="#3b4252",
        foreground="#d8dee9",
        secondary="#88c0d0",
        success="#a3be8c",
        warning="#ebcb8b",
        error="#bf616a",
    ),
    "sunset": Theme(
        name="sunset",
        primary="#fab387",
        dark=True,
        accent="#fab387",
        background="#1e1e2e",
        surface="#181825",
        panel="#313244",
        foreground="#cdd6f4",
        secondary="#f9e2af",
        success="#a6e3a1",
        warning="#fab387",
        error="#f38ba8",
    ),
    "ocean": Theme(
        name="ocean",
        primary="#74c7ec",
        dark=True,
        accent="#74c7ec",
        background="#1e1e2e",
        surface="#181825",
        panel="#313244",
        foreground="#cdd6f4",
        secondary="#89dceb",
        success="#a6e3a1",
        warning="#f9e2af",
        error="#f38ba8",
    ),
    "mono": Theme(
        name="mono",
        primary="#a0a0a0",
        dark=True,
        accent="#a0a0a0",
        background="#1a1a1a",
        surface="#111111",
        panel="#2a2a2a",
        foreground="#d0d0d0",
        secondary="#888888",
        success="#a0a0a0",
        warning="#c0c0c0",
        error="#ff6b6b",
    ),
}


class TypingTestApp(App):
    """The main typing-test application."""

    TITLE = "typing-test"
    SUB_TITLE = "practice your speed"

    CSS = """
    Screen {
        align: center middle;
    }
    Footer {
        dock: bottom;
    }
    """

    SCREENS = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cfg = load_config()
        self._current_theme_name = self.cfg.get("theme", "midnight")
        self.theme_colors: dict[str, str] = THEME_COLORS.get(
            self._current_theme_name, THEME_COLORS["midnight"]
        )

    def on_mount(self) -> None:
        # Register all custom themes
        for name, theme_obj in TEXTUAL_THEMES.items():
            self.register_theme(theme_obj)

        # Apply the saved theme
        self.theme = self._current_theme_name

        # Register screens lazily
        from typingtest.ui.screens.splash import SplashScreen
        from typingtest.ui.screens.typing_screen import TypingScreen
        from typingtest.ui.screens.result import ResultScreen
        from typingtest.ui.screens.history import HistoryScreen

        self.install_screen(SplashScreen, "splash")
        self.install_screen(TypingScreen, "typing")
        self.install_screen(ResultScreen, "result")
        self.install_screen(HistoryScreen, "history")

        self.push_screen("splash")

    def apply_theme(self, theme_name: str) -> None:
        """Switch to a new theme at runtime."""
        self._current_theme_name = theme_name
        self.theme_colors = THEME_COLORS.get(theme_name, THEME_COLORS["midnight"])
        self.theme = theme_name
