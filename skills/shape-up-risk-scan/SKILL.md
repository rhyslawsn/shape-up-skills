---
name: "shape-up-risk-scan"
description: "Before betting on a Shape Up pitch, scan the real codebase for rabbit holes: where each element lands, missing precedent, tangled dependencies and hidden work, with patches and an appetite verdict."
---

# Shape Up Codebase Risk Scan

Shape Up, ch. 5: a fixed appetite is vulnerable to unknowns, so shapers hunt for rabbit holes **before** betting, turning a fat-tailed project into a thin-tailed one. This skill does that hunt against the actual code. Use it when a pitch (or a breadboard) is ready for de-risking, when the user asks "is this doable in N weeks?", "what could blow up?", "where would this go in the code?", or before a betting table.

It answers the book's questions with evidence:
- Does this need technical work we've never done here?
- Are we assuming parts fit together in ways nobody has checked?
- Is there a design problem we haven't actually solved?
- Are we leaving hard decisions to the team?

It is **not** an estimate and not an implementation plan. No task lists, no hours. Output is rabbit holes with patches, no-gos, questions for a technical expert, and a verdict against the appetite.

## Inputs
- The pitch: problem, **appetite**, solution elements. From chat, a pitch doc, or a Linear project (`shape-up-linear`).
- If one exists, the breadboard data (`breadboard` skill `read_data()`): its `places`, `affordances` and `new_places` are the element list. Never read them off an image.
- The repo. In order of preference:
  1. Already cloned in the session, or clone it: `gh repo clone <owner>/<repo> <dir> -- --depth 1` (gh is preconfigured), or `git clone --depth 1`.
  2. A folder connected from the user's computer: run `rg`/`grep` there with the device shell; copy `riskscan.py` there if it has Python and ripgrep, otherwise run the same searches by hand.
  3. Only GitHub connector access: use `search_code` and `get_file_contents` for the same questions (slower; say what you couldn't check).
Ask which repo if it isn't obvious. Read-only throughout: never commit, push, or change the user's code.

## Time box
Shaping moves fast, so the scan does too: aim for **~30–50 tool calls**. Prefer targeted searches and reading the 5–10 files that matter over reading the codebase. Stop when every element has a home and every risk has a patch. List what you didn't check rather than going deeper.

## Method
1. **Orient (5 min).** `orient(repo)` for stack, layout, key files, tests, CI, and the largest source files. Read the routes/schema files it lists and the README. Write a 5-line mental map: where screens, models, jobs and clients live.
2. **Search for the feature itself first.** Grep the pitch's own nouns and verbs (`locate(repo, [...])`). The most valuable finding is often that **part of it already exists** (in the dry run, "drafts" were already saved per room in the browser), which changes the problem, the appetite or both.
3. **Land every element.** For each breadboard place/affordance or pitch element, find the existing screen, component, controller, model or endpoint it touches. Mark it `existing`, `extend` (change something that exists) or `new`, with `file:line` evidence and the **nearest precedent** for anything new.
4. **Check precedent for each capability the pitch needs.** `precedent(repo)` gives quick hints (jobs, realtime, email, payments, auth, uploads, search, caching, flags, third-party APIs, push, i18n, analytics). Treat hits as leads and confirm by reading. A capability with **no precedent** (first background job, first payment, first realtime channel, first third-party API) is the classic rabbit hole.
5. **Trace the blast radius of each `extend`.** Count call sites of what you'd change, and look for:
   - **Caching and keys**: fragment/page caches, `touch`, cache keys built from `updated_at`, CDN or ISR revalidation. (Dry run: writing drafts onto a cached record would have broken sidebar caching.)
   - **Data**: migrations on big or hot tables, backfills, nullable vs default, unique indexes, multi-tenant scoping.
   - **Every client**: web, PWA, native apps, public API, webhooks, exports. A change in one shape must hold in all.
   - **Permissions**: who can see or do the new thing; row-level security; admin and guest roles.
   - **Hidden work**: notifications, search indexing, audit/logging, i18n, analytics, emails, settings screens, empty and error states.
   - **Tangles**: the largest files from `orient`, god objects, circular dependencies, code with no tests around it.
6. **Classify each finding.**
   - `rabbit-hole`: could blow the appetite; must be patched before betting.
   - `unknown`: plausible but unproven; needs a decision, a short spike, or an expert.
   - `known`: precedent exists, thin-tailed; just work.
7. **Patch each one** (the book's de-risking moves): `decide` (make the hard call now and write it into the pitch), `no-go` (declare the case out of bounds), `cut` (drop a non-essential element), `spike` (only if a day or two settles it, before the bet), `ask-expert`, or `accept` for known work.
8. **Write expert questions** in the book's form: "Is X possible in <appetite>?", not "Is X possible?". Include the constraint that makes it hard.
9. **Verdict against the appetite:** `fits`, `fits-with-patches`, or `does-not-fit`. If it doesn't fit, say what narrower problem would.

## Output
Build a `scan` dict and `render(scan, "/mnt/user-data/outputs/<pitch>-risk.md")`. That writes:
- `<name>.json`: the structured scan, the source of truth for later steps.
- `<name>.md`: a pitch-ready report (verdict, rabbit holes with patches and evidence, suggested no-gos, expert questions, where each element lands, known work, what wasn't checked). The same data is embedded in it, so `read_data()` works on either file.

Deliver both files into the chat. Then, in a few lines in chat: the verdict, the top 1–3 rabbit holes with their patches, and the questions to take to an engineer. Offer to fold the patches and no-gos into the pitch's **Rabbit holes** and **No-gos** sections (`shape-up-shaping`), or into the Linear project description (`shape-up-linear`).

Downstream uses of the data:
- Risks that survive into the bet mark their scopes `risk: "high"` on the hill chart (`hill-chart`), so the "push the scariest work uphill first" flag works.
- `does-not-fit` sends the pitch back to shaping. Don't let it reach the betting table as is.

### Scan shape
```
{
  "pitch": "...", "appetite": "Small batch: 2 weeks",
  "repo": {"name": "owner/repo", "commit": "abc1234"},
  "summary": "two or three sentences",
  "elements": [{"element": "...", "status": "existing|extend|new", "where": ["path:line"], "precedent": "..."}],
  "risks": [{"id": "R1", "title": "...", "severity": "rabbit-hole|unknown|known", "why": "...",
             "evidence": ["path:line", "absent: <what you searched for>"],
             "patch": {"type": "decide|no-go|cut|spike|ask-expert|accept", "text": "..."}}],
  "expert_questions": ["Is X possible in 2 weeks given Y?"],
  "no_gos": [],            # optional extra no-gos not tied to one risk
  "not_checked": ["..."],  # be honest about coverage
  "verdict": "fits|fits-with-patches|does-not-fit"
}
```
Every risk needs evidence: a `path:line`, or `absent: <the search that found nothing>`. Absence counts as evidence only if you say what you searched.

## Helper: `riskscan.py`
Write it to the scratchpad once per session. Needs Python 3 and ripgrep (`rg`); `orient`, `locate` and `precedent` only read files.
```python
"""riskscan.py: helpers for a Shape Up codebase risk scan (orient, locate, blast radius, report).

The judgement is yours; these helpers make the evidence fast and the output consistent.
  orient(repo)                -> dict: stack, manifests, top-level layout, key files, test/CI, size
  locate(repo, terms)         -> {term: {"files": n, "hits": n, "top": [(file, hits)...]}}  (ripgrep, case-insensitive)
  precedent(repo, kinds=None) -> {kind: [evidence files]} for common capabilities (jobs, realtime, email, payments...)
  render(scan, path)          -> writes path.json (source of truth) + path.md (pitch-ready report); returns md
  read_data(path)             -> the scan dict from its .json or the data block embedded in the .md
"""
import json, os, re, shutil, subprocess
from collections import Counter

DATA_KEY = "shapeup-data"
SKIP = ["!.git", "!node_modules", "!vendor", "!dist", "!build", "!.next", "!coverage", "!tmp", "!log", "!*.lock",
        "!*.min.js", "!*.map", "!public/assets", "!*.svg", "!*.snap"]
# precedent searches look at source only: no docs, CI, containers or ignore files
SOURCE_ONLY = ["!*.md", "!.github", "!Dockerfile*", "!.*ignore", "!*.yml", "!*.yaml", "!docs", "!test", "!tests", "!spec", "!__tests__"]

MANIFESTS = {
    "Gemfile": "Ruby", "package.json": "JavaScript/TypeScript", "pyproject.toml": "Python", "requirements.txt": "Python",
    "go.mod": "Go", "Cargo.toml": "Rust", "composer.json": "PHP", "pom.xml": "Java", "build.gradle": "JVM",
    "mix.exs": "Elixir", "Package.swift": "Swift", "pubspec.yaml": "Dart/Flutter", "deno.json": "Deno",
}
KEY_FILES = [  # routes, schema, app entry points: read these first
    "config/routes.rb", "db/schema.rb", "db/structure.sql", "prisma/schema.prisma", "schema.graphql",
    "app/router.tsx", "src/routes", "app/api", "pages/api", "src/app", "openapi.yaml", "openapi.json",
    "supabase/migrations", "migrations", "db/migrate", "alembic", "drizzle", "src/server", "server",
]
# capability -> ripgrep regex. "No precedent" for something the pitch needs is a risk signal, not proof.
PRECEDENT = {
    "background jobs": r"ActiveJob|perform_later|Sidekiq|SolidQueue|BullMQ|bullmq|celery|@shared_task|inngest|trigger\.dev|cron|pg_cron|queue\.add",
    "realtime / websockets": r"ActionCable|Turbo::StreamsChannel|broadcast_|socket\.io|WebSocket|supabase.*channel|pusher|ably|SSE|EventSource",
    "email": r"ActionMailer|deliver_later|deliver_now|nodemailer|from ['\"]resend|new Resend|sendgrid|postmark|aws-sdk-ses|SESClient|mailgun",
    "payments": r"stripe|Stripe|braintree|paddle|lemonsqueezy|checkout\.session|PaymentIntent",
    "auth / permissions": r"authorize|can\?|Pundit|CanCan|policy|requireAuth|getServerSession|auth\(\)|rls|row level security|role",
    "file uploads": r"ActiveStorage|has_one_attached|has_many_attached|multer|upload|S3Client|presigned|storage\.from",
    "search": r"pg_search|tsvector|elasticsearch|meilisearch|algolia|typesense|full.?text|FTS5|fts",
    "caching": r"Rails\.cache|<% cache |cached: true|cache\(|redis|Redis|unstable_cache|revalidate|memoize|lru",
    "feature flags": r"feature_flag|Flipper|flipper|LaunchDarkly|unleash|growthbook|posthog\.isFeatureEnabled|featureFlag",
    "third-party HTTP APIs": r"Net::HTTP|Faraday|HTTParty|axios|fetch\(|requests\.(get|post)|httpx",
    "push / mobile": r"web.?push|WebPush|apns|fcm|expo-notifications|service.?worker",
    "i18n": r"I18n\.t|\bt\(['\"]|i18next|useTranslation|gettext",
    "analytics / tracking": r"mixpanel|posthog|segment|amplitude|gtag|plausible|ahoy",
}


def _rg(repo, args):
    if not shutil.which("rg"):
        raise RuntimeError("ripgrep (rg) not found: install it or use grep -rIn as a fallback")
    cmd = ["rg", "--no-heading", "--hidden"] + [x for g in SKIP for x in ("-g", g)] + args
    # explicit "." and no stdin: otherwise rg searches stdin whenever it's a pipe (heredocs, subprocesses)
    out = subprocess.run(cmd + ["."], cwd=repo, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    return "\n".join(l[2:] if l.startswith("./") else l for l in out.splitlines())


def orient(repo):
    """Fast map of the codebase. Read the key files it lists before judging anything."""
    out = {"repo": os.path.abspath(repo)}
    try:
        out["commit"] = subprocess.run(["git", "log", "-1", "--format=%h %ad", "--date=short"], cwd=repo,
                                       capture_output=True, text=True).stdout.strip()
    except Exception:
        out["commit"] = None
    out["stack"] = sorted({lang for f, lang in MANIFESTS.items() if os.path.exists(os.path.join(repo, f))})
    out["manifests"] = [f for f in MANIFESTS if os.path.exists(os.path.join(repo, f))]
    out["top_level"] = sorted(d + ("/" if os.path.isdir(os.path.join(repo, d)) else "")
                              for d in os.listdir(repo) if not d.startswith(".git"))
    out["key_files"] = [k for k in KEY_FILES if os.path.exists(os.path.join(repo, k))]
    files = [l for l in _rg(repo, ["--files"]).splitlines()]
    ext = Counter(os.path.splitext(f)[1] or os.path.basename(f) for f in files)
    out["files"] = len(files)
    out["extensions"] = ext.most_common(8)
    out["tests"] = sorted({f.split("/")[0] + "/" for f in files
                           if re.search(r"(^|/)(test|tests|spec|__tests__)/|\.test\.|\.spec\.|_test\.", f)})[:5]
    out["ci"] = [f for f in files if f.startswith(".github/workflows/") or f in (".gitlab-ci.yml", ".circleci/config.yml")]
    # largest source files: places where changes tend to get tangled
    sizes = []
    for f in files:
        if re.search(r"\.(rb|js|jsx|ts|tsx|py|go|rs|ex|exs|php|java|kt|swift|vue|svelte)$", f):
            try:
                sizes.append((sum(1 for _ in open(os.path.join(repo, f), errors="ignore")), f))
            except OSError:
                pass
    out["largest_source_files"] = [(f, n) for n, f in sorted(sizes, reverse=True)[:8]]
    return out


def locate(repo, terms, top=6, glob=None):
    """Where each term lives: file count, hit count, and the busiest files. Use domain words from the pitch
    and breadboard (model names, screen names, affordance verbs), not generic ones."""
    res = {}
    for t in terms:
        args = ["-i", "-c", t] + (["-g", glob] if glob else [])
        rows = [l.rsplit(":", 1) for l in _rg(repo, args).splitlines() if ":" in l]
        rows = sorted(((f, int(n)) for f, n in rows), key=lambda r: -r[1])
        res[t] = {"files": len(rows), "hits": sum(n for _, n in rows), "top": rows[:top]}
    return res


def precedent(repo, kinds=None):
    """Which common capabilities already exist in the codebase (evidence = up to 5 files each)."""
    out = {}
    for k, rx in PRECEDENT.items():
        if kinds and k not in kinds:
            continue
        files = sorted(set(_rg(repo, [x for g in SOURCE_ONLY for x in ("-g", g)] + ["-l", "-e", rx]).splitlines()))
        out[k] = files[:5] + ([f"... +{len(files) - 5} more"] if len(files) > 5 else [])
    return out


# ---------------- report ----------------
SEVERITY = {"rabbit-hole": 0, "unknown": 1, "known": 2}
PATCH = {"decide": "Decide now", "no-go": "Declare a no-go", "cut": "Cut back", "spike": "Spike before betting",
         "ask-expert": "Ask a technical expert", "accept": "Accept (thin-tailed)"}
VERDICT = {"fits": "Fits the appetite", "fits-with-patches": "Fits the appetite if the patches below are adopted",
           "does-not-fit": "Doesn't fit the appetite: narrow the problem or reshape"}


def validate(scan):
    req = ["pitch", "appetite", "repo", "elements", "risks", "expert_questions", "verdict"]
    missing = [k for k in req if k not in scan]
    assert not missing, f"scan missing {missing}"
    assert scan["verdict"] in VERDICT, f"verdict must be one of {list(VERDICT)}"
    for r in scan["risks"]:
        assert r.get("severity") in SEVERITY, f"risk {r.get('id')}: severity must be one of {list(SEVERITY)}"
        assert r.get("patch", {}).get("type") in PATCH, f"risk {r.get('id')}: patch.type must be one of {list(PATCH)}"
        assert r.get("evidence"), f"risk {r.get('id')}: needs file:line evidence (or 'absent: <what you searched>')"
    for e in scan["elements"]:
        assert e.get("status") in ("existing", "extend", "new"), f"element {e.get('element')}: bad status"
    return True


def to_markdown(scan):
    L = [f"# Risk scan: {scan['pitch']}", "",
         f"**Appetite:** {scan['appetite']}  ·  **Repo:** {scan['repo'].get('name', '')} @ {scan['repo'].get('commit', '')}  ·  "
         f"**Verdict:** {VERDICT[scan['verdict']]}", ""]
    if scan.get("summary"):
        L += [scan["summary"], ""]
    risks = sorted(scan["risks"], key=lambda r: SEVERITY[r["severity"]])
    holes = [r for r in risks if r["severity"] != "known"]
    if holes:
        L += ["## Rabbit holes and unknowns (for the pitch)", ""]
        for r in holes:
            L.append(f"- **{r['title']}** ({r['severity']}). {r['why']}")
            L.append(f"  - {PATCH[r['patch']['type']]}: {r['patch']['text']}")
            L.append(f"  - Evidence: {', '.join(r['evidence'])}")
        L.append("")
    nogos = [r["patch"]["text"] for r in risks if r["patch"]["type"] == "no-go"]
    if nogos or scan.get("no_gos"):
        L += ["## Suggested no-gos", ""] + [f"- {x}" for x in nogos + scan.get("no_gos", [])] + [""]
    if scan["expert_questions"]:
        L += ["## Questions for a technical expert", ""] + [f"- {q}" for q in scan["expert_questions"]] + [""]
    L += ["## Where each element lands", "", "| Element | Status | Where | Precedent |", "|---|---|---|---|"]
    for e in scan["elements"]:
        L.append(f"| {e['element']} | {e['status']} | {', '.join(e.get('where', [])) or '—'} | {e.get('precedent') or '—'} |")
    L.append("")
    known = [r for r in risks if r["severity"] == "known"]
    if known:
        L += ["## Known work (thin-tailed, no action needed)", ""] + [f"- {r['title']}: {r['why']}" for r in known] + [""]
    if scan.get("not_checked"):
        L += ["## Not checked", ""] + [f"- {x}" for x in scan["not_checked"]] + [""]
    L += [f"<!-- {DATA_KEY}: {json.dumps(scan).replace('>', chr(92) + 'u003e')} -->", ""]  # '>' escaped so the comment can't close early
    return "\n".join(L)


def render(scan, path):
    """Validate, then write <base>.json and <base>.md (the .md embeds the same data). Returns the markdown."""
    validate(scan)
    base = path.rsplit(".", 1)[0]
    json.dump(scan, open(base + ".json", "w"), indent=2)
    md = to_markdown(scan)
    open(base + ".md", "w").write(md)
    return md


def read_data(path):
    if path.endswith(".json"):
        return json.load(open(path))
    m = re.search(r"<!-- %s: (.*?) -->" % DATA_KEY, open(path).read(), re.S)
    return json.loads(m.group(1)) if m else None
```

### Example (from a dry run on basecamp/once-campfire)
```python
from riskscan import *
o = orient("campfire"); print(o["key_files"], o["largest_source_files"][:3])
print(locate("campfire", ["draft", "composer", "unread", "membership"]))   # 'draft' already lives in composer_controller.js
print(precedent("campfire", ["background jobs", "realtime / websockets", "caching"]))
scan = {
  "pitch": "Drafts that follow you across devices", "appetite": "Small batch: 2 weeks",
  "repo": {"name": "basecamp/once-campfire", "commit": o["commit"].split()[0]},
  "summary": "Same-device drafts already exist (localStorage per room). New work is server-side drafts and a sidebar marker.",
  "elements": [
    {"element": "Draft saved per room", "status": "existing", "where": ["app/javascript/controllers/composer_controller.js:22"], "precedent": "localStorage composer-draft-<roomId>"},
    {"element": "Draft on another device", "status": "new", "where": ["db/schema.rb:82"], "precedent": "none"},
    {"element": "Sidebar draft marker", "status": "extend", "where": ["app/views/users/sidebars/show.html.erb:23"], "precedent": "unread dot"}],
  "risks": [
    {"id": "R1", "title": "Problem may already be solved", "severity": "rabbit-hole",
     "why": "Same-device drafts persist today, with a system test; only cross-device is missing.",
     "evidence": ["app/javascript/controllers/composer_controller.js:22-27", "test/system/composer_test.rb:32"],
     "patch": {"type": "decide", "text": "Narrow the pitch to cross-device drafts plus the marker."}},
    {"id": "R2", "title": "Draft writes bust sidebar caches", "severity": "rabbit-hole",
     "why": "Sidebar rows are fragment-cached on the membership; a draft column there re-renders rows on every save.",
     "evidence": ["app/views/users/sidebars/rooms/_direct.html.erb:1"],
     "patch": {"type": "decide", "text": "Own drafts table, saved without touching the membership."}},
    {"id": "R3", "title": "Live sync between two open devices", "severity": "unknown",
     "why": "Both devices save; syncing drafts live would be its own project.",
     "evidence": ["absent: searched 'draft' in app/channels"],
     "patch": {"type": "no-go", "text": "No live sync; last save wins."}}],
  "expert_questions": ["Is moving drafts server-side with debounced saves possible in 2 weeks without touching membership caching?"],
  "not_checked": ["Native/PWA clients beyond the web composer"],
  "verdict": "fits-with-patches"}
render(scan, "/mnt/user-data/outputs/drafts-risk.md")
```

## Checklist
- [ ] Searched for the feature itself before anything else
- [ ] Every element landed: existing / extend / new, with evidence and nearest precedent
- [ ] Every capability with no precedent called out
- [ ] Caching, data, clients, permissions and hidden work checked for each `extend`
- [ ] Every risk has evidence and a patch; no estimates or task lists
- [ ] Expert questions phrased "possible in <appetite>?"
- [ ] Verdict given; `not_checked` honest; .json and .md delivered