---
name: deal-review-contact
compatibility: Requires HubSpot MCP connector to be active. Will not function without it.
description: >
  Contact-level (no-deal) segment of the deal-review family. Use for companies that have NO
  associated deal object — score who to approach and why the company never converted, and produce
  a company-level conversation picture. Trigger on "run the contact revival", "score these
  contacts/companies", "which contacts should I approach", "who do we speak to first", "no-deal
  contact map", "why is there no deal on this company", or a HubSpot Company/Contact ID shared for
  evaluation. Produces a five-sheet Excel (+ ledger) AND (on confirmation) writes a signal note +
  an approach task back onto the company.
  DISAMBIGUATION — this skill is ONLY for companies with no deal object. If the company has a deal
  at Stage 8 (Dormant) use deal-review-dormant; Stage 9 (Closed Lost) use deal-review-closed-lost;
  an open-pipeline deal use deal-review-active. Any company WITH a deal object is OUT OF SCOPE here.
---

# Contact Revival Scorer

## Purpose

For a set of **no-deal** companies, read everything logged in HubSpot and produce,
per company: a Conversation Signal Summary, the Key Problem Identified, and the
Recommended Next Step — plus a ranked list of who to approach first. The AE reviews
and iterates after. No input is required upfront.

The deliverable is a five-sheet Excel (see Step 7), with **Signal & Key Problem**
as the centerpiece.

---

## Run Configuration — Set Before Every Run

_Nothing about a specific AE is hardcoded. The values below are an example run — change the AE name and Owner ID to run for any AE in the org._

| Setting | Value |
|---------|-------|
| AE in scope | _your AE's name_ |
| Owner ID | _your AE's HubSpot owner ID_ |
| HubSpot portal | _your HubSpot portal ID (org-level)_ |
| Create-date filter | OFF (do not apply any company create-date window) |
| Scope gate | Activity-gated (see Ground Rules) |
| Out of scope | all other AEs are NOT part of this run |
| Output | One workbook for the AE in scope, appended across batches |

To run a different AE, change the owner ID and AE name here. Everything else holds.

---

## Ground Rules (read before running)

**Start at the company, never the contact.** Pull the company record and its
activity first, then drop into contacts. Company-level signals override contact-level.

**Scope = no-deal companies owned by the AE. No create-date filter.**
- The universe is every company owned by the AE (Run Configuration owner ID) with
  **no associated deal object**. There is no create-date window. Do not exclude any
  company on the basis of when it was created.
- A company is **no-deal** when `num_associated_deals` is **absent** on the record.
  In this portal the property is not set to "0" — it simply does not exist when the
  company has no deal. Filter with `NOT_HAS_PROPERTY num_associated_deals`. Companies
  where the property exists have at least one deal and are out of scope here.

**Activity gate — routes a company, never excludes it.** Because there is no
create-date bound, presence of logged outreach is used to ROUTE each no-deal company
into one of three sets. Nothing is silently dropped; every company appears in the
output somewhere.

| Set | Condition | Treatment |
|-----|-----------|-----------|
| Deep-read | `num_contacted_notes` >= 1 (at least one logged call, email or meeting) | Full Step 2–7 deep read and scoring. |
| Notes-only verify | `notes_last_updated` present but `num_contacted_notes` = 0 | Light check: pull the note(s). If it is only the assignment note / admin noise, list as HOLD-cold. If a substantive human note exists, promote to deep-read. |
| Bulk-list cold | No activity at all (no `notes_last_updated`, `num_contacted_notes` = 0) | Listed as HOLD-cold, no body reads. Enrich + confirm product before any first outbound. |

**Routing vs ranking — do not confuse them.** Presence of outreach is allowed only
as the routing gate above. Recency is **never** used to rank a company or to include
or exclude anything within the deep-read set. Within the deep-read set, recency is
*reported* inside the signal summary, not used as a filter.

**Lifecycle stage is NOT a filter.** It is unreliable in this portal. Record it as
a reported field only. Do not include or exclude any company based on lifecycle.

