---
name: deal-review-dormant
compatibility: Requires HubSpot MCP connector to be active. Will not function without it.
description: >
  Dormant (passive pipeline) segment of the deal-review family. Use when the user asks to score
  dormant deals, run the dormant revival, prioritise the passive pipeline, rank dormant deals, or
  decide which dormant deals to contact first. Triggered by "score dormant deals", "run the dormant
  revival", "rank dormant deals", "passive pipeline", "stage 8", "which dormant deals to
  contact", or "process the dormant batch". Produces a scored Excel workbook AND (on confirmation)
  writes a revival note + re-engagement task back onto every deal.
  DISAMBIGUATION — this skill is ONLY for deals at dealstage 900000070 (Stage 8 — Dormant). If the
  deals are Closed Lost (stage 9) use deal-review-closed-lost. If the company has no deal object use
  deal-review-contact. If the deals are open pipeline use deal-review-active.
  For the direct-sales (hunting) pipeline; AE + Owner ID set per run in Run Configuration.
---

# Deal Review — Dormant Revival

Dormant segment of the deal-review family. Score dormant deals out of 100 across 6 filters, assign
a priority tier (HIGH / MEDIUM / LOW), and produce **two deliverables in one pass**:

1. An **Excel workbook** — scoring methodology + one row per deal + summary/flags.
2. **HubSpot writeback** (on confirmation) — a revival note + a re-engagement task on every scored deal.

This mirrors the `deal-review-active` main workflow: confirm scope → executable pull → score →
Excel → writeback → verify.

This skill has two reference files. Read them when directed:
- `references/scoring-rubric.md` — exact scoring brackets for all 6 filters + intent signal classification
- `references/data-pull-methodology.md` — executable pull mechanics + dormant drop reason classification

---

## Run Configuration — Set Before Every Run

This skill is org-usable. Nothing about a specific AE is hardcoded in the logic — set the run's
identity here and the rest of the skill reads from it. Confirm these with the user before pulling.

| Setting | Value (set per run) |
|---------|---------------------|
| AE in scope (`<AE>`) | _your AE's name_ |
| Owner ID (`<owner_id>`) | _your AE's HubSpot owner ID_ |
| Pipeline | Direct Sales — Hunting (adjust if your org differs) |
| Segment stage ID | `900000070 (Stage 8 — Dormant)` — fixed for this segment (org-level constant) |
| Create-date window start | `2024-12-02` (default; change per program) |
| Writeback mention owner | same as Owner ID above |

Wherever the skill says `<owner_id>`, `<AE>`, or "the AE in scope", substitute the values above.
Stage IDs are org-level HubSpot constants shared across every AE — they are not per-run.

---

## Scope — Read This Before Anything Else

Built for the configured direct-sales (hunting) pipeline — set the AE and Owner ID in Run Configuration. Does not apply to:
- CAM or farming deals
- Cross-sell or upsell opportunities
- Any deal owned outside the configured AE's direct sales pipeline

---

## Step 0 — Inputs to Confirm Before Starting

Owner, stage, and date are fixed for this segment, but confirm before pulling:

1. **Batch size** — score the full dormant window (~20 deals), or a capped subset?
2. **Writeback** — after the Excel is reviewed, post notes + re-engagement tasks to HubSpot, or read-only? (Default: build Excel, confirm again before writeback.)
3. **Test first** — post 1–2 deals as a test before the full writeback batch. (Default: yes.)

If a previous run is in context, reuse its answers and confirm only changes.

---

## HubSpot Query — Apply Exactly Before Pulling Any Deals

Filter on **both** conditions together (see `references/data-pull-methodology.md` for exact tool syntax):

- `dealstage = 900000070` (Stage 8 — Dormant)
- `createdate > 2024-12-02`

This returns the active dormant deal set (~20 deals). Do not use any other filter.
Do not use `hs_is_closed_lost = true` alone — it returns both Dormant and Closed Lost
and will corrupt the batch.

