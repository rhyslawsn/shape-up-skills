---
name: "fat-marker-sketch"
description: "Draw Shape Up fat marker sketches: deliberately rough, low-fidelity UI sketches (PNG + SVG + JSON data) with annotation callouts, for shaping and pitches."
---

# Fat Marker Sketch

A **fat marker sketch** is "a sketch of a UI concept at very low fidelity drawn with a thick line" (Shape Up, ch. 4 & 6). The thick line makes detail impossible, which keeps attention on *which elements exist and how they're arranged* rather than on styling. Use this skill whenever shaping work (see `shape-up-shaping`) needs a visual, or the user asks for a rough sketch, low-fi mockup, or "fat marker" drawing.

## When to sketch vs. breadboard
- **Breadboard** (words: places → affordances → connections) when the question is *flow*: what screens exist and where each action leads.
- **Fat marker sketch** when the **2D arrangement is the problem**: what goes where on one screen, grouping, hierarchy, where an affordance lives.
- Often both: breadboard the flow, then fat-marker the one screen whose layout is the linchpin.

## Two modes (from the book)
1. **Exploration sketch** — during shaping. Fast, several alternatives, can be near-indecipherable to outsiders. Produce 2–3 variants side by side when there's a real layout choice (e.g. "Add" inside each group vs. in the item menu).
2. **Pitch sketch** — redrawn for people who weren't in the room. Still rough, but legible: design in black ink, **labels and notes in a second colour**, **numbered callouts** keyed to short notes. When placement in the existing app matters, sketch the new affordances **on top of a faded screenshot** of the current UI and add a note that designers are free to change the layout.

## Rules that keep it a fat marker sketch
- Only these marks: screen/container boxes, buttons (outline or filled for primary), input fields, checkboxes, image boxes (box with an X), dots, lines/dividers, **scribbles for any body copy**, and short handwritten labels.
- **Real words only where the words are the design**: screen title, button labels, a key heading. Everything else is a scribble.
- **No** colour fills beyond black/white, icons, real images, exact spacing, typography choices, shadows, or pixel alignment. If you're tempted to add detail, the sketch is answering a question that belongs to the design team.
- Keep it to roughly 5–12 elements per screen. More means the scope isn't narrow enough or it should be split into two sketches.
- **New vs existing**: when showing a change to an existing screen, draw what's new in the annotation colour (or call it out) so the delta is obvious.
- Callouts explain *decisions and boundaries* ("tick = cooked, moves to bottom", "no ratings in v1"), not appearance.
- Canvas presets: desktop 800×500, mobile 360×640, dialog/popover 480×320. Match a screenshot's aspect ratio when overlaying one.

