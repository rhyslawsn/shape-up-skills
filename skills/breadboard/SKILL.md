---
name: "breadboard"
description: "Breadboard a UI flow the Shape Up way: places, affordances and connections in words, rendered as a hand-drawn diagram (PNG + SVG + JSON data) for shaping and pitches."
---

# Breadboard

A **breadboard** is "a UI concept that defines affordances and their connections without visual styling" (Shape Up, ch. 4). Borrowed from electrical engineering: all the components and wiring, none of the industrial design. Use it during shaping (see `shape-up-shaping`) whenever the question is **flow**: what places exist, what people can do in each, and where each action leads. Also use when the user asks to map a user flow, sketch screens and navigation, or "breadboard" something.

Use `fat-marker-sketch` instead when the question is the 2D layout of one screen. Often you breadboard first, then fat-marker the one linchpin screen.

## The three elements
1. **Places** — things you can navigate to: screens, dialogs, menus, popovers, emails, notifications, pages. Written as an underlined name.
2. **Affordances** — things the user can see or act on in that place: buttons, links, fields, toggles, and also important copy or data shown. Listed under the place.
3. **Connection lines** — arrows from an affordance to the place it takes the user.

Everything is **words, not pictures**. No layout, no sizes, no visual hierarchy. Topology only: what connects to what.

## Method
1. **Find the entry point** in the existing product. Start from a place that already exists (mark it `[existing]`) and the affordance that kicks the flow off.
2. **Walk the flow forward.** For each new place, list only the affordances needed to solve the shaped problem, then follow each one to where it leads.
3. **Interrogate as you write.** Breadboarding's main value is that writing the flow "confronts us with questions we didn't originally think of." At each step ask:
   - What does the user need to see here to decide?
   - What happens on success, on failure, on cancel? Where do they land after?
   - Is there an existing place this should live in instead of a new one?
   - How is this turned off / undone / edited later, and by whom?
   - Does another role (admin, client, invoicer) need a place or affordance too?
   Record unresolved questions as `>` notes on the relevant place.
4. **Try alternatives.** If a step feels heavy, breadboard a second version (e.g. a separate Setup screen vs. a checkbox on the existing payment form) and compare: fewer new places and more reuse of existing ones usually fit a tighter appetite.
5. **Stop at the macro level.** No field-level validation, copy, or ordering beyond what's essential. If you're specifying details, they belong to the build team.
6. **Extract the elements.** End with a short list of what's actually new (e.g. "'Use this to Autopay?' checkbox on the existing payment form; 'Disable Autopay' on the invoicer's side"). This list goes into the pitch's Solution section.

## Notation
Write breadboards in this plain-text notation. It reads fine in chat, a doc or a pitch as-is, and the renderer below turns it into a diagram.

```
# Place name              a place
# Place name [existing]   an existing place (drawn grey)
- Affordance              something to see or act on
- Affordance -> Place     leads to another place
- Affordance -> Place : condition   labelled connection (e.g. "card valid")
> note                    open question or shaping decision (drawn in red)
// comment                ignored
```
Places referenced with `->` but never defined are added automatically as `[existing]`. Connections that loop back to an earlier place (Cancel, Done) are drawn as a small grey "→ Place" tag rather than a long arrow, to keep the diagram readable.

### Example
```
# Invoice [existing]
- Pay now -> Payment form
- Turn on Autopay -> Setup Autopay

# Payment form
- Card fields
- Use this to Autopay? (checkbox)
- Pay -> Confirmation
> Checkbox only shows for recurring invoices

# Setup Autopay
- Card fields
- Pay current invoice too?
- Save -> Confirmation : card valid
- Cancel -> Invoice

# Confirmation
- "Autopay is on" message
- Done -> Invoice

# Invoicer dashboard [existing]
- Disable Autopay -> Invoice
```

## Structured data — never OCR a breadboard
`render()` writes three files with the same base name:
- `name.png` / `name.svg` — the diagram for people.
- `name.json` — the **source of truth**: `title`, `question`, `places` (each with `existing`, `affordances` [{label, to, condition}] and `notes`), a flat `connections` list [{from, via, to, condition}], `new_places`, `open_questions` [{place, note}], and the original notation in `source`.

The same JSON is **embedded** in the SVG (`<metadata id="shapeup-data">`) and the PNG (iTXt chunk `shapeup-data`).

