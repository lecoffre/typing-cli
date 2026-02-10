"""Integration test for all new features."""

import asyncio
import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

from typingtest.ui.app import TypingTestApp


async def test():
    app = TypingTestApp()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.press("a")
        await pilot.pause()
        print(f"1. Screen: {app.screen.__class__.__name__}", flush=True)

        # Check cursor vs correct colors
        tc = app.theme_colors
        print(f"2. Cursor: {tc['cursor']} | Correct: {tc['correct']}", flush=True)
        assert "on" in tc["cursor"], "Cursor should have background color"
        assert tc["cursor"] != tc["correct"], "Must be distinct"
        print("   OK cursor distinct from correct", flush=True)

        # Check milestone bar exists
        m = app.screen.query_one("#milestone-bar")
        print("3. Milestone bar: found", flush=True)

        # Switch to code mode
        await pilot.press("ctrl+m")
        await pilot.pause()

        area = app.screen.query_one("#typing-area")
        has_nl = "\n" in area.target_text
        print(f"4. Code mode: has newlines={has_nl}, len={len(area.target_text)}", flush=True)
        assert has_nl, "Code snippet should have newlines"

        # Switch back to words and complete a test
        await pilot.press("ctrl+m")
        await pilot.pause()

        area = app.screen.query_one("#typing-area")
        for char in area.target_text:
            await pilot.press(char)
        await pilot.pause()
        await pilot.pause()

        print(f"5. Result: {app.screen.__class__.__name__}", flush=True)

        bd = app.screen.query_one("#score-breakdown")
        total = app.screen.query_one("#score-total")
        print("6. Score widgets: found", flush=True)

        # Wait for animation to complete
        await pilot.pause(delay=4)
        print("7. Animation completed", flush=True)

        print("--- ALL TESTS PASSED ---", flush=True)


asyncio.run(test())