**Product is inferred from CRM, never asked upfront.** Scan all calls, emails and
notes for any mention of Empuls, Plum, Compass or Loyalife.
- Found → use it for ICP ranking. Flag: `Product: [X] — inferred from CRM.`
- Not found → complete the output anyway. Flag: `Product: NOT FOUND in CRM. ICP
  ranking skipped; contacts ordered by seniority only. AE to confirm.`

---

## HubSpot property cheat-sheet (this portal)

Use these directly; do not rediscover them.

| Need | Property / method |
|------|-------------------|
| No-deal companies for the AE | `companies` where `hubspot_owner_id` = owner ID AND `NOT_HAS_PROPERTY num_associated_deals` |
| Real outreach happened (call/email/meeting) | `num_contacted_notes` >= 1. Counts ONLY logged calls/emails/meetings — never plain notes, so the auto "Hunting Account … Happy Hunting!" note does not trip it. |
| Any activity at all (incl. notes/tasks) | `notes_last_updated` is present |
| Last call/email/meeting timestamp (recency + batch sort) | `notes_last_contacted` |
| Per-channel recency | `hs_last_logged_call_date`, `hs_last_logged_outgoing_email_date`, `hs_last_booked_meeting_date` |
| Contact / deal counts | `num_associated_contacts`, `num_associated_deals` |
| Email body | NOT retrievable. `hs_email_text` / `hs_email_html` are hidden ("property is hidden and cannot be queried"). Read subject + direction + reply count only. |

---

## Step 0 — Build the universe and the three sets

1. Pull all no-deal companies for the AE (owner ID + `NOT_HAS_PROPERTY num_associated_deals`).
   Record the total count.
2. Split into the three sets using the activity gate table above
   (`num_contacted_notes` and `notes_last_updated`). Record the count of each set.
3. Order the deep-read set by `notes_last_contacted` descending (hottest first).
4. Proceed in batches (see Batching and Resume).

---

## Batching and Resume

A faithful deep read cannot process the whole deep-read set in one pass. Run in batches.

- **Batch size: 25** companies from the deep-read set, in `notes_last_contacted`
  descending order.
- **Checkpoint after every company.** As each company is finished, append its rows to
  the workbook on disk AND write its company ID to a `Processed Ledger` tab (company ID,
  company name, batch number, timestamp). Never hold a whole batch in memory and write
  once at the end — an interruption would lose it.
- **Resume rule.** On any new batch or restart, first read the `Processed Ledger` tab and
  skip every company ID already present. Never double-process a company.
- **Stop condition.** End a batch after 25 newly-processed companies (or when the
  deep-read set is exhausted), write the workbook, and report: batch number, companies
  processed this batch, cumulative processed, remaining in deep-read set.
- The notes-only verify set and the bulk-list cold set are processed once, in a single
  light pass each, and recorded on their own rows — they are not part of the 25-per-batch
  count.

---

## Step 1 — Confirm Scope and Hard Out-of-Scope

This skill scores no-deal companies only. Before scoring, exclude — with a visible
block stating the reason — any company that hits either condition:

| Out-of-scope condition | What to write |
|------------------------|---------------|
| Company has any associated **deal object** (any stage) | `OUT OF SCOPE — has a deal. Route to the deal scorer.` |
| Conversation shows a **signed / onboarding / invoice / implementation / customer** state, even with no deal object on this exact record (likely a duplicate or sister record) | `OUT OF SCOPE — customer/duplicate signal: [quote the evidence]. Verify, merge, route to deal/farming scorer.` |

Never skip an exclusion silently. Record the lifecycle stage value found as context,
but do not let it gate anything.

---

## Step 2 — Pull Data (company first) with a Completeness Protocol

**Filter activity to the AE being processed** for verdict and ranking. Activity by
any other rep goes into context and triggers the coordination rule in Step 3a — it
never silently drives the verdict. State the AE name at the top of every company block.

