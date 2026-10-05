"""Check every skill in skills/: frontmatter is valid, and the helper code embedded in SKILL.md
runs exactly as written (helpers are extracted from the ```python blocks, examples are executed).

    python tests/run_skill_code.py            # all skills
    python tests/run_skill_code.py hill-chart # one skill

Needs: python3, pillow, playwright (+ chromium), graphviz (dot), ripgrep (rg), node/npm, git.
"""
import os, re, subprocess, sys, tempfile, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
OUT = "/mnt/user-data/outputs/"


def frontmatter(md):
    m = re.match(r"---\n(.*?)\n---\n", md, re.S)
    assert m, "missing YAML frontmatter"
    fm = dict(re.findall(r"^(\w+):\s*\"?(.*?)\"?\s*$", m.group(1), re.M))
    assert fm.get("name") and fm.get("description"), "frontmatter needs name and description"
    assert len(fm["description"]) <= 1024, "description over 1024 chars"
    return fm


def py_blocks(md):
    return re.findall(r"```python\n(.*?)```", md, re.S)


def module_blocks(md):
    """Helper modules: python blocks that start with a '<name>.py' docstring."""
    return [(re.match(r'"""(\w+)\.py', b).group(1), b) for b in py_blocks(md) if re.match(r'"""\w+\.py', b)]


def run(code, cwd):
    p = subprocess.run([sys.executable, "-c", code], cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600)
    if p.returncode:
        raise RuntimeError(p.stderr[-3000:])
    return p.stdout


def check(name):
    md = open(os.path.join(SKILLS, name, "SKILL.md")).read()
    fm = frontmatter(md)
    assert fm["name"] == name, f"frontmatter name {fm['name']!r} != folder {name!r}"
    mods = module_blocks(md)
    if not mods:
        return "frontmatter ok (no code)"
    work = tempfile.mkdtemp(prefix=f"{name}-")
    out = os.path.join(work, "out") + "/"
    os.makedirs(out)
    for mod, code in mods:
        open(os.path.join(work, mod + ".py"), "w").write(code)
        run(f"import {mod}", work)                          # imports cleanly
    examples = [b for b in py_blocks(md) if not re.match(r'"""\w+\.py', b) and "..." not in b.split("#")[0]]
    notes = []
    if name == "breadboard":                                # example is notation, not python
        src = re.findall(r"### Example\n```\n(.*?)```", md, re.S)[0]
        open(os.path.join(work, "ex.txt"), "w").write(src)
        examples = ["from breadboard import *\nd_src=open('ex.txt').read()\nrender(d_src, '" + out + "ex.svg', title='t', question='q')\n"
                    "d=read_data('" + out + "ex.png'); assert d and d['places'], 'no data in png'\n"
                    "assert parse(to_text(d))[1] == parse(d_src)[1], 'round trip'"]
    if name == "shape-up-risk-scan" and not os.path.exists(os.path.join(work, "campfire")):
        subprocess.run(["git", "clone", "--depth", "1", "-q", "https://github.com/basecamp/once-campfire.git",
                        os.path.join(work, "campfire")], check=True)
    for ex in examples:
        ex = "\n".join(l for l in ex.replace(OUT, out).splitlines() if not l.lstrip().startswith("# next time"))
        run(ex, work)
        notes.append("example ok")
    made = sorted(os.listdir(out))
    if name == "fat-marker-sketch":
        run("from fatmarker import *\nfor f in ['dinners-sketch.png','dinners-sketch-v2.json']:\n"
            "    d=read_data('" + out + "'+f); assert d and d['ops'], f", work)
    if name == "hill-chart":
        run("from hillchart import *\nd=read_data('" + out + "autopay-hill.png'); assert d['updates'], 'no data'\n"
            "assert len(to_db(d))>0 and from_db_dir", work)
        page = re.findall(r"```html\n(.*?)```", md, re.S)[0]
        js = re.findall(r"<script>(.*?)</script>", page, re.S)[0]
        open(os.path.join(work, "page.js"), "w").write(js)
        subprocess.run(["node", "--check", os.path.join(work, "page.js")], check=True)
        notes.append("page script parses")
    return f"{len(mods)} helper(s), {', '.join(notes)}; wrote {len(made)} files"


def main(names):
    names = names or sorted(d for d in os.listdir(SKILLS) if os.path.isfile(os.path.join(SKILLS, d, "SKILL.md")))
    failed = 0
    for n in names:
        try:
            print(f"PASS {n}: {check(n)}")
        except Exception as e:
            failed += 1
            print(f"FAIL {n}: {e}")
            traceback.print_exc(limit=1)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
