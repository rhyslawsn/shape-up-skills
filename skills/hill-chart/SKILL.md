---
name: hill-chart
description: Track a Shape Up cycle with hill charts: a live page where the team drags scopes uphill/downhill, plus PNG snapshots, JSON data and a status-without-asking report.
---

# Hill Chart

From Shape Up ch. 13. Every scope has two phases: **uphill**, figuring out the approach (unknowns, problem-solving), then **downhill**, execution once all the work is visible. The top of the hill is "I know exactly what to do; no unknowns left." A hill chart plots each scope as a dot on that curve. It replaces task counts (which grow as work is discovered) and estimates (which hide uncertainty), and lets managers see **how work is moving** without asking for status.

Use this skill when a team is building a bet and wants to track or report progress, when the user gives a status update on scopes, or asks what's stuck, at risk, or ready to cut. Scopes come from `shape-up-building` (map the scopes); use their names exactly.

## Where a hill chart lives
- **Live page (default for a real cycle).** One published Artifact per project per cycle. Anyone the user shares it with can drag dots and save an update; every save is a dated snapshot, so the history builds itself. Claude seeds it and reads it back through `ArtifactData`.
- **Files only** (no team page wanted, or Artifacts unavailable): a `.json` file holds the data; `render()` makes the PNG. Update it with `update()` whenever the user reports positions.

Either way, the **data is the source of truth**: the store (live page) or the `.json` (files). The PNG and SVG embed the same JSON (`shapeup-data` metadata, like the other Shape Up skills). **Never read dot positions off an image**; use `read_data()` or the store.

## Data model
Positions run **0–100**: 0 = not started, **50 = top of the hill**, 100 = done.
```
meta/project      {project, start, end}                 cycle dates YYYY-MM-DD
scopes/<id>       {name, risk: high|normal|low, order}
updates/<auto>    {date, ts, by, positions: {scope_id: 0-100}, note}
```
An update only lists the scopes that moved; a scope keeps its last position otherwise. The JSON file form is the same thing flattened: `{kind:"hill-chart", project, cycle:{start,end}, scopes:[...], updates:[{at, by, positions, note}]}`.

