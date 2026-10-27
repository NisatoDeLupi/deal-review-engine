---
name: deal-review-closed-lost
compatibility: Requires HubSpot MCP connector to be active. Will not function without it.
description: >
  Closed Lost segment of the deal-review family. Use when the user asks to score closed lost
  deals, classify closed lost drop reasons, run the closed lost revival batch, or identify which
  closed lost deals are worth re-engaging. Triggered by "run closed lost", "score these closed
  lost deals", "classify closed lost", "closed lost batch", "which closed lost deals should we
  revive", "revive lost deals", "stage 9", or "process closed lost". Produces a scored Excel
  workbook AND (on confirmation) writes a revival note + re-engagement task back onto every deal.
  DISAMBIGUATION — this skill is ONLY for deals at dealstage 900000056 (Stage 9 — Closed Lost).
  If the deals are Dormant (stage 8) use deal-review-dormant. If the company has no deal object
  use deal-review-contact. If the deals are open pipeline use deal-review-active.
  For the direct-sales (hunting) pipeline; AE + Owner ID set per run in Run Configuration.
---

# Deal Review — Closed Lost Revival

Closed Lost segment of the deal-review family. Fetch all Closed Lost deals in the active scoring
window, score each out of 100 across 5 filters, assign a priority tier, and produce **two
deliverables in one pass**:

1. An **Excel workbook** — scorecard + one row per deal + filtered action sheets.
2. **HubSpot writeback** (on confirmation) — a revival note + a re-engagement task on every scored deal.

This mirrors the `deal-review-active` (main pipeline) workflow: confirm scope → executable pull →
score → Excel → writeback → verify.

This skill has two reference files. Read them when directed:
- `references/scoring-rubric.md` — exact scoring brackets for Filters 2–5 + Contact Quality / ICP definitions
- `references/data-pull-methodology.md` — executable three-step data pull protocol + drop reason classification

---

## Run Configuration — Set Before Every Run

This skill is org-usable. Nothing about a specific AE is hardcoded in the logic — set the run's
identity here and the rest of the skill reads from it. Confirm these with the user before pulling.

| Setting | Value (set per run) |
|---------|---------------------|
| AE in scope (`<AE>`) | _your AE's name_ |
| Owner ID (`<owner_id>`) | _your AE's HubSpot owner ID_ |
| Pipeline | Direct Sales — Hunting (adjust if your org differs) |
| Segment stage ID | `900000056 (Stage 9 — Closed Lost)` — fixed for this segment (org-level constant) |
| Create-date window start | `2024-12-02` (default; change per program) |
| Writeback mention owner | same as Owner ID above |

Wherever the skill says `<owner_id>`, `<AE>`, or "the AE in scope", substitute the values above.
Stage IDs are org-level HubSpot constants shared across every AE — they are not per-run.

---

## Scope — Read This Before Anything Else

Built for the configured direct-sales (hunting) pipeline — set the AE and Owner ID in Run Configuration. Does not apply to:
- CAM or farming deals
- Cross-sell, upsell, renewal, or expansion opportunities
- Any deal outside the direct sales pipeline

Empuls Gifting deals are scored normally. Flag as `PURSUE WITH CAUTION — Empuls Gifting. Verify product fit before outreach.` Carry this flag through to the output and Recommended Next Step.

---

## Step 0 — Inputs to Confirm Before Starting

Owner, stage, and date are fixed for this segment (below), but confirm these before pulling — same as the main skill's confirm step:

1. **Batch size** — score the full active window, or a capped subset this run?
2. **Writeback** — after the Excel is reviewed, should notes + re-engagement tasks be posted to HubSpot, or is this a read-only scoring run? (Default: build Excel, then confirm again before any writeback.)
3. **Test first** — post 1–2 deals as a test before the full writeback batch. (Default: yes.)

If a previous run is in context, reuse its answers and just confirm changes.

---

## HubSpot Query — Apply Exactly Before Pulling Any Deals

Filter on **all three** conditions together at the query level using these exact HubSpot property names and values:

```
dealstage = 900000056
createdate > <window_start>            # Run Configuration — default 2024-12-02
hubspot_owner_id = <owner_id>          # Run Configuration — the AE being scored
```

Do not substitute label strings (e.g. `closedlost`) for the numeric stage ID — label strings are unreliable across pipelines.
Do not substitute any other date field (e.g. `notes_last_updated`, `hs_lastmodifieddate`, `hs_last_activity_date`) for `createdate` — these measure different things and will return wrong deal sets.
Do not drop the `hubspot_owner_id` filter — this system scores the AE's pipeline only.

Applying all conditions at query time limits the pull to the active scoring window only.
Do not pull all Closed Lost deals and filter afterward — this wastes tokens and API calls.