**Contacts are pulled via the COMPANY → CONTACT association.**
- Take **every** contact associated with the company.
- **No contact-owner filter. No contact create-date filter.** "No owner" contacts
  and contacts created at any time are included. (Filtering on owner or contact-date is
  what silently drops contacts — e.g. a company that shows 5 contacts in HubSpot must
  return 5 here, not 1.)

**Read order (company first, then engaged contacts):**
1. Company record — name, industry, employee count, lifecycle (reported only), owner, full contact list
2. Notes — full bodies (swept at **company** level; this catches company-only notes)
3. Calls — full bodies, dates, duration, direction, disposition
4. Emails — subject, direction, to/from, dates, reply count and reply rate.
   **Email body is NOT retrievable**: HubSpot hides `hs_email_text` / `hs_email_html`
   ("property is hidden and cannot be queried"), so email prose cannot be read. Infer
   the topic from the subject line and whether the contact replied (reply count > 0 or
   a matching INCOMING_EMAIL); rely on notes, calls and meetings for actual content.
5. Meetings — outcome, attendees, dates, body
   Sweep calls, emails and meetings at **both company and contact level**, then
   dedupe by engagement ID. Person-level activity (calls/emails/meetings) lives on
   the contact; company-only items (often notes) live on the company. Both are required.

**Completeness audit (per company).** First retrieve the engagement *count*, then
the full bodies, then write an audit line: `Notes: pulled N / read N | Calls: N |
Emails: N | Meetings: N`. If pulled != read for any source, **stop on that company
and flag it** — do not proceed on partial data. Full bodies always; never rely on
previews.

**Property-level gate vs body-level rule.** `num_contacted_notes` is only the routing
pre-filter. Once inside a company, apply the meaningful-activity rule on the actual
bodies: a company routed to deep-read whose only logged item turns out to be noise
(assignment note, bounced call, bulk sequence email) drops to HOLD-cold and is noted.

**System noise — does NOT count as meaningful engagement:**
- The "Hunting Account … assigned as the Company Owner … Happy Hunting!" assignment note.
- Admin notes such as "make me the company owner", "update the SDR owner / inside sales status".
- Bulk / sequence marketing emails (e.g. automated "your invite for [date]", "reserved a spot") — counted as outbound touches only, never as replies or real conversation.

**Split contacts into two pools before any contact-level calls:**
- **Engaged** — appears in >=1 real activity (call, email, note, meeting) at company
  or contact level. Pull full history.
- **Listed** — on the company record with zero activity anywhere. Pull name + title
  only; no further calls. Check for duplicate names/emails and flag.

**No-shows** are found by reading, not a field. Flag No Show when a meeting outcome
= No Show or any activity body contains "no show", "didn't show", "did not attend",
"missed the call/meeting", "didn't join". One distinct date = First; two or more = Repeat.

When company-level and contact-level signals conflict, company-level wins — and say so.

---

## Step 3 — Hard Exclusions (per engaged contact)

| Condition | Flag |
|-----------|------|
| Any note/email contains a stop-outreach / do-not-contact request | `DO NOT CONTACT — contact requested no further outreach` |
| Structural DQ: genuinely wrong product category, or a true headcount/size mismatch | `EXCLUDED — Structural DQ. Timing cannot resolve this.` |

A timing DQ ("not now", "revisit next quarter", "budget cycle") is **not** a hard
exclusion — pass it through with a Timing DQ label in Step 4.

Headcount caution: do not apply a "<10 employees" structural DQ when the use case is
**customer-facing** (e.g. customer rewards / loyalty sized on the prospect's customer
base, not its own headcount). State the reasoning.

---

## Step 3a — Other-AE Coordination (MANDATORY in output)