## Placing a dot from what people say
Build your way uphill: thinking isn't progress until something is built.
- **~15** — "I've thought about it" (approach considered, nothing built).
- **~30** — "I've validated the approach" (a spike or first working piece).
- **~45–50** — "I've built enough that I don't believe there are other unknowns."
- **50–100** — downhill, roughly by share of the remaining execution done; **100** only when it's deployed.
If someone reports theory-only progress, keep the dot low and say why. A dot that later **slides back** means an unknown surfaced: record it honestly (it's useful signal), don't hide it.

## Reading the chart (the report)
`report()` (and the live page's Status panel) flags what deserves a conversation:
- **Stuck uphill** — no movement for 5+ days while uphill. Ask "What can we solve to get this over the hill?", about the work, never "are you stuck?".
- **Slid back** — an unknown appeared; check whether earlier progress was only theoretical.
- **Uphill past the midpoint** — hammer the scope or cut it (`shape-up-building`); unsolved work disqualifies an extension.
- **High-risk scope not over the hill** — the scariest work should go uphill first (solve in the right sequence).
- **Most scopes never placed** — the scope map may be wrong.
Also look for a dot that stays put while the team reports progress: the scope probably bundles separate concerns. Suggest **refactoring it into smaller scopes** (e.g. "Notify" → email template / delivery / in-app display), then add them and mark the old one done or remove it.

When summarising, lead with the one-line summary, then only the flagged scopes, each with the specific question to ask. Don't recite every dot.

## Live page: setup
1. Write `hillchart.py` and the page template (both below) to the scratchpad. In the template, change the `<title>` to `<Project> Hill Chart`.
2. Publish it with the Artifact tool: `icon: "chart"`, `capabilities: {"db": {}, "user": {"scopes": ["profile"]}}`, a one-sentence description naming the project and cycle.
3. Seed the store: build the data with `new(project, start, end, scopes)` (plus `update(...)` for any positions the user already gave), then pass `to_db(data)` as the `writes` of one `ArtifactData` `batch` (max 50 writes per call; split if needed). Seed only the user's real scopes and positions, never invented ones.
4. Functional check: one `ArtifactData` `list` of `scopes` and `updates` to confirm the writes landed. Tell the user the page is private until they share it from its Share menu, and that teammates need Contributor access to drag and save.

## Live page: reading it back
`ArtifactData` `get` meta/project and `list` scopes and updates, each with the same `out_dir` (e.g. the scratchpad `hill/db`), then:
```python
d = from_db_dir(".../hill/db")
r = render(d, "/mnt/user-data/outputs/<project>-hill-<date>.svg")   # PNG + SVG + JSON snapshot
print(report_text(r))
```
Send the PNG and JSON into the chat when the user wants a snapshot (e.g. for a weekly note or kick-off/cool-down review). To record positions the user tells you in chat, add an `updates` document with `ArtifactData` `set` (new doc id, `by: null` means it came from Claude). To add or rename scopes, write `scopes/<id>`; deleting a scope is a user decision.

## Files-only mode
```python
from hillchart import *
d = new("Autopay", "2026-10-05", "2026-11-13", ["Setup screen", {"name": "Charge job", "risk": "high"}, "Disable"])
update(d, {"Setup screen": 30, "Charge job": 15}, at="2026-10-12", by="Sam", note="Spiked the charge job")
r = render(d, "/mnt/user-data/outputs/autopay-hill.svg")   # writes .json, .svg, .png
print(report_text(r))
# next time: d = read_data(".../autopay-hill.json"); update(d, {...}); render(d, same path)
```
`render(..., as_of="YYYY-MM-DD")` shows the chart as it stood on a past date.

## Image conventions
Dots use the validated categorical palette in scope order (never re-coloured when scopes are added); every dot is direct-labelled and listed in the legend, since several hues sit below 3:1 contrast. A hollow ring marks each scope's position at its previous update; ⚠ marks scopes with a flag. Look at the PNG with Read before sending it, only to check layout (labels clear of dots and each other), never to read data.

## `hillchart.py`
```python
"""hillchart.py: Shape Up hill charts as data + picture + status report.

Data (one JSON file per project/cycle; the source of truth):
{
  "kind": "hill-chart", "version": 1,
  "project": "Autopay", "cycle": {"start": "2026-10-05", "end": "2026-11-13"},
  "scopes": [{"id": "setup", "name": "Setup screen", "risk": "high"}, ...],   # risk: high|normal|low (optional)
  "updates": [{"at": "2026-10-12", "by": "Sam", "positions": {"setup": 20, ...}, "note": "..."}, ...]
}
Positions run 0-100: 0 = start, 50 = top of the hill (all unknowns solved), 100 = done.
Each update only needs the scopes that changed; a scope keeps its last position otherwise.

render() writes name.svg, name.png and name.json, with the data embedded in the SVG
(<metadata id="shapeup-data">) and PNG (text chunk "shapeup-data"); read_data() reads any of them.
report() returns the status-without-asking summary: phase, movement, and flags.
"""
import base64, datetime as dt, glob, html, json, math, os, re, shutil, subprocess

DATA_KEY = "shapeup-data"
# validated categorical order (dataviz reference palette), assigned by scope order, never cycled
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SURFACE, INK, INK2, MUTED, SERIOUS = "#fcfcfb", "#0b0b0b", "#52514e", "#b9b8b2", "#ec835a"


# ---------------- data ----------------
def new(project, start, end, scopes):
    """scopes: list of names or dicts {id, name, risk}."""
    out = []
    for s in scopes:
        s = {"name": s} if isinstance(s, str) else dict(s)
        s.setdefault("id", re.sub(r"\W+", "-", s["name"].lower()).strip("-"))
        s.setdefault("risk", "normal")
        out.append(s)
    return {"kind": "hill-chart", "version": 1, "project": project,
            "cycle": {"start": start, "end": end}, "scopes": out, "updates": []}


def update(data, positions, at=None, by=None, note=None):
    """Record a snapshot. positions: {scope_id_or_name: 0-100}. Unknown names are added as new scopes."""
    ids = {s["id"]: s for s in data["scopes"]}
    names = {s["name"].lower(): s["id"] for s in data["scopes"]}
    clean = {}
    for k, v in positions.items():
        sid = k if k in ids else names.get(str(k).lower())
        if sid is None:  # scope discovered mid-cycle
            data["scopes"].append(new("", "", "", [k])["scopes"][0])
            sid = data["scopes"][-1]["id"]
        clean[sid] = max(0, min(100, float(v)))
    data["updates"].append({"at": at or dt.date.today().isoformat(), "by": by, "positions": clean, "note": note})
    data["updates"].sort(key=lambda u: u["at"])
    return data


def history(data):
    """{scope_id: [(date, pos), ...]} carrying positions forward only when they were reported."""
    h = {s["id"]: [] for s in data["scopes"]}
    for u in data["updates"]:
        for sid, p in u["positions"].items():
            h.setdefault(sid, []).append((u["at"], p))
    return h


def current(data, as_of=None):
    """Latest known position per scope (None if never placed) as of a date."""
    cur = {s["id"]: None for s in data["scopes"]}
    for u in data["updates"]:
        if as_of and u["at"] > as_of:
            break
        cur.update(u["positions"])
    return cur


def phase(p):
    if p is None: return "not started"
    if p >= 100: return "done"
    if p > 50: return "downhill"
    if p == 50: return "top of hill"
    return "uphill"


def report(data, as_of=None, stuck_days=5):
    """Status without asking: one row per scope plus flags worth a conversation."""
    today = as_of or (data["updates"][-1]["at"] if data["updates"] else dt.date.today().isoformat())
    d = lambda s: dt.date.fromisoformat(s)
    start, end = d(data["cycle"]["start"]), d(data["cycle"]["end"])
    elapsed = max(0.0, min(1.0, (d(today) - start).days / max(1, (end - start).days)))
    cur, hist = current(data, today), history(data)
    rows, flags = [], []
    for s in data["scopes"]:
        sid, p = s["id"], cur[s["id"]]
        pts = [(a, v) for a, v in hist.get(sid, []) if a <= today]
        last_move = None
        for i in range(len(pts) - 1, 0, -1):
            if pts[i][1] != pts[i - 1][1]:
                last_move = pts[i][0]; break
        since = (d(today) - d(last_move or (pts[0][0] if pts else today))).days
        prev = pts[-2][1] if len(pts) > 1 else None
        delta = None if (p is None or prev is None) else p - prev
        rows.append({"id": sid, "name": s["name"], "risk": s.get("risk", "normal"), "position": p,
                     "phase": phase(p), "change_since_last_report": delta, "days_since_moved": since})
        if p is not None and p < 50 and since >= stuck_days:
            flags.append({"scope": s["name"], "kind": "stuck-uphill",
                          "say": f"'{s['name']}' has been uphill without moving for {since} days. What's the unknown holding it back?"})
        if delta is not None and delta < 0:
            flags.append({"scope": s["name"], "kind": "slid-back",
                          "say": f"'{s['name']}' slid back ({prev:g} → {p:g}). An unknown surfaced; was the uphill progress built or only thought through?"})
        if elapsed >= 0.5 and (p is None or p < 50):
            flags.append({"scope": s["name"], "kind": "uphill-late",
                          "say": f"Past the cycle midpoint and '{s['name']}' is still uphill. Scope-hammer it or cut it; uphill work can't justify an extension."})
        if s.get("risk") == "high" and elapsed >= 0.33 and (p is None or p < 50):
            flags.append({"scope": s["name"], "kind": "risky-not-first",
                          "say": f"'{s['name']}' is marked high-risk but isn't over the hill yet. Push the scariest work uphill first."})
    if len(data["scopes"]) and sum(r["position"] is None for r in rows) > len(rows) / 2 and elapsed > 0.25:
        flags.append({"scope": None, "kind": "unmapped",
                      "say": "Most scopes have never been placed. Are these the real scopes yet, or does the map need redrawing?"})
    done = sum(r["phase"] == "done" for r in rows)
    over = sum(r["position"] is not None and r["position"] >= 50 for r in rows)
    return {"project": data["project"], "as_of": today, "cycle_elapsed": round(elapsed, 2),
            "summary": f"{over}/{len(rows)} scopes over the hill, {done} done, {round(elapsed*100)}% of the cycle gone.",
            "scopes": rows, "flags": flags}


def report_text(r):
    lines = [f"{r['project']} — {r['as_of']}: {r['summary']}"]
    for s in r["scopes"]:
        p = "—" if s["position"] is None else f"{s['position']:g}"
        ch = "" if s["change_since_last_report"] in (None, 0) else f" ({s['change_since_last_report']:+g})"
        moved = "" if s["position"] is None else f"  last moved {s['days_since_moved']}d ago"
        lines.append(f"  {s['name']:<22} {s['phase']:<12} {p:>4}{ch}{moved}")
    if r["flags"]:
        lines.append("Worth a conversation:")
        by_scope = {}
        for f in r["flags"]:
            by_scope.setdefault(f["scope"], []).append(f["say"])
        for says in by_scope.values():
            lines.append("  • " + " ".join(says))
    return "\n".join(lines)


# ---------------- picture ----------------
def _font_b64():
    cache = os.path.expanduser("~/.cache/fatmarker/kalam-700.woff2")  # shared with the other Shape Up skills
    if not os.path.exists(cache):
        tmp = os.path.dirname(cache); os.makedirs(tmp, exist_ok=True)
        try:
            subprocess.run(["npm", "pack", "@fontsource/kalam", "--silent"], cwd=tmp, check=True, capture_output=True)
            tgz = sorted(glob.glob(os.path.join(tmp, "fontsource-kalam-*.tgz")))[-1]
            subprocess.run(["tar", "xzf", tgz, "-C", tmp], check=True)
            shutil.copy(os.path.join(tmp, "package/files/kalam-latin-700-normal.woff2"), cache)
        except Exception:
            return None
    return base64.b64encode(open(cache, "rb").read()).decode()


def _hill_xy(p, X0, W, BASE, H):
    x = X0 + W * p / 100
    y = BASE - H * (1 - math.cos(2 * math.pi * p / 100)) / 2   # smooth hill, peak at 50
    return x, y


def svg(data, as_of=None, trail=True, stuck_days=5):
    W, H, X0, BASE = 760, 230, 70, 330
    r = report(data, as_of, stuck_days)
    cur = {s["id"]: s["position"] for s in r["scopes"]}
    hist = history(data)
    flagged = {f["scope"] for f in r["flags"] if f["kind"] in ("stuck-uphill", "slid-back", "uphill-late")}
    color = {s["id"]: SERIES[i] if i < len(SERIES) else INK2 for i, s in enumerate(data["scopes"])}
    e = html.escape
    o = []
    pts = " ".join(f"{_hill_xy(p/2, X0, W, BASE, H)[0]:.1f},{_hill_xy(p/2, X0, W, BASE, H)[1]:.1f}" for p in range(0, 201))
    o.append(f'<line x1="{X0-20}" y1="{BASE}" x2="{X0+W+20}" y2="{BASE}" stroke="{MUTED}" stroke-width="2"/>')
    o.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    tx, ty = _hill_xy(50, X0, W, BASE, H)
    o.append(f'<line x1="{tx}" y1="{ty-14}" x2="{tx}" y2="{BASE}" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 6"/>')
    o.append(f'<text x="{X0+W*0.25}" y="{BASE+34}" text-anchor="middle" class="t2">Figuring things out</text>')
    o.append(f'<text x="{X0+W*0.75}" y="{BASE+34}" text-anchor="middle" class="t2">Making it happen</text>')
    o.append(f'<text x="{X0-20}" y="40" class="t1" font-size="26">{e(data["project"])}</text>')
    o.append(f'<text x="{X0+W+20}" y="40" text-anchor="end" class="t2">{e(r["as_of"])} · {round(r["cycle_elapsed"]*100)}% of cycle</text>')
    placed = sorted([(cur[s["id"]], s) for s in data["scopes"] if cur[s["id"]] is not None], key=lambda t: t[0])
    # ghost of each scope's previous reported position (hollow, same colour): shows movement at a glance
    if trail:
        for p, s in placed:
            hp = [v for a, v in hist.get(s["id"], []) if a <= r["as_of"]]
            if len(hp) > 1 and hp[-2] != p:
                gx, gy = _hill_xy(hp[-2], X0, W, BASE, H)
                o.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="7" fill="{SURFACE}" stroke="{color[s["id"]]}" stroke-width="2.5" opacity=".7"/>')
    # dots, then direct labels on the outside of the hill (left when uphill, right when downhill), nudged apart
    dots = []
    for p, s in placed:
        x, y = _hill_xy(p, X0, W, BASE, H)
        dots.append((x, y))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{color[s["id"]]}" stroke="{SURFACE}" stroke-width="2"/>')
    boxes = [(x - 12, y - 12, x + 12, y + 12) for x, y in dots]
    hit = lambda b: any(not (b[2] < c[0] or b[0] > c[2] or b[3] < c[1] or b[1] > c[3]) for c in boxes)
    for p, s in sorted(placed, key=lambda t: -abs(t[0] - 50)):
        x, y = _hill_xy(p, X0, W, BASE, H)
        lab = s["name"] + (" \u26a0" if s["name"] in flagged else "")
        w = len(lab) * 9 + 6
        if 42 <= p <= 58 or p >= 97 or p <= 3:
            anchor, lx, ly = "middle", x, y - 24
        elif p < 50:
            anchor, lx, ly = "end", x - 16, y - 8
        else:
            anchor, lx, ly = "start", x + 16, y - 8
        for _ in range(8):
            x0 = lx - w if anchor == "end" else lx - w / 2 if anchor == "middle" else lx
            b = (x0, ly - 14, x0 + w, ly + 6)
            if not hit(b):
                break
            ly -= 20
            lx += -6 if anchor == "end" else 6 if anchor == "start" else 0
        boxes.append(b)
        if abs(ly - (y - 8)) > 30 and anchor != "middle":
            o.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{lx:.1f}" y2="{ly+2:.1f}" stroke="{MUTED}" stroke-width="1.5"/>')
        o.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" class="t1">{e(lab)}</text>')
    # legend: every scope, incl. unplaced ones
    ly = BASE + 70
    lx = X0 - 20
    for s in data["scopes"]:
        lab = s["name"] + ("" if cur[s["id"]] is not None else " (not placed)")
        wid = 34 + len(lab) * 8.6
        if lx + wid > X0 + W + 20:
            lx, ly = X0 - 20, ly + 26
        o.append(f'<circle cx="{lx+8}" cy="{ly-5}" r="7" fill="{color[s["id"]]}"/>')
        o.append(f'<text x="{lx+22}" y="{ly}" class="t2">{e(lab)}</text>')
        lx += wid
    keys = []
    if trail and any(len([v for a, v in hist.get(s["id"], []) if a <= r["as_of"]]) > 1 for s in data["scopes"]):
        keys.append("hollow ring = position at the previous update")
    if flagged:
        keys.append("⚠ = worth a conversation (see report)")
    if keys:
        ly += 30
        o.append(f'<text x="{X0-20}" y="{ly}" class="t2">{e("   ·   ".join(keys))}</text>')
    height = ly + 24
    font = _font_b64()
    ff = "Kalam, 'Comic Sans MS', 'Marker Felt', cursive"
    style = ("<style>" + (f'@font-face{{font-family:Kalam;font-weight:700;src:url(data:font/woff2;base64,{font}) format("woff2")}}' if font else "")
             + f".t1{{font:700 17px {ff};fill:{INK}}} .t2{{font:700 15px {ff};fill:{INK2}}}</style>")
    payload = {**data, "report": r}
    meta = f'<metadata id="{DATA_KEY}"><![CDATA[{json.dumps(payload)}]]></metadata>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {height}" width="900" height="{height}">'
            f'{meta}{style}<rect width="100%" height="100%" fill="{SURFACE}"/>' + "".join(o) + "</svg>")


def render(data, path, as_of=None, trail=True, png=True, stuck_days=5):
    """Write name.json (data), name.svg and name.png (data embedded in both). Returns the report."""
    base = path.rsplit(".", 1)[0]
    json.dump(data, open(base + ".json", "w"), indent=2)
    s = svg(data, as_of, trail, stuck_days)
    open(base + ".svg", "w").write(s)
    if png:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                b = p.chromium.launch(); pg = b.new_page(device_scale_factor=2)
                pg.goto("file://" + os.path.abspath(base + ".svg")); pg.wait_for_timeout(300)
                pg.locator("svg").screenshot(path=base + ".png"); b.close()
            from PIL import Image, PngImagePlugin
            im = Image.open(base + ".png"); info = PngImagePlugin.PngInfo()
            info.add_itxt(DATA_KEY, json.dumps(data)); im.save(base + ".png", pnginfo=info)
        except ImportError:
            pass
    return report(data, as_of, stuck_days)


def read_data(path):
    """Hill chart data from its .json, .svg or .png - never read positions off the picture."""
    if path.endswith(".json"):
        return json.load(open(path))
    if path.endswith(".svg"):
        m = re.search(r'<metadata id="%s"><!\[CDATA\[(.*?)\]\]></metadata>' % DATA_KEY, open(path).read(), re.S)
        d = json.loads(m.group(1)) if m else None
        if d: d.pop("report", None)
        return d
    if path.endswith(".png"):
        from PIL import Image
        raw = Image.open(path).text.get(DATA_KEY)
        return json.loads(raw) if raw else None
    raise ValueError("expected .json, .svg or .png")


# ---------------- live page bridge ----------------
# The live hill chart page stores: meta/project {project,start,end}, scopes/<id> {name,risk,order},
# updates/<auto> {date,ts,by,positions,note}. These convert between that store and the JSON above.
def from_db(meta, scopes, updates):
    """Build hill-chart data from ArtifactData reads. Each arg is the doc body (meta) or a list of
    {id, data} / flat dicts with an 'id' key (scopes, updates), as ArtifactData list returns them."""
    flat = lambda rows: [({"id": r["id"], **r["data"]} if "data" in r else dict(r)) for r in rows]
    sc = sorted(flat(scopes), key=lambda r: r.get("order", 0))
    d = new(meta.get("project", "Hill chart"), meta.get("start", ""), meta.get("end", ""),
            [{"id": r["id"], "name": r["name"], "risk": r.get("risk", "normal")} for r in sc])
    for u in sorted(flat(updates), key=lambda r: r.get("ts") or r.get("date")):
        d["updates"].append({"at": u["date"], "by": u.get("by"), "positions": u.get("positions", {}), "note": u.get("note")})
    return d


def to_db(data):
    """`writes` for an ArtifactData 'batch' (max 50 per call) that seed the live page from hill-chart data."""
    ops = [{"op": "set", "collection": "meta", "doc_id": "project",
            "data": {"project": data["project"], "start": data["cycle"]["start"], "end": data["cycle"]["end"]}}]
    for i, s in enumerate(data["scopes"]):
        ops.append({"op": "set", "collection": "scopes", "doc_id": s["id"], "data": {"name": s["name"], "risk": s.get("risk", "normal"), "order": i}})
    for i, u in enumerate(data["updates"]):
        ops.append({"op": "set", "collection": "updates", "doc_id": f"seed-{i:03d}",
                    "data": {"date": u["at"], "ts": u["at"] + "T12:00:00Z", "by": None, "positions": u["positions"], "note": u.get("note")}})
    return ops


def from_db_dir(out_dir):
    """Build hill-chart data from ArtifactData reads saved with out_dir
    (<out_dir>/meta/project.json, <out_dir>/scopes/*.json, <out_dir>/updates/*.json)."""
    load = lambda f: json.load(open(f))
    rows = lambda c: [{"id": os.path.basename(f)[:-5], "data": load(f)} for f in sorted(glob.glob(os.path.join(out_dir, c, "*.json")))]
    return from_db(load(os.path.join(out_dir, "meta", "project.json")), rows("scopes"), rows("updates"))

```

## Live page template (`hill-chart.html`)
```html
<title>Cycle Hill Chart</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Kalam:wght@700&family=Atkinson+Hyperlegible:wght@400;700&display=swap">
<style>
/* Layout: one working column: header, the hill (full width), then status + history side by side, stacking on phones. */
:root{
  --bg:#f6f6f3; --panel:#fdfdfb; --fg:#171715; --fg2:#55544f; --muted:#a9a8a1; --line:#dddcd5;
  --accent:#2a5bd7; --serious:#c4562d; --serious-bg:#fbe9e1;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#e87ba4; --s6:#008300; --s7:#4a3aa7; --s8:#e34948;
  --hand:"Kalam","Comic Sans MS","Marker Felt",cursive;
  --body:"Atkinson Hyperlegible",system-ui,-apple-system,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#1a1a19; --panel:#222220; --fg:#f4f4f1; --fg2:#c3c2b7; --muted:#6c6b66; --line:#363633;
  --accent:#7aa2f7; --serious:#ec835a; --serious-bg:#3a2820;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181; --s6:#008300; --s7:#9085e9; --s8:#e66767; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#1a1a19; --panel:#222220; --fg:#f4f4f1; --fg2:#c3c2b7; --muted:#6c6b66; --line:#363633;
  --accent:#7aa2f7; --serious:#ec835a; --serious-bg:#3a2820;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181; --s6:#008300; --s7:#9085e9; --s8:#e66767; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:15px/1.5 var(--body);padding-inline:16px;padding-block:20px 40px}
main{max-width:980px;margin:0 auto;display:grid;gap:18px}
header{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:6px 16px}
h1{font:700 30px/1.15 var(--hand);margin:0;text-wrap:balance}
.meta{color:var(--fg2);font-variant-numeric:tabular-nums}
.bar{height:6px;border-radius:3px;background:var(--line);overflow:hidden;width:160px;display:inline-block;vertical-align:middle;margin-left:8px}
.bar>i{display:block;height:100%;background:var(--fg2)}
.hillwrap{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding-block:8px;overflow-x:auto}
svg{display:block;width:100%;min-width:560px;height:auto;touch-action:none}
.hill{fill:none;stroke:var(--fg);stroke-width:3;stroke-linecap:round}
.base{stroke:var(--line);stroke-width:2}
.mid{stroke:var(--muted);stroke-width:2;stroke-dasharray:6 6}
.lab{font:700 17px var(--hand);fill:var(--fg)}
.lab2{font:700 15px var(--hand);fill:var(--fg2)}
.dot{cursor:grab;stroke:var(--panel);stroke-width:2.5}
.dot:focus{outline:none;stroke:var(--fg);stroke-width:3}
.dot.ro{cursor:default}
.ghost{fill:var(--panel);stroke-width:2.5;opacity:.7}
.save{display:flex;flex-wrap:wrap;gap:8px;align-items:center;background:var(--panel);border:1px solid var(--accent);border-radius:10px;padding:10px 12px}
.save input{flex:1 1 220px;min-width:0}
input,select,button{font:inherit;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:7px;padding:6px 10px}
button{cursor:pointer}
button.primary{background:var(--accent);border-color:var(--accent);color:var(--panel);font-weight:700}
button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.cols{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.cols{grid-template-columns:1fr}}
section{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;min-width:0}
h2{font:700 13px var(--body);letter-spacing:.06em;text-transform:uppercase;color:var(--fg2);margin:0 0 10px}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:2px 14px;padding-block:7px;border-top:1px solid var(--line);font-variant-numeric:tabular-nums}
.row:first-child{border-top:0}
.row .flag{grid-column:1/-1}
@media (max-width:480px){.row{grid-template-columns:minmax(0,1fr) auto}.row>.phase:nth-child(3){grid-column:2}}
.sw{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:8px;vertical-align:-1px}
.phase{color:var(--fg2);white-space:nowrap}
.flag{display:block;margin-top:4px;background:var(--serious-bg);color:var(--fg);border-left:3px solid var(--serious);padding:4px 8px;border-radius:4px;font-size:14px}
.flag b{color:var(--serious)}
.hist{list-style:none;margin:0;padding:0;display:grid;gap:8px;max-height:340px;overflow:auto}
.hist li{display:grid;gap:2px;padding:6px 8px;border-radius:7px;cursor:pointer}
.hist li[aria-current="true"]{background:var(--bg);outline:1px solid var(--line)}
.hist .when{font-weight:700;font-variant-numeric:tabular-nums}
.hist .what{color:var(--fg2);font-size:14px}
.empty{color:var(--fg2)}
.add{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.add input{flex:1 1 160px;min-width:0}
.note{color:var(--fg2);font-size:14px}
@media (max-width:600px){.lab{font-size:24px}.lab2{font-size:21px}h1{font-size:26px}}
</style>

<main>
  <header>
    <h1 id="title">Hill chart</h1>
    <div class="meta" id="cycle">Loading the cycle…</div>
  </header>

  <div class="hillwrap"><svg id="hill" viewBox="0 0 900 420" role="img" aria-label="Hill chart"></svg></div>

  <div class="save" id="savebar" hidden>
    <span><b id="pendingCount">0</b> scope(s) moved. Save them as one update so the history shows the movement.</span>
    <input id="noteInput" type="text" placeholder="Optional note: what changed or what's blocking">
    <button class="primary" id="saveBtn">Save update</button>
    <button id="discardBtn">Discard</button>
  </div>

  <div class="cols">
    <section aria-labelledby="statusH">
      <h2 id="statusH">Status</h2>
      <div id="status" class="empty">No scopes yet. Ask Claude to set up this cycle's scopes, or add the first one below.</div>
      <form class="add" id="addForm" hidden>
        <input id="newScope" type="text" placeholder="New scope, e.g. Autosave" aria-label="New scope name">
        <select id="newRisk" aria-label="Risk"><option value="normal">Normal risk</option><option value="high">High risk</option><option value="low">Low risk</option></select>
        <button>Add scope</button>
      </form>
      <p class="note" id="howto" hidden>Drag a dot along the hill (or focus it and use the arrow keys). Left of the line: still figuring it out. Right: just execution.</p>
    </section>
    <section aria-labelledby="histH">
      <h2 id="histH">History</h2>
      <ul class="hist" id="hist"><li class="empty">Updates appear here each time someone saves positions.</li></ul>
    </section>
  </div>
</main>

<script>
const $ = id => document.getElementById(id);
const SERIES = ["--s1","--s2","--s3","--s4","--s5","--s6","--s7","--s8"];
const STUCK_DAYS = 5;
const S = { meta:null, scopes:[], updates:[], pending:{}, viewAt:null, canWrite:false, names:{}, db:null, user:null };
const W=760, H=230, X0=70, BASE=330;
const LABW = matchMedia("(max-width:600px)").matches ? 1.4 : 1;
const hx = p => X0 + W*p/100;
const hy = p => BASE - H*(1-Math.cos(2*Math.PI*p/100))/2;
const today = () => new Date().toISOString().slice(0,10);
const days = (a,b) => Math.round((new Date(b)-new Date(a))/864e5);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const color = sc => `var(${SERIES[S.scopes.indexOf(sc)] || "--fg2"})`;

function orderedUpdates(){ return [...S.updates].sort((a,b)=> (a.ts||a.date).localeCompare(b.ts||b.date)); }
function asOfList(){ const u = orderedUpdates(); return S.viewAt ? u.filter(x => (x.ts||x.date) <= S.viewAt) : u; }
function positionsAt(list){ const cur={}; for (const u of list) Object.assign(cur, u.positions||{}); return cur; }
function historyOf(id, list){ return list.filter(u => u.positions && id in u.positions).map(u => [u.date, u.positions[id]]); }
function phase(p){ return p==null?"not placed":p>=100?"done":p>50?"downhill":p===50?"top of hill":"uphill"; }

function report(){
  const list = asOfList(), cur = positionsAt(list);
  const lastDate = list.length ? list[list.length-1].date : today();
  const asOf = S.viewAt ? S.viewAt.slice(0,10) : (today() > lastDate ? today() : lastDate);
  const m = S.meta || {};
  const elapsed = (m.start && m.end) ? Math.max(0, Math.min(1, days(m.start, asOf)/Math.max(1, days(m.start, m.end)))) : 0;
  const rows = S.scopes.map(sc => {
    const p = cur[sc.id] ?? null, h = historyOf(sc.id, list);
    let last = h.length ? h[0][0] : asOf;
    for (let i=h.length-1;i>0;i--) if (h[i][1]!==h[i-1][1]) { last=h[i][0]; break; }
    const since = Math.max(0, days(last, asOf)), prev = h.length>1 ? h[h.length-2][1] : null;
    const flags=[];
    if (p!=null && p<50 && since>=STUCK_DAYS) flags.push(`Uphill with no movement for ${since} days. What's the unknown holding it back?`);
    if (prev!=null && p<prev) flags.push(`Slid back (${prev} → ${p}). An unknown surfaced.`);
    if (elapsed>=0.5 && (p==null || p<50)) flags.push(`Past the midpoint and still uphill. Hammer the scope or cut it.`);
    if (sc.risk==="high" && elapsed>=0.33 && (p==null || p<50)) flags.push(`High-risk work should be over the hill first.`);
    return {sc, p, since, prev, flags};
  });
  return {rows, elapsed, asOf};
}

