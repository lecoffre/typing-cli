"""Splash screen — ASCII art welcome screen."""

from __future__ import annotations

from textual import events
from textual.screen import Screen
from textual.containers import Center, Middle
from textual.widgets import Static

try:
    from pyfiglet import figlet_format
except ImportError:
    def figlet_format(text: str, font: str = "slant") -> str:  # type: ignore[misc]
        return text

SPLASH_ART = figlet_format("typing test", font="slant")

TAGLINE = "Practice your typing speed — right from the terminal."
PROMPT = "Press any key to start  •  Ctrl+Q to quit"


class SplashScreen(Screen):
    """Full-screen splash with ASCII art logo."""

    DEFAULT_CSS = """
    SplashScreen {
        align: center middle;
    }
    SplashScreen #splash-art {
        width: auto;
        height: auto;
        content-align: center middle;
        text-align: center;
        color: $accent;
    }
    SplashScreen #tagline {
        width: auto;
        height: 1;
        content-align: center middle;
        text-align: center;
        margin-top: 1;
        color: $text-muted;
    }
    SplashScreen #prompt {
        width: auto;
        height: 1;
        content-align: center middle;
        text-align: center;
        margin-top: 2;
        color: $text-disabled;
    }
    """

    def compose(self):
        with Middle():
            with Center():
                yield Static(SPLASH_ART, id="splash-art")
            with Center():
                yield Static(TAGLINE, id="tagline")
            with Center():
                yield Static(PROMPT, id="prompt")

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key == "ctrl+q":
            self.app.exit()
        else:
            self.app.push_screen("typing")
