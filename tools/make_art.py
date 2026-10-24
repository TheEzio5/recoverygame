"""Generates every picture the app uses. Run from the project folder:
    python tools/make_art.py
Needs Pillow only (pip install pillow). Edit colours / drawings and re-run."""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- sunrise scene
def scene(w, h):
    """Sunrise over hills with a path. Used for icon, splash and banners."""
    k = 2
    W, H = w * k, h * k
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    top, mid, low = (11, 29, 58), (88, 64, 120), (246, 160, 77)
    horizon = int(H * 0.62)
    for y in range(H):
        t = min(y / horizon, 1)
        c = lerp(top, mid, t / 0.6) if t < 0.6 else lerp(mid, low, (t - 0.6) / 0.4)
        d.line([(0, y), (W, y)], fill=c)
    random.seed(7)
    for _ in range(int(40 * W * H / (1024 * 1024 * 4)) + 12):
        x, y = random.randint(0, W), random.randint(0, int(H * 0.35))
        r = random.choice([2, 3, 4]) * max(1, min(W, H) // 1024)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 244, 214))
    cx, cy, R = W // 2, horizon, int(min(W, H) * 0.17)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - R * 2, cy - R * 2, cx + R * 2, cy + R * 2], fill=(120, 70, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(min(W, H) // 22))
    img = ImageChops.add(img, glow)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 226, 150))

    def hills(base, amp, color, phase):
        pts = [(0, H)]
        for x in range(0, W + 1, 8):
            pts.append((x, base - amp * math.sin(x / W * math.pi * 2 + phase)
                        - amp * 0.4 * math.sin(x / W * math.pi * 5 + phase)))
        pts.append((W, H))
        d.polygon(pts, fill=color)

    hills(int(H * 0.70), H * 0.035, (58, 40, 84), 0.5)
    hills(int(H * 0.80), H * 0.04, (30, 24, 58), 2.0)
    pw = W * 0.08
    path = [(W / 2 - pw, H), (W / 2 + pw, H), (W / 2 + pw * 0.25, H * 0.74), (W / 2 - pw * 0.25, H * 0.74)]
    d.polygon([(int(x), int(y)) for x, y in path], fill=(246, 196, 120))
    return img.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- glyphs (0..100 space)
class Pen:
    def __init__(self, size):
        self.s = size / 100.0
        self.img = Image.new("RGBA", (size, size), CLEAR)
        self.d = ImageDraw.Draw(self.img)

    def p(self, *xy):
        return [v * self.s for v in xy]

    def rect(self, x0, y0, x1, y1, fill=WHITE, r=0):
        if r:
            self.d.rounded_rectangle(self.p(x0, y0, x1, y1), radius=r * self.s, fill=fill)
        else:
            self.d.rectangle(self.p(x0, y0, x1, y1), fill=fill)

    def circle(self, cx, cy, r, fill=WHITE):
        self.d.ellipse(self.p(cx - r, cy - r, cx + r, cy + r), fill=fill)

    def ellipse(self, x0, y0, x1, y1, fill=WHITE):
        self.d.ellipse(self.p(x0, y0, x1, y1), fill=fill)

    def poly(self, pts, fill=WHITE):
        self.d.polygon([(x * self.s, y * self.s) for x, y in pts], fill=fill)

    def line(self, pts, width, fill=WHITE):
        self.d.line([(x * self.s, y * self.s) for x, y in pts], fill=fill,
                    width=int(width * self.s), joint="curve")

    def pie(self, cx, cy, r, a0, a1, fill=WHITE):
        self.d.pieslice(self.p(cx - r, cy - r, cx + r, cy + r), a0, a1, fill=fill)

    def text(self, xy, s, size, fill=WHITE, bold=True):
        f = ImageFont.truetype(FONT_BOLD if bold else FONT, int(size * self.s))
        self.d.text((xy[0] * self.s, xy[1] * self.s), s, font=f, fill=fill, anchor="mm")


def g_ga(p):
    for cx, cy, r in ((28, 42, 9), (50, 34, 11), (72, 42, 9)):
        p.circle(cx, cy, r)
        p.pie(cx, cy + 22, r + 6, 180, 360)


def g_rehab(p):
    p.poly([(14, 44), (50, 16), (86, 44)])
    p.rect(22, 42, 78, 82, r=3)
    p.rect(46, 50, 54, 74, fill=CLEAR)
    p.rect(38, 58, 62, 66, fill=CLEAR)


def g_work(p):
    p.rect(38, 22, 62, 34, r=3)
    p.rect(44, 27, 56, 34, fill=CLEAR)
    p.rect(18, 32, 82, 78, r=6)
    p.rect(18, 52, 82, 56, fill=CLEAR)
    p.rect(46, 49, 54, 59, fill=WHITE)


def g_exercise(p):
    p.rect(30, 46, 70, 54)
    p.rect(20, 30, 30, 70, r=3)
    p.rect(70, 30, 80, 70, r=3)
    p.rect(11, 39, 20, 61, r=3)
    p.rect(80, 39, 89, 61, r=3)