function draw(){
  const svg = $("hill"), r = report(), list = asOfList();
  const live = !S.viewAt;
  const cur = {...positionsAt(list), ...(live ? S.pending : {})};
  let pts=""; for (let i=0;i<=200;i++){ const p=i/2; pts+=`${hx(p).toFixed(1)},${hy(p).toFixed(1)} `; }
  let o = `<line class="base" x1="${X0-20}" y1="${BASE}" x2="${X0+W+20}" y2="${BASE}"/>
    <polyline class="hill" points="${pts}"/>
    <line class="mid" x1="${hx(50)}" y1="${hy(50)-14}" x2="${hx(50)}" y2="${BASE}"/>
    <text class="lab2" x="${X0+W*.25}" y="${BASE+34}" text-anchor="middle">Figuring things out</text>
    <text class="lab2" x="${X0+W*.75}" y="${BASE+34}" text-anchor="middle">Making it happen</text>`;
  if (!S.scopes.length) o += `<text class="lab2" x="450" y="${BASE-120}" text-anchor="middle">No scopes on the hill yet</text>`;
  // ghosts: previous saved position for scopes that moved at their last update
  for (const sc of S.scopes){
    const h = historyOf(sc.id, list), now = cur[sc.id];
    const pend = live && sc.id in S.pending;
    if (!h.length || (!pend && h.length<2)) continue;
    const prev = pend ? h[h.length-1][1] : h[h.length-2][1];
    if (now!=null && prev!==now) o += `<circle class="ghost" cx="${hx(prev)}" cy="${hy(prev)}" r="7" stroke="${color(sc)}"/>`;
  }
  const placed = S.scopes.filter(sc => cur[sc.id]!=null).map(sc => ({sc, p:cur[sc.id]}));
  const boxes = placed.map(({p}) => [hx(p)-12, hy(p)-12, hx(p)+12, hy(p)+12]);
  const hit = b => boxes.some(c => !(b[2]<c[0]||b[0]>c[2]||b[3]<c[1]||b[1]>c[3]));
  const flagged = new Set(r.rows.filter(x=>x.flags.length).map(x=>x.sc.id));
  let labels="";
  for (const {sc,p} of [...placed].sort((a,b)=>Math.abs(b.p-50)-Math.abs(a.p-50))){
    const x=hx(p), y=hy(p), t = sc.name + (flagged.has(sc.id)?" ⚠":"") + (live && sc.id in S.pending ? " •" : "");
    const w = t.length*9*LABW+6;
    let a, lx, ly;
    if ((p>=42&&p<=58)||p>=97||p<=3){a="middle";lx=x;ly=y-24}else if(p<50){a="end";lx=x-16;ly=y-8}else{a="start";lx=x+16;ly=y-8}
    let b;
    for (let k=0;k<8;k++){ const x0 = a==="end"?lx-w:a==="middle"?lx-w/2:lx; b=[x0,ly-14,x0+w,ly+6]; if(!hit(b)) break; ly-=20; lx+= a==="end"?-6:a==="start"?6:0; }
    boxes.push(b);
    if (Math.abs(ly-(y-8))>30 && a!=="middle") labels += `<line x1="${x}" y1="${y}" x2="${lx}" y2="${ly+2}" stroke="var(--muted)" stroke-width="1.5"/>`;
    labels += `<text class="lab" x="${lx}" y="${ly}" text-anchor="${a}">${esc(t)}</text>`;
  }
  let dots="";
  for (const {sc,p} of placed){
    const ro = !(S.canWrite && live) ? " ro" : "";
    dots += `<circle class="dot${ro}" data-id="${esc(sc.id)}" cx="${hx(p)}" cy="${hy(p)}" r="11" fill="${color(sc)}" tabindex="${ro?-1:0}" role="slider" aria-label="${esc(sc.name)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(p)}" aria-valuetext="${esc(sc.name)}: ${phase(p)}, ${Math.round(p)}"></circle>`;
  }
  // unplaced scopes wait at the foot of the hill as hollow chips the team can drag on
  let tray="", tx=X0-20;
  for (const sc of S.scopes.filter(sc => cur[sc.id]==null)){
    tray += `<circle class="dot${S.canWrite&&live?"":" ro"}" data-id="${esc(sc.id)}" data-tray="1" cx="${tx+8}" cy="${BASE+70}" r="8" fill="${color(sc)}" tabindex="${S.canWrite&&live?0:-1}" role="slider" aria-label="${esc(sc.name)} (not placed)" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"></circle><text class="lab2" x="${tx+22}" y="${BASE+75}">${esc(sc.name)}</text>`;
    tx += 40 + sc.name.length*8.5*LABW;
  }
  if (tray) tray = `<text class="lab2" x="${X0-20}" y="${BASE+56}" font-size="13">Not on the hill yet${S.canWrite&&live?": drag onto it":""}</text>` + tray;
  svg.innerHTML = o + labels + dots + tray;
  renderSide(r); renderSave();
}

