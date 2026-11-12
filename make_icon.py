# Builds the app icon + plain splash background into the generated Android project.
# Usage: python3 tools/make_icon.py [android_res_dir]
import os, sys, glob
from PIL import Image, ImageDraw

RES = sys.argv[1] if len(sys.argv) > 1 else "android/app/src/main/res"
BG = (14, 26, 43, 255)
TEAL = (45, 212, 191, 255)
PAPER = (232, 241, 245, 255)
INK = (90, 110, 135, 255)
K = 4  # supersampling


def foreground():
    S = 432 * K
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def R(*a): return [v * K for v in a]
    d.rounded_rectangle(R(150, 120, 262, 300), radius=14 * K, fill=PAPER)
    for y, x2 in ((142, 246), (166, 246), (190, 246), (214, 212)):
        d.rounded_rectangle(R(166, y, x2, y + 9), radius=4 * K, fill=INK)
    cx, cy = 244, 256
    d.ellipse(R(cx - 42, cy - 42, cx + 42, cy + 42), fill=TEAL)
    d.ellipse(R(cx - 26, cy - 26, cx + 26, cy + 26), fill=BG)
    d.line(R(274, 286, 298, 310), fill=TEAL, width=16 * K)
    d.ellipse(R(290, 302, 306, 318), fill=TEAL)
    return im


FG = foreground()


def legacy(size, round_):
    S = size * K
    base = Image.new("RGBA", (S, S), BG)
    f = FG.resize((int(S * 1.15), int(S * 1.15)), Image.LANCZOS)
    off = (f.width - S) // 2
    f = f.crop((off, off, off + S, off + S))
    base.alpha_composite(f)
    mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mask)
    if round_:
        md.ellipse([0, 0, S - 1, S - 1], fill=255)
    else:
        md.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=255)
    base.putalpha(mask)
    return base.resize((size, size), Image.LANCZOS)


DENS = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
for name, px in DENS.items():
    d = os.path.join(RES, "mipmap-" + name)
    os.makedirs(d, exist_ok=True)
    legacy(px, False).save(os.path.join(d, "ic_launcher.png"))
    legacy(px, True).save(os.path.join(d, "ic_launcher_round.png"))
    fpx = int(px * 108 / 48)
    FG.resize((fpx, fpx), Image.LANCZOS).save(os.path.join(d, "ic_launcher_foreground.png"))

vals = os.path.join(RES, "values")
os.makedirs(vals, exist_ok=True)
with open(os.path.join(vals, "ic_launcher_background.xml"), "w", encoding="utf-8") as fh:
    fh.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#0E1A2B</color>\n</resources>\n')

solid = Image.new("RGB", (16, 16), BG[:3])
for p in glob.glob(os.path.join(RES, "drawable*", "splash.png")):
    solid.save(p)
print("icon done")
