"""Generate the site's images: favicon, touch icon, social card and one artwork per question type.
Run: python3 tools/make_art.py   (needs Pillow)
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK, PAPER, HOT = "#0b0b0b", "#ffffff", "#e8461e"
TYPES = ["Geography", "Ancient History", "History", "Science & Nature", "Words & Language", "Film & TV",
         "Music", "Sport", "Food & Drink", "Art & Books", "People & Politics", "Business & Money"]
slug = lambda s: "".join(c if c.isalnum() else "-" for c in s.lower().replace("&", "and")).replace("--", "-").replace("--", "-").strip("-")

# ---------- favicon: a folded quesadilla, half-moon with charred dots ----------
FAV = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<style>.p{fill:#0b0b0b}.d{fill:#e8461e}@media (prefers-color-scheme:dark){.p{fill:#f4f4f4}}</style>
<path class="p" d="M4 40a28 28 0 0 1 56 0z"/>
<circle class="d" cx="22" cy="30" r="3.2"/><circle class="d" cx="34" cy="24" r="2.6"/><circle class="d" cx="44" cy="32" r="3"/><circle class="d" cx="30" cy="35" r="2"/>
<rect class="p" x="4" y="44" width="56" height="4"/>
</svg>
"""
open(os.path.join(ROOT, "favicon.svg"), "w").write(FAV)

def quesadilla(draw, cx, cy, r, ink=INK, hot=HOT):
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=ink)
    for dx, dy, s in [(-.43, -.36, .11), (.07, -.57, .09), (.43, -.29, .1), (-.07, -.18, .07)]:
        x, y, rr = cx + dx * r, cy + dy * r, s * r
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=hot)
    draw.rectangle([cx - r, cy + r * .14, cx + r, cy + r * .28], fill=ink)

for size, name in [(180, "apple-touch-icon.png"), (32, "favicon-32.png")]:
    im = Image.new("RGB", (size * 4, size * 4), PAPER); d = ImageDraw.Draw(im)
    quesadilla(d, size * 2, size * 2.35, size * 1.55)
    im.resize((size, size), Image.LANCZOS).save(os.path.join(ROOT, name))

# ---------- social card ----------
def font(names, size):
    for n in names:
        try: return ImageFont.truetype(n, size)
        except OSError: pass
    return ImageFont.load_default()
SERIF = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
MONO = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
W, H = 1200, 630
im = Image.new("RGB", (W * 2, H * 2), PAPER); d = ImageDraw.Draw(im); S = 2
d.rectangle([0, 0, W * S, H * S], fill=PAPER)
d.line([80 * S, 150 * S, (W - 80) * S, 150 * S], fill=INK, width=2 * S)
d.text((80 * S, 92 * S), "HOT QUESADILLAS", font=font(MONO, 26 * S), fill=INK)
d.text((80 * S, 210 * S), "Twenty-five questions", font=font(SERIF, 72 * S), fill=INK)
d.text((80 * S, 300 * S), "you can work out.", font=font(SERIF, 72 * S), fill=INK)
d.text((80 * S, 450 * S), "A fresh batch every Friday.", font=font(MONO, 26 * S), fill="#555555")
d.text((80 * S, 495 * S), "Turn down the heat if you need a clue.", font=font(MONO, 26 * S), fill="#555555")
quesadilla(d, (W - 175) * S, 330 * S, 118 * S)
im.resize((W, H), Image.LANCZOS).save(os.path.join(ROOT, "img", "social.png"))

