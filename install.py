#!/usr/bin/env python3
"""One-line installer for typing-cli.

Usage (copy-paste in any terminal):
    Windows PowerShell:  python -c "import urllib.request as u; exec(u.urlopen('https://raw.githubusercontent.com/lecoffre/typing-cli/main/install.py').read())"
    macOS/Linux:         python3 -c "import urllib.request as u; exec(u.urlopen('https://raw.githubusercontent.com/lecoffre/typing-cli/main/install.py').read())"
"""

from __future__ import annotations

import os
import platform
import shutil
import site
import subprocess
import sys


def main() -> None:
    print("\n⌨️  Installing typing-cli...\n")

    # 1. Install the package
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--user", "--upgrade", "typing-cli"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    # 2. Find the user Scripts directory
    if platform.system() == "Windows":
        scripts_dir = os.path.join(site.getusersitepackages().rsplit("site-packages")[0], "Scripts")
    else:
        scripts_dir = os.path.join(site.getuserbase(), "bin")

    # 3. Check if typing-cli is accessible
    if shutil.which("typing-cli"):
        print("\n✅ typing-cli is installed and ready!")
        print("   Just type: typing-cli\n")
        return

    # 4. Add to PATH if needed
    if platform.system() == "Windows":
        _add_to_path_windows(scripts_dir)
    else:
        _add_to_path_unix(scripts_dir)

    print(f"\n✅ typing-cli installed successfully!")
    print(f"   Scripts directory added to PATH: {scripts_dir}")
    print(f"\n   ⚠️  Please restart your terminal, then type: typing-cli\n")


def _add_to_path_windows(scripts_dir: str) -> None:
    """Add scripts_dir to Windows user PATH (permanent)."""
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        ) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path = ""

            if scripts_dir.lower() in current_path.lower():
                return  # already in PATH

            new_path = f"{current_path};{scripts_dir}" if current_path else scripts_dir
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)

        # Broadcast the change so new terminals pick it up
        try:
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 0x0002, 5000, None
            )
        except Exception:
            pass
    except Exception as e:
        print(f"   ⚠️  Could not update PATH automatically: {e}")
        print(f"   Add this to your PATH manually: {scripts_dir}")


def _add_to_path_unix(scripts_dir: str) -> None:
    """Add scripts_dir to shell profile (permanent)."""
    shell = os.environ.get("SHELL", "/bin/bash")
    if "zsh" in shell:
        profile = os.path.expanduser("~/.zshrc")
    elif "fish" in shell:
        profile = os.path.expanduser("~/.config/fish/config.fish")
    else:
        profile = os.path.expanduser("~/.bashrc")

    line = f'\nexport PATH="$PATH:{scripts_dir}"\n'

    try:
        existing = ""
        if os.path.exists(profile):
            with open(profile, "r") as f:
                existing = f.read()

        if scripts_dir in existing:
            return  # already in profile

        with open(profile, "a") as f:
            f.write(f"\n# Added by typing-cli installer\n{line}")
    except Exception as e:
        print(f"   ⚠️  Could not update {profile}: {e}")
        print(f"   Add this to your PATH: export PATH=\"$PATH:{scripts_dir}\"")


if __name__ == "__main__":
    main()
