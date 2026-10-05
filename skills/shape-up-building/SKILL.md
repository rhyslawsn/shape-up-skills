---
name: shape-up-building
description: Run a Shape Up build cycle: hand over the project, get one piece done, map scopes, track uphill/downhill on hill charts, scope-hammer, and decide when to stop.
---

# Shape Up — Building (Part 3 of Basecamp's Shape Up)

Use when a team (or the user solo) is executing a bet: kicking off, breaking down work, reporting status, deciding what to cut, or deciding whether something is done. Source: basecamp.com/shapeup, chapters 10–14.

## Hand over responsibility
- **Assign projects, not tasks.** Splitting a pitch into tasks up front "puts it through a paper shredder". The team gets the whole pitch and defines its own tasks within its boundaries.
- **Done means deployed** by the end of the cycle, including QA. Small batch projects deploy as each finishes. Thin-tailed extras (help docs, marketing, announcements) can happen in cool-down.
- **Kick-off**: set up a project space with only the team, post the pitch (or a restatement) with sketches, hold a call for questions.
- **Getting oriented**: the first few days look quiet — people are learning the system and finding where to start. Don't demand status; if silence lasts past ~3 days, check in.
- **Imagined vs discovered tasks**: the real work, and most of the hard parts, are discovered by doing. Expect the task list to grow.

## Get one piece done
- Don't build horizontally (all design, then all code) — lots done, nothing *really* done.
- Build one **vertical slice** end to end in a few days: real UI wired to real code, clickable.
- **Affordances before pixels**: unstyled HTML with the right buttons/fields is enough for programming to start; visual polish comes later.
- **Programmers don't wait for design**: the pitch is enough to start modelling; scaffold with stubs, mock data, hard-coded auth if needed.
- Design and code take turns on the same piece, without formal handoffs.
- Pick the first piece by: **Core** (central to the concept), **Small** (done in a few days), **Novel** (removes the most uncertainty).

## Map the scopes
- Organise by **structure, not by person** — not "design" and "programming" lists.
- **Scopes** = integrated slices that can be built, integrated and finished independently in a few days or less. Bigger than tasks, smaller than the project; their names become the project's language.
- Scopes are **discovered, not planned** — usually settling by end of week 1 / start of week 2. Expect reshuffling.
- **Good scopes**: you can see the whole project with nothing worrying hidden; conversations flow; new tasks have an obvious home.
- **Redraw when**: a scope holds unrelated tasks (hard to say how done it is); it has a grab-bag name ("front-end", "bugs") — a junk drawer that's never finished; it's too big to finish soon.
- **Patterns**:
  - **Layer cake** — thin UI + thin back end; size it by UI surface area; keep design and code tasks together.
  - **Iceberg** — far more back end than UI (or the reverse). Question whether the complexity is necessary; factor the UI out and split the big side into separate concerns that can finish in stages.
  - **Chowder** — a small list of loose tasks that fit nowhere. Over 3–5 items, a scope is hiding in it.
- Mark **nice-to-haves with `~`** at the start of the task (or scope). That's the machete for cutting later.

## Show progress: hill charts
See the `hill-chart` skill for the live page, snapshots and report.
- Task counts lie (tasks get discovered); estimates hide uncertainty ("4 hours" known vs unknown).
- Every scope has an **uphill** phase (figuring out the approach — unknowns) and a **downhill** phase (execution — all unknowns solved). The top of the hill is "I know exactly what to do".
- Plot each scope as a dot; the team updates positions themselves; compare snapshots over time to see what's **moving** vs **stuck** — status without asking.
- **Nobody says "I don't know"** — a dot that doesn't move raises the hand for them. Ask "what can we solve to get this over the hill?", not "are you stuck?". Make it about the work, not the person.
- A stuck dot may be a **badly drawn scope**: split it (e.g. "Notify" → email template, delivery back end, in-app display) so parts move independently.
- **Build your way uphill**: first third = "I've thought about it", second = "I've validated the approach", top = "I've built enough that no unknowns remain". Theory-only progress slides back.
- **Solve in the right sequence**: push the scariest, most novel scopes uphill first; leave routine work for the end. Like an inverted pyramid — by the deadline, important things should be downhill and only routine items and nice-to-haves left to trim.

## Decide when to stop
- **Compare down to the baseline**, not up to the ideal: what do customers do today without this? "This is a big improvement over the workaround" beats "it's never good enough". Aim pride at the right target.
- **Limits motivate trade-offs**: when someone adds something or finds an edge case, first ask "is there time for this?"
- **Scope grows like grass** — not anyone's fault; projects are opaque until you're in them. Give the team the authority and responsibility to keep cutting.
- **Cutting scope isn't lowering quality**: stay picky about code, design, copy and performance; be selective about *what* to build. Choosing core over peripheral differentiates the product.
- **Scope hammering** questions:
  - Is this a must-have? Could we ship without it? What happens if we don't do it?
  - Is this a new problem, or one customers already live with?
  - How likely is this case? When it happens, which customers see it — core or edge?
  - What's the actual impact? How aligned is this with the intended audience?
  Marking an item `~` nice-to-have *is* the hammering. Must-haves gate a scope being done; nice-to-haves are done only with spare time and usually never get built.
- **QA is for the edges**: designers/programmers own baseline quality and write their own tests. QA arrives late to hunt edge cases; its findings are nice-to-haves by default (keep them on a separate list; move to a scope only if promoted to must-have). QA and code review are level-ups, not gates.
- **Extending a project** — rare, at most a couple of weeks, and only if *both*: (1) every remaining item is a true must-have that survived hammering, and (2) all remaining work is **downhill**. Any uphill work means a shaping hole — cancel and reshape instead. Prefer using cool-down slack. Routine extensions signal shaping or team problems.

## How to help the user
- **Kick-off**: restate the pitch for the team; suggest the first core/small/novel slice.
- **Breakdown**: turn a list of discovered tasks into named scopes; flag grab-bags, oversize scopes, icebergs, and long chowder; mark `~` items.
- **Status**: use the `hill-chart` skill; highlight anything stuck since last update with a concrete "what unknown is blocking this?" question.
- **Cutting**: run the scope-hammering questions over the remaining work and return a must-have vs `~` list.
- **Deadline calls**: apply the baseline comparison and extension criteria; default to ship-what's-done or cancel-and-reshape.
- If the team uses Linear, see the `shape-up-linear` skill.