# ---------- one artwork per type: line-drawn motifs on paper, 600x400 ----------
def art(t, rnd):
    w, h = 600, 400
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{t}">',
             '<style>.g{fill:none;stroke:#0b0b0b;stroke-width:1.4}.f{fill:#0b0b0b}.h{fill:#e8461e}.bg{fill:#ffffff}'
             '@media (prefers-color-scheme:dark){.g{stroke:#f4f4f4}.f{fill:#f4f4f4}.bg{fill:#0b0b0b}}</style>',
             f'<rect class="bg" width="{w}" height="{h}"/>']
    add = parts.append
    if t == "Geography":   # contour lines around two peaks
        for k in range(1, 14):
            for cx, cy, s in [(220, 210, 1), (410, 170, .8)]:
                r = k * 14 * s
                pts = " ".join(f"{cx + (r + 6 * math.sin(a * 5 + k)) * math.cos(a):.1f},{cy + (r * .7 + 5 * math.cos(a * 3 + k)) * math.sin(a):.1f}" for a in [i / 40 * 2 * math.pi for i in range(41)])
                add(f'<polyline class="g" points="{pts}"/>')
        add('<circle class="h" cx="410" cy="170" r="6"/>')
    elif t == "Ancient History":   # a colonnade
        add('<rect class="f" x="110" y="96" width="380" height="16"/><polygon class="f" points="110,96 300,40 490,96"/>')
        for k in range(6):
            x = 130 + k * 66
            for j in range(9): add(f'<line class="g" x1="{x + j * 4}" y1="122" x2="{x + j * 4}" y2="320"/>')
        add('<rect class="f" x="96" y="320" width="408" height="14"/><rect class="f" x="80" y="340" width="440" height="12"/><circle class="h" cx="300" cy="74" r="7"/>')
    elif t == "History":   # a timeline with ticks
        add('<line class="g" x1="60" y1="210" x2="540" y2="210"/>')
        for k in range(25):
            x = 60 + k * 20; L = 34 if k % 5 == 0 else 14
            add(f'<line class="g" x1="{x}" y1="{210 - L}" x2="{x}" y2="{210 + L}"/>')
        add('<circle class="h" cx="380" cy="210" r="10"/>')
    elif t == "Science & Nature":   # orbits
        for k, (rx, ry, rot) in enumerate([(220, 70, 0), (220, 70, 60), (220, 70, 120)]):
            add(f'<ellipse class="g" cx="300" cy="200" rx="{rx}" ry="{ry}" transform="rotate({rot} 300 200)"/>')
        add('<circle class="f" cx="300" cy="200" r="16"/><circle class="h" cx="512" cy="200" r="7"/>')
    elif t == "Words & Language":   # a letter grid
        letters = "HOTQUESADILLAS"
        for r in range(5):
            for c in range(9):
                ch = rnd.choice("ABCDEFGHIJKLMNOPRSTUVWY") if not (r == 2 and 2 <= c < 7) else "QUESO"[c - 2]
                cls = "h" if (r == 2 and 2 <= c < 7) else "f"
                add(f'<text class="{cls}" x="{84 + c * 54}" y="{96 + r * 62}" font-family="Georgia,serif" font-size="34" text-anchor="middle">{ch}</text>')
    elif t == "Film & TV":   # film strip
        add('<rect class="f" x="40" y="130" width="520" height="140"/>')
        for k in range(14): add(f'<rect class="bg" x="{52 + k * 37}" y="140" width="20" height="14"/><rect class="bg" x="{52 + k * 37}" y="246" width="20" height="14"/>')
        for k in range(4): add(f'<rect class="bg" x="{60 + k * 125}" y="166" width="108" height="68"/>')
        add('<circle class="h" cx="364" cy="200" r="12"/>')
    elif t == "Music":   # waveform
        for k in range(60):
            x = 60 + k * 8; a = abs(math.sin(k / 4.2)) * 110 * (0.4 + rnd.random() * 0.6)
            add(f'<line class="g" x1="{x}" y1="{200 - a:.1f}" x2="{x}" y2="{200 + a:.1f}" stroke-width="3"/>')
        add('<circle class="h" cx="300" cy="200" r="7"/>')
    elif t == "Sport":   # a pitch
        add('<rect class="g" x="70" y="70" width="460" height="260"/><line class="g" x1="300" y1="70" x2="300" y2="330"/><circle class="g" cx="300" cy="200" r="52"/>')
        add('<rect class="g" x="70" y="140" width="70" height="120"/><rect class="g" x="460" y="140" width="70" height="120"/><circle class="h" cx="300" cy="200" r="7"/>')
    elif t == "Food & Drink":   # quesadilla wedges on a plate
        add('<circle class="g" cx="300" cy="200" r="150"/><circle class="g" cx="300" cy="200" r="132"/>')
        for k in range(4):
            a0 = k * 90 + 8; a1 = a0 + 74
            p = lambda a, r: f"{300 + r * math.cos(math.radians(a)):.1f},{200 + r * math.sin(math.radians(a)):.1f}"
            add(f'<polygon class="f" points="300,200 {p(a0, 110)} {p((a0 + a1) / 2, 116)} {p(a1, 110)}"/>')
        add('<circle class="h" cx="300" cy="200" r="9"/>')
    elif t == "Art & Books":   # stacked spines
        x = 110
        for k in range(11):
            wdt = rnd.choice([22, 28, 34]); hh = rnd.randint(170, 250)
            add(f'<rect class="{"f" if k % 3 else "g"}" x="{x}" y="{320 - hh}" width="{wdt}" height="{hh}"/>'); x += wdt + 6
        add(f'<circle class="h" cx="{x + 30}" cy="300" r="9"/><line class="g" x1="90" y1="320" x2="510" y2="320"/>')
    elif t == "People & Politics":   # a seating chamber of dots
        for row in range(6):
            r = 80 + row * 26; n = 9 + row * 3
            for k in range(n):
                a = math.pi + math.pi * k / (n - 1)
                cls = "h" if (row == 3 and k == n // 2) else "f"
                add(f'<circle class="{cls}" cx="{300 + r * math.cos(a):.1f}" cy="{300 + r * math.sin(a):.1f}" r="6"/>')
    elif t == "Business & Money":   # a rising chart
        add('<line class="g" x1="70" y1="330" x2="530" y2="330"/><line class="g" x1="70" y1="70" x2="70" y2="330"/>')
        y = 300; pts = []
        for k in range(12):
            y -= rnd.randint(-10, 32); pts.append(f"{90 + k * 38},{max(90, y)}")
        add(f'<polyline class="g" stroke-width="3" points="{" ".join(pts)}"/>')
        lx, ly = pts[-1].split(","); add(f'<circle class="h" cx="{lx}" cy="{ly}" r="8"/>')
    add("</svg>")
    return "\n".join(parts)

rnd = random.Random(7)
for t in TYPES:
    open(os.path.join(ROOT, "img", "types", f"{slug(t)}.svg"), "w").write(art(t, rnd))
print("art written")