Use `search_crm_objects` for the pull (see `references/data-pull-methodology.md` for exact tool syntax).

**Stage ID Reference — Direct Sales Pipeline:**

| Stage ID | Label | Action |
|----------|-------|--------|
| `900000056` | 9 — Closed Lost | ✅ Score these |
| `900000070` | 8 — Dormant | ❌ Exclude — route to deal-review-dormant |
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

- Different AEs own deals at the same company → **score the AE's deal** but flag the conflict visibly. Do not hold the AE's deal pending the other AE's resolution — the other AE may be inactive and unaware. Surface the conflict in Key Problems Identified and Recommended Next Step so it can be coordinated.

```
FLAGGED — MULTI-AE SAME COMPANY
In-scope AE's deal: [Deal Name] | Record ID: [ID]
Company: [Company Name]
Other AE's deal: [Deal Name] | Record ID: [ID] | Owner: [Other AE Name] | Stage: [Stage Label]
Action required: Flag to the AE — coordinate with [Other AE Name] before any outreach to avoid clash. Other AE may be unaware of this deal. Do not hold scoring pending coordination.
```
The in-scope AE's deal proceeds to scoring. The conflict flag carries through to Key Problems Identified and Recommended Next Step.

- Two deals, same company name, different company records → apply steps above across both, then flag:
`DUPLICATE COMPANY RECORDS — same name found twice. Recommend merging.`

---

## Step 1 — Pull All Data Sources Simultaneously

Read `references/data-pull-methodology.md` for the full executable pull and drop reason classification protocol.

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
Cannot be overridden by score. **No re-engagement task is written back for these deals** (note only).

**Check B — Active Deal at Same Company:**
If HubSpot shows a non-closed, non-dormant deal at the same company →
flag: `ACTIVE DEAL EXISTS — coordinate with deal owner before any outreach.`

Proceed to Step 3 only after checks are written visibly.

---

## Step 3 — Score Across 5 Filters

Read `references/scoring-rubric.md` for exact brackets and evidence requirements.

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
For the full procedure, read `references/data-pull-methodology.md`.

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
Re-engagement date: BLANK — AE must set manually. **No re-engagement task written back** (note only).

**DATA VAGUE — 10 pts (hold)**
Activity exists but drop reason cannot be determined. Quote the found content exactly. Do not interpret.
Flag: `DATA VAGUE — [exact quote]. Meaning unclear. Manual review needed.`
Re-engagement date: BLANK — AE must set manually. **No re-engagement task written back** (note only).

---

## Step 4 — Assign Priority Tier

Priority tier determines **how urgently the AE should act** on the re-engagement date derived in Filter 1.
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
| 🗄 ARCHIVE | Below 25 | Do not pursue | No outreach unless the AE explicitly overrides |

### How to write the tier in output

```
TOTAL: [X] / 100 | TIER: 🔥 HIGH (Score [X] — re-engage within [urgency band])
```

Example: `TOTAL: 82 / 100 | TIER: 🔥 HIGH (Score 82 — re-engage this week)`

- Scores of exactly 45, 70 — apply the tier as defined. Note as borderline.
- Urgency band is advisory. the AE may accelerate or defer based on their read of the account.

---

## Step 5 — Write Output Per Deal

Produce this block for every deal. No deal is skipped silently.

Every scored deal must include all three mandatory output sections — Conversation Signal Summary,
Key Problem Identified, and Recommended Next Step. None of the three can be omitted or merged.
These are the sections the AE reads — everything else in the block is scoring infrastructure.
They also become the three narrative columns in the Excel (Step 7) and the body of the HubSpot note (Step 8).

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
[ACTION] · [Re-engagement date: Month Year / BLANK] · <AE>
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

## Step 7 — Build the Excel Workbook

Use the bundled generator `scripts/generate_excel.py` — the shared, tested builder for the deal-based
scorers (closed-lost and dormant). Do not hand-roll the workbook; assemble the JSON payload and
invoke the script:

```
python scripts/generate_excel.py '<json_payload>' Closed_Lost_Revival_<N>_Deals.xlsx
```

It produces a 3-sheet workbook: **Scoring Methodology**, **Scored Deals** (one row per deal, banner
+ frozen header, colour-coded tiers), and **Summary & Flags**.

Assemble the payload from the per-deal blocks (Step 5). Schema (see the docstring at the top of
`scripts/generate_excel.py` for the full field list):

```
{
  "meta":  { "owner", "pipeline", "date", "total_deals" },
  "deals": [ { rank, deal_name, record_id, hs_link, amount, drop_reason_field,
               filter1_score, classification, classification_confidence, competitor,
               deepest_stage, filter2_score, last_meaningful_activity, filter3_score,
               filter4_score, associated_contacts, filter5_score, total_score,
               priority_tier, re_engagement_date, timeline_basis, recommended_next_step,
               key_concerns, evidence_reference, data_flag, contact_person,
               conversation_signal_summary } ],
  "excluded": [ { deal_name, record_id, reason } ],
  "flagged":  [ { deal_name, record_id, reason } ]
}
```