**Stage ID Reference — Direct Sales - Passive Pipeline:**

| Stage ID | Label | Action |
|----------|-------|--------|
| `900000070` | 8 — Dormant | ✅ Score these |
| `900000056` | 9 — Closed Lost | ❌ Exclude — route to deal-review-closed-lost |
| `9000000002` | 6 — Confirmed & Signed | ❌ Exclude |
| `9000000001` | 7 — Closed Won | ❌ Exclude |

**Post-pull verification:** Check `dealstage` on every record after fetching.
If any record shows a stage other than `900000070`:
`EXCLUDED — dealstage [ID] is not Stage 8 Dormant. Remove from batch.`
Do not score excluded deals under any circumstances.

---

## Pre-Scoring Exclusions

Write a visible exclusion block before scoring begins. List every excluded deal and
the exact reason. Never silently skip a deal.

1. **Date filter:** Create Date on or before the window start (default 02 Dec 2024) →
   `EXCLUDED — Create Date on or before the window start (default 02 Dec 2024). Outside scoring window.`

2. **Same AE, same company, active deal exists:** If the AE owns another deal at the
   same company at stage Confirmed & Signed (`9000000002`) or Closed Won (`9000000001`) →
   `DUPLICATE — ACTIVE DEAL EXISTS (same AE, same company). Exclude from scoring.`
   Do not delete — flag only.
   If the other deal belongs to a **different AE**: score the AE's deal independently
   and add a caution note in the Recommended Next Step.

3. **Empuls Gifting:** Do not exclude. Flag as:
   `PURSUE WITH CAUTION — Empuls Gifting. Verify product fit before outreach.`
   Score normally. Carry this flag through to the output.

---

## Step 1 — Pull All Data Sources Simultaneously

Read `references/data-pull-methodology.md` for the full executable pull and drop reason classification protocol.

Pull ALL sources at the same time for every deal — no gates, no conditionals, no
cascades. Data unhygiene is the default reality: AEs log activity inconsistently
across deal, company, and contact records. Pulling everything simultaneously is
the only way to get a complete picture. Missing data on one source never stops
the pull or the scoring elsewhere.

Pull simultaneously:
1. **Deal page** — stage, amount, close date, owner, drop reason field
2. **Company page** — company-level notes, all deals at this company (stages + owners),
   account-level context that may not appear on the deal record
3. **Contact record(s)** — name, title, authority level, lead status, contact-level notes
4. **Call logs** — date, duration, content of notes
5. **Email history** — sent/received, dates, substantive content
6. **AE notes** — all manually written entries on the deal record

Write a visible checkpoint after pulling. A visible checkpoint is a mandatory
written line per source confirming what was found or explicitly stating what was
missing. Silent skips are scoring errors.

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
Do not score. Cannot be overridden. **No re-engagement task written back** (note only, if any).

**Check B — Active Deal at Same Company (same AE):**
If the AE owns another deal at this company at Confirmed & Signed or Closed Won →
`DUPLICATE — ACTIVE DEAL EXISTS` — stop scoring.
If the other deal is open/active → note as context, continue scoring.
If owned by a different AE → score independently, add caution note to output.

**Check C — Empuls Gifting:**
Carry the `PURSUE WITH CAUTION` flag into the output. Score normally.

Proceed to Step 3 only if Checks A and B are clear.

---

## Step 3 — Score Across 6 Filters

Read `references/scoring-rubric.md` for exact brackets and evidence requirements.

Total score is out of 100. Every score must cite a specific HubSpot data point.
Never infer or guess.

| Filter | Max | What it measures |
|--------|-----|-----------------|
| 1. Dormant Deal Drop Reason | 20 | Why did this deal go dormant? Timing/internal = higher. Fit rejection = lower. |
| 2. Deepest Stage Reached | 20 | How far did the deal progress before going dormant? |
| 3. Recency of Last Meaningful Activity | 15 | How recent was the last substantive touchpoint? |
| 4. Deal Amount (₹) | 15 | Is this deal worth the AE's time? |
| 5. Intent Signal | 20 | What did the client actually say or signal? See `references/scoring-rubric.md` for the 3-level classification. |
| 6. Contact Quality | 10 | Right person? Authority level × ICP match. |

