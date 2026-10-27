# Scoring Rubric — Dormant Deal Drop Reason Classification (Filters 1–6)

Reference this file when scoring all 6 filters.
Intent signal classification is defined in `data-pull-methodology.md` — read that first.

---

## Filter 1 — Dormant Deal Drop Reason (20 pts)

Why did this deal go dormant? Recoverable reasons score higher. Fit rejections score lower.
Use the drop reason classification from `data-pull-methodology.md` (Internal vs External)
to determine the bracket.

| Drop Reason | Category | Score |
|-------------|----------|-------|
| No Response | Timing | 20 |
| Client dropped the plan | Internal / Timing | 16 |
| Tech delay (internal to client) | Internal | 14 |
| Price is too high | Commercial | 12 |
| Discount not suited / Loss of champion | Structural | 10 |
| Bad CS experience / Invoice issues | Experience / Admin | 5–6 |
| Product / feature mismatch | Fit | 4 |
| Opted to competitor / Disqualified | External / Conviction | 2–3 |
| Blank / not filled | Unknown | 8 (hold score) |
| Data missing entirely | Unknown | 0 |

Write the drop reason category in the output. Quote the source that determined it.

---

## Filter 2 — Deepest Stage Reached (20 pts)

How far did this deal progress before going dormant? Use stage history, not just the
current stage field. AEs do not always update stages accurately — corroborate with
call logs, emails, and notes to confirm the deepest real stage reached.

Do not score above Prospect unless a call, note, or email confirms a proposal was sent
or a substantive meeting occurred.

| Stage | Score |
|-------|-------|
| 5 — Negotiation | 20 |
| 4 — Proposal | 16 |
| 3 — Opportunity | 12 |
| 2 — Qualified | 8 |
| 1 — Prospect | 4 |
| Pre-prospect / Unknown / No evidence of engagement | 0 |

---

## Filter 3 — Recency of Last Meaningful Activity (15 pts)

Meaningful activity is defined in `data-pull-methodology.md`. Always identify the last
meaningful activity date explicitly before scoring. Do not use the last logged activity
date if that activity is non-meaningful (blank call, system log, admin update).

If no meaningful activity exists: score = 0.
Flag: `No meaningful activity found — all logged activity is blank or admin only.`

| Last Meaningful Activity | Score |
|--------------------------|-------|
| Within 3 months | 15 |
| 3–6 months ago | 11 |
| 6–12 months ago | 8 |
| 12–18 months ago | 4 |
| 18+ months ago | 0 |

---

## Filter 4 — Deal Amount ₹ (15 pts)

Use the HubSpot deal amount field directly. Do not override with a number referenced
in notes — if the field is blank, score 0 and note the referenced value as context only.

| Amount | Score |
|--------|-------|
| ₹5,00,000 and above | 15 |
| ₹3,00,000 – ₹4,99,999 | 12 |
| ₹1,00,000 – ₹2,99,999 | 9 |
| ₹25,000 – ₹99,999 | 6 |
| ₹1 – ₹24,999 | 3 |
| ₹0 / blank / placeholder | 0 |

---

## Filter 5 — Intent Signal (20 pts)

Use the 3-level classification from `data-pull-methodology.md`. Read the full
conversation across all sources before scoring. Do not carry intent signals from
one deal to another, even at the same company.

| Level | Label | Score | What it means |
|-------|-------|-------|---------------|
| 3 | High Intent | 20 | Budget discussed + timeline confirmed + multiple POCs + legal/finance involved |
| 2 | Medium Intent | 13 | Meeting happened, discussions occurred, single POC, named drop reason — no explicit rejection |
| 1 | Low Intent | 7 | Meeting or proposal sent, but no response or minimal replies after |
| 0 | No Signal | 0 | No substantive conversation found on any source |

Write the level and label in the output. Quote the specific note, call, or email
that determined the classification.

---

## Filter 6 — Contact Quality (10 pts)

Contact Quality = Authority Level × ICP Match. Two dimensions scored independently
and multiplied. Raw score is out of 9. Scale to /10 using: ROUND(raw / 9 × 10, 0).

If multiple contacts are associated, score the strongest contact.
State which contact was scored and why.

---

### Dimension A — Authority Level (1–3)

| Score | Label | Who qualifies |
|-------|-------|---------------|
| 3 | Economic Buyer / Decision Maker | CHRO, VP HR, Head of People, CFO, CEO (SMB), CMO, VP Sales — can approve budget and sign off |
| 2 | Champion / Influencer | HR Manager, HR Business Partner, Team Lead with DM access — can build internal case, cannot sign |
| 1 | End User / Wrong Function | Ops Manager, Finance Exec with no HR/Rewards mandate, IT contact — no path to decision |