The five `filterN_score` fields map 1:1 to the SKILL.md scores; `total_score` must equal their sum.
Put DO NOT CONTACT / Data Missing / Data Vague / Active-Deal notes in `data_flag`, and Multi-AE /
superseded records in `flagged` / `excluded`. Present the workbook to the user before any writeback.

---

## Step 8 — Write Back to HubSpot (on confirmation)

Only run this step after the user has reviewed the Excel and confirmed writeback (Step 0). Same
mechanics and guardrails as the `deal-review-active` main skill.

**Per scored deal, create up to two records:**

1. **Revival note** on the deal — always. Body = Conversation Signal Summary + Key Problem + Recommended Next Step + score/tier line. Tagged to the AE in scope using HubSpot's `<span data-mention-id="<owner_id>">` syntax — NOT plain `@`. No emojis in the note (strip tier emoji; write "HIGH"/"MEDIUM"/etc.).
2. **Re-engagement task** — only when a re-engagement date exists. Owner = the AE in scope (`<owner_id>`). `hs_timestamp` = the re-engagement date from Filter 1. `hs_task_subject` = `Re-engage (Closed Lost): <Deal Name> — <Tier>`. `hs_task_body` = the Recommended Next Step verbatim (action + hook + POC). `hs_task_priority` from tier (HIGH→HIGH, MEDIUM→MEDIUM, LOW→LOW).

**Do NOT create a re-engagement task** for: DO NOT CONTACT, Data Missing, Data Vague, or 🗄 ARCHIVE deals. Post the note only (for ARCHIVE, note records the decision; DO NOT CONTACT note records the client request).

**Guardrails (identical to the main skill):**
- `manage_crm_objects` is hard-capped at **10 objects per batch**. Plan batches accordingly.
- **Test 1–2 deals first** unless the user said run all — confirm the note renders and the mention tags before bulk.
- Mentions only work via `<span data-mention-id="...">`, never plain text `@Name`.
- No emojis in notes or tasks.
- Sequence batches by tier: HIGH → MEDIUM → LOW → ARCHIVE. Post note + task for a deal together so an interruption leaves whole deals complete.

Every batch should return `successful: N, failed: 0`. Track running totals.

---

## Step 9 — Final Validation

Before delivering any output, confirm:

- [ ] All three query filters applied at HubSpot fetch level: `dealstage = 900000056` AND `createdate > 2024-12-02` AND `hubspot_owner_id = <owner_id>          # Run Configuration — the AE being scored`
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
- [ ] Multi-AE flagged deals: the AE's deal is scored, conflict flagged in Key Problems Identified and Recommended Next Step
- [ ] Priority tier urgency band stated in output alongside tier label
- [ ] Excel workbook built via `scripts/generate_excel.py` (3 sheets); `total_score` equals sum of the five filter scores for every deal
- [ ] Writeback (if run): no re-engagement task created for DO NOT CONTACT / Data Missing / Data Vague / ARCHIVE; every batch returned failed: 0; mentions tagged correctly

Any failed check → fix before output. Do not deliver a batch with known errors.

---

## Output Deliverables

Every run produces:
1. **Excel workbook** — `Closed_Lost_Revival_<N>_Deals.xlsx` (3 sheets, via `scripts/generate_excel.py`)
2. **Run summary** — batch completion block (tier counts, exclusions, flags, score verification)
3. **HubSpot writeback (on confirmation)** — one revival note per scored deal + one re-engagement task per deal that has a re-engagement date

---

## Reference Files

Read these when you reach the relevant step:
- `references/data-pull-methodology.md` — executable pull mechanics + drop reason classification. Read at Step 1 / Filter 1.
- `references/scoring-rubric.md` — Filters 2–5 brackets + ICP definitions + Excel column mapping. Read at Step 3.
- `scripts/generate_excel.py` — bundled 3-sheet workbook generator (shared with deal-review-dormant). Invoke at Step 7.

---

## Edge Cases

- **No data returned for any source:** Flag it. Score what is available. Never stop scoring.
- **Deal amount blank:** Filter 4 = 0. Note: "Deal amount not populated in HubSpot."
- **Contact title blank:** Do not infer seniority. Score Contact Quality lower. Note the gap.
- **Activity only in WhatsApp/Teams notes:** Note "Activity referenced in notes but not logged in CRM — verify with AE." Do not count for recency scoring.
- **Score exactly 45 or 70:** Apply the tier as defined. Note as borderline.
- **Same company, different AE:** Score independently. Add caution note. No duplicate rule applies.
