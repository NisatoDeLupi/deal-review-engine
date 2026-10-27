# Cross-Sell Logic Reference

## 1. Core rules by current product

### Company currently uses Plum

| Condition | Recommend |
|---|---|
| Headcount ≥ 500 | Empuls |
| B2C base present (any value) | Loyalife |
| Headcount ≥ 500 AND B2C present | Both Empuls and Loyalife |
| Headcount < 500, B2B only | Empuls (still pitch, smaller scope) |
| Sales team size large (200+) | Also add Compass |

### Company currently uses Empuls

| Condition | Recommend |
|---|---|
| B2B company (no B2C base) | Plum |
| B2C base present | Plum AND Loyalife |
| B2C present AND headcount ≥ 500 | Plum AND Loyalife |
| Sales team size 200+ | Also add Compass |
| Already on Empuls | Also run Empuls add-on pitch (Step 7 of SKILL.md) |

### Company currently uses Compass

| Condition | Recommend |
|---|---|
| Headcount ≥ 500 | Empuls |
| Headcount < 500 | Plum |
| B2C base present | Plum AND Loyalife (always, regardless of headcount) |
| B2C present AND headcount ≥ 500 | Plum AND Loyalife AND Empuls |

---

## 2. B2C override rules

If B2C Customer Base column has ANY value — a number, the word "Yes", or any text —
the company is treated as B2C. This is a hard signal.

B2C = true triggers:
- Loyalife is always added to Recommended Products
- Plum is also always added (goes to different persona than Loyalife)

B2C = false (column is blank or "No"):
- Loyalife is NOT recommended unless Loyalife Fit = Strong in existing columns

---

## 3. Headcount thresholds

Use the LOWER bound of any range given (e.g. "500–1,000" → use 500).

| Threshold | What it unlocks |
|---|---|
| Any headcount | Plum is always eligible as a gifting layer |
| ≥ 500 employees | Empuls becomes a strong recommendation |
| < 500 employees | Empuls is still pitched but framed as "start small, scale up" |
| Sales team ≥ 200 | Compass becomes eligible regardless of current product |
| Sales team < 200 | Compass only recommended if Compass Fit = Strong or Moderate |

---

## 4. Channel partner signal

If Channel Partner Network column is populated (any value):

- Add Loyalife as a recommendation for channel loyalty (even if not B2C)
- Add note in Strategic Triggers: "Channel partner network signals opportunity
  for structured partner incentive program via Loyalife"
- If Own Platform = Yes AND channel partners exist: flag API Marketplace in
  Strategic Triggers as a future conversation (do not actively pitch)

---

## 5. Multi-product accounts

If the company has deals for 2 or more Xoxoday products:

Step 1 — Identify which products are ACTIVE (not closed-lost).
Step 2 — Treat all active products as "currently used."
Step 3 — Apply cross-sell rules for each active product independently.
Step 4 — Merge the resulting Recommended Products lists, remove duplicates.
Step 5 — For any product they already actively use, do NOT recommend it again.
          Instead, run the Empuls add-on logic (SKILL.md Step 7) if Empuls is active,
          or note "already active — deepen usage" for other products.
Step 6 — Build Outreach Tracks: pair each recommended product with its target
          persona. Each track is independent — different product, different buyer.

Closed-lost deals: treat as if the product was never used.

---

## 6. No lead product — each product reaches its own persona

Every eligible product is pitched simultaneously to a completely different buyer.
There is no clash because the messages never reach the same person.

- Column 33 (Recommended Products) = all eligible products listed
- Column 34 (Outreach Tracks) = each product paired with its target persona:

  Empuls → VP HR / Head People Operations
  Loyalife → CMO / Head of CX / VP Marketing
  Compass → VP Sales / CRO
  Plum → Head HR / Head Admin

Columns 35, 36, 37 use the [PRODUCT] tag format — each tag is one independent
outreach track, not a ranked list.

Exception: company < 100 employees where one person owns multiple functions —
lead with the product matching their primary title, mention others briefly.

---

## 7. Empuls add-on logic

Trigger ONLY when current product = Empuls (active deal or Product Currently Used = Empuls).
This is an upsell within Empuls, not a cross-sell to a new product.

Three fixed add-on modules:

1. **Fitness Challenges** — wellness goals with automated reward milestones.
   Best for: 500+ employees, manufacturing, IT services, BPO, FMCG.
   Stat: 3x participation vs. standalone wellness apps.

2. **L&D Incentives** — rewards tied to course completions and certifications within LMS.
   Best for: EdTech, IT services, consulting, companies with own learning platforms.

3. **Referral Incentives** — automated reward payouts across the full referral journey.
   Best for: high-growth companies actively hiring, IT services, staffing-adjacent.

Recommend all 3 but highlight 1–2 most relevant to this company.
Target persona: HRBP, L&D Head, TA Lead — NOT the CHRO / VP HR.