def g_programming(p):
    p.line([(36, 30), (14, 50), (36, 70)], 9)
    p.line([(64, 30), (86, 50), (64, 70)], 9)
    p.line([(56, 26), (44, 74)], 8)


def g_rest(p):
    p.circle(46, 52, 28)
    p.circle(58, 44, 24, fill=CLEAR)
    p.text((72, 26), "z", 26)
    p.text((82, 14), "z", 16)


def g_status(p):
    p.rect(20, 56, 34, 80, r=2)
    p.rect(43, 38, 57, 80, r=2)
    p.rect(66, 22, 80, 80, r=2)


def g_back(p):
    p.poly([(16, 50), (46, 24), (46, 76)])
    p.rect(42, 41, 84, 59, r=2)


def g_save(p):
    p.rect(20, 20, 80, 80, r=6)
    p.rect(32, 20, 62, 40, fill=CLEAR)
    p.rect(54, 24, 59, 36, fill=WHITE)
    p.rect(30, 54, 70, 80, fill=CLEAR)
    p.rect(34, 58, 66, 80, fill=WHITE)


def g_endday(p):
    p.pie(50, 62, 24, 180, 360)
    for a in (-60, -30, 0, 30, 60):
        r = math.radians(a - 90)
        p.line([(50 + 30 * math.cos(r), 62 + 30 * math.sin(r)),
                (50 + 40 * math.cos(r), 62 + 40 * math.sin(r))], 4)
    p.rect(14, 62, 86, 68, r=2)
    p.rect(30, 74, 70, 79, r=2)


def g_finances(p):
    p.circle(50, 50, 32)
    p.text((50, 52), "€", 46, fill=CLEAR)


def g_safeguards(p):
    p.poly([(50, 14), (82, 25), (82, 50), (50, 86), (18, 50), (18, 25)])
    p.line([(35, 48), (46, 60), (66, 36)], 8, fill=CLEAR)


def g_story(p):
    p.poly([(14, 28), (47, 36), (47, 82), (14, 74)])
    p.poly([(53, 36), (86, 28), (86, 74), (53, 82)])
    for y in (46, 56, 66):
        p.line([(22, y - 2), (40, y + 3)], 3, fill=CLEAR)
        p.line([(60, y + 3), (78, y - 2)], 3, fill=CLEAR)


def g_relapse(p):
    p.circle(37, 38, 15)
    p.circle(63, 38, 15)
    p.poly([(23, 46), (77, 46), (50, 80)])


def g_start(p):
    p.circle(50, 42, 15)
    for a in range(0, 360, 45):
        r = math.radians(a)
        p.line([(50 + 22 * math.cos(r), 42 + 22 * math.sin(r)),
                (50 + 31 * math.cos(r), 42 + 31 * math.sin(r))], 4)
    p.pie(50, 124, 56, 180, 360)


def g_load(p):
    p.rect(16, 28, 46, 40, r=3)
    p.rect(16, 34, 84, 78, r=5)
    p.rect(22, 46, 78, 49, fill=CLEAR)


def g_exit(p):
    p.rect(30, 18, 70, 82, r=3)
    p.circle(60, 50, 3.5, fill=CLEAR)
    p.rect(14, 80, 86, 85, r=2)


def g_help(p):                      # lifebuoy
    p.circle(50, 50, 34)
    p.circle(50, 50, 16, fill=CLEAR)
    for a in (45, 135, 225, 315):
        r = math.radians(a)
        p.line([(50 + 15 * math.cos(r), 50 + 15 * math.sin(r)),
                (50 + 37 * math.cos(r), 50 + 37 * math.sin(r))], 7, fill=CLEAR)


def g_link(p):                      # globe
    p.circle(50, 50, 33)
    p.circle(50, 50, 27, fill=CLEAR)
    p.ellipse(37, 17, 63, 83)
    p.ellipse(42, 22, 58, 78, fill=CLEAR)
    p.rect(17, 47, 83, 53)
    p.rect(47, 17, 53, 83)


def g_test(p):                      # clipboard with a check mark
    p.rect(24, 22, 76, 86, r=6)
    p.rect(38, 14, 62, 30, r=4)
    p.rect(44, 19, 56, 25, fill=CLEAR)
    p.line([(36, 58), (46, 69), (66, 44)], 8, fill=CLEAR)