## Process
1. Confirm the one question the sketch must answer and the elements already agreed in shaping (from the breadboard or element list).
2. Lay out a coordinate plan in your head: top bar, main column, side areas. Sketch at the macro level only.
3. Write a short script using the helper below, giving the sketch a `title` and the `question` it answers; `save()` writes the PNG, SVG and JSON into `/mnt/user-data/outputs/` (or the user's connected folder).
4. **Look at the PNG** with Read before sharing. Check: nothing overlaps illegibly, callout arrows point at the right element, legend isn't clipped, it reads as rough rather than polished.
5. Deliver the PNG into the chat (SendUserFile) together with its `.json`, and, if it's for a pitch, embed the PNG in the pitch doc beside the text it illustrates. Put the callout notes in the legend *and* repeat anything critical in the pitch text.
6. For alternatives, render each variant as its own file (`sketch-a.png`, `sketch-b.png`) and state the trade-off in one line each.

## Structured data — never OCR a sketch
Every `save()` writes three files with the same base name:
- `name.png` — the picture for people.
- `name.svg` — scalable picture.
- `name.json` — the **source of truth**: canvas, seed, title, question, a `summary` (written text, buttons and whether primary, fields, counts of checkboxes/images, callouts with their legend notes) and the replayable `ops` list.

The same JSON is **embedded** in the SVG (`<metadata id="shapeup-data">`) and the PNG (iTXt chunk `shapeup-data`), so the image carries its own data.

Rules:
- To find out what a sketch contains (one you made earlier, one the user attached, or one in a connected folder), call `read_data(path)` on the `.json`, `.svg` or `.png`. **Do not look at the image to recover its contents.** Only use Read on the PNG to judge visual quality.
- To change a sketch, `s = Sketch.from_dict(read_data(path))`, add calls (or edit `d["ops"]` before rebuilding), and `save()` under a new name such as `-v2`. The rebuilt sketch is pixel-identical before your edits because the `seed` is stored.
- Chat uploads, docs and image hosts may strip PNG metadata, so **always ship the `.json` beside the PNG**, and commit all three files when saving into a connected folder.
- If `read_data` returns `None` (metadata stripped, or a sketch from elsewhere), ask for the `.json`. Fall back to reading the image only if there's no data at all, and then rebuild it as a new sketch so it has data from then on.
- `screenshot` ops store the file path, not the image, so keep the screenshot file with the sketch if you'll need to rebuild it.

## Helper: `fatmarker.py`
Write this file once per session (e.g. to the scratchpad) and import it. It needs Python and, for PNG output and auto-fitting, Playwright with Chromium. It fetches the Kalam handwriting font from npm (`@fontsource/kalam`) on first use and embeds it in the SVG so the file is self-contained; if npm is unreachable it falls back to system cursive fonts.

API summary (coordinates in px, origin top-left; `marker` sets stroke thickness, default 7):
- `Sketch(w, h, seed=1, marker=7, title=None, question=None)` — change `seed` for a different hand-drawn wobble; always set `title` and `question` (stored in the data).
- `box(x,y,w,h, color=INK, fill=None)` — screens, panels, cards.
- `button(x,y,w,h,"Label", filled=False)` — filled = primary action.
- `field(x,y,w,h,"placeholder")`, `checkbox(x,y,checked=False)`, `image(x,y,w,h)`, `dot(x,y)`, `line(x1,y1,x2,y2)`.
- `text(x,y,"Words", size=None, anchor="start")` — only for words that are part of the design.
- `scribble(x,y,w, lines=1, gap=None)` — placeholder body copy.
- Annotation layer (second colour): `callout(n, x, y, target=(tx,ty))`, `note(x,y,"text")`, `arrow(x1,y1,x2,y2)`, `legend(["note 1", "note 2"])` (placed to the right, numbered to match callouts, wrapped at 30 chars).
- `screenshot(path, opacity=0.35)` — call first to sketch over the existing UI.
- `save("name.svg")` — writes an auto-fitted SVG, a 2× PNG and a JSON beside it, data embedded in all three.
- `to_dict()`, `Sketch.from_dict(d)`, `read_data(path)` — structured data in and out (see above).

```python
"""fatmarker.py: rough, low-fidelity UI sketches as self-contained SVG + PNG + JSON.

Every save() writes name.svg, name.png and name.json. The same JSON is embedded in the SVG
(<metadata id="shapeup-data">) and the PNG (text chunk "shapeup-data"), so read_data(path) on any
of the three files returns the sketch's structure without looking at pixels, and
Sketch.from_dict(read_data(path)) rebuilds it for editing.
"""
import base64, functools, glob, html, inspect, json, math, os, random, re, subprocess

INK, NOTE = "#1f1f1f", "#e0442e"  # design ink, annotation colour

def _font_b64():
    """Find or fetch the Kalam font (npm @fontsource/kalam) and return base64 woff2, or None."""
    cache = os.path.expanduser("~/.cache/fatmarker/kalam-700.woff2")
    if not os.path.exists(cache):
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        tmp = os.path.dirname(cache)
        try:
            subprocess.run(["npm", "pack", "@fontsource/kalam", "--silent"], cwd=tmp, check=True, capture_output=True)
            tgz = glob.glob(os.path.join(tmp, "fontsource-kalam-*.tgz"))[0]
            subprocess.run(["tar", "xzf", tgz, "-C", tmp], check=True)
            os.rename(os.path.join(tmp, "package/files/kalam-latin-700-normal.woff2"), cache)
        except Exception:
            return None
    return base64.b64encode(open(cache, "rb").read()).decode()

DATA_KEY = "shapeup-data"


def _rec(fn):
    """Record top-level primitive calls so the sketch can be saved as data and replayed."""
    sig = inspect.signature(fn)
    @functools.wraps(fn)
    def wrap(self, *a, **k):
        if self._depth == 0:
            args = sig.bind(self, *a, **k).arguments
            args.pop("self")
            self.ops.append({"op": fn.__name__, **{n: (list(v) if isinstance(v, tuple) else v) for n, v in args.items()}})
        self._depth += 1
        try:
            return fn(self, *a, **k)
        finally:
            self._depth -= 1
    return wrap


class Sketch:
    def __init__(self, w=800, h=500, seed=1, marker=7, title=None, question=None):
        """title: short name. question: the one layout question this sketch answers."""
        self.w, self.h, self.m, self.seed = w, h, marker, seed
        self.title, self.question = title, question
        self.r = random.Random(seed)
        self.els, self.ops, self._depth = [], [], 0

    # ---- low-level rough strokes ----
    def _j(self, a=1.0):
        return self.r.uniform(-a, a) * self.m * 0.35

    def _seg(self, x1, y1, x2, y2, color=INK, width=None, overshoot=True):
        width = width or self.m
        if overshoot:
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1
            o = self.m * 0.5
            x1, y1 = x1 - dx / L * o * self.r.random(), y1 - dy / L * o * self.r.random()
            x2, y2 = x2 + dx / L * o * self.r.random(), y2 + dy / L * o * self.r.random()
        mx, my = (x1 + x2) / 2 + self._j(), (y1 + y2) / 2 + self._j()
        self.els.append(
            f'<path d="M{x1+self._j(.5):.1f},{y1+self._j(.5):.1f} Q{mx:.1f},{my:.1f} {x2+self._j(.5):.1f},{y2+self._j(.5):.1f}" '
            f'stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

    # ---- primitives ----
    @_rec
    def line(self, x1, y1, x2, y2, color=INK, width=None):
        self._seg(x1, y1, x2, y2, color, width)

    @_rec
    def box(self, x, y, w, h, color=INK, width=None, fill=None):
        if fill:
            self.els.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" rx="4"/>')
        for a, b in [((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)), ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))]:
            self._seg(*a, *b, color=color, width=width)

    @_rec
    def text(self, x, y, s, size=None, color=INK, anchor="start"):
        size = size or self.m * 3.4
        self.els.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
                        f'dominant-baseline="middle" font-family="Kalam, \'Comic Sans MS\', \'Marker Felt\', cursive" font-weight="700">{html.escape(s)}</text>')

    @_rec
    def button(self, x, y, w, h, label, filled=False):
        if filled:
            self.box(x, y, w, h, fill=INK)
            self.text(x + w / 2, y + h / 2, label, anchor="middle", color="#fff", size=min(h * 0.55, self.m * 3.4))
        else:
            self.box(x, y, w, h)
            self.text(x + w / 2, y + h / 2, label, anchor="middle", size=min(h * 0.55, self.m * 3.4))

    @_rec
    def field(self, x, y, w, h, placeholder=None):
        self.box(x, y, w, h, width=self.m * 0.7)
        if placeholder:
            self.text(x + self.m * 2, y + h / 2, placeholder, color="#9a9a94", size=min(h * 0.5, self.m * 3))

    @_rec
    def scribble(self, x, y, w, lines=1, gap=None, color=INK):
        """Wavy line(s) standing in for body copy."""
        gap = gap or self.m * 4
        for i in range(lines):
            ww = w if i < lines - 1 or lines == 1 else w * self.r.uniform(.45, .8)
            yy, step = y + i * gap, self.m * 2.2
            xx = x
            d = f"M{x:.1f},{yy:.1f}"
            up = True
            while xx < x + ww:
                nx = min(xx + step, x + ww)
                d += f" Q{(xx+nx)/2:.1f},{yy + (-1 if up else 1)*self.m*0.9:.1f} {nx:.1f},{yy:.1f}"
                xx, up = nx, not up
            self.els.append(f'<path d="{d}" stroke="{color}" stroke-width="{self.m*0.6}" fill="none" stroke-linecap="round" opacity=".55"/>')

    @_rec
    def image(self, x, y, w, h):
        self.box(x, y, w, h)
        self._seg(x, y, x + w, y + h, width=self.m * 0.5, overshoot=False)
        self._seg(x + w, y, x, y + h, width=self.m * 0.5, overshoot=False)

    @_rec
    def checkbox(self, x, y, size=None, checked=False):
        s = size or self.m * 4
        self.box(x, y, s, s, width=self.m * 0.7)
        if checked:
            self._seg(x + s * .2, y + s * .55, x + s * .45, y + s * .8, overshoot=False)
            self._seg(x + s * .45, y + s * .8, x + s * .9, y + s * .1, overshoot=False)

    @_rec
    def dot(self, x, y, r=None, color=INK):
        r = r or self.m * 0.9
        self.els.append(f'<circle cx="{x+self._j(.3):.1f}" cy="{y+self._j(.3):.1f}" r="{r}" fill="{color}"/>')

    @_rec
    def arrow(self, x1, y1, x2, y2, color=NOTE, width=None, bend=0.2):
        width = width or self.m * 0.6
        mx, my = (x1 + x2) / 2 - (y2 - y1) * bend, (y1 + y2) / 2 + (x2 - x1) * bend
        self.els.append(f'<path d="M{x1},{y1} Q{mx:.1f},{my:.1f} {x2},{y2}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round"/>')
        ang = math.atan2(y2 - my, x2 - mx)
        for da in (2.6, -2.6):
            L = self.m * 2.4
            self._seg(x2, y2, x2 + L * math.cos(ang + da), y2 + L * math.sin(ang + da), color, width, overshoot=False)

    # ---- annotation layer (second colour) ----
    @_rec
    def callout(self, n, x, y, target=None):
        r = self.m * 2.6
        self.els.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{NOTE}"/>')
        self.text(x, y + 1, str(n), anchor="middle", color="#fff", size=r * 1.3)
        if target:
            tx, ty = target
            ang = math.atan2(ty - y, tx - x)
            self.arrow(x + r * math.cos(ang), y + r * math.sin(ang), tx, ty)

    @_rec
    def note(self, x, y, s, size=None, anchor="start"):
        self.text(x, y, s, size=size or self.m * 2.8, color=NOTE, anchor=anchor)

    @_rec
    def screenshot(self, path, x=0, y=0, w=None, h=None, opacity=0.35):
        """Faded screenshot of the existing UI to sketch on top of. Call first."""
        mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
        data = base64.b64encode(open(path, "rb").read()).decode()
        self.els.insert(0, f'<image href="data:{mime};base64,{data}" x="{x}" y="{y}" width="{w or self.w}" height="{h or self.h}" opacity="{opacity}" preserveAspectRatio="xMidYMid meet"/>')

    @_rec
    def legend(self, items, x=None, y=None, wrap=30):
        """Numbered notes matching callouts, in the annotation colour, to the right of the sketch."""
        import textwrap
        x = self.w + self.m * 5 if x is None else x
        yy = self.m * 4 if y is None else y
        for i, s in enumerate(items, 1):
            self.callout(i, x + self.m * 2.6, yy)
            for j, ln in enumerate(textwrap.wrap(s, wrap)):
                self.note(x + self.m * 7, yy + j * self.m * 4, ln)
            yy += max(1, len(textwrap.wrap(s, wrap))) * self.m * 4 + self.m * 3.5

    # ---- structured data ----
    def to_dict(self):
        """Machine-readable sketch: replayable ops plus a semantic summary for quick reading."""
        words = lambda op: [o.get("label") or o.get("s") or o.get("placeholder") for o in self.ops if o["op"] == op]
        legend = next((o["items"] for o in self.ops if o["op"] == "legend"), [])
        return {
            "kind": "fat-marker-sketch", "version": 1,
            "title": self.title, "question": self.question,
            "canvas": {"w": self.w, "h": self.h}, "seed": self.seed, "marker": self.m,
            "summary": {
                "text": words("text"),
                "buttons": [{"label": o["label"], "primary": bool(o.get("filled"))} for o in self.ops if o["op"] == "button"],
                "fields": words("field"),
                "checkboxes": sum(o["op"] == "checkbox" for o in self.ops),
                "images": sum(o["op"] == "image" for o in self.ops),
                "notes": words("note"),
                "callouts": [{"n": o["n"], "target": o.get("target"),
                              "note": legend[o["n"] - 1] if 0 < o["n"] <= len(legend) else None}
                             for o in self.ops if o["op"] == "callout"],
                "legend": legend,
            },
            "ops": self.ops,
        }

    @classmethod
    def from_dict(cls, d):
        """Rebuild a sketch from to_dict()/read_data() output, e.g. to edit and re-save it."""
        s = cls(d["canvas"]["w"], d["canvas"]["h"], seed=d.get("seed", 1), marker=d.get("marker", 7),
                title=d.get("title"), question=d.get("question"))
        for o in d["ops"]:
            o = dict(o); op = o.pop("op")
            for k in ("target",):
                if isinstance(o.get(k), list):
                    o[k] = tuple(o[k])
            getattr(s, op)(**o)
        return s

    # ---- output ----
    def svg(self, embed_font=True, viewbox=None):
        font = _font_b64() if embed_font else None
        style = (f'<style>@font-face{{font-family:Kalam;font-weight:700;src:url(data:font/woff2;base64,{font}) format("woff2")}}</style>'
                 if font else "")
        x, y, w, h = viewbox or (-20, -20, self.w + 40, self.h + 40)
        meta = f'<metadata id="{DATA_KEY}"><![CDATA[{json.dumps(self.to_dict())}]]></metadata>'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}">'
                f'{meta}{style}<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fdfcf8"/>' + "".join(self.els) + "</svg>")

    def save(self, path, png=True):
        """Write name.svg (viewBox auto-fitted), name.png (2x) and name.json; data embedded in all three."""
        base = path.rsplit(".", 1)[0]
        path = base + ".svg"
        json.dump(self.to_dict(), open(base + ".json", "w"), indent=2)
        open(path, "w").write(self.svg())
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return path  # SVG only; viewBox not auto-fitted, so keep legends inside w/h
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(device_scale_factor=2)
            pg.goto("file://" + os.path.abspath(path))
            pg.wait_for_timeout(300)
            bb = pg.evaluate("""() => { const s=document.querySelector('svg'); const r=s.querySelector('rect'); r.remove();
                                 const b=s.getBBox(); return [b.x,b.y,b.width,b.height]; }""")
            pad = 20
            vb = (min(bb[0], 0) - pad, min(bb[1], 0) - pad, max(bb[0] + bb[2], self.w) - min(bb[0], 0) + 2 * pad,
                  max(bb[1] + bb[3], self.h) - min(bb[1], 0) + 2 * pad)
            vb = tuple(round(v, 1) for v in vb)
            open(path, "w").write(self.svg(viewbox=vb))
            if png:
                pg.goto("file://" + os.path.abspath(path))
                pg.wait_for_timeout(300)
                pg.locator("svg").screenshot(path=base + ".png")
            b.close()
        if png:
            _png_embed(base + ".png", self.to_dict())
        return path


def _png_embed(png_path, data):
    from PIL import Image, PngImagePlugin
    im = Image.open(png_path)
    info = PngImagePlugin.PngInfo()
    info.add_itxt(DATA_KEY, json.dumps(data))
    im.save(png_path, pnginfo=info)


def read_data(path):
    """Return the structured data behind a sketch/breadboard from its .json, .svg or .png - no OCR needed."""
    if path.endswith(".json"):
        return json.load(open(path))
    if path.endswith(".svg"):
        m = re.search(r'<metadata id="%s"><!\[CDATA\[(.*?)\]\]></metadata>' % DATA_KEY, open(path).read(), re.S)
        return json.loads(m.group(1)) if m else None
    if path.endswith(".png"):
        from PIL import Image
        raw = Image.open(path).text.get(DATA_KEY)
        return json.loads(raw) if raw else None
    raise ValueError("expected .json, .svg or .png")
```

### Example
```python
from fatmarker import *
s = Sketch(760, 480, seed=3, title="Dinner plan", question="Where does 'cooked' live on the weekly list?")
s.box(0, 0, 760, 480)
s.text(30, 40, "This week's dinners", size=30)
s.button(590, 20, 140, 44, "+ Add", filled=True)
for i, day in enumerate(["Mon", "Tue", "Wed"]):
    y = 100 + i * 110
    s.text(30, y + 10, day, size=24)
    s.image(110, y - 20, 110, 80)
    s.scribble(245, y, 280, lines=2, gap=28)
    s.checkbox(660, y - 4, checked=(i == 0))
s.callout(1, 600, 120, target=(655, 105))
s.callout(2, 560, 250, target=(455, 222))
s.legend(["Tick = cooked, moves to bottom", "Recipe title + 1 line, no ratings"])
s.save("/mnt/user-data/outputs/dinners-sketch.svg")   # -> .svg, .png, .json

# later, or in another session:
d = read_data("/mnt/user-data/outputs/dinners-sketch.png")
d["summary"]["callouts"]   # [{'n': 1, 'target': [655, 105], 'note': 'Tick = cooked, moves to bottom'}, ...]
s2 = Sketch.from_dict(d); s2.note(30, 450, "v2: add 'Leftovers' row"); s2.save("/mnt/user-data/outputs/dinners-sketch-v2.svg")
```

## Without the helper
If Python/Playwright aren't available, hand-write SVG with the same conventions: `stroke-width` 6–8 on an ~800px canvas, `stroke-linecap="round"`, slightly curved `Q` paths instead of perfect lines, black ink, one annotation colour (#e0442e), red numbered circles for callouts, wavy paths for text. As a last resort, describe the sketch as a labelled ASCII layout and say that it stands in for a drawing.

## Checklist before sharing
- [ ] Answers one layout question; elements match what was agreed in shaping
- [ ] Thick, wobbly, unmistakably unfinished
- [ ] Body copy is scribbles; only design-critical words written out
- [ ] New elements / decisions are in the annotation colour with numbered callouts
- [ ] Legend legible, not clipped; PNG checked visually
- [ ] `title` and `question` set; `.json` delivered alongside the PNG
- [ ] If over a screenshot: note that layout is a suggestion and designers have latitude