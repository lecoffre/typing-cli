"""CLI entry point — `typing-cli` command."""

from __future__ import annotations

import os
import platform
import shutil
import site

import click

from typingtest import __version__


def _ensure_path() -> None:
    """If typing-cli isn't on PATH, add the Scripts dir automatically."""
    if shutil.which("typing-cli"):
        return

    if platform.system() == "Windows":
        scripts = os.path.join(
            site.getusersitepackages().rsplit("site-packages")[0], "Scripts"
        )
        if not os.path.isdir(scripts):
            return
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE,
            ) as key:
                try:
                    cur, _ = winreg.QueryValueEx(key, "Path")
                except FileNotFoundError:
                    cur = ""
                if scripts.lower() in cur.lower():
                    return
                new = f"{cur};{scripts}" if cur else scripts
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new)
            # broadcast so new terminals pick it up
            try:
                import ctypes
                ctypes.windll.user32.SendMessageTimeoutW(
                    0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None
                )
            except Exception:
                pass
            click.echo(
                f"\n✅ 'typing-cli' has been added to your PATH."
                f"\n   Restart your terminal, then just type: typing-cli\n"
            )
        except Exception:
            pass
    else:
        scripts = os.path.join(site.getuserbase(), "bin")
        if not os.path.isdir(scripts):
            return
        shell = os.environ.get("SHELL", "/bin/bash")
        rc = os.path.expanduser(
            "~/.zshrc" if "zsh" in shell
            else "~/.config/fish/config.fish" if "fish" in shell
            else "~/.bashrc"
        )
        try:
            existing = open(rc).read() if os.path.exists(rc) else ""
            if scripts in existing:
                return
            with open(rc, "a") as f:
                f.write(f'\n# Added by typing-cli\nexport PATH="$PATH:{scripts}"\n')
            click.echo(
                f"\n✅ 'typing-cli' has been added to your PATH."
                f"\n   Restart your terminal, then just type: typing-cli\n"
            )
        except Exception:
            pass


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-v", "--version", prog_name="typing-cli")
def main() -> None:
    """⌨️  typing-cli — practice your typing speed in the terminal."""
    _ensure_path()

    from typingtest.ui.app import TypingTestApp

    app = TypingTestApp()
    app.run()


if __name__ == "__main__":
    main()