---

### Dimension B — ICP Match (1–3)

Match on title and region using the hardcoded ICP definitions below.

Score 3 = Exact match to a listed persona for that product and region
Score 2 = Adjacent — relevant department, not primary buyer
Score 1 = Wrong function entirely for this product

#### EMPULS — Employee Engagement

**India**
Score 3 (Top): CHRO, Head of Employee Experience
Score 3: VP / Director HR, Head of People & Culture, Head of HR Operations, Head of Total Rewards, HR Business Partner Leader
Score 2: HR Manager, HR Business Partner, L&D Head, Talent Acquisition Head
Score 1: Sales, Marketing, Finance, IT, Operations

**Southeast Asia**
Score 3 (Top): Head of People & Culture, Employee Experience Lead
Score 3: HR Director, HR Transformation Head, HR Operations Head, Talent & Culture Head
Score 2: HR Manager, HR Business Partner
Score 1: Sales, Marketing, Finance, IT, Operations

**Middle East**
Score 3 (Top): Head of HR, People & Culture Head
Score 3: HR Director, Employee Engagement Lead, Total Rewards Head
Score 2: HR Manager, HR Business Partner
Score 1: Sales, Marketing, Finance, IT, Operations

**US / Europe**
Score 3: VP People, Chief People Officer, Director HR, Head of Total Rewards, Employee Experience Director, People Operations Head
Score 2: HR Manager, HR Business Partner, L&D Head
Score 1: Sales, Marketing, Finance, IT, Operations

---

#### PLUM — Rewards & Incentives

**India**
Score 3: Head of Sales, Sales Operations Head, Trade Head / Trade Manager, Channel Sales Head, Partnerships Head, Marketing Head, Growth Head, Customer Success Head
Score 2: Sales Manager, Marketing Manager, Growth Manager, BD Manager
Score 1: HR, Finance, IT, Operations

**Southeast Asia**
Score 3: Growth Head, Marketing Director, Partnerships Head, Channel Partnerships Head, Revenue Operations Head
Score 2: Sales Manager, Marketing Manager, Growth Manager
Score 1: HR, Finance, IT, Operations

**Middle East**
Score 3: Marketing Director, Partnerships Head, Channel Sales Director, Business Development Head
Score 2: Sales Manager, Marketing Manager, BD Manager
Score 1: HR, Finance, IT, Operations

**US / Europe**
Score 3: VP Partnerships, Head of Growth, Customer Marketing Head, Revenue Operations Head, Channel Partnerships Director
Score 2: Partnerships Manager, Growth Manager, Marketing Manager
Score 1: HR, Finance, IT, Operations

---

#### LOYALIFE — Customer Loyalty

**India**
Score 3 (Top): Loyalty Program Head, Marketing Director
Score 3: Head of CRM, Customer Experience Head, Digital Marketing Head, Head of Customer Engagement
Score 2: Brand Manager, CRM Manager, Digital Marketing Manager
Score 1: HR, Finance, IT, Sales

**Southeast Asia**
Score 3: Loyalty Program Director, CRM Head, Digital Marketing Director, Customer Experience Head
Score 2: Brand Manager, CRM Manager, Digital Marketing Manager
Score 1: HR, Finance, IT, Sales

**Middle East**
Score 3: Loyalty Head, Customer Experience Director, Marketing Director, CRM Director
Score 2: Brand Manager, CRM Manager, Marketing Manager
Score 1: HR, Finance, IT, Sales

**US / Europe**
Score 3: Director Loyalty Programs, CRM Director, VP Marketing, Customer Engagement Director, Lifecycle Marketing Head
Score 2: Brand Manager, CRM Manager, Marketing Manager
Score 1: HR, Finance, IT, Sales

---

### Contact Quality Score Table

| Raw Score (A × B) | Scaled /10 | Contact Strength | Action |
|-------------------|------------|-----------------|--------|
| 9 (3×3) | 10 | Perfect — Economic Buyer, exact ICP | Prioritise regardless of other signals |
| 6 (3×2 or 2×3) | 7 | Strong — right authority or right persona | Structured outreach, plan one escalation step |
| 4 (2×2) | 4 | Moderate — Champion, adjacent fit | Slow path expected. Plan escalation sequence. |
| 3 (3×1 or 1×3) | 3 | Mismatch — power without fit, or fit without power | Re-map contact before outreach |
| 2 (2×1 or 1×2) | 2 | Poor | Flag for contact enrichment before any call |
| 1 (1×1) | 1 | Dead end | Do not outreach until better contact found |