GLYPHS = {
    # key: (drawing, tile colour, banner title)
    "ga": (g_ga, "#2e9c8f", "G.A. Meeting"),
    "rehab": (g_rehab, "#3b82c4", "Rehabilitation"),
    "work": (g_work, "#c77d2c", "Work"),
    "exercise": (g_exercise, "#3aa05a", "Exercise"),
    "programming": (g_programming, "#5b5fc7", "Programming"),
    "rest": (g_rest, "#7a5bb5", "Rest"),
    "status": (g_status, "#4a6fa5", "Your Status"),
    "back": (g_back, "#6b7280", "Back"),
    "save": (g_save, "#2a9db5", "Save"),
    "endday": (g_endday, "#e0763a", "End of Day"),
    "finances": (g_finances, "#2f9e6e", "Finances"),
    "safeguards": (g_safeguards, "#2c4a7a", "Safeguards"),
    "story": (g_story, "#9a6b3f", "Recovery Story"),
    "relapse": (g_relapse, "#c05a7a", "Honest Day"),
    "start": (g_start, "#e89a3c", "Start Journey"),
    "load": (g_load, "#4a86a8", "Load Journey"),
    "exit": (g_exit, "#8a4a4a", "Exit"),
    "help": (g_help, "#c0504d", "Get Help Now"),
    "link": (g_link, "#2f7fbf", "Open link"),
    "test": (g_test, "#5a76b8", "Self-check"),
}


def glyph_layer(key, size):
    pen = Pen(size)
    GLYPHS[key][0](pen)
    return pen.img


def make_icons():
    S = 256
    for key, (_, color, _) in GLYPHS.items():
        base = hexc(color)
        tile = Image.new("RGBA", (S, S), CLEAR)
        grad = Image.new("RGBA", (S, S))
        gd = ImageDraw.Draw(grad)
        for y in range(S):
            gd.line([(0, y), (S, y)], fill=lerp(lerp(base, (255, 255, 255), 0.18), base, y / S) + (255,))
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=S // 5, fill=255)
        tile.paste(grad, (0, 0), mask)
        g = glyph_layer(key, S * 2).resize((S, S), Image.LANCZOS)
        g = g.resize((int(S * 0.72), int(S * 0.72)), Image.LANCZOS)
        tile.alpha_composite(g, ((S - g.width) // 2, (S - g.height) // 2))
        tile.save(os.path.join(ASSETS, "icons", f"{key}.png"))


def make_banners():
    W, H = 1080, 420
    font = ImageFont.truetype(FONT_BOLD, 84)
    # scene banners
    for key, title in (("title", "Recovery Quest"), ("journey", "Your Journey"),
                       ("welcome", "Welcome back")):
        img = scene(W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.text((W // 2, 70), title, font=font, fill=(255, 236, 190, 255), anchor="mm")
        img.convert("RGB").save(os.path.join(ASSETS, "banners", f"{key}.png"))
    # activity banners: coloured sky + big glyph + hills
    for key, (_, color, title) in GLYPHS.items():
        if key in ("back", "exit", "load", "start", "save", "link"):
            continue
        base = hexc(color)
        dark = lerp(base, (10, 14, 30), 0.65)
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        for y in range(H):
            d.line([(0, y), (W, y)], fill=lerp(dark, lerp(base, (255, 255, 255), 0.15), y / H))
        r = random.Random(key)
        for _ in range(26):
            x, y, s = r.randint(0, W), r.randint(0, H // 2), r.choice([2, 3, 4])
            d.ellipse([x - s, y - s, x + s, y + s], fill=lerp(base, (255, 255, 255), 0.7))
        pts = [(0, H)] + [(x, H - 60 - 30 * math.sin(x / 170 + 1)) for x in range(0, W + 1, 12)] + [(W, H)]
        d.polygon(pts, fill=lerp(dark, (0, 0, 0), 0.35))
        img = img.convert("RGBA")
        glyph = glyph_layer(key, 700).resize((260, 260), Image.LANCZOS)
        shadow = Image.new("RGBA", glyph.size, CLEAR)
        shadow.paste((0, 0, 0, 90), (0, 0), glyph.split()[3])
        img.alpha_composite(shadow, (150 + 6, 80 + 8))
        img.alpha_composite(glyph, (150, 80))
        d = ImageDraw.Draw(img)
        size = 84
        f = font
        while d.textlength(title, font=f) > W - 470 - 40 and size > 30:
            size -= 4
            f = ImageFont.truetype(FONT_BOLD, size)
        d.text((470, H // 2 - 6), title, font=f, fill=(255, 255, 255, 255), anchor="lm")
        img.convert("RGB").save(os.path.join(ASSETS, "banners", f"{key}.png"))


def make_app_icon_and_splash():
    scene(1024, 1024).save(os.path.join(ASSETS, "icon.png"))      # RGB: iOS forbids transparency
    W, H = 1080, 1920
    sp = Image.new("RGB", (W, H), (11, 29, 58))
    sp.paste(scene(W, W), (0, (H - W) // 2 + 140))
    dd = ImageDraw.Draw(sp)
    dd.text((W // 2, 340), "Recovery Quest", font=ImageFont.truetype(FONT_BOLD, 96),
            fill=(255, 236, 190), anchor="mm")
    dd.text((W // 2, 450), "One day at a time.", font=ImageFont.truetype(FONT, 44),
            fill=(210, 200, 225), anchor="mm")
    sp.save(os.path.join(ASSETS, "presplash.png"))


if __name__ == "__main__":
    os.makedirs(os.path.join(ASSETS, "icons"), exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "banners"), exist_ok=True)
    make_app_icon_and_splash()
    make_icons()
    make_banners()
    print("art generated in", ASSETS)
