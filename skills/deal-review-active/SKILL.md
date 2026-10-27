---
name: hubspot-deal-review
description: Conduct a structured pipeline review across a sales team's open HubSpot deals — reading notes, emails, and call logs end-to-end — then posting deal-by-deal summaries with manager notes and creating follow-up tasks. Use this skill whenever the user asks for a pipeline review, deal review, AE accountability check, weekly sales cadence, monthly QBR prep, hunting team review, or wants to audit email/call activity across deals or add notes and tasks across multiple deals in bulk. Trigger even if the user says "review my reps", "pipeline hygiene", "what are my open deals doing", "are reps calling customers", "check email activity on my deals", "I need to chase the team on stalled deals", "Q-close review", or any variant — this skill reads ALL engagement types (notes + emails + calls) and produces both an Excel report and HubSpot updates in one pass.
---

# HubSpot Deal Review

A reusable workflow for conducting structured pipeline reviews across a sales team. Output: an Excel workbook with compliance scoring + bulk HubSpot notes and tasks posted directly on every deal.

## When to use this skill

Trigger whenever the user wants to:
- Review pipeline across a team or a subset of AEs
- Check AE documentation discipline (which deals lack notes)
- Push the team on stalled deals via manager notes inside HubSpot
- Create follow-up tasks for themselves across many deals in one pass
- Prep for QBR, monthly close-out, Q1/Q2/Q3/Q4 review
- Audit a hunting team or farming team's open deals

If the user gives a smaller scope (e.g. "review just AE_27's deals" or "review only Negotiation stage"), apply the same workflow but filter accordingly.

## Inputs to confirm before starting

Before pulling data, confirm these with the user:

1. **AE scope** — which owners' deals to pull (names + HubSpot owner IDs if known)
2. **Stage scope** — which pipeline stages to include (default: Prospect, Need Analysis, Opportunity, Proposal, Negotiation — exclude closed-won, closed-lost)
3. **AE task due** — when the AE action task should be due (default: T+1 business day)
4. **Manager review task gap** — how many business days after the AE task for the manager review (default: T+4 business days, so manager task is T+5 from posting)
5. **Note style** — combined "ABHIMANYU NOTES" section (manager note + next action together) or separate sections
6. **Test first?** — run 1-2 test deals before bulk, or run all at once

If the user has run this before and the previous run is in context, reuse the same defaults and just confirm scope changes.

## Workflow

### Step 1: Verify identity
Call `HubSpot:get_user_details` first. The returned `userId` is the manager's owner ID — used for posting notes and (by default) for task ownership.

### Step 2: Pull all open deals
Use `HubSpot:search_crm_objects` to pull deals matching:
- Owner ID in the scoped AE list
- Dealstage in the scoped stages (NOT closed-won, NOT closed-lost — see `references/hubspot_reference.md` for stage IDs across Empuls/Compass/Plum/Loyalife pipelines)
- Properties to fetch: `dealname`, `dealstage`, `amount`, `deal_currency_code`, `hubspot_owner_id`, `closedate`, `createdate`, `hs_lastmodifieddate`, `pipeline`

Confirm the total count back to the user before proceeding. If unexpectedly high (>100) or low (<10), pause and validate scope.

### Step 3: Pull all engagement types per deal
For each deal, fetch **notes, emails, and calls** — all three. AE context lives across all of these surfaces, and reviewing notes alone misses 30-50% of the actual deal activity (especially for AEs who prefer emailing directly without logging notes).

Use `HubSpot:get_crm_objects` with `associations: ["notes", "emails", "calls"]`, then for each associated engagement ID, fetch the body via a follow-up call:

