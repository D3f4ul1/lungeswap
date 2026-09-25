#!/usr/bin/env python3
"""Generate the LungeSwap icon and logo.

The art is authored on a 32x32 grid -- the same resolution as a vanilla item sprite -- and
then scaled up with nearest-neighbour, so every pixel stays square and crisp instead of going
soft. That is what makes it read as Minecraft art rather than as a resized drawing.

Run it from the project root:

    python tools/make_icon.py

Writes:
    src/main/resources/assets/lungeswap/icon.png   128x128, the in-game mod icon
    logo.png                                       512x512, for the README and mod pages
"""

from math import cos, radians, sin

from PIL import Image, ImageDraw, ImageFilter

BASE = 32   # authoring resolution
ICON = 128  # in-game mod icon
LOGO = 512  # README / mod page

# Vanilla-adjacent palette: flat fills with a dark outline and a light/dark edge pair, which
# is how vanilla sprites stay readable when they are only a handful of pixels across.
OUTLINE = (22, 18, 28, 255)

BG = (34, 39, 47, 255)
BEVEL_LIGHT = (78, 88, 104, 255)
BEVEL_DARK = (19, 22, 27, 255)

WOOD_LIGHT = (172, 136, 90, 255)
WOOD_MID = (124, 94, 58, 255)
WOOD_DARK = (85, 62, 37, 255)

# Diamond-tier spear head: cyan reads as the tier people actually fight with.
HEAD_LIGHT = (108, 245, 226, 255)
HEAD_MID = (43, 179, 163, 255)

GREEN_LIGHT = (150, 226, 106, 255)
GREEN_MID = (98, 179, 59, 255)
GREEN_DARK = (52, 107, 28, 255)

CX = CY = 15.5  # centre of the art
RING_R = 11.5   # radius of the arrow ring

# The spear runs along the main diagonal, so the arrow heads sit on the *other* diagonal where
# nothing else is happening. Overlapping them was what turned the top-right corner into mush.
HEADS = (40.0, 220.0)
ARC_A = (250, 40)  # sweeps clockwise over the top
ARC_B = (70, 220)  # sweeps clockwise under the bottom


def background():
    """A flat beveled panel, framed the way a vanilla inventory slot is."""
    img = Image.new("RGBA", (BASE, BASE), BG)
    d = ImageDraw.Draw(img)

    d.line([(0, 0), (BASE - 1, 0)], fill=BEVEL_LIGHT, width=2)
    d.line([(0, 0), (0, BASE - 1)], fill=BEVEL_LIGHT, width=2)
    d.line([(0, BASE - 1), (BASE - 1, BASE - 1)], fill=BEVEL_DARK, width=2)
    d.line([(BASE - 1, 0), (BASE - 1, BASE - 1)], fill=BEVEL_DARK, width=2)
    return img


def with_outline(img, color=OUTLINE, thickness=1):
    """Ring the opaque pixels in a dark border, as vanilla sprites do."""
    grown = img.getchannel("A").filter(ImageFilter.MaxFilter(2 * thickness + 1))
    border = Image.new("RGBA", img.size, color)
    border.putalpha(grown)
    return Image.alpha_composite(border, img)


def _ring_arc(d, radius, start, end, color):
    d.arc(
        [CX - radius, CY - radius, CX + radius, CY + radius],
        start=start,
        end=end,
        fill=color,
        width=1,
    )


def _arrowhead(d, angle_deg, size=3.4):
    """A chunky triangle sitting at the leading end of an arc, pointing the way it travels."""
    th = radians(angle_deg)
    px, py = CX + RING_R * cos(th), CY + RING_R * sin(th)
    tx, ty = -sin(th), cos(th)   # tangent: the direction a clockwise arc is moving
    ux, uy = -ty, tx             # perpendicular, to spread the base of the head
    d.polygon(
        [
            (px + tx * size, py + ty * size),
            (px - tx * size * 0.45 + ux * size, py - ty * size * 0.45 + uy * size),
            (px - tx * size * 0.45 - ux * size, py - ty * size * 0.45 - uy * size),
        ],
        fill=GREEN_MID,
    )


def swap_arrows():
    """Two arcs chasing each other, so the ring reads as motion rather than decoration."""
    img = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    for start, end in (ARC_A, ARC_B):
        # Three concentric 1px arcs give a lit inner edge and a shaded outer one, so the ring
        # has volume without turning into a thick band.
        _ring_arc(d, RING_R + 1, start, end, GREEN_DARK)
        _ring_arc(d, RING_R, start, end, GREEN_MID)
        _ring_arc(d, RING_R - 1, start, end, GREEN_LIGHT)

    for angle in HEADS:
        _arrowhead(d, angle)
    return img


def spear():
    """A diamond spear along the main diagonal, its tip breaking just past the ring."""
    img = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Shaft, drawn one column at a time. A 45 degree band has to be a vertical run per column:
    # offsetting a thick line diagonally makes the light and dark edges collide between steps,
    # which shows up as a candy-cane checkerboard instead of a smooth shaft.
    # Centred on the ring: the spear's midpoint lands on (CX, CY) rather than a pixel off it.
    butt_x, butt_y = 5, 26
    collar_x, collar_y = 20, 11
    for i in range(collar_x - butt_x + 1):
        x = butt_x + i
        top = butt_y - i - 1
        d.point((x, top), fill=WOOD_LIGHT)
        d.point((x, top + 1), fill=WOOD_MID)
        d.point((x, top + 2), fill=WOOD_DARK)

    tip = (26, 5)
    base_lo = (22, 13)  # lower-right corner of the blade
    base_hi = (18, 9)   # upper-left corner, where the highlight goes
    d.polygon([tip, base_lo, base_hi], fill=HEAD_MID)
    d.polygon([tip, base_hi, (collar_x, collar_y)], fill=HEAD_LIGHT)
    return img


def compose():
    art = background()
    art = Image.alpha_composite(art, with_outline(swap_arrows()))
    art = Image.alpha_composite(art, with_outline(spear()))
    return art


def main():
    art = compose()
    art.resize((ICON, ICON), Image.NEAREST).save("src/main/resources/assets/lungeswap/icon.png")
    art.resize((LOGO, LOGO), Image.NEAREST).save("logo.png")
    print(f"wrote icon.png ({ICON}x{ICON}) and logo.png ({LOGO}x{LOGO})")


if __name__ == "__main__":
    main()
