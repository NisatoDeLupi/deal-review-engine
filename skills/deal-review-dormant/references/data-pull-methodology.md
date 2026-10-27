# Simultaneous Data Pull — Dormant Deal Drop Reason Classification

Use this guide every time you need to pull data and classify a deal's dormant drop reason.
Pull all sources at the same time. Write a visible output block for each source.
Missing data on one source never stops the pull or the scoring on other sources.

---


## Executable Pull — Exact MCP Tool Mechanics

Use the HubSpot MCP tools the same way the `deal-review-active` main skill does.

**1. Fetch the deal set:** `search_crm_objects` with `objectType: "deals"`, filtering
`dealstage = 900000070` (Stage 8 — Dormant) and `createdate > <window_start>` (default 2024-12-02). Request properties:
`dealname, dealstage, amount, deal_currency_code, hubspot_owner_id, closedate, createdate,
hs_lastmodifieddate, pipeline`.

**2. Pull associations per deal:** `get_crm_objects` with
`associations: ["notes", "emails", "calls", "meetings", "contacts", "companies"]`.

**3. Fetch each engagement body** via a follow-up call using the exact property fields:
- **Notes** — `objectType: "notes"`, body in `hs_note_body` (HTML).
- **Emails** — `objectType: "emails"`, body in `hs_email_text` (plain, preferred) or `hs_email_html`; plus `hs_email_subject`, `hs_email_direction`, `hs_email_status`, `hs_timestamp`.
- **Calls** — `objectType: "calls"`, body in `hs_call_body`; plus `hs_call_title`, `hs_call_duration` (ms), `hs_call_direction`, `hs_call_disposition`, `hs_timestamp`.
- **Meetings** — `objectType: "meetings"`, title + notes + outcome + `hs_timestamp`.

**Known association quirk (do not skip):** NOTE queries reliably return their deal association, but
EMAIL and CALL engagements often do **not** surface through the deal-association call because of a
CRM cache sync gap. To avoid silently dropping emails/calls, run a **per-deal, `createdate`-filtered
engagement query** for EMAIL and CALL as a residual pass, then dedupe by engagement ID. Never
conclude "No emails/No calls" from the association call alone — confirm with the residual pass first.

## Why Simultaneous Pull

AEs in this pipeline log activity inconsistently. A call outcome may appear in company
notes but not the deal record. A champion change may be visible only in the contact
record. Pricing discussions may exist only in email threads. Gating the pull on one
source before moving to the next means critical signals will be missed. Pull everything
at once; flag what is missing; score what is available.

---

## What to Pull (All Sources, Every Deal)

| Source | What to look for |
|--------|-----------------|
| Deal page | Stage, amount, close date, owner, drop reason field (if filled) |
| Company page | All other deals at this company (stage + AE owner), company-level notes, any account context not tagged to the deal |
| Contact record(s) | Name, title, lead status (Disqualified / Closed Deal / Active), contact-level notes |
| Call logs | Date, duration, substantive content of notes. Blank calls do not count as meaningful activity. |
| Email history | Sent/received, dates, content. System-generated or admin emails do not count. |
| AE notes | All manually written entries on the deal record |

---

## Meaningful Activity — Definition

A touchpoint counts as meaningful activity only if it contains substantive content:
- Call with a logged note that references the deal, the client, or any outcome
- Email with actual content (not a bounce, auto-reply, or blank thread)
- AE-written note with deal context

The following do NOT count:
- Blank call logs (no body content)
- No-answer call attempts with no note
- Field updates or admin/system logs
- No-reply email attempts with no content

If the last logged activity is non-meaningful, keep going back in the log until you
find the last meaningful touchpoint, or declare: `No meaningful activity found.`

---

## Drop Reason Classification — Internal vs External

After pulling all sources, classify the drop reason as Internal or External.
This classification feeds Filter 1 (Dormant Deal Drop Reason) in the scoring rubric.

### Internal Shift — Language signals to look for

The deal went dormant because of something happening *inside the client's organisation*,
not because of a competitor or a product rejection. Classify as Internal if any of the
following language or situations appear across any source:

- "Budget frozen", "budget cut", "no budget this quarter/year"
- "Reorg happening", "team restructuring", "leadership change"
- "Decision deferred", "putting on hold", "not a priority right now"
- "POC left the company", "our champion moved on", "new person taking over"
- "Internal priorities shifted", "mandate withdrawn internally"
- "We need to align internally first", "getting internal approvals"
- Legal, finance, or procurement team involvement causing a delay (not a rejection)
- Deal going quiet after internal discussions without an explicit external reason given

### External Shift — Language signals to look for

The deal went dormant because the client chose something *outside* — a competitor,
a different solution, or explicitly disqualified themselves. Classify as External if:

- Competitor name explicitly mentioned ("went with Darwinbox", "signed with Leapsome")
- "Went with another vendor", "evaluated and chose a different solution"
- "Already signed elsewhere", "contract signed with X"
- "Not a fit for our needs", "your product doesn't cover what we need"
- Contact status set to Disqualified with no internal reason on record
- AE note confirms disqualification due to product/fit mismatch

### When signal is unclear

- **DATA MISSING:** No notes, no calls, no emails with substantive content across all sources.
  Flag: `DATA MISSING — no meaningful activity found after full data pull.`
  Score Filter 1 at 0. Drop reason: BLANK.

- **DATA VAGUE:** Activity exists but drop reason cannot be determined.
  Quote the exact content found. Do not interpret.
  Flag: `DATA VAGUE — [exact quote]. Meaning unclear. Manual review needed.`
  Score Filter 1 at 8/20 (hold score). Drop reason: BLANK.

---

## Intent Signal Classification — 3 Levels

This feeds Filter 5 (Intent Signal) in the scoring rubric. Read the full conversation
across all sources before classifying. Do not rely on a single note or call.

**Level 3 — High Intent**
Multiple signals of serious engagement present. Apply Level 3 if ALL of the following
are true:
- Budget was explicitly discussed (a number or range was mentioned)
- Timeline was confirmed (a specific quarter, month, or deadline was named)
- Multiple POCs were involved (2+ contacts from the client side)
- Internal teams (legal, finance, or procurement) were looped in

These deals had real buying intent before going dormant. The drop was situational,
not a rejection.

**Level 2 — Medium Intent**
Active engagement existed but without the depth of Level 3. Apply Level 2 if:
- At least one meeting or substantive call happened
- A single POC was engaged and discussions occurred over time
- The deal dropped for a named reason (budget freeze, champion left, delay)
  but there was no explicit rejection of the product or vendor

These deals had real contact and progress. Revival is plausible with the right trigger.

**Level 1 — Low Intent**
Post-outreach silence or minimal engagement. Apply Level 1 if:
- A meeting or discovery call happened, OR an initial proposal was sent
- But the client gave no response or only minimal acknowledgment after that
- No substantive discussion on record — just outreach attempts with no reply

These deals have the weakest revival signal. The client was never deeply engaged.

**Level 0 — No Signal**
No substantive conversation found. No calls with content, no emails with content,
no AE notes with deal context. Score Filter 5 at 0.

---

## Competitor Field

List ALL competitors named across all sources for the deal.
Format: `Competitor(s): [Name 1], [Name 2]` or `Competitor(s): Not named`
This field appears in the output regardless of Internal/External classification.

---

## 12-Month Competitor Contract Assumption

For every External-classified deal, include:
`Assumption: Competitor contracts assumed to be 12 months from last meaningful activity date.`

If a note, call, or email explicitly mentions a different contract duration, use that
and flag: `Duration from notes: [X months] — overrides default assumption.`
