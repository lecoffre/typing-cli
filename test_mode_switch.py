"""Test mode switching and restart in code mode."""
import asyncio
import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

from typingtest.ui.app import TypingTestApp


async def test():
    app = TypingTestApp()
    async with app.run_test(size=(80, 24)) as pilot:
        # Go to typing screen
        await pilot.press("a")
        await pilot.pause()

        screen = app.screen
        mode1 = screen.cfg.get("mode")
        text1 = screen.query_one("#typing-area").target_text[:30]
        print(f"1. Initial mode: {mode1}")
        print(f"   Text: {text1}")

        # Ctrl+G → switch to code mode
        await pilot.press("ctrl+g")
        await pilot.pause()

        screen = app.screen
        mode2 = screen.cfg.get("mode")
        text2 = screen.query_one("#typing-area").target_text[:30]
        print(f"2. After Ctrl+G: {mode2}")
        print(f"   Text: {text2}")
        assert mode2 == "code", f"Expected 'code', got '{mode2}'"

        # Ctrl+R → restart in code mode
        await pilot.press("ctrl+r")
        await pilot.pause()

        screen = app.screen
        mode3 = screen.cfg.get("mode")
        text3 = screen.query_one("#typing-area").target_text[:30]
        print(f"3. After Ctrl+R: {mode3} (still code)")
        print(f"   Text: {text3}")
        assert mode3 == "code", f"Expected 'code', got '{mode3}'"

        # Ctrl+G → switch back to words mode
        await pilot.press("ctrl+g")
        await pilot.pause()

        screen = app.screen
        mode4 = screen.cfg.get("mode")
        text4 = screen.query_one("#typing-area").target_text[:30]
        print(f"4. After Ctrl+G back: {mode4}")
        print(f"   Text: {text4}")
        assert mode4 == "words", f"Expected 'words', got '{mode4}'"

        # Ctrl+K → cycle code lang, should auto-switch to code
        await pilot.press("ctrl+k")
        await pilot.pause()

        screen = app.screen
        mode5 = screen.cfg.get("mode")
        code_lang = screen.cfg.get("code_language")
        print(f"5. After Ctrl+K: mode={mode5}, lang={code_lang}")
        assert mode5 == "code", f"Expected 'code', got '{mode5}'"

        print()
        print("=== ALL TESTS PASSED ===")


if __name__ == "__main__":
    asyncio.run(test())
