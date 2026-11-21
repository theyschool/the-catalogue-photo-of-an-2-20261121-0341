#!/usr/bin/env python3
"""AQUASHELLA - catalogue photo of an impossible gadget.

Renders entry.png (1024x1024) with PIL only: a studio product shot of a
miniature umbrella device that keeps a goldfish dry. A round glass fishbowl
holds one orange goldfish; a slim chrome stand clamped to the bowl rim holds
a small deep-red umbrella canopy directly over the fish. One accessory only:
a small white product tag reading AQUASHELLA tied to the stand.
Deterministic: no randomness, fixed geometry, two runs are byte-identical.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

S = 2  # supersample factor
W = 1024 * S
H = 1024 * S

FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def sc(v):
    return v * S


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bottom, y / max(1, h - 1)))
    return img


def ellipse(d, box, **kw):
    d.ellipse([sc(box[0]), sc(box[1]), sc(box[2]), sc(box[3])], **kw)


def main():
    # ---- backdrop: warm off-white studio sweep with soft radial glow ----
    img = vgrad(W, H, (250, 246, 238), (226, 218, 203)).convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([sc(90), sc(30), sc(934), sc(760)], fill=(255, 255, 255, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(sc(90)))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img, "RGBA")

    cx, cy, R = 512, 618, 302  # bowl centre / radius (design coords)

    # ---- soft contact shadow + faint reflection under bowl ----
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([sc(cx - 300), sc(872), sc(cx + 300), sc(952)], fill=(60, 48, 32, 120))
    sd.ellipse([sc(cx - 210), sc(884), sc(cx + 210), sc(938)], fill=(50, 40, 26, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(sc(16)))
    img = Image.alpha_composite(img, sh)
    # gentle floor reflection of the bowl base (own layer: Draw replaces,
    # it does not blend, so translucent shapes must live on a clear layer)
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    ellipse(rd, (cx - 235, 896, cx + 235, 950), fill=(168, 196, 205, 46))
    ellipse(rd, (cx - 150, 906, cx + 150, 940), fill=(240, 140, 60, 26))
    img = Image.alpha_composite(img, refl)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- chrome stand (behind bowl): base clamp, vertical pole, top arm ----
    chrome = (196, 202, 208, 255)
    chrome_hi = (244, 248, 250, 255)
    chrome_lo = (128, 136, 144, 255)
    # vertical pole on the right, rising from behind the bowl to above the rim
    d.rounded_rectangle([sc(742), sc(196), sc(758), sc(560)], radius=sc(8), fill=chrome)
    d.rectangle([sc(745), sc(196), sc(750), sc(560)], fill=chrome_hi)
    d.rectangle([sc(753), sc(196), sc(757), sc(560)], fill=chrome_lo)
    # top arm reaching left over the bowl centre
    d.rounded_rectangle([sc(512), sc(188), sc(758), sc(204)], radius=sc(8), fill=chrome)
    d.rectangle([sc(512), sc(191), sc(758), sc(195)], fill=chrome_hi)
    # centre drop rod from arm down to the canopy apex
    d.rounded_rectangle([sc(505), sc(196), sc(519), sc(300)], radius=sc(6), fill=chrome)
    d.rectangle([sc(508), sc(196), sc(512), sc(300)], fill=chrome_hi)
    # joints: round knobs where arm meets pole and at the drop rod
    ellipse(d, (734, 178, 766, 210), fill=chrome, outline=chrome_lo, width=sc(2))
    ellipse(d, (740, 184, 754, 198), fill=chrome_hi)
    ellipse(d, (496, 282, 528, 314), fill=chrome, outline=chrome_lo, width=sc(2))
    ellipse(d, (503, 289, 516, 302), fill=chrome_hi)
    # clamp gripping the bowl rim on the right
    d.rounded_rectangle([sc(726), sc(516), sc(776), sc(566)], radius=sc(10),
                        fill=(90, 96, 104, 255), outline=(52, 56, 62, 255), width=sc(2))
    ellipse(d, (740, 530, 762, 552), fill=chrome_lo, outline=(40, 44, 50, 255), width=sc(2))
    ellipse(d, (747, 537, 755, 545), fill=chrome_hi)

    # ---- fishbowl glass shell ----
    bowl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bowl)
    bd.ellipse([sc(cx - R), sc(cy - R), sc(cx + R), sc(cy + R)], fill=(206, 226, 232, 46))
    img = Image.alpha_composite(img, bowl)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- water: clipped to bowl, surface below the canopy ----
    water_top = 566
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([sc(cx - R + 10), sc(cy - R + 10), sc(cx + R - 10), sc(cy + R - 10)], fill=255)
    md.rectangle([0, 0, W, sc(water_top)], fill=0)
    wg = vgrad(W, H, (148, 205, 220), (52, 122, 158)).convert("RGBA")
    wg.putalpha(mask)
    img = Image.alpha_composite(img, wg)
    # water surface: bright ellipse line at the waterline (own layer)
    surf = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sfd = ImageDraw.Draw(surf)
    ellipse(sfd, (cx - 268, water_top - 13, cx + 268, water_top + 13),
            fill=(196, 232, 240, 120), outline=(232, 248, 252, 190), width=sc(2))
    ellipse(sfd, (cx - 268, water_top - 13, cx + 268, water_top + 13),
            outline=(240, 252, 255, 160), width=sc(1))
    img = Image.alpha_composite(img, surf)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- goldfish (hero, centred, facing right, under the canopy) ----
    fish = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fish, "RGBA")
    fx, fy = 500, 668  # fish centre
    # tail fin: soft fan behind the body (left)
    fd.polygon([(sc(fx - 92), sc(fy - 6)), (sc(fx - 178), sc(fy - 62)),
                (sc(fx - 158), sc(fy)), (sc(fx - 178), sc(fy + 62))],
               fill=(232, 110, 38, 235))
    fd.polygon([(sc(fx - 92), sc(fy - 4)), (sc(fx - 150), sc(fy - 40)),
                (sc(fx - 138), sc(fy)), (sc(fx - 150), sc(fy + 40))],
               fill=(245, 140, 55, 220))
    # dorsal fin on top
    fd.polygon([(sc(fx - 40), sc(fy - 58)), (sc(fx + 18), sc(fy - 92)),
                (sc(fx + 52), sc(fy - 52))], fill=(232, 110, 38, 230))
    # body
    fd.ellipse([sc(fx - 105), sc(fy - 64), sc(fx + 115), sc(fy + 64)], fill=(243, 124, 40, 255))
    # pectoral fin
    fd.polygon([(sc(fx + 28), sc(fy + 22)), (sc(fx - 6), sc(fy + 66)),
                (sc(fx + 52), sc(fy + 52))], fill=(238, 118, 40, 255))
    img_fish_shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fsd = ImageDraw.Draw(img_fish_shade)
    # shaded crown (darker) and pale belly for roundness, on a clear layer
    fsd.pieslice([sc(fx - 105), sc(fy - 64), sc(fx + 115), sc(fy + 64)],
                 start=180, end=360, fill=(214, 88, 22, 110))
    fsd.pieslice([sc(fx - 100), sc(fy - 40), sc(fx + 108), sc(fy + 66)],
                 start=20, end=160, fill=(255, 196, 120, 120))
    # gill curve
    fsd.arc([sc(fx + 34), sc(fy - 46), sc(fx + 96), sc(fy + 46)],
            start=300, end=60, fill=(196, 74, 18, 200), width=sc(4))
    # subtle scale arcs
    for gx in (-52, -16, 20):
        fsd.arc([sc(fx + gx), sc(fy - 30), sc(fx + gx + 44), sc(fy + 30)],
                start=290, end=70, fill=(255, 170, 90, 90), width=sc(2))
    fish = Image.alpha_composite(fish, img_fish_shade)
    fd = ImageDraw.Draw(fish, "RGBA")
    # eye: white, iris, pupil, catchlight
    fd.ellipse([sc(fx + 74), sc(fy - 30), sc(fx + 104), sc(fy)], fill=(255, 252, 246, 255))
    fd.ellipse([sc(fx + 80), sc(fy - 25), sc(fx + 99), sc(fy - 6)], fill=(30, 26, 24, 255))
    fd.ellipse([sc(fx + 84), sc(fy - 23), sc(fx + 91), sc(fy - 16)], fill=(255, 255, 255, 255))
    # mouth: small surprised "o" at the snout
    fd.ellipse([sc(fx + 106), sc(fy - 8), sc(fx + 118), sc(fy + 6)],
               outline=(178, 62, 14, 255), width=sc(3))
    img = Image.alpha_composite(img, fish)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- glass front + bubbles on one clear layer, composited over ----
    glass = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(glass)
    # bubbles rising beside the fish
    for (bx, by, br) in [(640, 600, 9), (662, 556, 6), (628, 520, 5), (356, 612, 7), (338, 566, 5)]:
        ellipse(gd2, (bx - br, by - br, bx + br, by + br),
                fill=(235, 250, 253, 70), outline=(240, 252, 255, 170), width=sc(2))
        ellipse(gd2, (bx - br * 0.4, by - br * 0.5, bx, by - br * 0.1), fill=(255, 255, 255, 170))
    # outline, rim, highlight streak
    ellipse(gd2, (cx - R, cy - R, cx + R, cy + R), outline=(148, 172, 182, 200), width=sc(4))
    ellipse(gd2, (cx - R + 7, cy - R + 7, cx + R - 7, cy + R - 7), outline=(255, 255, 255, 110), width=sc(2))
    # top opening rim (thick glass lip, sized to the bowl's chord there)
    ellipse(gd2, (cx - 152, 336, cx + 152, 372),
            fill=(214, 233, 238, 90), outline=(140, 164, 176, 220), width=sc(5))
    ellipse(gd2, (cx - 132, 342, cx + 132, 364),
            outline=(255, 255, 255, 170), width=sc(2))
    ellipse(gd2, (cx + 176, cy - 80, cx + 198, cy + 40), fill=(255, 255, 255, 30))
    img = Image.alpha_composite(img, glass)
    d = ImageDraw.Draw(img, "RGBA")
    # long studio highlight streak down the left glass
    streak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    std = ImageDraw.Draw(streak)
    std.ellipse([sc(cx - 262), sc(cy - 190), sc(cx - 168), sc(cy + 150)], fill=(255, 255, 255, 88))
    streak = streak.filter(ImageFilter.GaussianBlur(sc(10)))
    # keep the streak on the glass only
    gmask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gmask).ellipse([sc(cx - R), sc(cy - R), sc(cx + R), sc(cy + R)], fill=255)
    img.paste(Image.alpha_composite(img, streak), (0, 0), gmask)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- umbrella canopy: deep red dome directly over the fish ----
    ux, uy = 512, 470  # canopy centre; dome spans y 330..500
    canopy = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(canopy, "RGBA")
    # dome body
    cd.pieslice([sc(ux - 196), sc(uy - 148), sc(ux + 196), sc(uy + 148)],
                start=180, end=360, fill=(178, 30, 42, 255))
    cd.rectangle([sc(ux - 196), sc(uy - 2), sc(ux + 196), sc(uy + 4)], fill=(178, 30, 42, 255))
    # scalloped lower edge: overlapping circles cut the hem into arcs
    for i in range(6):
        sx = ux - 196 + i * 65 + 32
        cd.ellipse([sc(sx - 34), sc(uy - 16), sc(sx + 34), sc(uy + 22)], fill=(178, 30, 42, 255))
    img = Image.alpha_composite(img, canopy)
    # alternating panel shading (left lit, right in shade) on a clear layer
    cshade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    csd = ImageDraw.Draw(cshade)
    for i in range(6):
        shade = [(255, 255, 255, 34), (0, 0, 0, 0), (255, 255, 255, 14),
                 (0, 0, 0, 26), (0, 0, 0, 48), (0, 0, 0, 70)][i]
        if shade[3]:
            csd.pieslice([sc(ux - 196), sc(uy - 148), sc(ux + 196), sc(uy + 148)],
                         start=180 + i * 30, end=210 + i * 30, fill=shade)
    # soft top highlight
    csd.ellipse([sc(ux - 130), sc(uy - 128), sc(ux - 10), sc(uy - 62)], fill=(255, 255, 255, 46))
    # clip the shading to the dome silhouette so wedges cannot spill
    dome_mask = Image.new("L", (W, H), 0)
    dmd = ImageDraw.Draw(dome_mask)
    dmd.pieslice([sc(ux - 196), sc(uy - 148), sc(ux + 196), sc(uy + 148)],
                 start=180, end=360, fill=255)
    for i in range(6):
        sx = ux - 196 + i * 65 + 32
        dmd.ellipse([sc(sx - 34), sc(uy - 16), sc(sx + 34), sc(uy + 22)], fill=255)
    cshade.putalpha(Image.composite(cshade.split()[3], Image.new("L", (W, H), 0), dome_mask))
    img = Image.alpha_composite(img, cshade)
    d = ImageDraw.Draw(img, "RGBA")
    # cream segment ribs from apex to hem
    for i in range(7):
        ang = math.pi + i * (math.pi / 6)
        ex = ux + 196 * math.cos(ang)
        ey = uy + 148 * math.sin(ang) * 0.98 + 6
        d.line([sc(ux), sc(uy - 140), sc(ex), sc(ey)], fill=(246, 232, 205, 235), width=sc(4))
    # hem trim: scallop outlines only
    for i in range(6):
        sx = ux - 196 + i * 65 + 32
        d.arc([sc(sx - 34), sc(uy - 16), sc(sx + 34), sc(uy + 22)],
              start=0, end=180, fill=(120, 16, 28, 255), width=sc(3))
    # apex cap + finial ball where the drop rod meets the canopy
    ellipse(d, (ux - 13, uy - 168, ux + 13, uy - 138), fill=(52, 56, 62, 255))
    ellipse(d, (ux - 17, uy - 152, ux + 17, uy - 118), fill=chrome, outline=chrome_lo, width=sc(2))
    ellipse(d, (ux - 8, uy - 146, ux + 2, uy - 134), fill=chrome_hi)
    # umbrella shaft + curved handle hanging below the canopy toward the fish
    d.rectangle([sc(ux - 4), sc(uy + 2), sc(ux + 4), sc(uy + 74)], fill=(70, 74, 80, 255))
    d.arc([sc(ux - 4), sc(uy + 52), sc(ux + 44), sc(uy + 100)],
          start=0, end=180, fill=(70, 74, 80, 255), width=sc(7))

    # ---- the ONE accessory: white product tag tied to the stand ----
    # string from the pole out to the tag, which hangs clear of the canopy
    d.line([sc(756), sc(300), sc(806), sc(330)], fill=(120, 104, 84, 255), width=sc(3))
    tag = Image.new("RGBA", (sc(212), sc(100)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rounded_rectangle([0, 0, sc(212) - 1, sc(100) - 1], radius=sc(12),
                         fill=(253, 252, 248, 255), outline=(196, 188, 172, 255), width=sc(3))
    td.ellipse([sc(12), sc(38), sc(36), sc(62)], outline=(150, 140, 122, 255), width=sc(3))
    try:
        f_tag = ImageFont.truetype(FONT_SANS_BOLD, sc(20))
        f_sub = ImageFont.truetype(FONT_SANS, sc(15))
    except Exception:
        f_tag = ImageFont.load_default()
        f_sub = f_tag
    td.text((sc(47), sc(28)), "AQUASHELLA", font=f_tag, fill=(52, 48, 44, 255))
    td.text((sc(48), sc(60)), "fish umbrella", font=f_sub, fill=(128, 120, 108, 255))
    tag = tag.rotate(-10, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(tag, (sc(764), sc(318)))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- downscale to final size and save ----
    final = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    final.save(out, "PNG", optimize=True)
    print("wrote", out, final.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
