---
name: "shape-up-linear"
description: "Run Shape Up in Linear: pitches as projects, betting-table docs on cycles, scopes as milestones, ~nice-to-haves, hill-chart project updates, and the circuit breaker at cycle end."
---

# Shape Up in Linear

Maps the Shape Up method (`shape-up-shaping`, `shape-up-betting`, `shape-up-building`, `hill-chart`) onto Linear through the Linear connector. Use it whenever the user wants Shape Up work set up, tracked, reviewed or closed out in Linear: "set up Linear for Shape Up", "put this pitch in Linear", "run the betting table", "kick off the cycle", "post the weekly update", "what's the state of the cycle", "close out the cycle".

## The mapping

| Shape Up | Linear | Notes |
|---|---|---|
| Cycle (6 weeks) + cool-down (2 weeks) | Team **cycle**, 6 weeks, with a 2-week **cooldown** | Set once in Team settings > Cycles (UI only). Issues can't be assigned to a cooldown, which matches the book. |
| Pitch | **Project**, status **Backlog**, project label **Pitch** | Description = the pitch's five ingredients. Summary = the problem in one line. |
| Raw idea | Nothing, or a line in its owner's own list | Don't create projects or issues for raw ideas. |
| Betting table | **Document attached to the upcoming cycle**: "Betting table: Cycle N" | Records pitches considered, bets, teams, and why others were passed. |
| Bet (big batch) | Pitch project → status **Planned**, label **Big batch**, start = cycle start, target = cycle end, lead set | One project per bet. |
| Bet (small batch) | One project per 1–2 week item, label **Small batch**, own target date inside the cycle | Each ships on its own. |
| Pitch not bet | Project → **Canceled**, comment "Not bet in Cycle N" | No backlog. If it comes back, reshape and re-pitch (reopen to Backlog with the new pitch). |
| Kick-off | Cycle doc section + first **project update** ("Kick-off", On track) | Project description already holds the pitch. |
| Assign projects, not tasks | The team creates the issues | Claude never breaks a pitch into issues up front. |
| Scope | **Project milestone** (no target date needed) | Milestone progress % shows per scope. Create milestones when the team names scopes, usually end of week 1. Ignore Linear's yellow "current milestone" highlight. |
| Discovered task | Issue in the project, in the cycle, on its scope's milestone | |
| Chowder | Project issues with **no milestone** | More than 3–5 means a scope is hiding. |
| Nice-to-have | Title starts with **`~ `** and issue label **Nice-to-have** | Everything else in a scope is a must-have. Scope done = all must-haves done. |
| QA finding | Issue labels **QA** + **Nice-to-have**, no milestone | Promote to must-have: remove Nice-to-have and `~`, move onto the scope's milestone. |
| Hill chart | `hill-chart` live page, linked in the project's **links** | Positions are judgement calls; never infer them from milestone % (task counts mislead). |
| Status without asking | Weekly **project update**, health from the hill report | See mapping below. |
| Circuit breaker | Unshipped at cycle end → project **Canceled**, open issues **Canceled** | Required: Linear otherwise rolls unfinished issues into the next cycle. |
| Multi-cycle effort | **Initiative** grouping one project per cycle | Bet one cycle at a time; each cycle's project has its own shaped end state. |
| Bugs | Team issues outside projects; fixed in cool-down | Crises only interrupt a cycle. Big bugs get pitched. Optional annual **Bug smash** cycle with no projects. |
| R&D / cleanup mode | Project label **R&D** (expect no ship); cleanup cycles use plain issues, no projects | |