Rules:
- To find out what a breadboard contains, call `read_data(path)` on its `.json`, `.svg` or `.png`. **Don't look at the image to recover its contents**; only Read the PNG to judge layout quality.
- To change one, `text = to_text(read_data(path))` (or use `d["source"]`), edit the notation, and `render()` under a new name such as `-v2`.
- Use the data directly downstream: `new_places` and the affordances of new places become the pitch's element list; `open_questions` become rabbit holes or no-gos; `connections` give the flows to walk through in slow motion.
- Chat uploads, docs and image hosts may strip PNG metadata, so **always ship the `.json` beside the PNG**, and commit all three files when saving into a connected folder. If `read_data` returns `None`, ask for the `.json` or the notation.

## Rendering
Write `breadboard.py` (below) once per session to the scratchpad and call `render(text, "/mnt/user-data/outputs/<name>.svg", title=..., question=...)`. It uses Graphviz (`dot`) for layout and Playwright/Chromium for the PNG, and embeds the Kalam handwriting font (fetched from npm `@fontsource/kalam`, shared cache with `fat-marker-sketch`) so it matches the book's hand-drawn look. Pass `rankdir="TB"` for tall, mostly-linear flows. If `dot` is missing it writes a Mermaid `.mmd` file instead, which can be rendered in a page or doc that supports Mermaid.

Then:
1. **Look at the PNG** with Read before sharing: every arrow should start at the right affordance and land on the right place; nothing overlaps; notes are legible. If the graph tangles, split it into two breadboards (main flow, secondary flow) or switch `rankdir`.
2. Deliver the PNG and its `.json` into the chat (SendUserFile). For a pitch, include **both** the rendered image and the text notation so readers who weren't there can follow it.
3. List the open questions (`>` notes) separately after the image so they get answered or become rabbit holes / no-gos in the pitch.

