---
name: Xoxoday Closed Lost Revival Scoring
compatibility: Requires HubSpot MCP connector to be active. Will not function without it.
description: >
  Use when the user asks to score closed lost deals, classify closed lost drop reasons,
  run the closed lost revival batch, or identify which closed lost deals are worth
  re-engaging. Triggered by phrases like "run closed lost", "score these closed lost deals",
  "classify closed lost", "closed lost batch", "which closed lost deals should we revive",
  "process closed lost", or "run the closed lost scoring". Also trigger whenever the user
  asks to evaluate, prioritise, or summarise deals and the context is the Closed Lost pipeline.
  This skill is exclusively for the Hunting Team direct sales pipeline.
---

# Xoxoday Closed Lost Revival Scoring System

## Purpose

Fetch all Closed Lost deals from HubSpot that meet the active scoring window, score each
one out of 100 across 5 filters, assign a priority tier, and produce a structured output
per deal — so the AE knows which deals are worth re-engaging, when, and what to say.

This skill has two reference files. Read them when directed:
- `scoring-rubric.md` — exact scoring brackets for Filters 2–5 + Contact Quality / ICP definitions
- `data-pull-methodology.md` — three-step data pull protocol + drop reason classification guide

---

## Scope — Read This Before Anything Else

Built exclusively for the **Hunting Team**. Does not apply to:
- CAM or farming deals
- Cross-sell, upsell, renewal, or expansion opportunities
- Any deal outside the direct sales pipeline

Empuls Gifting deals are scored normally. Flag as `PURSUE WITH CAUTION — Empuls Gifting. Verify product fit before outreach.` Carry this flag through to the output and Recommended Next Step.

---

## HubSpot Query — Apply Exactly Before Pulling Any Deals

Filter on **both** conditions together at the query level using these exact HubSpot property names and values:

```
dealstage = 900000056
createdate > 2024-12-02
hubspot_owner_id = 900000113
```

Do not substitute label strings (e.g. `closedlost`) for the numeric stage ID — label strings are unreliable across pipelines.
Do not substitute any other date field (e.g. `notes_last_updated`, `hs_lastmodifieddate`, `hs_last_activity_date`) for `createdate` — these measure different things and will return wrong deal sets.
Do not drop the `hubspot_owner_id` filter — this system scores AE_13's pipeline only.

Applying both conditions at query time limits the pull to the active scoring window only.
Do not pull all Closed Lost deals and filter afterward — this wastes tokens and API calls.

**Stage ID Reference — Direct Sales Pipeline:**

| Stage ID | Label | Action |
|----------|-------|--------|
| `900000056` | 9 — Closed Lost | ✅ Score these |
| `900000070` | 8 — Dormant | ❌ Exclude — different pipeline |
| `9000000002` | 6 — Confirmed & Signed | ❌ Exclude |
| `9000000001` | 7 — Closed Won | ❌ Exclude |

**Post-pull verification:** Check `dealstage` on every record after fetching.
If any record shows a stage other than `900000056`:
`EXCLUDED — dealstage [ID] is not Stage 9 Closed Lost. Remove from batch.`
Do not score excluded deals under any circumstances.

---

## Pre-Scoring Filters — Run on Every Deal Before Scoring

Write a visible exclusion block for every filtered deal. Never skip silently.

### Filter A — Duplicate Company / Two Deals Rule

Before scoring, check whether the associated company has more than one deal in HubSpot.

- One deal only → proceed to scoring.
- Same AE, other deal at stage Confirmed & Signed (stage ID `9000000002`) or Closed Won (stage ID `9000000001`) → exclude the Closed Lost deal.

```
EXCLUDED — SUPERSEDED BY CLOSED/SIGNED DEAL
Closed Lost deal: [Deal Name] | Record ID: [Closed Lost Record ID] | Stage ID: 900000056
Superseding deal: [Deal Name] | Record ID: [Superseding Record ID] | Stage ID: [9000000002 / 9000000001] | Stage label: [Confirmed & Signed / Closed Won] | Owner: [AE Name]
Reason: Same AE has a Confirmed & Signed or Closed Won deal at this company — the Closed Lost deal is superseded.
```

- Different AEs own deals at the same company → **score AE_13's deal** but flag the conflict visibly. Do not hold AE_13's deal pending the other AE's resolution — the other AE may be inactive and unaware. Surface the conflict in Key Problems Identified and Recommended Next Step so it can be coordinated.