After scoring all six filters, verify the six scores sum to the stated total.
Mismatch = recheck before proceeding. Non-negotiable.

---

## Step 4 — Assign Priority Tier

| Tier | Score | Meaning |
|------|-------|---------|
| 🔥 HIGH | 70–100 | Strong revival signal. AE acts now. |
| ⚡ MEDIUM | 25–69 | Real potential but not immediate. Plan for later. |
| 🗄 LOW | Below 25 | No revival value. Archive. |

**HIGH — pick exactly one timeline:**
- Score 85–100 AND recency within 3 months → **Within 2 business days**
- Score 70–84 OR recency 3–6 months → **This month**
- Score 70+ AND recency 6+ months → **This quarter**

**MEDIUM — pick exactly one timeline:**
- Recency within 6 months → **Next quarter**
- Recency 6+ months → **Next financial year**

**LOW:** Archive in HubSpot. Mark as reviewed. Not deleted — decision is deliberate
and visible to AE and manager.

The chosen timeline becomes the re-engagement task due date at writeback (Step 8).

---

## Step 5 — Write the Three Mandatory Output Sections

Every scored deal gets all three. No exceptions. These become the three narrative columns
in the Excel (Step 7) and the body of the HubSpot note (Step 8).

### Section 1 — Conversation Signal Summary

Factual read of what happened in this deal. Tone, direction, key exchanges.
Not an interpretation — what the data actually shows. 2–4 lines maximum. Plain language.

```
CONVERSATION SIGNAL SUMMARY:
[What happened. When. What was exchanged. How it ended.]
```

### Section 2 — Key Problem Identified

Single clearest reason the deal went dormant. One line. No hedging.

```
KEY PROBLEM IDENTIFIED:
[One line.]
```

Choose from or write a tighter equivalent: No response after proposal · Budget frozen /
internal priority shift · Champion left the company · Competitor selected · Product fit
mismatch · Pricing objection — no resolution · Tech/integration delay (internal) ·
Disqualified — wrong ICP · Data missing — cannot determine.

### Section 3 — Recommended Next Step

Scannable in 3 seconds. Keywords first, context second. Tier-based.

```
RECOMMENDED NEXT STEP:
[ACTION] · [TIMELINE] · [OWNER]
Re: [One hook — the specific thing to reference]
POC: [Name] ([Title]) — [Decision maker / Champion / Unknown]
⚠ [Caution flag if applicable]
```

🔥 HIGH → `CALL · [Within 2 business days / This month / This quarter] · <AE>`
⚡ MEDIUM → `HOLD · [Next quarter / Next financial year] · <AE>` + `Trigger: [what moves this to HIGH]`
🗄 LOW → `ARCHIVE · This week · the AE — No revival signal. Mark as reviewed. Do not pursue.`

Flagged deals (Stop Request, Duplicate) → flag label only, no next step.
Empuls Gifting → include next step with the PURSUE WITH CAUTION flag visible.

**Different-AE caution (add when applicable):**
```
⚠ ACTIVE DEAL AT SAME COMPANY — owned by [AE name].
Coordinate before outreach. Check associated contacts for overlap.
```

---

## Step 6 — Re-Rank the Full Batch

After all deals are scored, produce a ranked table sorted by score descending. the AE's working order.

```
Rank | Deal Name | Company | Score | Tier      | Timeline
-----|-----------|---------|-------|-----------|-------------------
1    | [Name]    | [Co]    | 87    | 🔥 HIGH   | Within 2 business days
```

Flagged/excluded deals go at the bottom, flag label in the Tier column. Do not mix into the ranking.

---

## Step 7 — Build the Excel Workbook