function renderSide(r){
  const m = S.meta;
  $("title").textContent = m?.project || "Hill chart";
  document.title = m?.project ? `${m.project} hill` : "Cycle Hill Chart";
  $("cycle").innerHTML = m?.start ? `${esc(m.start)} → ${esc(m.end)} · ${Math.round(r.elapsed*100)}% of cycle<span class="bar"><i style="width:${Math.round(r.elapsed*100)}%"></i></span>` : "No cycle dates set";
  if (S.scopes.length){
    $("status").className="";
    $("status").innerHTML = r.rows.map(x=>`<div class="row"><span><span class="sw" style="background:${color(x.sc)}"></span>${esc(x.sc.name)}${x.sc.risk==="high"?' <span class="phase">(high risk)</span>':""}</span><span class="phase">${phase(x.p)}</span><span class="phase">${x.p==null?"":x.since===0?"moved today":"moved "+x.since+"d ago"}</span>${x.flags.length?`<span class="flag"><b>⚠</b> ${x.flags.map(esc).join(" ")}</span>`:""}</div>`).join("");
  }
  const u = orderedUpdates().slice().reverse();
  if (u.length){
    const latest = `<li data-at="" aria-current="${!S.viewAt}"><span class="when">Latest</span><span class="what">Live positions${S.canWrite?", draggable":""}</span></li>`;
    $("hist").innerHTML = latest + u.map(x => {
      const moved = Object.keys(x.positions||{}).map(id => S.scopes.find(s=>s.id===id)?.name || id).join(", ");
      const who = x.by ? (S.names[x.by] || "Someone") : "Claude";
      return `<li data-at="${esc(x.ts||x.date)}" aria-current="${S.viewAt===(x.ts||x.date)}"><span class="when">${esc(x.date)} · ${esc(who)}</span><span class="what">${esc(moved)}${x.note?` — ${esc(x.note)}`:""}</span></li>`;
    }).join("");
  }
  $("addForm").hidden = !S.canWrite; $("howto").hidden = !S.canWrite || !S.scopes.length;
}
function renderSave(){
  const n = Object.keys(S.pending).length;
  $("savebar").hidden = !n; $("pendingCount").textContent = n;
}