- **Notes** — `objectType: "notes"`, body in `hs_note_body` (HTML)
- **Emails** — `objectType: "emails"`, body in `hs_email_text` (preferred — plain text) or `hs_email_html`. Also pull `hs_email_subject`, `hs_email_direction` (INCOMING/FORWARDED_EMAIL/OUTGOING/etc.), `hs_email_status`, `hs_email_from_email`, `hs_email_to_email`, `hs_timestamp`
- **Calls** — `objectType: "calls"`, body in `hs_call_body` (call notes typed by rep), plus `hs_call_title`, `hs_call_duration` (milliseconds), `hs_call_direction`, `hs_call_disposition` (connected/no-answer/voicemail/etc.), `hs_timestamp`. If `hs_call_recording_url` is present, note it but don't try to fetch audio.

Classify content across all three sources into:
- **AE Deal Summary** — substantive context (ES, HRMS, decision-maker, commercials, timeline, requirement) from any source
- **Manager Notes** — questions/asks from the manager (owner ID matches the manager)
- **Email Trail** — count of inbound vs outbound emails, last contact date, any commitments made in writing
- **Call Activity** — number of connected calls, no-answers, voicemails, last call date, key call notes

This expanded view also surfaces hidden risks:
- Deals with 0 emails AND 0 calls in the last 30 days → genuinely cold
- Deals with many outbound emails and no inbound → ghosted, not active
- Deals where rep has not made a call in 60+ days → low effort signal
- Email chains that reveal commitments the rep hasn't logged elsewhere (e.g., "we'll send a PO by Friday")

### Step 4: Score AE summary compliance + activity health
For each deal, assign two ratings:

**AE Summary status** (documentation discipline):
- `Yes` — complete summary across notes/emails/calls with ES, current setup, requirement, decision-maker, commercials, timeline
- `Partial` — some context but key fields missing
- `No` — zero usable AE context across any engagement type

**Activity status** (engagement health, last 30 days):
- `Active` — at least one connected call OR meaningful inbound email in last 30 days
- `One-way` — outbound emails or attempted calls but no customer response
- `Silent` — no engagement activity from either side in last 30 days
- `Dead` — no activity in last 60+ days

The combination matters. A deal marked `No` AE summary + `Silent` activity is the highest-risk category — invisible AND inactive. A deal marked `Yes` + `Active` is well-managed. Surface counts per AE across both axes for coaching.

### Step 4b: Classify content signals
Discipline + activity tell you *whether* the deal is healthy. Content signals tell you *what* the right action is. Before writing the next action, scan the engagement bodies for three classes of signal — these directly determine which pattern in `next_action_patterns.md` applies.

Read these supporting skills the first time you run this step (they sit at the project root, not under `references/`):

- **`buying-signal-amplification.md`** — read at Step 4b. Catches signals like "what's the pricing", "how quickly can we implement", "when we go live", "let me run this by my team", future-tense ownership language, urgency phrases. Any of these in a recent email/call → route to the `Strong buying intent, ready to close` pattern, not a generic follow-up.
- **`objection-recognition.md`** — read at Step 4b. Classifies pushbacks into Price / Timing / Need / Trust / Authority. Surface the specific objection in the note so the next action addresses *that* objection (e.g., "send competitive battlecard" for a Trust objection, not "schedule another call").
- **`decision-maker-identification.md`** — read at Step 4b whenever the POC's title looks junior (Manager / Deputy / Analyst / Coordinator) or emails show approvals being deferred upward. Triggers the `authority issue` pattern: escalate to senior title or demote stage.

Record per deal: `objections_detected` (list), `buying_signals_detected` (list), `authority_concern` (yes/no). These feed Step 5 directly.

### Step 5: Write the recommended next action
For every deal, write a 1-2 sentence concrete next action. Read `references/next_action_patterns.md` for guidance on framing by scenario (large deal missing context, dead POC, stalled commercial, ready-to-close, etc.).

**Pattern selection logic** — combine Step 4 (discipline + activity) with Step 4b (content signals) to pick the pattern:

