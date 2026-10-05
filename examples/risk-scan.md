# Risk scan: Drafts that follow you across devices

**Appetite:** Small batch: 2 weeks  ·  **Repo:** basecamp/once-campfire @ 254dd1d  ·  **Verdict:** Fits the appetite if the patches below are adopted

Most of this already exists: the composer saves a per-room draft in localStorage today. The real new work is moving drafts server-side for cross-device and adding a marker in the sidebar. Both have traps around caching and rich text.

## Rabbit holes and unknowns (for the pitch)

- **Problem may already be solved for most people** (rabbit-hole). Same-device drafts already persist across room switches, with a system test. Only cross-device is missing; check that's the real complaint before spending 2 weeks.
  - Decide now: Narrow the pitch to cross-device drafts plus the sidebar marker; drop 'save drafts' from the problem statement.
  - Evidence: app/javascript/controllers/composer_controller.js:22-27, test/system/composer_test.rb:32
- **Saving drafts on the membership busts sidebar caches** (rabbit-hole). Direct-room rows are fragment-cached on the membership (`cache membership`). Writing a draft column on every pause touches updated_at and re-renders rows constantly.
  - Decide now: Store drafts in their own table (user_id, room_id, body) and write with update_columns/no touch; render the marker from that table, not the cached row.
  - Evidence: app/views/users/sidebars/rooms/_direct.html.erb:1, db/schema.rb:82
- **Rich text drafts with attachments and mentions** (unknown). The composer is a rich text editor (lexxy). Today's draft stores the editor value; attachments and mention tokens may not round-trip through a server-side save.
  - Declare a no-go: Drafts keep text and mentions only; attachments are not kept in drafts.
  - Evidence: app/javascript/controllers/composer_controller.js:26, app/views/rooms/show/_composer.html.erb:28
- **Two devices editing the same draft at once** (unknown). With the room open on two devices, both save. Live-syncing drafts over ActionCable would be a project of its own.
  - Declare a no-go: No live sync. Last save wins; a draft loads when you open the room.
  - Evidence: absent: no draft channel; searched 'draft' in app/channels

## Suggested no-gos

- Drafts keep text and mentions only; attachments are not kept in drafts.
- No live sync. Last save wins; a draft loads when you open the room.

## Questions for a technical expert

- Is moving drafts to a server-side table with debounced saves possible in 2 weeks without touching membership caching?
- Does the lexxy editor value round-trip mentions safely if we store it server-side?

## Where each element lands

| Element | Status | Where | Precedent |
|---|---|---|---|
| Draft saved per room as you type | existing | app/javascript/controllers/composer_controller.js:22, test/system/composer_test.rb:32 | localStorage key composer-draft-<roomId> |
| Draft available on another device | new | db/schema.rb:82 (memberships) | none: drafts are browser-only today |
| Draft marker in the rooms sidebar | extend | app/views/users/sidebars/show.html.erb:23, app/javascript/controllers/rooms_list_controller.js | unread dot (memberships.unread_at, badge_dot_controller.js) |
| Sending clears the draft | existing | app/javascript/controllers/composer_controller.js:184 | already clears localStorage on submit |

## Known work (thin-tailed, no action needed)

- Sidebar marker next to the unread dot: Same pattern as the unread indicator, which already has a model scope, controller and JS.

## Not checked

- Native/PWA clients beyond the web composer
- Data retention or privacy expectations for stored drafts

<!-- shapeup-data: {"pitch": "Drafts that follow you across devices", "appetite": "Small batch: 2 weeks", "repo": {"name": "basecamp/once-campfire", "commit": "254dd1d"}, "summary": "Most of this already exists: the composer saves a per-room draft in localStorage today. The real new work is moving drafts server-side for cross-device and adding a marker in the sidebar. Both have traps around caching and rich text.", "elements": [{"element": "Draft saved per room as you type", "status": "existing", "where": ["app/javascript/controllers/composer_controller.js:22", "test/system/composer_test.rb:32"], "precedent": "localStorage key composer-draft-<roomId\u003e"}, {"element": "Draft available on another device", "status": "new", "where": ["db/schema.rb:82 (memberships)"], "precedent": "none: drafts are browser-only today"}, {"element": "Draft marker in the rooms sidebar", "status": "extend", "where": ["app/views/users/sidebars/show.html.erb:23", "app/javascript/controllers/rooms_list_controller.js"], "precedent": "unread dot (memberships.unread_at, badge_dot_controller.js)"}, {"element": "Sending clears the draft", "status": "existing", "where": ["app/javascript/controllers/composer_controller.js:184"], "precedent": "already clears localStorage on submit"}], "risks": [{"id": "R1", "title": "Problem may already be solved for most people", "severity": "rabbit-hole", "why": "Same-device drafts already persist across room switches, with a system test. Only cross-device is missing; check that's the real complaint before spending 2 weeks.", "evidence": ["app/javascript/controllers/composer_controller.js:22-27", "test/system/composer_test.rb:32"], "patch": {"type": "decide", "text": "Narrow the pitch to cross-device drafts plus the sidebar marker; drop 'save drafts' from the problem statement."}}, {"id": "R2", "title": "Saving drafts on the membership busts sidebar caches", "severity": "rabbit-hole", "why": "Direct-room rows are fragment-cached on the membership (`cache membership`). Writing a draft column on every pause touches updated_at and re-renders rows constantly.", "evidence": ["app/views/users/sidebars/rooms/_direct.html.erb:1", "db/schema.rb:82"], "patch": {"type": "decide", "text": "Store drafts in their own table (user_id, room_id, body) and write with update_columns/no touch; render the marker from that table, not the cached row."}}, {"id": "R3", "title": "Rich text drafts with attachments and mentions", "severity": "unknown", "why": "The composer is a rich text editor (lexxy). Today's draft stores the editor value; attachments and mention tokens may not round-trip through a server-side save.", "evidence": ["app/javascript/controllers/composer_controller.js:26", "app/views/rooms/show/_composer.html.erb:28"], "patch": {"type": "no-go", "text": "Drafts keep text and mentions only; attachments are not kept in drafts."}}, {"id": "R4", "title": "Two devices editing the same draft at once", "severity": "unknown", "why": "With the room open on two devices, both save. Live-syncing drafts over ActionCable would be a project of its own.", "evidence": ["absent: no draft channel; searched 'draft' in app/channels"], "patch": {"type": "no-go", "text": "No live sync. Last save wins; a draft loads when you open the room."}}, {"id": "R5", "title": "Sidebar marker next to the unread dot", "severity": "known", "why": "Same pattern as the unread indicator, which already has a model scope, controller and JS.", "evidence": ["app/models/membership.rb:15", "app/javascript/controllers/badge_dot_controller.js"], "patch": {"type": "accept", "text": "Follow the unread pattern."}}], "expert_questions": ["Is moving drafts to a server-side table with debounced saves possible in 2 weeks without touching membership caching?", "Does the lexxy editor value round-trip mentions safely if we store it server-side?"], "not_checked": ["Native/PWA clients beyond the web composer", "Data retention or privacy expectations for stored drafts"], "verdict": "fits-with-patches"} -->