Read `/mnt/skills/public/xlsx/SKILL.md` (the `xlsx` skill) first, then build the workbook.
File name: `Dormant_Revival_<N>_Deals.xlsx` in the outputs folder. Professional font (Arial),
one row per deal, wrapped narrative cells, frozen header, banner row.

(Note: dormant scores **6** filters and ships no bundled generator — build via the xlsx skill
with the columns below. The 5-filter `generate_excel.py` belongs to deal-review-closed-lost.)

Three sheets, mirroring the deal-review family layout:

**Sheet 1 — Scoring Methodology** — the 6-filter rubric + tier bands, for reviewer reference.

**Sheet 2 — Scored Deals** (one row per deal). Columns:
`Rank | Deal Name | Company | Amount (₹) | Drop Reason (Int/Ext) | Competitor(s) |
F1 Drop /20 | F2 Stage /20 | F3 Recency /15 | F4 Amount /15 | F5 Intent /20 | F6 Contact /10 |
TOTAL /100 | Tier | Timeline | Months Dormant | Conversation Signal Summary |
Key Problem Identified | Recommended Next Step | POC (Name/Title) | Data Flag | HS Link`

The six filter columns map 1:1 to the SKILL.md scores; TOTAL must equal their sum. Colour-code
the Tier column: HIGH green (`C6EFCE`), MEDIUM amber (`FFEB9C`), LOW grey (`D9D9D9`).

**Sheet 3 — Summary & Flags** — tier distribution, exclusion counts, and every deal carrying a
DO NOT CONTACT / Duplicate / Data Missing / Data Vague / Multi-AE flag with the recommended action.

Present the workbook to the user before any writeback.

---

## Step 8 — Write Back to HubSpot (on confirmation)

Only run after the user reviewed the Excel and confirmed writeback (Step 0). Same mechanics and
guardrails as the `deal-review-active` main skill.

**Per scored deal, create up to two records:**

1. **Revival note** on the deal — always. Body = Conversation Signal Summary + Key Problem + Recommended Next Step + score/tier line. Tagged to the AE in scope using `<span data-mention-id="<owner_id>">` — NOT plain `@`. No emojis (write "HIGH"/"MEDIUM"/"LOW", not the emoji).
2. **Re-engagement task** — for HIGH and MEDIUM only. Owner = the AE in scope (`<owner_id>`). `hs_timestamp` = due date derived from the Step 4 timeline (Within 2 business days / This month / This quarter / Next quarter / Next financial year), computed in **business days** from posting where the band is day-based. `hs_task_subject` = `Re-engage (Dormant): <Deal Name> — <Tier>`. `hs_task_body` = the Recommended Next Step verbatim. `hs_task_priority` from tier.

**Do NOT create a re-engagement task** for: 🗄 LOW (archive — note records the decision), DO NOT CONTACT, Duplicate, Data Missing, or Data Vague deals. Post the note only.

**Guardrails (identical to the main skill):**
- `manage_crm_objects` hard-capped at **10 objects per batch**. Plan batches accordingly.
- **Test 1–2 deals first** unless the user said run all.
- Mentions only work via `<span data-mention-id="...">`, never plain text.
- No emojis in notes or tasks.
- Sequence batches by tier: HIGH → MEDIUM → LOW. Post note + task for a deal together.

Every batch should return `successful: N, failed: 0`. Track running totals.

---

## Step 9 — Final Validation

Before delivering any output, confirm:

- [ ] `dealstage = 900000070` was the only stage pulled; Create Date filter was after the window start (default 02 Dec 2024)
- [ ] Confirmed & Signed and Closed Won were excluded
- [ ] All 6 sources were pulled simultaneously for every deal (email/call residual pass done)
- [ ] Every score cites a specific HubSpot data point
- [ ] Six filter scores sum to the stated total for each deal
- [ ] Pre-scoring exclusions written visibly before scoring block
- [ ] Every scored deal has all 3 mandatory output sections
- [ ] HIGH and MEDIUM timelines chosen from approved lists only
- [ ] Intent signals are deal-specific — not carried across deals
- [ ] Same-company different-AE deals scored independently with caution note
- [ ] Excel workbook built (3 sheets); TOTAL column equals sum of the six filter columns per row
- [ ] Writeback (if run): no re-engagement task for LOW / DO NOT CONTACT / Duplicate / Data flags; every batch returned failed: 0; mentions tagged correctly