| Inputs | Pattern to use |
|---|---|
| Buying signal detected + Active | Strong buying intent, ready to close |
| Objection detected (any type) | Address the specific objection — frame next action around the objection class |
| Authority concern flagged | Authority issue / escalate to senior title |
| Silent or Dead + no signals | Read `conversation-resurrection.md` for re-engagement framing, then long-silence pattern |
| `No` AE summary + large deal | URGENT summary required (largest-deal pattern) |
| Missed close date + no activity | Missed close date pattern |
| All others | Pick best fit from `next_action_patterns.md` |

Additional read at this step:

- **`conversation-resurrection.md`** — read at Step 5 for any deal flagged `Silent` or `Dead`. Gives richer framing than the one-line "long silence" pattern — context-aware re-engagement angles (value refresh, trigger event, new POC) that make the action specific instead of "ping them again".

Be specific and execution-oriented — name the person, the deliverable, the timeline. Vague "follow up" actions are not acceptable.

### Step 6: Build the Excel workbook
Read `/mnt/skills/public/xlsx/SKILL.md` first, then build a 5-sheet workbook:

1. **Summary** — AE compliance scorecard + activity scorecard + pipeline value by owner + critical attention list
2. **Deals** — all deals with: ID, Name, Owner, Stage, Product, Currency, Amount (native + INR), Created, Close, Last Activity, Days Idle, **Total Emails (in/out)**, **Total Calls (connected/attempted)**, **Last Email Date**, **Last Call Date**, Abhimanyu's Notes, AE Summary, AE Status (color-coded green/amber/red), **Activity Status (color-coded)**, Next Action, HubSpot link
3. **Missing AE Summary** — filtered action list sorted by status then value
4. **Silent / Dead deals** — filtered list of deals with no activity 30+ days, sorted by stage priority then value
5. **Stage View** — AE × stage matrix

Color coding:
- Stage: Negotiation green, Proposal amber, Opportunity light red, Need Analysis light blue, Prospect grey
- AE Status: Yes green (`C6EFCE`), Partial amber (`FFEB9C`), No red (`FFC7CE`)
- Activity Status: Active green, One-way amber, Silent light red, Dead dark red

INR conversion rates for reporting: USD≈90, AED≈25, SGD≈68 (confirm current rates if running outside India).

### Step 7: Show workbook + confirm before bulk posting
Present the workbook to the user. Confirm:
- The note template wording
- Task due date
- Task ownership
- Whether to test 1-2 deals first

**Always test 1-2 deals first** unless the user explicitly says "run all immediately." The test reveals formatting issues (mentions not tagging, layout bugs) before posting 170+ records.

### Step 8: Post notes and tasks in batches

For every deal, create **three records**:

1. **Note** — combined deal summary + manager notes + next action, tagged to the AE, cc'd to the manager
2. **AE action task** — for the AE to execute, due T+1 (next business day from posting)
3. **Manager review task** — for the manager to verify the AE acted, due T+4 (four business days after the AE task)

The two-task setup creates accountability: the AE has the action, the manager has a built-in review checkpoint to catch deals where the AE didn't follow through.

**Date math** — calculate due dates as business days from posting date (skip weekends):
- AE task due = posting date + 1 business day
- Manager task due = AE task due + 4 business days

Example: if posting on a Wednesday, AE task due Thursday, manager task due following Wednesday.

**Task details**:

| Field | AE task | Manager task |
|---|---|---|
| `hs_task_subject` | `Action required: <Deal Name>` | `Review: <Deal Name> — verify AE action` |
| `hs_task_body` | The action text (same as in the note) | `AE was tasked to: <action text>. Confirm completed. If not, escalate or reassign.` |
| `hubspot_owner_id` | Deal owner (AE) ID | Manager ID |
| `hs_timestamp` | T+1 (business day) | T+5 (business day) |
| `hs_task_priority` | Per deal urgency | Same priority as AE task |

HubSpot `manage_crm_objects` is limited to **10 objects per batch**. With 3 records per deal, plan: 85 deals × 3 = 255 records = ~26 batches.

Sequence batches by stage priority: Negotiation → Proposal → Opportunity → Need Analysis → Prospect. Within each stage, post all three record types together so any interruption leaves whole deals complete rather than half-updated.