## Ground rules
- **Look before writing.** Start every session with `list_teams`, `list_cycles` (teamId, type "current"/"next"), `list_project_labels` and `list_issue_labels`. Use the user's names for teams, statuses and labels where they already exist.
- **Ask before anything destructive or bulk.** Canceling projects or issues, changing many issues, or creating labels: list what will change and get a yes first.
- **Never invent work.** Only create pitches, scopes or issues the user or team actually named.
- **Respect the team's autonomy.** Claude may create milestones (scopes) and issues the team dictates, but doesn't assign tasks or set estimates. Shape Up has no estimates; leave `estimate` empty.
- **Small teams (2–3 people).** Cycles, cool-downs and betting-table docs are optional; keep pitches as projects, scopes as milestones and `~` nice-to-haves. Ask which parts they want.

## One-time setup
1. Check cycles: if `list_cycles` returns nothing, cycles are off. Tell the user to turn them on in **Team settings > Cycles**: each cycle lasts **6 weeks**, **2-week cooldown**, their start day. Recommend leaving "auto-add active issues" on only if they understand started issues will land in the cycle automatically. This can't be done through the connector.
2. Suggest (don't force) **auto-close** in Team settings > Workflows & automations, so stale backlog issues close themselves, the closest Linear gets to "let ideas go".
3. Create missing labels after confirming:
   - Project labels (`save_project_label`): **Pitch**, **Big batch**, **Small batch**, **R&D**.
   - Issue labels (`save_issue_label`): **Nice-to-have**, **QA**.
4. Optionally create a team document "How we Shape Up" (`save_document` with `team`) summarising the mapping table above for the team.

## Flows

### Put a pitch in Linear
After shaping (`shape-up-shaping`), create the project:
```
save_project  name: "<Pitch title>"  addTeams: ["<team>"]  state: "backlog"  labels: ["Pitch"]
              summary: "<the problem, one line>"
              description: <pitch markdown, template below>
              links: [{url: <breadboard/sketch/hill page or doc>, title: "..."}]   # optional
```
Pitch description template:
```
## Problem
<one concrete story; the current workaround (baseline)>

## Appetite
<Small batch: N weeks | Big batch: 6 weeks>, and why it's worth this much and no more.

## Solution
<elements; breadboard in text notation; note where designers have latitude>

## Rabbit holes
- <risk> → <decision that patches it>

## No-gos
- <explicitly out>
```
Breadboards and fat-marker sketches: paste the breadboard notation into the description; for sketches, link the PNG wherever the user keeps files, or attach it to a kick-off issue later. Don't paste image data.

### Run the betting table
1. Gather candidates: `list_projects` with `label: "Pitch"` and `state: "backlog"`, plus only pitches shaped since the last table (check `createdAt`/`updatedAt`). Ignore anything older unless someone re-pitched it.
2. Help evaluate with the five questions from `shape-up-betting` (problem matters? appetite right? solution attractive? right time? right people?). Decisions are the user's.
3. Record it: `save_document` with `cycle: "<next cycle number>"`, `team: "<team>"`, title "Betting table: Cycle N". Sections: Bets (project, batch size, team), Passed (project, one-line reason), Notes.
4. Apply the bets (after a yes):
   - Each bet: `save_project id:<project> state:"planned" labels:["Big batch"] (or ["Small batch"]) startDate:<cycle start> targetDate:<cycle end, or the small-batch item's date> lead:<person>`.
   - Each pass: `save_project id:<project> state:"canceled"` and `save_comment projectId:<project> body:"Not bet in Cycle N. Re-pitch if it keeps coming back."`

### Kick off the cycle
- Append a "Kick-off" section to the cycle's betting-table document (`save_document id:<doc> patch:[{op:"append", ...}]`): each bet, who's on it, and remarks on the cycle.
- For each bet: `save_project id:<project> state:"started"`, then `save_status_update type:"project" project:<project> health:"onTrack" body:"Kick-off. Team: ... Pitch is in the project description. First few days are for getting oriented; expect quiet."`
- If using the live hill chart, set it up with `hill-chart` (scopes come later), then `save_project id:<project> links:[{url:<hill page>, title:"Hill chart"}]`.
- Don't create issues. The team discovers them.

### Map the scopes
When the team names scopes (typically end of week 1):
- `save_milestone project:<project> name:"<Scope name>" description:"<one line: what done looks like>"` per scope (no target dates).
- Move existing issues onto scopes: `save_issue id:<issue> milestone:"<Scope name>"`. Leave leftovers as chowder.
- Add the same scopes to the hill chart (`hill-chart`: add `scopes/<id>` docs, or `update()` in files mode).
- Check the scope map against `shape-up-building`: grab-bag names ("Frontend", "Bugs"), unrelated tasks in one milestone, or a milestone too big to finish in a few days all mean redraw. To redraw: create the new milestones, move issues, then rename or delete the old one (delete only after a yes).

### Nice-to-haves and scope hammering
- Mark: `save_issue id:<issue> title:"~ <title>" addLabels:["Nice-to-have"]`.
- Promote to must-have: `save_issue id:<issue> title:"<title without ~>" removeLabels:["Nice-to-have"] milestone:"<scope>"`.
- QA findings: `save_issue team:<team> project:<project> cycle:<current> title:"~ <finding>" labels:["QA","Nice-to-have"]` (no milestone until promoted).
- To run a hammering pass, `list_issues project:<project> state:"unstarted"` (and "started"), then go through the questions in `shape-up-building` with the user and mark the results.

### Weekly status (status without asking)
1. Read the hill chart (`hill-chart`: `from_db_dir` + `report`).
2. Read Linear for context: `list_issues project:<project> fields:["title","status","statusType","projectMilestone","labels"]` to see must-haves left per scope, nice-to-haves and chowder size.
3. Post `save_status_update type:"project" project:<project> health:<from table> body:<template>`.

Health from the hill report:
| Hill report says | Health |
|---|---|
| Any scope **uphill past the cycle midpoint**, or more than half the scopes unplaced after week 2 | **offTrack** |
| Any scope **stuck uphill**, **slid back**, or a **high-risk** scope not over the hill | **atRisk** |
| Otherwise | **onTrack** |

Update template:
```
**<summary line from the hill report>**  ·  [Hill chart](<link>)

Needs a conversation:
- <scope>: <the flag's question>

Scopes: <scope>: <phase>, <must-haves left> must-haves left · ...
Nice-to-haves: <n> open (cut first if time runs short). Chowder: <n> issues.
```
Lead with what needs attention; don't list every issue. If nothing is flagged, say so in one line.

### End of the cycle (circuit breaker)
For each bet, decide with the user:
- **Shipped** (all must-haves done and deployed): cancel open nice-to-haves (`save_issue id:<issue> state:"canceled"`), then `save_project id:<project> state:"completed"` and a final project update (onTrack, what shipped, what was cut).
- **Not shipped, default**: list what will change and get a yes, then cancel the project's open issues (`state:"canceled"`) so Linear doesn't roll them into the next cycle, `save_project state:"canceled"`, and post an offTrack update: what shipped, what didn't, and what the shaping missed. If the idea still matters it gets reshaped (`shape-up-shaping`) and competes at the next betting table as a new pitch.
- **Extension** (rare): only if every open issue is a true must-have that survived hammering **and** every scope is downhill on the hill chart. Then keep it In Progress, move `targetDate` at most 2 weeks into the cool-down, and post an atRisk update saying why. Any uphill work means cancel and reshape instead.

### Cool-down and bugs
- During cool-down, list candidate bug fixes with `list_issues team:<team> label:"Bug"` (or the team's bug label) not in a project. The team picks; Claude doesn't schedule them.
- A bug that's too big for cool-down: shape it and create a pitch project like any other.
- Only true crises (data loss, app down, wrong data shown to many customers) interrupt a cycle.

## Checks before finishing any flow
- [ ] Read the current state first (teams, cycles, labels, the project) and used existing names
- [ ] Confirmed with the user before canceling, bulk-editing, or creating labels
- [ ] No issues or estimates invented for the team
- [ ] Unshipped projects' open issues canceled so they don't roll over
- [ ] Project update health matches the hill report, and leads with what needs attention