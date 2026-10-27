# Three-Step Data Pull — Closed Lost Classification

## Scope

This procedure applies exclusively to deals at dealstage `900000056` (Stage 9 — Closed Lost)
in the configured AE's pipeline (`hubspot_owner_id = <owner_id>` — see the skill's Run Configuration).
Do not apply this procedure to Dormant, Active, or any other pipeline deals.

---

## Executable Pull — Exact MCP Tool Mechanics

Use the HubSpot MCP tools the same way the `deal-review-active` main skill does.

**1. Fetch the deal set:**
`search_crm_objects` with `objectType: "deals"`, filtering `dealstage = 900000056`,
`createdate > <window_start>` (default 2024-12-02), `hubspot_owner_id = <owner_id>`. Request properties:
`dealname, dealstage, amount, deal_currency_code, hubspot_owner_id, closedate, createdate,
hs_lastmodifieddate, pipeline`.

**2. Pull associations per deal:**
`get_crm_objects` with `associations: ["notes", "emails", "calls", "meetings", "contacts", "companies"]`.

**3. Fetch each engagement body via a follow-up call** using the exact property fields:
- **Notes** — `objectType: "notes"`, body in `hs_note_body` (HTML).
- **Emails** — `objectType: "emails"`, body in `hs_email_text` (plain, preferred) or `hs_email_html`; plus `hs_email_subject`, `hs_email_direction` (INCOMING / OUTGOING / FORWARDED_EMAIL), `hs_email_status`, `hs_timestamp`.
- **Calls** — `objectType: "calls"`, body in `hs_call_body`; plus `hs_call_title`, `hs_call_duration` (ms), `hs_call_direction`, `hs_call_disposition` (connected / no-answer / voicemail), `hs_timestamp`.
- **Meetings** — `objectType: "meetings"`, title + notes + outcome + `hs_timestamp`.

**Known association quirk (do not skip):** NOTE queries reliably return their deal association, but
EMAIL and CALL engagements often do **not** surface through the deal-association call because of a
CRM cache sync gap. To avoid silently dropping emails/calls, run a **per-deal, `createdate`-filtered
engagement query** for EMAIL and CALL as a residual pass, keyed on the deal's associated contacts and
company, then dedupe by engagement ID. Never conclude "No emails/No calls" from the association call
alone — confirm with the residual pass first.

A blank `body` field on a call = no meaningful content logged. Score as non-meaningful activity.
A call with `body` content = read it. Even a short note counts if it references deal context.

Repeat this sequence on the Company page and Contact record(s) as Steps B and C below.

---

## How HubSpot Activity Data Is Fetched

HubSpot returns activities as CRM engagement objects associated with the deal record.
Each engagement has a `type` field and a `body` field. The `body` field contains the
actual content — call notes, email text, or manually written note text.

Pull activities in this exact order for every deal:

1. **All Activities** — pull the full engagement list on the deal record first. This is the primary pass and will capture most data in one call.

Then, for anything not surfaced in All Activities, pull each of the following as residual checks:

2. **Notes** — filter engagements where `type = NOTE`. Read the `body` field of each.
3. **Emails** — filter engagements where `type = EMAIL`. Read subject, body, sent/received direction, and date. (Apply the residual `createdate`-filtered pass above — emails frequently miss the deal-association call.)
4. **Calls** — filter engagements where `type = CALL`. Read `body` for call notes. Check duration. (Same residual pass applies.)
5. **Meetings** — filter engagements where `type = MEETING`. Read title and notes if present.

Steps 2–5 exist because All Activities does not always return every engagement type in full — residual checks ensure nothing is missed due to API pagination or type filtering gaps.

---

## Error Definition

Skipping any step without a written output block is a **visible error**.
A visible error means the batch output is incomplete and must not be delivered.
If a step is skipped, Claude must return to that step, complete it with a written output block,
and re-run all scoring and output that depends on it before proceeding.
There is no partial delivery when a step has been skipped.

---

Use this guide every time you need to classify a deal's drop reason.
Execute all three steps in order. Write a visible output block at each step.

---

## Step A — Deal Level

Pull: all notes, call logs, emails associated with the deal record.
Look for: any language signalling internal shift OR external competitor choice.

- If clear signal found: classify and proceed to scoring. Skip Steps B and C.
- If no signal or vague signal: proceed to Step B.

Output block:
```
Step A (Deal level): [Found / Not found — reference to what was read]
```

---

## Step B — Company Page

Pull: HubSpot company record for the associated company.
Look for: other deals at the same company, company-level notes, any account-level context.

- If clear signal found: classify and note source as "Company record — [field/note reference]."
- If still no signal: proceed to Step C.

Output block:
```
Step B (Company level): [Found / Not found — reference to what was read, or "Skipped — Step A sufficient"]
```

---

## Step C — Contact Level

Pull: HubSpot contact record(s) associated with the deal.
Look for: contact-level notes and any flags on the contact record.

Output block:
```
Step C (Contact level): [Found / Not found — reference to what was read, or "Skipped — Step A/B sufficient"]
```

---

## After All Three Steps

If still no clear reason after completing all three steps:

- **DATA MISSING** — No notes, no calls, no emails found anywhere. Nothing to read. Cannot classify.
  Flag: `DATA MISSING — no activity found after full three-step data pull`
  Score: 0 pts on Filter 1. Re-engagement date: BLANK. No re-engagement task written back.

- **DATA VAGUE** — Activity exists but drop reason cannot be determined.
  Quote the found content exactly as written. Do not interpret it.
  Flag: `DATA VAGUE — [exact quote from note/call/email]. Meaning unclear. Manual review needed.`
  Score: 10 pts (hold). Re-engagement date: BLANK. No re-engagement task written back.

---

## Competitor Field

List ALL competitors named across all notes, calls, and emails for the deal.
If multiple competitors are mentioned at different points, list all of them.
Format: `Competitor(s): [Name 1], [Name 2]` or `Competitor(s): Not named`
This field appears in the output regardless of Internal/External classification.

---

## 12-Month Competitor Contract Assumption

For every EXTERNAL deal, include this statement in the output:
`Assumption: Competitor contracts are assumed to be 1 year from last meaningful activity date.`

If a note, call, or email explicitly mentions a different contract duration — use that duration
instead and flag it: `Duration from notes: [X months] — overrides default assumption.`
