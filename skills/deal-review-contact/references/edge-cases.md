# Edge Cases — Contact Revival Scorer

## Table of Contents
1. [Data Quality Issues](#data-quality)
2. [System Noise & Completeness](#system-noise)
3. [Multi-Company Contacts](#multi-company)
4. [Conflicting Signals](#conflicting-signals)
5. [No-Show Handling](#no-show)
6. [Missing or Empty Fields](#missing-fields)
7. [Other-AE Coordination](#coordination)
8. [Out-of-Scope / Customer & Duplicate Signals](#out-of-scope)

---

## Data Quality Issues {#data-quality}

**Title field contains wrong data (phone, email, another name):** read note and call
bodies for the real role. If found: `Title field corrupted — [what it contained].
Role from notes: [what notes said].`

**Employee count looks wrong, or is misleading for the use case:** cross-check AE
notes. If the use case is **customer-facing** (customer rewards / loyalty sized on the
prospect's customer base, not its own headcount), do NOT apply a "<10 employees"
structural DQ. State: `HubSpot employee count: [X]; use case is customer-facing, sized
on [N] customers — headcount DQ does not apply.`

**Industry mis-tagged (e.g. a jewellery retailer tagged Food Production):** trust the
conversation/enrichment notes over the field. Note the correction as a data gap.

**Lifecycle stage:** record the value as context only. It is never a gate (it is
unreliable in this portal).

**Contact has no activity date anywhere:** note it as a data gap; do not infer inactivity.

---

## System Noise & Completeness {#system-noise}

These do NOT count as meaningful engagement and must not drive recency or verdict:
- The "Hunting Account … assigned as the Company Owner … Happy Hunting!" assignment note.
- Admin notes: "make me the company owner", "update the SDR owner / inside sales status".
- Bulk / sequence marketing emails (automated "your invite for [date]", "reserved a
  spot for you") — count as outbound touches only, never as replies.

**Completeness audit:** for each company, retrieve the engagement count first, then the
full bodies, then write `Notes: pulled N / read N | Calls: N | Emails: N | Meetings: N`.
If pulled ≠ read for any source, stop on that company and flag it. Never analyse on
partial data, and never rely on previews — always read full bodies. Sweep notes at
company level and calls/emails/meetings at both company and contact level, deduping by
engagement ID.

**Email body is unavailable.** HubSpot hides the email body properties
(`hs_email_text` / `hs_email_html`) — querying them returns "property is hidden and
cannot be queried." Only subject, direction, to/from, reply count, reply rate and
timestamp are readable. Treat email as a metadata signal: did we email, how often, did
they reply, and what was the subject. Get conversation substance from notes, calls and
meetings (whose bodies ARE readable). Record "email bodies not retrievable" as a
standing data gap in Confidence Flags on every run.

---

## Multi-Company Contacts {#multi-company}

**Contact associated with more than one company:** process only companies in scope
(no-deal, create-date window). List all companies checked in the checkpoints:
`Associated companies checked: [Company A — in scope ✅], [Company B — out of scope ❌].`

---

## Conflicting Signals {#conflicting-signals}

**Company-level positive, contact-level empty:** apply company-level. State:
`Company-level signal applied — [what notes said]. Contact-level empty. Company wins.`

**Contact-level positive, company-level negative:** company-level wins. State both and
flag for AE review.

**Two AE notes contradict:** use the most recent; state both and which was applied.

---

## No-Show Handling {#no-show}

**First no-show:** Sub-type No Show — First. No ranking penalty (a meeting was agreed;
something came up). The AE's follow-up behaviour matters, not the no-show itself.

**Repeat no-show (2+ distinct dates):** Sub-type No Show — Repeat. Drop one position
relative to seniority+ICP. State: `Repeat no-show — reliability pattern noted.`

**No-show with a logged rescheduling attempt:** note as context in the signal summary;
it does not change the sub-type but signals the AE believes intent exists.

---

## Missing or Empty Fields {#missing-fields}

| Missing field | What to do |
|---------------|------------|
| Job title blank | Seniority = Unknown (level 5). Flag the gap. |
| Employee count blank | Note as unavailable. Do not estimate. |
| No notes anywhere | Conversation signal = None. State explicitly. |
| No calls or emails | Note which source is missing; use what exists. |
| Zero activity anywhere | Conversation signal = None. Verdict defaults to Hold. |

Always reflect absence accurately — never infer a value not present in CRM.

---

## Other-AE Coordination {#coordination}

If any rep other than the AE being scored is working the company or its contacts
(any owner ID that is not the AE in scope),
this is **not** a footnote. It must appear in BOTH the Conversation Signal Summary
(name the rep, what they did, when) and the Recommended Next Step ("coordinate with
[rep] before outreach to avoid conflicting messaging"). See SKILL.md Step 3a.

---

## Out-of-Scope / Customer & Duplicate Signals {#out-of-scope}

A company is OUT OF SCOPE (do not score; route to the deal/farming scorer) when:
- it has any associated deal object, OR
- the conversation shows a signed / onboarding / invoice / implementation / customer
  state — even with no deal object on this exact record. This usually means a
  duplicate or sister company record (e.g. "Account_074" vs a signed "Account_073").

Write the evidence verbatim, recommend a merge, and exclude from the ranked output.