Any failed check → fix before output. Do not deliver a batch with known errors.

---

## Output Deliverables

Every run produces:
1. **Excel workbook** — `Dormant_Revival_<N>_Deals.xlsx` (3 sheets)
2. **Run summary** — ranked table + tier counts + exclusions + confidence flags
3. **HubSpot writeback (on confirmation)** — one revival note per scored deal + one re-engagement task per HIGH/MEDIUM deal

---

## Reference Files

- `references/data-pull-methodology.md` — executable pull mechanics + drop reason + intent classification. Read at Step 1.
- `references/scoring-rubric.md` — all 6 filter brackets + ICP definitions. Read at Step 3.
- `xlsx` skill (`/mnt/skills/public/xlsx/SKILL.md`) — read at Step 7 before building the workbook.

---

## Output Format — Full Deal Block

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEAL: [Deal Name] | COMPANY: [Company Name]
RECORD ID: [HubSpot ID] | AE: the AE in scope
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATA PULL COMPLETE:
✅ Deal page — [stage, amount, close date]
✅ Company page — [other deals: Y/N | account notes: Y/N]
✅ Contacts — [name, title]
✅ Calls — [count, last call date]
✅ Emails — [count, last email date]
✅ Notes — [count, signal noted or "none"]

PRE-SCORING CHECKS:
Stop Request: [None found / FLAGGED]
Duplicate Deal: [None found / FLAGGED]
Empuls Gifting: [No / PURSUE WITH CAUTION]

SCORES:
Dormant Deal Drop Reason:            [X]/20 — [one-line evidence]
Deepest Stage Reached:               [X]/20 — [one-line evidence]
Recency of Last Meaningful Activity: [X]/15 — [one-line evidence]
Deal Amount (₹):                     [X]/15 — [one-line evidence]
Intent Signal:                       [X]/20 — [Level + one-line evidence]
Contact Quality:                     [X]/10 — [Authority × ICP = raw, scaled to /10]
─────────────────────────────────────
TOTAL: [X]/100 | TIER: [🔥 HIGH / ⚡ MEDIUM / 🗄 LOW]

CONVERSATION SIGNAL SUMMARY:
[2–4 lines. Factual. What happened in this deal.]

KEY PROBLEM IDENTIFIED:
[One line.]

RECOMMENDED NEXT STEP:
[ACTION] · [TIMELINE] · [OWNER]
Re: [Hook]
POC: [Name] ([Title]) — [authority note]
⚠ [Caution flag if applicable]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Edge Cases

- **No data returned for any source:** Flag it. Score what is available. Never stop scoring.
- **Deal amount blank:** Filter 4 = 0. Note: "Deal amount not populated in HubSpot."
- **Contact title blank:** Do not infer seniority. Score Contact Quality lower. Note the gap.
- **Activity only in WhatsApp/Teams notes:** Note "Activity referenced in notes but not
  logged in CRM — verify with AE." Do not count for recency scoring.
- **Score exactly 25 or 70:** Apply the tier as defined. Note as borderline in Confidence Flags.
- **Same company, different AE:** Score independently. Add caution note. No duplicate rule.

---

## Confidence Flags

After the ranked table, flag any deal where: data was ambiguous or a judgment call was made;
score is within 2 points of a tier boundary; activity was referenced outside CRM; any source
returned no data; or the Empuls Gifting flag is active. Format:
`[Deal Name] — [Reason]. Recommend: [Verify in HubSpot / Check with AE / Accept as written]`
If no flags: `All deals in this batch processed with full data confidence.`
