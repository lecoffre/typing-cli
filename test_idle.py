"""Quick test for idle detection in Stats."""
import time
from typingtest.core.stats import Stats

s = Stats()
s.start()
s.record_keypress()
time.sleep(0.5)
s.record_keypress()
s.tick()
print(f"1. Active typing      — paused={s.is_paused}, elapsed={s.elapsed:.2f}s")
assert not s.is_paused, "Should NOT be paused while typing"

time.sleep(3.5)
s.tick()
print(f"2. After 3.5s idle    — paused={s.is_paused}, elapsed={s.elapsed:.2f}s")
assert s.is_paused, "Should be paused after 3.5s idle"
e1 = s.elapsed

time.sleep(2.0)
s.tick()
e2 = s.elapsed
print(f"3. After 2s more idle — paused={s.is_paused}, delta={abs(e2-e1):.3f}s (should be ~0)")
assert abs(e2 - e1) < 0.1, f"Elapsed grew by {abs(e2-e1):.3f}s during idle!"

s.record_keypress()
print(f"4. After resume       — paused={s.is_paused}, elapsed={s.elapsed:.2f}s")
assert not s.is_paused, "Should NOT be paused after resume"

print("\n✅ IDLE DETECTION TEST PASSED")
