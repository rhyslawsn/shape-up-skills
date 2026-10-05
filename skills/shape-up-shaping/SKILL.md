---
name: shape-up-shaping
description: Shape a raw feature idea into a bounded, de-risked Shape Up pitch: set appetite, narrow the problem, breadboard, find rabbit holes, write the pitch.
---

# Shape Up — Shaping (Part 1 of Basecamp's Shape Up)

Use when the user has a raw idea, feature request, customer complaint, or vague project ("redesign X", "add a calendar") and wants it turned into work a team can bet on. Output is a **pitch**. Source: basecamp.com/shapeup, chapters 2–6.

## What shaped work is
Shaped work sits at the right **level of abstraction**:
- **Not wireframes** — too concrete. They remove designer latitude, bias the team (especially when they come from someone senior), and hide complexity that blows estimates.
- **Not words alone** — too abstract ("build a calendar view"). The team can't make trade-offs; the project grows without bounds.

Good shaped work has three properties:
1. **Rough** — visibly unfinished, so builders know where their judgement goes.
2. **Solved** — the main elements and how they connect are worked out at the macro level; foreseeable rabbit holes are already patched.
3. **Bounded** — it has a fixed appetite and says explicitly what *not* to do.

Shaping is private, closed-door design work by one or two people (design sense + technical literacy + strategic judgement). It runs on a separate track from building and is never scheduled; ideas can be shelved without disappointing anyone. Nothing here is a commitment — there is no conveyor belt.

## The four steps

### 1. Set boundaries
- **Raw ideas get a soft no:** "Interesting. Maybe some day." Don't add them to a backlog or signal commitment.
- **Set the appetite** — how much time this is *worth*, not how long it will take. "Estimates start with a design and end with a number. Appetites start with a number and end with a design."
  - **Small batch:** 1–2 weeks for one designer + 1–2 programmers.
  - **Big batch:** a full 6-week cycle for the same team.
  - If it seems bigger than 6 weeks, **narrow the problem**, don't grow the appetite.
- **Fixed time, variable scope.** The appetite is a creative constraint; "good" is relative to it. There's always a better solution — the question is what the best one looks like *for this appetite*.
- **Narrow the problem.** Ask "what's really going wrong?" not "what could we build?". Find the specific story behind the request (the "calendar" request was really "I can't see free slots when working remotely").
- **Reject grab-bags** ("Files 2.0", "redesign the Files section"). Reframe to a specific pain ("sharing multiple files takes too many steps") or split into separately appetited projects.
- Exit criteria: **raw idea + appetite + narrow problem definition**.

### 2. Find the elements
Move fast, alone or with one trusted partner. Answer: where does this fit in the current system? How do people get to it? What are the key components and interactions? Where does it lead?

- **Breadboarding** (for flows): words, not pictures. See the `breadboard` skill.
  - **Places** — screens, dialogs, menus (write the name, underline it).
  - **Affordances** — buttons, fields, copy the user can act on (listed under the place).
  - **Connection lines** — arrows from affordances to the places they lead to.
  Focus on topology, not layout. Writing out flows surfaces questions you hadn't considered.
- **Fat marker sketches** (when 2D arrangement is the core problem): broad strokes that make detail impossible. See the `fat-marker-sketch` skill. Survey the field before committing to any layout.
- Output: a short list of **elements** — narrow, specific, concrete but non-prescriptive (e.g. "2-up month grid; dots not spanning pills; agenda list below, tap a day to scroll").

### 3. Risks and rabbit holes
Goal: turn a fat-tailed project (could take 3x) into a thin-tailed one. A single 2-week surprise eats a third of a 6-week bet. See the `shape-up-risk-scan` skill to check against a real codebase.
- **Walk the use case in slow motion**, step by step, looking for gaps.
- Ask: Does this need technical work we've never done? Are we assuming parts fit together in ways we haven't validated? Is there a design problem we haven't actually solved? Are we deferring a hard decision to the team?
- **Patch holes** with a decision now (e.g. completed to-dos stay where they are with "(Group name)" appended, rather than redesigning completed-item grouping). Make these trade-offs during shaping — they're much harder inside a cycle.
- **Declare out of bounds** — name use cases you won't support.
- **Cut back** — drop non-essential flourishes (or mark them as optional nice-to-haves).
- **Present to technical experts**, framed as "just an idea I'm shaping, not coming down the pipe". Ask "**Is X possible in 6 weeks?**", not "is X possible?". Rebuild it on a whiteboard from scratch, keep the clay wet, hunt for time bombs, invite simplifications.
- If no viable approach emerges, **don't pitch it** — keep shaping or drop it.

### 4. Write the pitch
Always present problem and solution together. Five ingredients:
1. **Problem** — ideally one specific story showing why the status quo fails. It's the baseline for judging the solution.
2. **Appetite** — part of the problem definition; stops debates about theoretically better but unaffordable solutions.
3. **Solution** — the elements, made concrete enough for people who weren't in the room: annotated breadboards, fat marker sketches redrawn legibly (labels in a different colour, numbered callouts), or affordances sketched onto a screenshot of the existing UI, with a note that designers have latitude.
4. **Rabbit holes** — specific details/decisions called out to keep the team out of trouble.
5. **No-gos** — functionality explicitly excluded to fit the appetite.

Pitches are posted for **asynchronous** review before the betting table. Comments can poke holes; they don't decide the bet.

## How to run this with the user
1. Ask for the raw idea and who it's for. Push back on grab-bags and on starting from a solution.
2. Dig for the specific story/pain and current workaround (baseline). Propose an appetite (small vs big batch) and confirm.
3. Draft breadboards in text and/or describe fat-marker layouts. Offer 2–3 alternative element sets when trade-offs exist.
4. Run a slow-motion walkthrough, list holes, and propose patches, out-of-bounds cases and cuts. Suggest specific questions to take to a technical expert.
5. Write the pitch using the template below. Keep it rough and bounded — never produce pixel-level specs.

### Pitch template
```
# <Pitch title>
## Problem
<One concrete story. Current workaround / baseline.>
## Appetite
<Small batch: N weeks | Big batch: 6 weeks> — why it's worth this much and no more.
## Solution
<Elements, breadboards, sketch descriptions. Note where designers have latitude.>
## Rabbit holes
- <Risk> → <decision that patches it>
## No-gos
- <Explicitly excluded>
```

## Anti-patterns to flag
- Estimating instead of setting appetite.
- Hi-fi mockups or task lists in a pitch.
- "Problem" sections that restate the solution.
- Unresolved technical unknowns handed to the team.
- No no-gos section (unbounded work grows).
