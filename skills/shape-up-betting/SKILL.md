---
name: shape-up-betting
description: Plan Shape Up cycles: run a betting table, choose pitches, protect six-week cycles and cool-down, apply the circuit breaker, handle bugs and feedback without backlogs.
---

# Shape Up — Betting & Cycle Planning (Part 2, plus Ch. 15 and appendices)

Use when the user is deciding what to work on next cycle, evaluating pitches, setting up cadences, handling incoming requests/bugs/post-launch feedback, or adopting Shape Up in a team. Source: basecamp.com/shapeup, chapters 7–9, 15, appendices.

## Bets, not backlogs
- Don't keep a central backlog. It becomes a weight of items nobody will do, demands grooming, and makes the team feel perpetually behind.
- Before each cycle, the **betting table** considers only pitches shaped in the last cycle (or deliberately revived). Unchosen pitches are let go — no tracking obligation.
- Lists are **decentralised**: support tracks top requests, product tracks ideas to shape, engineering tracks bugs they want to fix. They feed conversations, not the betting table directly.
- "Really important ideas come back." A one-off mention may not be a real problem; recurring complaints are a signal to shape and pitch. Anyone who cares about a passed-over pitch can re-lobby next cycle.

## Cadence
- **Six-week cycles**: long enough to finish something meaningful, short enough to feel the deadline from day one (the **time horizon**). Two-week sprints are too short and too planning-heavy.
- **Two-week cool-down** between cycles: no scheduled work. Bug fixes, exploration, self-directed work, and the betting table.
- **Team shapes**: 1 designer + 1–2 programmers; QA joins near the end. **Big batch** = one project for the whole cycle. **Small batch** = several 1–2 week projects that one team juggles and ships by cycle end.

## The betting table
- Small group of senior decision-makers (e.g. CEO/product authority, CTO, senior programmer, product strategist). 1–2 hours during cool-down. Pitches read in advance.
- Decisions are final — no "step two" approval layer. Output: which pitches, which teams, small vs big batch.
- **Questions to ask of each pitch**:
  1. **Does the problem matter?** Separate problem from solution. If the solution is complex, can a narrower one get 80% of the benefit for 20% of the change?
  2. **Is the appetite right?** If someone says no to the time, probe: "How would you feel if it were two weeks?" — the real objection may be technical or about the solution. Options: strengthen the problem case, reshape smaller, or let it go.
  3. **Is the solution attractive?** E.g. does it spend scarce screen real estate too cheaply? Small tweaks are fine; if it turns into a design session, stop — "we're not doing design here."
  4. **Is this the right time?** Recent cycles' themes, time since last big release, need for stabilisation, morale from repeated work in one area.
  5. **Are the right people available?** Skills needed (front-end, a strong scope hammer), rotation between big/small batch, vacations ("calendar Tetris").
- Afterwards, post a **kick-off message**: the bets, who's on each team, and context on the cycle.

## What a bet means
- **Payout** — shaped to deliver a meaningful, finished result in the cycle, not to fill time.
- **Commitment** — the team gets the whole cycle **uninterrupted**. "Losing the wrong hour can kill a day; losing a day can kill a week." New requests wait until the next betting table (at most ~6 weeks). Only true crises break this.
- **Capped downside** — the **circuit breaker**: projects that don't ship by the end of the cycle are **cancelled by default, not extended**. This prevents runaway projects, forces reshaping of what went wrong (it becomes a new pitch), and gives teams ownership of scope trade-offs.
- **Keep the slate clean** — bet only one cycle ahead; never carry leftover work over without reshaping and rebetting it. Keep any long-term roadmap informal. For multi-cycle efforts, shape what the *end of this cycle* looks like and keep the option to change course.

## Bugs
- Bugs aren't automatically more important than other work. Crises (data loss, app grinding to a halt, wrong data shown to many customers) are rare — drop everything only for those.
- Otherwise: (1) fix in cool-down, (2) shape big ones into a pitch and bet on them, (3) hold an annual **bug smash** cycle (e.g. over holidays).

## Product phase determines how you bet
- **Existing product**: shape → bet → build → ship within the cycle.
- **New product, R&D mode**: bet *time* to spike core pieces; fuzzy shaping; senior people do the work; expect to ship nothing — goal is the load-bearing architecture. Still one cycle at a time.
- **Production mode**: architecture settled; normal shaping; multiple teams; "shipped" = merged to main and not expected to be touched, though it can still be cut before launch.
- **Cleanup mode**: no shaping; leadership directs; no team boundaries; ship in small bites; max two cycles; make final cuts (smaller surface area = less support/maintenance). Guard against cold feet masquerading as must-haves.
- Risky experiments on an existing product can be bet like production-mode work (internal-only first version, rebet if promising).

## Move on (after shipping)
- Let post-launch feedback settle for a few days. Remember who the change was for; workflow changes draw disproportionate noise.
- Don't promise changes in response — commitments are debt that kills the clean slate. Treat feedback as **raw ideas**: they go back to step 1 of shaping and compete at the next betting table.

## Adjusting to size & adopting
- **2–3 people**: drop formal cycles, cool-down, pitches and betting tables. Keep the truths: set an appetite, shape the next thing, build it, repeat; vary lengths as needed.
- **Larger orgs**: formal cycles, a dedicated shaping track separate from builders, a betting table, and supporting teams (ops/support) so product teams stay uninterrupted. Fluidity becomes a liability as you grow.
- **Getting started** (pick one): (A) one 6-week experiment — shape one comfortably-sized project, dedicate 1 designer + 2 programmers, guarantee no interruptions, let them discover their own tasks, integrate early, skip scope mapping/hill charts at first; (B) start with shaping only, within the existing process; (C) start with 6-week cycles to reduce planning overhead. **Fix shipping first**, before improving discovery. Judge by the end result ("will we feel good about what we shipped?"), not by hour utilisation.

## How to help the user
- When given pitches: evaluate each against the five questions; recommend bets, team assignment, and what to pass on, and draft the kick-off message.
- When given a backlog: recommend letting it go — extract recurring themes worth shaping and route the rest to owners' own lists.
- When asked to extend an over-running project: apply the circuit breaker (see the `shape-up-building` skill's extension criteria) and recommend reshaping instead.
- When an urgent request lands mid-cycle: test it against the crisis definition; default answer is "next betting table".
- If the team uses Linear, see the `shape-up-linear` skill for how to record all of this there.