```
FLAGGED — MULTI-AE SAME COMPANY
AE_13's deal: [Deal Name] | Record ID: [ID]
Company: [Company Name]
Other AE's deal: [Deal Name] | Record ID: [ID] | Owner: [Other AE Name] | Stage: [Stage Label]
Action required: Flag to AE_13 — coordinate with [Other AE Name] before any outreach to avoid clash. Other AE may be unaware of this deal. Do not hold scoring pending coordination.
```
AE_13's deal proceeds to scoring. The conflict flag carries through to Key Problems Identified and Recommended Next Step.

- Two deals, same company name, different company records → apply steps above across both, then flag:
`DUPLICATE COMPANY RECORDS — same name found twice. Recommend merging.`

---

## Step 1 — Pull All Data Sources Simultaneously

Read `data-pull-methodology.md` for the full three-step pull and drop reason classification protocol.

Pull ALL sources at the same time for every deal — no gates, no conditionals, no cascades.
Data unhygiene is the default reality. Pulling everything simultaneously is the only way to
get a complete picture. Missing data on one source never stops the pull or scoring elsewhere.

Pull simultaneously:
1. **Deal page** — stage, amount, close date, owner, drop reason field
2. **Company page** — company-level notes, all deals at this company (stages + owners)
3. **Contact record(s)** — name, title, authority level, lead status, contact-level notes
4. **Call logs** — date, duration, content of notes
5. **Email history** — sent/received, dates, substantive content
6. **AE notes** — all manually written entries on the deal record

Write a visible checkpoint after pulling:

```
DATA PULL COMPLETE:
✅ Deal page — [stage, amount, close date]
✅ Company page — [other deals found: Y/N | account notes: Y/N]
✅ Contacts — [name, title — or "No contacts associated"]
✅ Calls — [count, last call date — or "No calls logged"]
✅ Emails — [count, last email date — or "No emails found"]
✅ Notes — [count — or "No notes found"]
⚠ [Source] — No data returned. Score reflects absence.
```

---

## Step 2 — Run Pre-Scoring Checks

**Check A — Stop Request:**
Any call log, email, or note containing a client request to stop follow-ups →
`DO NOT CONTACT — Client requested no further outreach.`
Score is still calculated but next step reads: `DO NOT CONTACT — only re-engage if client initiates.`
Cannot be overridden by score.

**Check B — Active Deal at Same Company:**
If HubSpot shows a non-closed, non-dormant deal at the same company →
flag: `ACTIVE DEAL EXISTS — coordinate with deal owner before any outreach.`

Proceed to Step 3 only after checks are written visibly.

---

## Step 3 — Score Across 5 Filters

Read `scoring-rubric.md` for exact brackets and evidence requirements.

Total score is out of 100. Every score must cite a specific HubSpot data point.
Never infer or guess.

| Filter | Max | What it measures |
|--------|-----|-----------------|
| 1. Drop Reason Classification | 25 | Why did the deal close lost? Internal = higher. External = lower. |
| 2. Deepest Stage Reached | 25 | How far did the deal progress before closing lost? |
| 3. Recency of Last Meaningful Activity | 20 | How recent was the last substantive touchpoint? |
| 4. Deal Amount (₹) | 20 | Is this deal worth the re-engagement effort? |
| 5. Contact Quality | 10 | Right person? Authority level × ICP match. |

After scoring all five filters, verify the five scores sum to the stated total.
Mismatch = recheck before proceeding. Non-negotiable.

---

## Filter 1 — Drop Reason Classification (25 pts)

This is the most important filter. Run the three-step data pull before classifying every deal.
For the full procedure, read `data-pull-methodology.md`.

### The Core Distinction

**EXTERNAL** = The client made an active, outward choice — they went elsewhere or ended the
conversation decisively. They chose against us.

**INTERNAL** = The client paused due to their own situation — budget, timing, priority shift,
no response. They did not choose against us; they stopped.

This distinction determines both the score and the re-engagement timeline logic.

---

**EXTERNAL — Client made an active choice to go elsewhere.**

HubSpot typically records this as: client chose another competitor, explicit rejection, or disqualified.

Score: **5 pts**

Re-engagement date = last meaningful activity date + 10 months.
This targets a 2-month window before the assumed 1-year competitor contract expires.

State in output:
`Re-engage: [Month Year] (last meaningful activity: [date] + 10 months)`
`Assumption: Competitor contract assumed 1 year. Re-engagement timed for pre-renewal window.`

If competitor contract duration is found in notes: adjust and flag the override.

---

**INTERNAL — Client's situation changed. Not a product rejection.**