```python
"""breadboard.py: Shape Up breadboards from a tiny text notation -> SVG + PNG (Graphviz), or Mermaid fallback.

Notation (one place per block):
    # Place name              a place: screen, dialog, menu, email, page...
    # Place name [existing]   an existing place (drawn grey) - things you're not changing
    - Affordance              something the user can see/act on (button, field, copy)
    - Affordance -> Place     an affordance that leads to another place
    - Affordance -> Place : condition   a labelled connection (label drawn in note colour)
    > note                    shaping note / open question (drawn in note colour)
Places referenced by -> but never defined are added automatically as [existing].

render() writes name.svg, name.png and name.json. The JSON (places, affordances, connections,
open questions, and the original notation) is also embedded in the SVG (<metadata id="shapeup-data">)
and PNG (text chunk "shapeup-data"), so read_data(path) on any of them returns the breadboard as data,
and to_text(read_data(path)) gives back editable notation.
"""
import base64, glob, html, json, os, re, shutil, subprocess

INK, OLD, NOTE = "#1f1f1f", "#9a9a94", "#e0442e"
DATA_KEY = "shapeup-data"


def parse(src):
    places, order = {}, []
    cur = None
    for raw in src.splitlines():
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if line.startswith("#"):
            m = re.match(r"#\s*(.+?)\s*(\[existing\])?$", line)
            name = m.group(1)
            cur = places.setdefault(name, {"existing": False, "items": [], "notes": []})
            cur["existing"] = bool(m.group(2))
            if name not in order:
                order.append(name)
        elif line.startswith("-") and cur is not None:
            m = re.match(r"-\s*(.+?)(?:\s*->\s*(.+?))?(?:\s*:\s*(.+))?$", line)
            cur["items"].append({"label": m.group(1), "to": m.group(2), "cond": m.group(3)})
        elif line.startswith(">") and cur is not None:
            cur["notes"].append(line[1:].strip())
    for name in list(order):
        for it in places[name]["items"]:
            t = it["to"]
            if t and t not in places:
                places[t] = {"existing": True, "items": [], "notes": []}
                order.append(t)
    return places, order


def back_edges(places, order):
    """Connections that close a loop (e.g. Cancel -> back to the start). Drawn inline as '-> Place' instead of an arrow."""
    back, state = set(), {}
    def dfs(n):
        state[n] = 1
        for i, it in enumerate(places[n]["items"]):
            t = it["to"]
            if not t:
                continue
            if state.get(t) == 1:
                back.add((n, i))
            elif t not in state:
                dfs(t)
        state[n] = 2
    for n in order:
        if n not in state:
            dfs(n)
    return back


def _id(name):
    return "p" + re.sub(r"\W", "_", name)


def to_dot(places, order, rankdir="LR"):
    e = html.escape
    back = back_edges(places, order)
    out = [f'digraph B {{ rankdir={rankdir}; bgcolor="transparent"; nodesep=0.5; ranksep=0.9; pad=0.3;',
           f'node [shape=plaintext fontname="Kalam Bold" fontsize=18 fontcolor="{INK}"];',
           f'edge [color="{INK}" penwidth=2 arrowhead=vee arrowsize=0.9 fontname="Kalam Bold" fontsize=14 fontcolor="{NOTE}"];']
    for name in order:
        p = places[name]
        col = OLD if p["existing"] else INK
        rows = [f'<TR><TD ALIGN="LEFT" PORT="title"><FONT POINT-SIZE="22" COLOR="{col}"><U><B>{e(name)}</B></U></FONT></TD></TR>']
        for i, it in enumerate(p["items"]):
            ref = f'  <FONT POINT-SIZE="15" COLOR="{OLD}">→ {e(it["to"])}</FONT>' if (name, i) in back else ""
            rows.append(f'<TR><TD ALIGN="LEFT" PORT="a{i}"><FONT COLOR="{col}">{e(it["label"])}</FONT>{ref}</TD></TR>')
        for n in p["notes"]:
            rows.append(f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="14" COLOR="{NOTE}">{e(n)}</FONT></TD></TR>')
        out.append(f'{_id(name)} [label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">{"".join(rows)}</TABLE>>];')
    for name in order:
        for i, it in enumerate(places[name]["items"]):
            if it["to"] and (name, i) not in back:
                lab = f' label=" {e(it["cond"])} "' if it["cond"] else ""
                out.append(f'{_id(name)}:a{i}:e -> {_id(it["to"])}:title:w [{lab}];' if rankdir == "LR"
                           else f'{_id(name)}:a{i} -> {_id(it["to"])}:title [{lab}];')
    out.append("}")
    return "\n".join(out)


def to_mermaid(places, order):
    """Fallback when Graphviz isn't installed (or for docs that render Mermaid)."""
    q = lambda t: t.replace('"', "#quot;")
    out = ["flowchart LR"]
    for name in order:
        p = places[name]
        body = "<br/>".join([f"<u><b>{q(name)}</b></u>"] + [q(it["label"]) for it in p["items"]] + [f"<i>{q(n)}</i>" for n in p["notes"]])
        out.append(f'  {_id(name)}["{body}"]')
        if p["existing"]:
            out.append(f"  style {_id(name)} color:{OLD}")
    for name in order:
        for it in places[name]["items"]:
            if it["to"]:
                lab = q(it["label"] + (f" ({it['cond']})" if it["cond"] else ""))
                out.append(f'  {_id(name)} -- "{lab}" --> {_id(it["to"])}')
    return "\n".join(out)


def to_dict(places, order, title=None, question=None):
    """Structured breadboard: places with affordances, a flat connection list, and open questions."""
    return {
        "kind": "breadboard", "version": 1, "title": title, "question": question,
        "places": [{"name": n, "existing": places[n]["existing"],
                    "affordances": [{"label": it["label"], "to": it["to"], "condition": it["cond"]} for it in places[n]["items"]],
                    "notes": places[n]["notes"]} for n in order],
        "connections": [{"from": n, "via": it["label"], "to": it["to"], "condition": it["cond"]}
                        for n in order for it in places[n]["items"] if it["to"]],
        "new_places": [n for n in order if not places[n]["existing"]],
        "open_questions": [{"place": n, "note": x} for n in order for x in places[n]["notes"]],
    }


def to_text(d):
    """Turn to_dict()/read_data() output back into breadboard notation for editing."""
    out = []
    for p in d["places"]:
        out.append(f"# {p['name']}" + (" [existing]" if p["existing"] else ""))
        for a in p["affordances"]:
            out.append(f"- {a['label']}" + (f" -> {a['to']}" if a["to"] else "") + (f" : {a['condition']}" if a["condition"] else ""))
        out += [f"> {n}" for n in p["notes"]]
        out.append("")
    return "\n".join(out).strip() + "\n"


def read_data(path):
    """Return the structured data behind a breadboard/sketch from its .json, .svg or .png - no OCR needed."""
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


def _png_embed(png_path, data):
    from PIL import Image, PngImagePlugin
    im = Image.open(png_path)
    info = PngImagePlugin.PngInfo()
    info.add_itxt(DATA_KEY, json.dumps(data))
    im.save(png_path, pnginfo=info)


def _font_b64():
    """Fetch Kalam from npm once: woff2 cached for embedding (shared with fat-marker-sketch),
    woff installed to ~/.fonts so Graphviz measures text with the real font."""
    cache = os.path.expanduser("~/.cache/fatmarker/kalam-700.woff2")
    sysfont = os.path.expanduser("~/.fonts/kalam-latin-700-normal.woff")
    if not (os.path.exists(cache) and os.path.exists(sysfont)):
        tmp = os.path.dirname(cache)
        os.makedirs(tmp, exist_ok=True)
        os.makedirs(os.path.dirname(sysfont), exist_ok=True)
        try:
            subprocess.run(["npm", "pack", "@fontsource/kalam", "--silent"], cwd=tmp, check=True, capture_output=True)
            tgz = sorted(glob.glob(os.path.join(tmp, "fontsource-kalam-*.tgz")))[-1]
            subprocess.run(["tar", "xzf", tgz, "-C", tmp], check=True)
            shutil.copy(os.path.join(tmp, "package/files/kalam-latin-700-normal.woff2"), cache)
            shutil.copy(os.path.join(tmp, "package/files/kalam-latin-700-normal.woff"), sysfont)
            subprocess.run(["fc-cache", "-f"], capture_output=True)
        except Exception:
            if not os.path.exists(cache):
                return None
    return base64.b64encode(open(cache, "rb").read()).decode()


def render(src, path, rankdir="LR", png=True, title=None, question=None):
    """Write name.svg, name.png and name.json (data embedded in all three).
    Returns the SVG path, or a .mmd Mermaid file (plus .json) if Graphviz is missing."""
    places, order = parse(src)
    base = path.rsplit(".", 1)[0]
    data = to_dict(places, order, title, question)
    data["source"] = src.strip() + "\n"
    json.dump(data, open(base + ".json", "w"), indent=2)
    if not shutil.which("dot"):
        open(base + ".mmd", "w").write(to_mermaid(places, order))
        return base + ".mmd"
    font = _font_b64()  # before dot, so Graphviz measures text with the real font
    svg = subprocess.run(["dot", "-Tsvg"], input=to_dot(places, order, rankdir), capture_output=True, text=True, check=True).stdout
    svg = svg[svg.index("<svg"):]
    ff = "Kalam, 'Comic Sans MS', 'Marker Felt', cursive"
    svg = svg.replace('font-family="Kalam Bold"', f'font-family="{ff}"').replace(' font-weight="bold"', '')
    svg = re.sub(r'<text (?![^>]*font-weight)', '<text font-weight="700" ', svg)
    style = (f'<style>@font-face{{font-family:Kalam;font-weight:700;src:url(data:font/woff2;base64,{font}) format("woff2")}}</style>'
             if font else "")
    meta = f'<metadata id="{DATA_KEY}"><![CDATA[{json.dumps(data)}]]></metadata>'
    head = meta + style + '<rect width="100%" height="100%" fill="#fdfcf8"/>'
    svg = re.sub(r"(<svg[^>]*>)", lambda m: m.group(1) + head, svg, count=1)
    # round line caps for a marker feel
    svg = svg.replace('stroke-width="2"', 'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"')
    open(base + ".svg", "w").write(svg)
    if png:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                b = p.chromium.launch()
                pg = b.new_page(device_scale_factor=2)
                pg.goto("file://" + os.path.abspath(base + ".svg"))
                pg.wait_for_timeout(300)
                pg.locator("svg").screenshot(path=base + ".png")
                b.close()
            _png_embed(base + ".png", data)
        except ImportError:
            pass
    return base + ".svg"
```

## Checklist
- [ ] Starts from an existing place; existing places marked `[existing]`
- [ ] Only words: places, affordances, connections — no layout or styling
- [ ] Every affordance that goes somewhere has an arrow; every place is reachable
- [ ] Success, cancel and "how do I turn this off later" paths covered
- [ ] Open questions captured as `>` notes and listed after the diagram
- [ ] Ends with a short list of new elements for the pitch
- [ ] PNG checked visually before sharing
- [ ] `title` and `question` set; `.json` delivered alongside the PNG