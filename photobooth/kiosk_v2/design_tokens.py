"""FEAT-022 shared visual tokens, transcribed from FEAT-021 at 672e3f7089bb.

Source of truth: meong_fly_painter.py and meong_fly_polish.py on the
read-only game branch. This module is self-contained: no cross-branch import,
no game implementation, graphics context, I/O or hardware dependencies.
"""

SPACE = "#050C2F"
PANEL = "#0B1543"
PANEL_EDGE = "#57499A"
INK = "#070D26"
WHITE = "#F8F8FF"
PINK = "#FF55AB"
CYAN = "#58D1FF"
GOLD = "#FFDC78"
PURPLE = "#B385FF"
MUTED = "#B9BFDE"  # FEAT-022 readable secondary text, not a game token.
SHADOW = "#03051A"  # FEAT-021 arcade_card shadow.

# Exact button face/border colors from FEAT-021's arcade_button renderer.
BUTTON_COLORS = {
    "primary": "#FF53A9",
    "secondary": "#4DCCFA",
    "tertiary": "#1B295B",
    "muted": "#454764",  # FEAT-022 disabled state.
}
BUTTON_EDGES = {
    "primary": "#FFA5DA",
    "secondary": "#AFF1FF",
    "tertiary": "#9594D2",
    "muted": MUTED,
}

PIXEL_NOTCH_DP = 6
PIXEL_INSET_DP = 3


def stepped_rects(x, y, width, height, notch):
    """Two positive rectangles forming an axis-aligned clipped-corner panel.

    Renderers can apply the same geometry to a shadow, border and inner face.
    No rounded-corner textures or per-frame rasterization are necessary.
    """
    if width <= 0 or height <= 0:
        return ()
    cut = min(max(0, notch), width / 2, height / 2)
    return (
        (x + cut, y, width - 2 * cut, height),
        (x, y + cut, width, height - 2 * cut),
    )