Use the note and task templates in `references/templates.md` exactly — they are formatted to render correctly in the HubSpot UI with working @mentions.

### Step 9: Verify and report
Every batch returns `successful: N, failed: 0`. Track running totals. At the end, report:
- Total notes posted
- Total tasks created
- Total failures (should be 0)
- Cleanup items (any test duplicates that need manual deletion)
- Top critical-attention deals
- Coaching priorities (which AEs are below compliance bar)
- **Activity insights** — deals likely cold despite being in advanced stages, AEs with low call activity, deals where customer commitments in emails haven't been followed up on

## Surfacing engagement findings in the note

When emails or calls reveal something the AE hasn't logged in notes, the ABHIMANYU NOTES section should call this out explicitly. Examples:

- "Email trail shows customer asked for proposal on Apr 12 — still not sent."
- "Last call was Mar 8 (no-answer). 60 days silent. Decide rescue vs closed-lost this week."
- "12 outbound emails, 0 inbound since Feb. Customer has ghosted — likely closed-lost."
- "Call notes from Apr 22 mention CHRO approval pending — chase that thread."

This makes the review valuable beyond just "AE didn't write a note" — it surfaces actual deal-level intelligence buried in inbox/call records.

## Output deliverables

Every run should produce:

1. **Excel workbook** — `Deal_Review_All_<N>_Deals.xlsx` in `/mnt/user-data/outputs/`
2. **HubSpot notes** — one per deal, tagged to AE, cc'd to manager (count = N)
3. **HubSpot AE action tasks** — one per deal, assigned to the deal owner, due T+1 (count = N)
4. **HubSpot manager review tasks** — one per deal, assigned to the manager, due T+5 (count = N)
5. **Run summary** — counts by stage, by AE, compliance scorecard, top risks, recommended next steps

Total HubSpot records per run: 3 × N deals.

## Reference files

Read these when you reach the relevant step.

**Local references** (inside this skill folder, under `references/`):

- `references/templates.md` — exact HTML for HubSpot notes and task properties. Read at Step 8 before posting.
- `references/hubspot_reference.md` — owner IDs, stage IDs, pipeline IDs, batch limits, API quirks. Read at Step 2.
- `references/next_action_patterns.md` — how to frame recommended actions for different deal situations. Read at Step 5.

**Supporting skills** (sibling skills at the project root — read at the indicated step the first time you encounter the trigger condition; not needed every run):

- `buying-signal-amplification.md` — read at Step 4b. Detect explicit, implicit, and verbal buying signals in email/call content.
- `objection-recognition.md` — read at Step 4b. Classify Price / Timing / Need / Trust / Authority objections so the next action addresses the right one.
- `decision-maker-identification.md` — read at Step 4b when the POC looks junior or approvals are deferring upward.
- `conversation-resurrection.md` — read at Step 5 for any `Silent` or `Dead` deal needing a re-engagement angle.

## Critical reminders

- **Mentions only work via HubSpot's `<span data-mention-id="...">` syntax**, NOT plain text `@Name`. Plain text won't notify the person.
- **Batch size is hard-capped at 10**. Don't attempt 11+ — it fails the entire batch.
- **Test before bulk** — posting 3 records per deal × 85 deals = 255 records. A formatting bug means cleaning up 255 records.
- **Two tasks per deal**: AE task (deal owner, T+1) for action + Manager task (manager, T+5) for review. This is the accountability pattern — don't collapse to one task.
- **AE task body** repeats the action text verbatim. **Manager task body** references it: "AE was tasked to: <X>. Confirm completed."
- **Business days only** for due-date math — skip Saturday/Sunday. If posting Thursday, AE task is Friday (T+1), manager task is the following Thursday (T+5).
- **No emojis in notes or tasks** — keeps records professional and search-friendly.
- **Always confirm scope (AE list + stages + count) before pulling data**. A misconfigured scope wastes time and pollutes deals with wrong-stage notes.
