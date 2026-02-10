"""Stats calculator — WPM, accuracy, timing with idle detection."""

from __future__ import annotations

import time

# Seconds of inactivity before the timer auto-pauses
IDLE_THRESHOLD = 3.0


class Stats:
    """Tracks timing and computes WPM / accuracy for a typing session.

    The timer automatically pauses after IDLE_THRESHOLD seconds of
    inactivity so that AFK time doesn't ruin the WPM score.
    """

    def __init__(self) -> None:
        self._start_time: float | None = None
        self._end_time: float | None = None
        self._last_keypress: float | None = None
        self._total_idle: float = 0.0       # accumulated idle seconds
        self._idle_since: float | None = None  # when the current idle spell started
        self._paused: bool = False

    def start(self) -> None:
        """Mark the beginning of the test (called on first keypress)."""
        if self._start_time is None:
            self._start_time = time.time()
            self._last_keypress = self._start_time

    def stop(self) -> None:
        """Mark the end of the test."""
        # flush any pending idle time
        self._flush_idle()
        self._end_time = time.time()

    def record_keypress(self) -> None:
        """Call on every keypress to track activity."""
        now = time.time()

        if self._paused and self._idle_since is not None:
            # we were paused — accumulate the idle span
            self._total_idle += now - self._idle_since
            self._idle_since = None
            self._paused = False

        self._last_keypress = now

    def tick(self) -> None:
        """Called periodically (~10 Hz) to detect transitions to idle."""
        if self._start_time is None or self._end_time is not None:
            return
        if self._paused:
            return  # already paused, nothing to do

        now = time.time()
        if self._last_keypress and (now - self._last_keypress) >= IDLE_THRESHOLD:
            # transition to idle: the idle clock starts at the last keypress
            self._idle_since = self._last_keypress
            self._paused = True

    # ── computed properties ───────────────────────────────────────────

    @property
    def started(self) -> bool:
        """Whether the test timer has started (first keypress received)."""
        return self._start_time is not None

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def elapsed(self) -> float:
        """Active typing seconds (total time minus idle time)."""
        if self._start_time is None:
            return 0.0
        end = self._end_time or time.time()
        total = end - self._start_time

        idle = self._total_idle
        # if currently paused, add the ongoing idle span too
        if self._paused and self._idle_since is not None:
            idle += time.time() - self._idle_since

        return max(total - idle, 0.001)

    def wpm(self, chars_typed: int) -> int:
        """Standard WPM = (characters / 5) / minutes."""
        minutes = self.elapsed / 60
        if minutes <= 0:
            return 0
        return int((chars_typed / 5) / minutes)

    def raw_wpm(self, chars_typed: int) -> int:
        """Raw WPM ignoring accuracy."""
        return self.wpm(chars_typed)

    def net_wpm(self, chars_typed: int, accuracy: float) -> int:
        """Net WPM = raw_wpm × accuracy%."""
        return int(self.raw_wpm(chars_typed) * (accuracy / 100))

    @property
    def elapsed_display(self) -> str:
        """Human-readable elapsed time (e.g. '12.3s')."""
        return f"{self.elapsed:.1f}s"

    # ── internal ──────────────────────────────────────────────────────

    def _flush_idle(self) -> None:
        """Flush any pending idle span into the accumulator."""
        if self._paused and self._idle_since is not None:
            self._total_idle += time.time() - self._idle_since
            self._idle_since = None
            self._paused = False
