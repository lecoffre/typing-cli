"""Check for updates on PyPI and self-update."""

from __future__ import annotations

import subprocess
import sys
import threading
from typing import Callable

from typingtest import __version__

# Cache the result so we only hit the network once per session.
_latest_version: str | None = None
_check_done = threading.Event()


def _parse_version(v: str) -> tuple[int, ...]:
    """Convert '0.2.0' → (0, 2, 0) for comparison."""
    return tuple(int(x) for x in v.strip().split("."))


def check_for_update_async(callback: Callable[[str | None], None]) -> None:
    """Check PyPI in a background thread; call *callback(latest)* when done.

    *latest* is the version string if an update is available, else ``None``.
    The callback is invoked from the background thread — use
    ``app.call_from_thread`` if you need to touch the UI.
    """
    def _worker() -> None:
        global _latest_version
        try:
            import urllib.request
            import json

            url = "https://pypi.org/pypi/typing-cli/json"
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read())
            latest = data["info"]["version"]

            if _parse_version(latest) > _parse_version(__version__):
                _latest_version = latest
            else:
                _latest_version = None
        except Exception:
            _latest_version = None
        finally:
            _check_done.set()
            callback(_latest_version)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def run_self_update() -> tuple[bool, str]:
    """Upgrade typing-cli via pip. Returns (success, message)."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "--upgrade", "typing-cli"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True, "✅ Updated! Restart typing-cli to use the new version."
        return False, f"❌ Update failed:\n{result.stderr.strip()}"
    except Exception as exc:
        return False, f"❌ Update failed: {exc}"
