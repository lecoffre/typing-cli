"""Animated pixel-art racing car using half-block rendering.

Each cell renders two vertical pixels via '▀' with fg (top) / bg (bottom).
This doubles vertical resolution for a true pixel-art look.

Car color stays the same always.  Only particles, trail, and perceived
speed (oscillation) vary per tier.  8 frames for smooth animation.
"""

from __future__ import annotations

import copy
from rich.text import Text
from rich.style import Style
from textual.widget import Widget
from textual.timer import Timer


# ── Pixel color indices ───────────────────────────────────────────────
_ = 0   # transparent
K = 1   # black (outline, underbody)
R = 2   # red (main body)
Y = 3   # yellow (cockpit detail)
G = 4   # dark gray (accents)
X = 5   # hurt flash
P = 6   # particle / trail

# ── Base car pixel grid (23 cols × 8 rows) ───────────────────────────

_CAR: list[list[int]] = [
    [K,K,K,_,_,_,_,_,K,K,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [K,R,K,_,_,_,K,K,R,K,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [K,R,K,_,_,K,R,R,R,K,K,_,_,_,_,_,_,_,_,_,_,_,_],
    [K,R,K,K,K,R,R,R,R,K,Y,K,_,K,K,K,K,K,_,_,_,_,_],
    [K,K,G,G,K,K,R,R,R,R,R,R,R,R,R,K,G,G,K,K,_,_,_],
    [_,K,G,K,G,K,R,R,R,R,R,R,R,R,K,G,K,K,G,R,K,K,_],
    [_,K,G,K,G,K,R,R,R,R,R,R,R,K,K,G,K,K,G,R,R,R,K],
    [_,_,K,K,K,K,K,K,K,K,K,K,_,_,K,K,K,K,K,K,K,K,K],
]

_CAR_ROWS = len(_CAR)
_CAR_COLS = len(_CAR[0])

_CANVAS_W = 34
_CANVAS_H = _CAR_ROWS   # 8
_N_FRAMES = 8            # total animation frames

# ── Car base palette (always the same red car) ───────────────────────
_CAR_PALETTE: dict[int, str] = {
    K: "#1e1e2e",
    R: "#dc2626",
    Y: "#facc15",
    G: "#4b5563",
    X: "#ef4444",
}

# ── Particle color (always gray) ─────────────────────────────────────
_PARTICLE_COLOR = "#585b70"

# ── Per-tier motion config ───────────────────────────────────────────
# (oscillation_amplitude, trail_length, particle_rows)
# oscillation is applied smoothly over 8 frames
# trail extends behind the car body
# particle_rows: fixed rows where single dots scroll linearly ← at 1 col/frame

_TIER_MOTION: dict[str, tuple[int, int, list[int]]] = {
    "idle":      (0, 0, []),
    "cruise":    (1, 2, [5]),
    "speed":     (2, 3, [3, 6]),
    "turbo":     (2, 4, [2, 5, 7]),
    "nitro":     (3, 5, [1, 3, 5, 7]),
    "legendary": (3, 6, [0, 2, 4, 5, 7]),
}

# Smooth oscillation offsets over 8 frames (sine-like: 0→peak→0)
_OSC_8 = [0, 1, 2, 2, 2, 1, 0, 0]

# ── Hurt overlay ─────────────────────────────────────────────────────
_FX_HURT: list[tuple[int, int, int]] = [
    (4, 10, X), (4, 11, X),
    (3, 9, X),
]

# ── Tier thresholds ──────────────────────────────────────────────────

_TIERS: list[tuple[str, int]] = [
    ("idle",      0),
    ("cruise",    30),
    ("speed",     50),
    ("turbo",     70),
    ("nitro",     90),
    ("legendary", 120),
]

_TIER_LABELS: dict[str, str] = {
    "idle":      "parked",
    "cruise":    "cruise",
    "speed":     "speed!",
    "turbo":     "TURBO",
    "nitro":     "NITRO!",
    "legendary": "LEGEND",
}


def _tier_for_wpm(wpm: int) -> str:
    tier = "idle"
    for name, threshold in _TIERS:
        if wpm >= threshold:
            tier = name
    return tier


def _build_canvas(tier: str, frame: int, hurt: bool) -> list[list[int]]:
    """Build canvas with car + trail + particles."""
    canvas: list[list[int]] = [[0] * _CANVAS_W for _i in range(_CANVAS_H)]

    car = copy.deepcopy(_CAR)
    if hurt:
        for r, c, v in _FX_HURT:
            if 0 <= r < _CAR_ROWS and 0 <= c < _CAR_COLS:
                car[r][c] = v

    amp, trail_len, p_rows = _TIER_MOTION.get(tier, (0, 0, []))
    osc_val = _OSC_8[frame % _N_FRAMES]
    offset = round(osc_val * amp / 2)

    # Place car
    for r in range(_CAR_ROWS):
        for c in range(_CAR_COLS):
            dc = c + offset
            if 0 <= dc < _CANVAS_W and car[r][c] != 0:
                canvas[r][dc] = car[r][c]

    if hurt or tier == "idle":
        return canvas

    # Trail: sparse pixels behind the car body (rows 4-7)
    for tr in (4, 5, 6, 7):
        for i in range(1, trail_len + 1):
            tc = offset - i
            if (i + tr + frame) % 3 == 0:
                continue
            if 0 <= tc < _CANVAS_W and canvas[tr][tc] == 0:
                canvas[tr][tc] = P

    # Particles: single dots scrolling left, only behind the car
    car_left = offset  # leftmost car column
    for pi, pr in enumerate(p_rows):
        pc = (car_left - 2 - pi * 7 - frame * 2) % _CANVAS_W
        # only keep if it falls in the zone behind (left of) the car
        if pc >= car_left:
            continue
        if 0 <= pr < _CANVAS_H and 0 <= pc < _CANVAS_W and canvas[pr][pc] == 0:
            canvas[pr][pc] = P

    return canvas


def _render_halfblock(grid: list[list[int]], tier: str, hurt: bool) -> Text:
    """Render pixel grid using half-block technique."""
    pal = dict(_CAR_PALETTE)
    pal[P] = "#ef4444" if hurt else _PARTICLE_COLOR

    text = Text()
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    for y in range(0, rows, 2):
        top_row = grid[y]
        bot_row = grid[y + 1] if y + 1 < rows else [0] * cols

        for x in range(cols):
            top = top_row[x]
            bot = bot_row[x]

            if top == 0 and bot == 0:
                text.append(" ")
            elif top == 0 and bot != 0:
                text.append("▄", style=Style(color=pal[bot]))
            elif top != 0 and bot == 0:
                text.append("▀", style=Style(color=pal[top]))
            elif top == bot:
                text.append("█", style=Style(color=pal[top]))
            else:
                text.append("▀", style=Style(color=pal[top], bgcolor=pal[bot]))
        text.append("\n")

    return text


class CharacterWidget(Widget):
    """Pixel-art F1 car. Same color always; particles & speed vary by tier."""

    DEFAULT_CSS = """
    CharacterWidget {
        width: 36;
        height: 6;
        content-align: center middle;
        text-align: center;
        margin-bottom: 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._wpm: int = 0
        self._tier_name: str = "idle"
        self._frame_idx: int = 0
        self._hurt: bool = False
        self._hurt_timer: Timer | None = None
        self._anim_timer: Timer | None = None

    def on_mount(self) -> None:
        self._anim_timer = self.set_interval(0.15, self._next_frame)

    def _next_frame(self) -> None:
        self._frame_idx = (self._frame_idx + 1) % _N_FRAMES
        self.refresh()

    def set_performance(self, wpm: int) -> None:
        if wpm == self._wpm:
            return
        self._wpm = wpm
        new_tier = _tier_for_wpm(wpm)
        if new_tier != self._tier_name:
            self._tier_name = new_tier
        self.refresh()

    def flash_hurt(self) -> None:
        self._hurt = True
        self.refresh()
        if self._hurt_timer is not None:
            self._hurt_timer.stop()
        self._hurt_timer = self.set_timer(0.3, self._recover)

    def _recover(self) -> None:
        self._hurt = False
        self._hurt_timer = None
        self.refresh()

    def reset(self) -> None:
        self._wpm = 0
        self._tier_name = "idle"
        self._frame_idx = 0
        self._hurt = False
        if self._hurt_timer is not None:
            self._hurt_timer.stop()
            self._hurt_timer = None
        self.refresh()

    def render(self) -> Text:
        tier = self._tier_name
        canvas = _build_canvas(
            "hurt" if self._hurt else tier,
            self._frame_idx,
            self._hurt,
        )
        text = _render_halfblock(canvas, tier, self._hurt)

        # Label
        if self._hurt:
            label_str = "crash!"
            label_style = "bold #f38ba8"
        elif self._wpm > 0:
            tag = _TIER_LABELS.get(tier, "")
            label_str = f"{tag} {self._wpm}"
            label_style = f"dim {_CAR_PALETTE[R]}"
        else:
            label_str = _TIER_LABELS.get(tier, "")
            label_style = f"dim {_CAR_PALETTE[R]}"

        text.append(label_str.center(_CANVAS_W), style=label_style)
        return text