If notes or activity show **any rep other than the AE being scored** working the
company or its contacts — **any other AE/owner (any owner ID that is not the AE in scope)** — you MUST surface it explicitly in **both**:
- the **Conversation Signal Summary** (name the rep and what they did/when), and
- the **Recommended Next Step** (e.g. "coordinate with [rep] before any outreach to
  avoid conflicting messaging").

Never bury this in a footnote. It changes how the AE acts.

---

## Step 4 — Classify Each Engaged Contact

Exactly one sub-type, based on what is explicitly logged:

| Sub-Type | When |
|----------|------|
| Ghosted | Outreach logged, zero reply ever. |
| No Show — First | One no-show on a distinct date. |
| No Show — Repeat | Two or more no-shows on distinct dates. |
| Replied, Not Converted | Reply exists, no meeting / no next step logged. |
| Timing DQ | DQ logged, reason is timing only. |
| AE Disqualified | DQ logged, reason is fit/size but not structural. |

If sub-type can't be determined: `Sub-type: Unknown — insufficient CRM data. AE to review.`

---

## Step 5 — Rank Contacts (no numeric score)

Ranked by two factors in order.

**Primary — Seniority:** 1 VP/C-suite/CHRO/CPO · 2 Director/Sr Manager/Head of · 3
Manager · 4 IC/Executive/Analyst · 5 Unknown/blank. If the title is blank or
corrupted, read note bodies for the role and state the correction.

**Secondary — ICP match** (breaks ties within a seniority tier). Read
`references/icp-definitions.md`. Tier labels only — there is no numeric score:

| ICP tier | Sort within seniority |
|----------|----------------------|
| Exact match — Top Persona ★ | First, flag ★ TOP PERSONA |
| Exact match | First |
| Adjacent (right function, not listed) | Second |
| Wrong function for this product | Third |
| Product unknown | Seniority order only, no ICP label |

Apply separately to Engaged and Listed pools; never mix them.

---

## Step 6 — Verdict and Tier

**Verdict:**
| Verdict | When |
|---------|------|
| 🟢 Approach | >=1 engaged contact at Director+ with ICP match (or unknown product) and no negative company signal |
| 🟡 Hold | No senior engaged contact, OR a clear timing block (state the re-engage date), OR only the prior POC is dark/DNC and a new contact is needed |
| 🔴 Do Not Approach | All engaged contacts excluded (DNC / structural DQ), OR explicit rejection logged |

**Tier (priority layer, on top of the verdict):**
| Tier | When |
|------|------|
| 🔵 ACTIVE NOW | A real touch or booked meeting in the last ~90 days |
| 🟠 RE-APPROACH | Qualified before but last meaningful touch/reply >90 days ago, prior approaches exist, a viable (non-excluded) contact exists, and no recent explicit "no" |
| 🟡 HOLD | Recent "no", cold, no senior contact, or a timing block. Bulk-list cold companies sit here. |
| 🔴 OUT OF SCOPE | Has a deal / customer / duplicate (from Step 1) |

If all contacts are Listed with none engaged: verdict = Hold; first target = highest
seniority + ICP from the Listed pool.

---

## Step 7 — Output: the Five-Sheet Excel (+ ledger)

Produce one workbook. Professional font (Arial), one row per company on the summary
sheets, full wrapped text in the narrative cells. Header rows are Arial 10 bold, white
text on dark navy (1F3864 fill); titles Arial 12 bold; body Arial 9, wrapped, top-aligned;
freeze panes at A3. Tier fills: ACTIVE NOW DDEBF7, RE-APPROACH FCE4D6, HOLD FFF2CC,
OUT OF SCOPE / cold F2F2F2.

1. **Run Notes** — AE and owner ID, run date, scope statement (**create-date filter NOT
   used**; universe is no-deal companies owned by the AE; activity-gated into deep-read /
   notes-only verify / bulk-list cold; lifecycle NOT used; recency reported not filtered),
   the three-set counts, the meaningful-activity rule, the email-body limitation (subject
   + reply count only; body hidden by HubSpot), product inference note, batch status,
   verdict/tier legend.
2. **Batch Summary** — `Rank | Tier | Company | Verdict | Product | Last meaningful
   activity | Recency | Approached? | Top contact (entry) | Title | Recommended next step | HS`.
   Sorted: ACTIVE NOW → RE-APPROACH → HOLD → OUT OF SCOPE, then seniority of top contact.
3. **Signal & Key Problem (centerpiece)** — `# | Tier | Company | Conversation Signal
   Summary | Key Problem Identified | Recommended Next Step`. The signal summary is
   company-level first then contact-level, with dates and names, conflicts stated, and
   **any other-AE involvement named (Step 3a)**. The next step is one specific action
   referencing actual CRM content — and repeats any other-AE coordination.
4. **Ranked Contacts** — `Company | Role in plan (ENTRY/Escalate/Listed/EXCL/OUT) |
   Name | Title | ENG/LIST | Re-approach? | Status / sub-type | Signal (CRM) | HS`.
5. **Confidence Flags** — `Company / item | Issue | Recommended action`. Include every
   completeness-audit mismatch, data gap, duplicate, corrupted title, unknown product,
   conflicting signal, and the standing email-body limitation.

Plus a **Processed Ledger** tab — `Company ID | Company | Batch | Timestamp` — written
incrementally for resume (see Batching and Resume).

Behind the sheets, keep a per-company working block (verdict, tier, checkpoints,
signal, ranked contacts, next steps) so the analysis is auditable.

---

## Step 8 — Confidence Flags

Flag every instance where: a completeness audit mismatched; a title was blank/corrupted
and seniority came from notes; a sub-type was uncertain; company- and contact-level
signals conflicted; product was not found; a duplicate/customer signal appeared; a
deep-read company turned out to be noise-only and dropped to cold; or another rep was
working the account. Format: `[Company / Contact] — [Reason] → Recommend: [action]`.
Always include the standing flag: `Email bodies not retrievable — HubSpot hides the
property in this portal.`

---

---

## Step 9 — Write Back to HubSpot (on confirmation)

Only run after the user reviewed the Excel and confirmed writeback. There is no deal object, so
records attach to the **company** (and optionally the top-ranked entry contact). Same guardrails as
the `deal-review-active` main skill.

**Per in-scope company, create up to two records:**

1. **Signal note** on the company — always. Body = Conversation Signal Summary + Key Problem Identified + Recommended Next Step + verdict/tier line. Tag the AE in scope (Run Configuration owner ID) using `<span data-mention-id="<owner_id>">` — never plain `@`. No emojis (write "APPROACH"/"HOLD"/"DO NOT APPROACH"). Name any other-AE involvement (Step 3a) in the note.
2. **Approach task** — only for ACTIVE NOW and RE-APPROACH tiers. Owner = the AE in scope. Attach to the company (or the top-ranked entry contact). `hs_task_subject` = `Approach (No-deal): <Company> — <top contact>`. `hs_task_body` = the Recommended Next Step verbatim, including any other-AE coordination note. `hs_timestamp` = now+1 business day for ACTIVE NOW, or the stated re-approach date for RE-APPROACH.

**Do NOT create an approach task** for: HOLD, DO NOT APPROACH / OUT OF SCOPE, or any DO NOT CONTACT / structural-DQ company. Post the note only (records the decision / coordination need).

**Guardrails (identical to the main skill):**
- `manage_crm_objects` hard-capped at **10 objects per batch**.
- **Test 1-2 companies first** unless the user said run all.
- Mentions only via `<span data-mention-id="...">`; no emojis; sequence by tier
  (ACTIVE NOW then RE-APPROACH then HOLD then OUT OF SCOPE); post note + task for a company together.
- Writeback runs per processed batch and is recorded in the Processed Ledger so a resume never double-posts.

Every batch should return `successful: N, failed: 0`. Track running totals.


For data-quality issues, multi-company contacts, conflicting signals, no-show edge
cases, and missing fields — read `references/edge-cases.md` when you hit a situation
the steps above don't cover. For ICP persona tables per product per geography — read
`references/icp-definitions.md` at Step 5.