// dragging along the hill: x maps to position, y follows the curve
let drag=null;
function toPos(evt){
  const svg=$("hill"), pt=svg.createSVGPoint(); pt.x=evt.clientX; pt.y=evt.clientY;
  const p = pt.matrixTransform(svg.getScreenCTM().inverse());
  return Math.max(0, Math.min(100, Math.round((p.x - X0)/W*100)));
}
$("hill").addEventListener("pointerdown", e => {
  const d = e.target.closest(".dot"); if (!d || d.classList.contains("ro")) return;
  drag = d.dataset.id; d.setPointerCapture(e.pointerId); e.preventDefault();
});
$("hill").addEventListener("pointermove", e => { if (!drag) return; S.pending[drag] = toPos(e); draw(); });
window.addEventListener("pointerup", () => { drag=null; });
$("hill").addEventListener("keydown", e => {
  const d = e.target.closest(".dot"); if (!d || d.classList.contains("ro")) return;
  const step = e.shiftKey ? 5 : 1, id = d.dataset.id;
  const cur = {...positionsAt(asOfList()), ...S.pending}[id] ?? 0;
  if (e.key==="ArrowRight"||e.key==="ArrowUp") S.pending[id]=Math.min(100,cur+step);
  else if (e.key==="ArrowLeft"||e.key==="ArrowDown") S.pending[id]=Math.max(0,cur-step);
  else return;
  e.preventDefault(); draw();
  document.querySelector(`.dot[data-id="${CSS.escape(id)}"]`)?.focus();
});
$("hist").addEventListener("click", e => {
  const li = e.target.closest("li[data-at]"); if (!li) return;
  S.viewAt = li.dataset.at || null; draw();
});
$("discardBtn").onclick = () => { S.pending={}; $("noteInput").value=""; draw(); };
$("saveBtn").onclick = async () => {
  if (!S.db) return;
  const positions = {...S.pending}, note = $("noteInput").value.trim();
  const now = new Date();
  $("saveBtn").disabled = true;
  try {
    await S.db.collection("updates").add({ date: now.toISOString().slice(0,10), ts: now.toISOString(), by: S.me || null, positions, note: note || null });
    S.pending = {}; $("noteInput").value = "";
  } catch (err) {
    $("pendingCount").textContent = "Couldn't save: " + (err?.code === "invalid_argument" ? "you have view-only access." : "try again in a moment.");
  } finally { $("saveBtn").disabled = false; draw(); }
};
$("addForm").addEventListener("submit", async e => {
  e.preventDefault(); const name = $("newScope").value.trim(); if (!name || !S.db) return;
  const id = name.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"") || ("s"+Date.now());
  await S.db.doc("scopes/"+id).set({ name, risk: $("newRisk").value, order: S.scopes.length });
  $("newScope").value = "";
});

