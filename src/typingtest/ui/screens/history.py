"""History screen — view past scores in a table."""

from __future__ import annotations

from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import DataTable, Footer, Static

from typingtest.core.config import load_history


class HistoryScreen(Screen):
    """Displays the user's score history as a table."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("tab", "new_test", "New test", show=True),
        Binding("ctrl+q", "quit_app", "Quit", show=True),
    ]

    DEFAULT_CSS = """
    HistoryScreen {
        align: center middle;
    }
    HistoryScreen #history-container {
        width: 80;
        max-width: 95%;
        height: 80%;
        padding: 1 0;
    }
    HistoryScreen #history-title {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    HistoryScreen #no-data {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-align: center;
        color: $text-muted;
    }
    HistoryScreen DataTable {
        height: 1fr;
    }
    """

    def compose(self):
        history = load_history()

        with Vertical(id="history-container"):
            yield Static("⏳  SCORE HISTORY  ⏳", id="history-title")

            if not history:
                yield Static("No scores yet — complete a test first!", id="no-data")
            else:
                table = DataTable(id="history-table", zebra_stripes=True)
                table.cursor_type = "row"
                yield table
        yield Footer()

    def on_mount(self) -> None:
        history = load_history()
        if not history:
            return

        table = self.query_one("#history-table", DataTable)
        table.add_columns("#", "Date", "WPM", "Raw", "Acc%", "Time", "Lang")

        for i, entry in enumerate(reversed(history), 1):
            date_str = entry.get("date", "—")
            # shorten ISO date
            if "T" in date_str:
                date_str = date_str.replace("T", " ")

            table.add_row(
                str(i),
                date_str,
                str(entry.get("wpm", 0)),
                str(entry.get("raw_wpm", 0)),
                f"{entry.get('accuracy', 0)}%",
                f"{entry.get('time', 0)}s",
                entry.get("language", "—"),
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_new_test(self) -> None:
        # pop back, possibly through result screen, to typing screen
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()