Examples: Budget deferred | Plan dropped | Internal restructuring | Tech delay | No response | "Will revisit next quarter / next FY"

Score range: **18–25 pts**
- 25 pts: Explicit timeline given — client indicated intent to return
- 21 pts: Clear internal reason stated, no specific timeline
- 18 pts: Reason implies internal shift but not explicitly stated

Re-engagement timeline for Internal deals — derive from signals in this order:
1. Specific timeline in notes ("revisit Q2", "next FY", "after appraisal") → use that
2. Clear internal reason, no timeline → default: 6 months from last meaningful activity
3. DATA VAGUE or DATA MISSING → BLANK, AE sets manually

State the source in output:
- `Timeline: Signal-based — note from [date] referenced [specific timeline]`
- `Timeline: Default — 6 months from last meaningful activity ([date]) = [target month/year]`
- `Timeline: BLANK — data insufficient, AE to set manually`

Add this note to Recommended Next Step for all Internal deals:
`Verify with AE that this company is not also being worked in the Dormant pipeline before outreach.`

---

**DATA MISSING — 0 pts**
No notes, no calls, no emails found after completing all three data pull steps.
Flag: `DATA MISSING — no activity found after full three-step data pull`
Re-engagement date: BLANK — AE must set manually.

**DATA VAGUE — 10 pts (hold)**
Activity exists but drop reason cannot be determined. Quote the found content exactly. Do not interpret.
Flag: `DATA VAGUE — [exact quote]. Meaning unclear. Manual review needed.`
Re-engagement date: BLANK — AE must set manually.

---

## Step 4 — Assign Priority Tier

Priority tier determines **how urgently AE_13 should act** on the re-engagement date derived in Filter 1.
The urgency band is advisory — it does not change the re-engagement date calculation.
The re-engagement date is always set by Internal/External timeline logic in Filter 1.

### Tier Assignment

| Tier | Score Band | Urgency Band | Advisory Action |
|------|-----------|--------------|-----------------|
| 🔥 HIGH | 85–100 | Immediate | Re-engage within 1–2 business days of re-engagement date |
| 🔥 HIGH | 78–84 | This week | Re-engage within the same business week as re-engagement date |
| 🔥 HIGH | 70–77 | This month | Re-engage within the calendar month of re-engagement date |
| ⚡ MEDIUM | 60–69 | Next month | Re-engage the month following re-engagement date |
| ⚡ MEDIUM | 45–59 | This quarter | Re-engage within the same quarter as re-engagement date |
| 📋 LOW | 35–44 | Next quarter | Re-engage the following quarter from re-engagement date |
| 📋 LOW | 25–34 | 6 months | Re-engage approximately 6 months from re-engagement date |
| 🗄 ARCHIVE | Below 25 | Do not pursue | No outreach unless AE_13 explicitly overrides |

### How to write the tier in output

```
TOTAL: [X] / 100 | TIER: 🔥 HIGH (Score [X] — re-engage within [urgency band])
```

Example: `TOTAL: 82 / 100 | TIER: 🔥 HIGH (Score 82 — re-engage this week)`

- Scores of exactly 45, 70 — apply the tier as defined. Note as borderline.
- Urgency band is advisory. AE_13 may accelerate or defer based on her read of the account.

---

## Step 5 — Write Output Per Deal

Produce this block for every deal. No deal is skipped silently.

Every scored deal must include all three mandatory output sections — Conversation Signal Summary,
Key Problem Identified, and Recommended Next Step. None of the three can be omitted or merged.
These are the sections AE_13 reads — everything else in the block is scoring infrastructure.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEAL: [Deal Name] | COMPANY: [Company Name]
RECORD ID: [HubSpot ID] | HS LINK: [URL]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATA PULL COMPLETE:
✅ Deal page — [stage, amount, close date]
✅ Company page — [other deals: Y/N | account notes: Y/N]
✅ Contacts — [name, title — or "No contacts associated"]
✅ Calls — [count, last call date — or "No calls logged"]
✅ Emails — [count, last email date — or "No emails found"]
✅ Notes — [count — or "No notes found"]

PRE-SCORING CHECKS:
Stop Request: [None found / DO NOT CONTACT]
Active Deal at Same Company: [None found / FLAGGED]
Empuls Gifting: [No / PURSUE WITH CAUTION]

