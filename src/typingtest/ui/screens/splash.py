"""Splash screen — ASCII art welcome screen."""

from __future__ import annotations

from textual import events, work
from textual.binding import Binding
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

    BINDINGS = [
        Binding("ctrl+u", "do_update", "Update", show=False),
    ]

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
    SplashScreen #update-banner {
        width: auto;
        height: 1;
        content-align: center middle;
        text-align: center;
        margin-top: 1;
        color: $warning;
    }
    """

    _update_available: str | None = None

    def compose(self):
        with Middle():
            with Center():
                yield Static(SPLASH_ART, id="splash-art")
            with Center():
                yield Static(TAGLINE, id="tagline")
            with Center():
                yield Static("", id="update-banner")
            with Center():
                yield Static(PROMPT, id="prompt")

    def on_mount(self) -> None:
        self._check_update()

    @work(thread=True)
    def _check_update(self) -> None:
        """Check PyPI for a newer version in the background."""
        from typingtest.core.updater import check_for_update_async

        check_for_update_async(self._on_update_result)

    def _on_update_result(self, latest: str | None) -> None:
        if latest:
            self._update_available = latest
            self.app.call_from_thread(self._show_update_banner, latest)

    def _show_update_banner(self, latest: str) -> None:
        banner = self.query_one("#update-banner", Static)
        banner.update(f"🔄 Update available: v{latest}  —  Press Ctrl+U to update")

    def action_do_update(self) -> None:
        if not self._update_available:
            self.notify("Already up to date!", severity="information")
            return
        self.notify("Updating…", severity="information")
        self._run_update()

    @work(thread=True)
    def _run_update(self) -> None:
        from typingtest.core.updater import run_self_update

        success, message = run_self_update()
        self.app.call_from_thread(
            self.notify,
            message,
            severity="information" if success else "error",
            timeout=8,
        )

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key == "ctrl+q":
            self.app.exit()
        elif event.key == "ctrl+u":
            self.action_do_update()
        else:
            self.app.push_screen("typing")
