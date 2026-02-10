"""CLI entry point — `typing-cli` command."""

from __future__ import annotations

import click

from typingtest import __version__


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-v", "--version", prog_name="typing-cli")
def main() -> None:
    """⌨️  typing-cli — practice your typing speed in the terminal."""
    from typingtest.ui.app import TypingTestApp

    app = TypingTestApp()
    app.run()


if __name__ == "__main__":
    main()