--- CLASSIFICATION ---
Drop Reason: [Internal / External / Data Missing / Data Vague]
Confidence: [Confirmed / Flag]
Evidence: [Reference to specific note/call/email/field — date and source only]
Data Vague Quote (if applicable): "[Exact text as written in HubSpot]"
Competitor(s): [Name(s) / Not named]
Competitor Assumption: [Standard 12-month / Duration from notes: X months]

SCORES:
Filter 1 — Drop Reason Classification:        [X] / 25 — [one-line evidence]
Filter 2 — Deepest Stage Reached:             [X] / 25 — [one-line evidence]
Filter 3 — Recency of Last Meaningful Activity:[X] / 20 — [date + source]
Filter 4 — Deal Amount (₹):                   [X] / 20 — [amount + field reference]
Filter 5 — Contact Quality:                   [X] / 10 — [Authority × ICP = raw, scaled to /10]
──────────────────────────────────────────────
Score check: [F1] + [F2] + [F3] + [F4] + [F5] = [Total] ✓
TOTAL: [X] / 100 | TIER: [🔥 HIGH / ⚡ MEDIUM / 📋 LOW / 🗄 ARCHIVE]

CONVERSATION SIGNAL SUMMARY:
[2–4 lines. Factual read of what happened in this deal — tone, direction, key exchanges, how it ended. Not an interpretation. What the data actually shows. No filler.]

KEY PROBLEM IDENTIFIED:
[One line. The single clearest reason this deal closed lost.]
[If Multi-AE flag applies: "Multi-AE conflict — [Other AE Name] owns a deal at this company. Coordinate before outreach."]

RECOMMENDED NEXT STEP:
[ACTION] · [Re-engagement date: Month Year / BLANK] · AE_13
Re: [One hook — the specific thing to reference from the conversation]
POC: [Name] ([Title]) — [Decision maker / Champion / Unknown]
Timeline basis: [Signal-based / Default 6 months / Pre-renewal window / BLANK — AE to set]
⚠ [Caution flag if applicable — include Multi-AE coordination note here if flagged]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 6 — Batch Completion Block

After all deals are processed, produce this summary:

```
--- CLOSED LOST BATCH SUMMARY ---
Deals fetched: [N]
Excluded — Wrong deal stage: [count — list deal names and actual stages]
Excluded — Superseded by Closed/Signed deal: [count — list deal names]
Flagged — Multi-AE same company: [count — list deal names]
Deals scored: [count]

🔥 HIGH: [count]
⚡ MEDIUM: [count]
📋 LOW: [count]
🗄 ARCHIVE: [count]
Data Missing flags: [count — list deal names]
Data Vague flags: [count — list deal names]
DO NOT CONTACT flags: [count — list deal names]
Active Deal Exists flags: [count — list deal names]
Score verification: All [N] deals passed ✓ / [N] deals failed — see above
--- END BATCH ---
```

---

## Step 7 — Final Validation

Before delivering any output, confirm:

- [ ] All three query filters applied at HubSpot fetch level: `dealstage = 900000056` AND `createdate > 2024-12-02` AND `hubspot_owner_id = 900000113`
- [ ] Post-pull stage verification done on every record
- [ ] All 6 data sources pulled simultaneously for every deal
- [ ] Every score cites a specific HubSpot data point
- [ ] Five filter scores sum to the stated total for each deal
- [ ] Pre-scoring exclusions written visibly before scoring block — Closed Lost Record ID and Superseding Record ID both stated explicitly
- [ ] Every scored deal has a complete output block including Next Step
- [ ] Re-engagement dates derived from correct logic for Internal vs External
- [ ] Competitor field populated on every deal (named or "Not named")
- [ ] Intent signals are deal-specific — not carried across deals
- [ ] DO NOT CONTACT flags are not overridden by score
- [ ] Multi-AE flagged deals: AE_13's deal is scored, conflict flagged in Key Problems Identified and Recommended Next Step
- [ ] Priority tier urgency band stated in output alongside tier label

Any failed check → fix before output. Do not deliver a batch with known errors.

---

## Edge Cases

- **No data returned for any source:** Flag it. Score what is available. Never stop scoring.
- **Deal amount blank:** Filter 4 = 0. Note: "Deal amount not populated in HubSpot."
- **Contact title blank:** Do not infer seniority. Score Contact Quality lower. Note the gap.
- **Activity only in WhatsApp/Teams notes:** Note "Activity referenced in notes but not logged in CRM — verify with AE." Do not count for recency scoring.
- **Score exactly 45 or 70:** Apply the tier as defined. Note as borderline.
- **Same company, different AE:** Score independently. Add caution note. No duplicate rule applies.