async function nameAll(){
  const ids = [...new Set(S.updates.map(u=>u.by).filter(Boolean))];
  if (!S.user || !ids.length) return;
  const ps = await S.user.profiles(ids);
  for (const id of ids) S.names[id] = ps?.[id]?.name || "Someone";
  draw();
}

draw();
(async () => {
  const [db, user] = await Promise.all([claude.use("db"), claude.use("user")]);
  S.db = db; S.user = user;
  if (!db){ $("cycle").textContent = "Open this page signed in to see the cycle."; return; }
  S.me = user ? await user.id() : null;
  const cw = user ? await user.can("data.write") : null;
  S.canWrite = cw !== false;
  db.doc("meta/project").onSnapshot(s => { S.meta = s.exists ? s.data() : null; draw(); });
  db.collection("scopes").onSnapshot(q => { S.scopes = q.docs.map(d => ({id:d.id, ...d.data()})).sort((a,b)=>(a.order??0)-(b.order??0)); draw(); });
  db.collection("updates").onSnapshot(q => { S.updates = q.docs.map(d => ({id:d.id, ...d.data()})); draw(); nameAll(); });
})();
</script>
```

## Checklist
- [ ] Scope names match the scope map; risky scopes marked `risk: "high"`
- [ ] Positions follow the uphill thirds; theory-only work stays low
- [ ] Data came from the store or JSON, never from an image
- [ ] Report leads with the summary and the flagged scopes, each with its question
- [ ] Snapshot PNG + JSON delivered when a snapshot was asked for
- [ ] Live page: private until shared; teammates need Contributor to save updates
