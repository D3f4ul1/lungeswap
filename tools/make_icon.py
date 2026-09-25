#!/usr/bin/env python3
"""Generate the LungeSwap icon and logo.

The spear is the *actual* vanilla Netherite Spear item texture, read straight out of the
Minecraft client jar -- not a redraw. Everything else (panel, ring, halo) is drawn on a 64x64
grid and the whole thing is nearest-neighbour upscaled, so the vanilla sprite lands on a clean
integer scale and its pixels stay square and untouched.

Because the sprite is Mojang's asset, it is deliberately NOT vendored into this repository.
The script reads it from your local Minecraft client jar, which means:

    - you need Minecraft 1.21.11 installed through Fabric Loom (run ./gradlew build once), and
    - anyone regenerating the icon needs the same.

Usage:

    python tools/make_icon.py                    # writes the real asset paths
    python tools/make_icon.py --out /tmp/icons   # write elsewhere, for a look

Writes, relative to --out (project root by default):
    src/main/resources/assets/lungeswap/icon.png   128x128, the in-game mod icon
    logo.png                                       512x512, for the README and mod pages
"""

import argparse
import io
import pathlib
import zipfile

from PIL import Image, ImageDraw, ImageFilter

VERSION = "1.21.11"
SPRITE = "assets/minecraft/textures/item/netherite_spear.png"

BASE = 64    # authoring grid
SPRITE_SCALE = 2  # 16x16 vanilla sprite -> 32x32 on the authoring grid
ICON = 128   # BASE * 2
LOGO = 512   # BASE * 8

# Netherite palette: dark and purple, matching the material the sprite is made of.
BG = (30, 22, 34, 255)
BG_LIT = (78, 56, 92, 255)
BG_DARK = (14, 10, 16, 255)

ACCENT_LIT = (214, 176, 250, 255)
ACCENT_MID = (162, 106, 226, 255)
ACCENT_DARK = (92, 52, 150, 255)

# The sprite is very dark (its brightest pixels only reach about #8F8F8F), so on a dark panel
# it disappears without something behind it. A crisp pixel halo keeps it readable and still
# looks hand-made rather than like a soft Photoshop glow.
HALO = (168, 128, 226, 255)

# Ring radius on the 64 grid. The sprite reaches out to radius 21.2, so the band has to start
# outside that or the tip collides with the ring instead of sitting cleanly inside it.
RING_R = 25
RING_W = 5      # ring thickness


def find_sprite():
    """Pull the vanilla spear texture out of the local Minecraft client jar."""
    jar = (
        pathlib.Path.home()
        / ".gradle/caches/fabric-loom" / VERSION / "minecraft-client.jar"
    )
    if not jar.is_file():
        raise SystemExit(
            f"Could not find the Minecraft client jar at:\n  {jar}\n"
            "Install Minecraft through Fabric Loom (run ./gradlew build once) and retry."
        )
    with zipfile.ZipFile(jar) as z:
        return Image.open(io.BytesIO(z.read(SPRITE))).convert("RGBA")


def panel():
    """A dark beveled panel, framed the way a vanilla inventory slot is."""
    img = Image.new("RGBA", (BASE, BASE), BG)
    d = ImageDraw.Draw(img)
    w = 3
    d.line([(0, 0), (BASE - 1, 0)], fill=BG_LIT, width=w)
    d.line([(0, 0), (0, BASE - 1)], fill=BG_LIT, width=w)
    d.line([(0, BASE - 1), (BASE - 1, BASE - 1)], fill=BG_DARK, width=w)
    d.line([(BASE - 1, 0), (BASE - 1, BASE - 1)], fill=BG_DARK, width=w)
    return img


def ring():
    """Two arcs chasing each other, so the ring reads as motion rather than decoration."""
    img = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = (BASE - 1) / 2

    def arc(radius, start, end, color):
        d.arc([cx - radius, cy - radius, cx + radius, cy + radius],
              start=start, end=end, fill=color, width=1)

    # Five concentric 1px arcs: lit inside, shaded outside, so the band has volume.
    bands = ((RING_R + 2, ACCENT_DARK), (RING_R + 1, ACCENT_DARK), (RING_R, ACCENT_MID),
             (RING_R - 1, ACCENT_MID), (RING_R - 2, ACCENT_LIT))
    for start, end in ((250, 40), (70, 220)):
        for radius, color in bands:
            arc(radius, start, end, color)

    from math import cos, radians, sin
    for ang in (40.0, 220.0):
        th = radians(ang)
        px, py = cx + RING_R * cos(th), cy + RING_R * sin(th)
        tx, ty = -sin(th), cos(th)
        ux, uy = -ty, tx
        sz = RING_W + 1.6
        d.polygon([(px + tx * sz, py + ty * sz),
                   (px - tx * sz * .5 + ux * sz, py - ty * sz * .5 + uy * sz),
                   (px - tx * sz * .5 - ux * sz, py - ty * sz * .5 - uy * sz)],
                  fill=ACCENT_MID)
    return img


def halo(sprite):
    """A pixel rim hugging the sprite's silhouette, so the dark sprite lifts off the panel."""
    # Dilate by two grid units: one grid unit is half a sprite pixel, so this reads as a
    # one-pixel rim at the sprite's own pixel scale.
    grown = sprite.getchannel("A").filter(ImageFilter.MaxFilter(5))
    rim = Image.new("RGBA", sprite.size, HALO)
    rim.putalpha(grown)
    return rim


def compose(sprite):
    placed = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    scaled = sprite.resize((sprite.width * SPRITE_SCALE, sprite.height * SPRITE_SCALE),
                           Image.NEAREST)
    offset = ((BASE - scaled.width) // 2, (BASE - scaled.height) // 2)
    placed.paste(scaled, offset)

    art = panel()
    art = Image.alpha_composite(art, halo(placed))
    art = Image.alpha_composite(art, ring())
    return Image.alpha_composite(art, placed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".", help="output directory (default: project root)")
    args = ap.parse_args()
    out = pathlib.Path(args.out)

    art = compose(find_sprite())

    icon_path = out / "src/main/resources/assets/lungeswap/icon.png"
    icon_path.parent.mkdir(parents=True, exist_ok=True)
    art.resize((ICON, ICON), Image.NEAREST).save(icon_path)
    art.resize((LOGO, LOGO), Image.NEAREST).save(out / "logo.png")
    print(f"wrote {icon_path} ({ICON}x{ICON}) and {out / 'logo.png'} ({LOGO}x{LOGO})")


if __name__ == "__main__":
    main()
