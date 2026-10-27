---
name: Xoxoday Farming ABM Enrichment
description: >
  Use when the user asks to enrich farming accounts, run ABM enrichment, process
  a batch of companies, add new columns to the farming Excel, enrich company data,
  generate pitch angles, run cross-sell logic, identify upsell opportunities,
  or any variation of "enrich this sheet", "process this batch", "run the farming
  enrichment", "add company summary", "find the right product to pitch". Also
  trigger when the user uploads or references the Farming_ABM_Campaign.xlsx or
  any sheet named after an AE (AE_22, AE_74, AE_56, AE_62, AE_47).
  This skill governs ALL enrichment work for the Xoxoday farming / cross-sell ABM campaign.
---

# Xoxoday Farming ABM Enrichment

## Purpose

Enrich existing Xoxoday farming accounts — companies already using at least one
Xoxoday product — with AI-generated company intelligence and rule-based cross-sell
recommendations. The goal is to enable each AE to pitch every eligible product
simultaneously to the correct buyer persona, without manual research per company.

---

## How to execute an enrichment run — two phases

A typical sheet has 100–250 companies and 9 enrichment columns. Six of those
columns are pure functions of the existing Excel cells (headcount, current
product, B2C flag, channel, sales team size, fit ratings). The other three are
genuine company-knowledge tasks — what the business does, who its sister
verticals are, what use cases land best for this specific operation.

Mixing these two kinds of work in the same per-row loop is the main source of
slow, inconsistent enrichment runs. Splitting them makes the run cheaper, more
reproducible, and recoverable when something goes wrong halfway through.

So when a run begins, treat it as two phases.

### Phase 1 — Rule-based columns via a single Python pass

These six columns are deterministic — same input row, same output, every time:

- Col 32 Growth Stage (from Est. Headcount via Step 4 thresholds)
- Col 33 Recommended Products (from references/cross-sell-logic.md — current
  product + headcount + B2C + channel + sales team size + fit ratings)
- Col 34 Outreach Tracks (each recommended product paired with its fixed persona)
- Col 36 Ideal Buyer Personas (fixed Tier 1 / Tier 2 lists per product, Step 6B)
- Col 37 The pitch *template* selection plus the warm-in line and company-name
  substitution (the specific factual personalisation inside the pitch happens
  in Phase 2 — see below)
- Col 39 Priority Score (the Step 7 formula, with floor 1 and ceiling 10)

A bundled Python module lives at `scripts/enrich_engine.py`. It implements
every rule in this file and in `references/cross-sell-logic.md`. Use it rather
than re-deriving the logic in chat — the rules are the contract, and running
them in code is how that contract stays honoured across runs.

Typical Phase 1 shape:

```python
import openpyxl, sys
sys.path.insert(0, '/path/to/skill/scripts')
from enrich_engine import build_enrichment, write_batch

wb = openpyxl.load_workbook(WORKBOOK)
ws = wb[SHEET_NAME]
headers = [c.value for c in ws[1]]
rows = [{headers[c-1]: ws.cell(row=r, column=c).value
         for c in range(1, len(headers)+1)} for r in range(2, ws.max_row+1)]
# Phase 1 fills rule-based columns for every row in one pass, no LLM calls.
```

Phase 1 runs in seconds, costs nothing, and is fully reproducible — the same
company on two different runs will produce identical Recommended Products,
Outreach Tracks and Priority Score. If a future run gives a different answer
for those columns, the rules themselves have changed, not the model's mood
that day. That property is the reason this phase exists.

### Phase 2 — AI-judgment columns, in batches of 25 with a save after each batch

These four columns need actual company knowledge or company-anchored reasoning,
which is what Claude is for:

- Col 30 Company Summary — 3–4 sentences using real public facts about the
  specific company. If the company is genuinely unknown, write "Insufficient
  public information" rather than inventing detail.
- Col 31 Sister Verticals / Divisions — named subsidiaries or business lines.
- Col 35 Key Use Cases — per recommended product, anchored to *this* company's
  actual sales team size, B2C base, channel network, platform and industry.
- Col 38 Strategic Triggers — 2–4 concrete signals (funding round, geographic
  expansion, headcount growth, B2C scale, channel presence, vertical context).

Plus the company-specific factual substitutions inside the pitch (Col 37) that
go beyond the template warm-in — e.g. naming an actual product family,
referencing the real channel network, citing the real headcount range.

Work through rows 25 at a time, and after each batch is enriched write those
rows to Excel before starting the next batch. The helper `write_batch` in
`scripts/enrich_engine.py` exists for exactly this. Holding 250 rows of
enriched content in memory until the end is the failure mode to avoid — if
the run is interrupted, every completed batch is already saved, and you can
resume from the next one.

### Announcing the plan

Before running anything, state the plan in one sentence so the user knows
what to expect:

> "Phase 1: running a Python script across all N rows to populate the six
> rule-based columns (Growth Stage, Recommended Products, Outreach Tracks,
> Buyer Personas, pitch template selection, Priority Score). Phase 2:
> enriching in batches of 25 rows, saving the workbook after each batch, for
> the four AI-judgment columns (Company Summary, Sister Verticals, Key Use
> Cases, Strategic Triggers) plus company-specific pitch personalisation."

This sets the right mental model — the user understands which parts are
mechanical and which parts genuinely depend on company knowledge, and they
can interrupt and resume safely between batches.

---

## Products and their buyers

| Product | What it does | Primary buyer |
|---|---|---|
| Empuls | Employee engagement, R&R, surveys, wellness, peer recognition | HR / People / Culture / Total Rewards |
| Plum | Digital rewards catalog, gifting, payout infrastructure | HR / Admin / Procurement / Partnerships |
| Compass | Sales incentive automation, commission tracking, SPIFF management | VP Sales / CRO / Head Sales Ops |
| Loyalife | Customer loyalty programs, membership, retention, channel loyalty | VP Marketing / CMO / Head CX / Head CRM |

---

## Step 1 — Read the existing row

For each company extract:
- Company Name
- Industry / Vertical
- Est. Headcount
- B2C Customer Base — if ANY value is present (a number, text, or "Yes"), treat as B2C
- Channel Partner Network — note if populated
- Own Platform — Yes/No and platform name
- Product Currently Used
- Empuls fit / Compass fit / Loyalife fit ratings
- Priority Tier

Enrich every company regardless of Priority Tier, Sales Disqualified status,
or any content in the Comments column. These fields do not affect enrichment.

---

## Step 2 — Generate Company Summary

Write 3–4 sentences covering exactly:
1. What the company does and which industry
2. Who their end customers are (B2B, B2C, or both) and approximate scale
3. Growth stage and any notable public signal (funding, expansion, headcount growth, IPO)
4. One sentence connecting the company specifically to Xoxoday's products

Rules:
- Be specific and factual. Use real numbers where available.
- Never use: "leading provider", "innovative solutions", "cutting-edge", "dynamic"
- If public information is scarce, write what is known honestly

---

## Step 3 — Identify Sister Verticals / Divisions

List any subsidiaries, divisions, or distinct business lines the company operates.
Example: "Account_058 operates Account_057 & Paper, Account_037, and Account_151."
If none found: "No major divisions identified."

---

## Step 4 — Determine Growth Stage

Apply the FIRST definition below that fits the company. Use the lower bound when
headcount is a range (e.g. 500–1,000 → use 500).

**Startup** — Founded within last 5 years AND headcount below 200 AND Series A
or earlier (or pre-revenue). No significant enterprise client base yet.

**Growth** — Headcount 200–800 AND Series B or C funded. Revenue growing fast,
product-market fit established, actively hiring across functions.

**Scale-up** — Headcount 800–2,000 AND Series C/D or revenue-funded. Expanding
to new geographies or verticals. Moving from founder-led to process-led operations.

**Mid-Market** — Headcount 2,000–5,000. Stable revenue, multiple business units,
structured HR and sales functions. May be listed or PE-backed.

**Enterprise** — Headcount 5,000–50,000. Established brand, complex procurement,
multiple decision-maker layers. Listed company or large PE-backed group.

**Conglomerate** — Headcount above 50,000 OR a group company with 3 or more
distinct subsidiary businesses across different industries under one parent entity.

---

## Step 5 — Apply cross-sell logic

Read references/cross-sell-logic.md fully before this step.

That file contains:
- Which products to recommend based on current product + headcount + B2C flag
- How to handle companies already on multiple Xoxoday products
- The Empuls add-on pitch logic (for companies already on Empuls)
- How to build Outreach Tracks — pairing each product with its target persona

Output from this step:
- Recommended Products — all eligible, comma-separated
- Outreach Tracks — each product paired with its target persona (e.g. Empuls → VP HR,
  Loyalife → CMO / Head of CX). Each track is independent — different product,
  different buyer, no clash.

---

## Step 6 — Generate per-product pitch content

For EACH product in Recommended Products, generate all four items below.

---

### 6A — Key Use Cases

Write 2–3 use cases specific to this company's business, industry, and scale.
Reference real signals from the row: sales team size, B2C base, channel partners,
platform, headcount.

Bad: "Empuls can help with employee engagement."
Good: "Incentivise 400+ inside sales reps with real-time leaderboards tied to
daily policy issuance targets — replacing manual SPIFF spreadsheets that currently
cause payout disputes and ops overhead."

---

### 6B — Ideal Buyer Persona

Use only the personas listed below. List Tier 1 first (max 3 personas), then
one Tier 2 persona. Never invent personas outside this list.

**Empuls**

Tier 1:
- CHRO / Chief People Officer / Chief Human Resources Officer
- VP HR / VP People / VP Employee Experience
- Head HR / Head People Operations / Head Employee Experience
- Director HR / Director People Operations / Director Employee Engagement

Tier 2 (pick one most relevant):
- Employee Engagement Manager
- Rewards & Recognition Manager / Total Rewards Manager
- HRBP
- Culture Manager
- People Operations Manager / People Success Manager

**Plum**

Tier 1:
- Head of Rewards / Head of R&R
- HR Head / VP HR (employee gifting context)
- Head of Admin / Head of Procurement
- Head of Partnerships / VP Partnerships (partner rewards context)

Tier 2 (pick one):
- HR Manager / Senior HR Manager
- Admin Manager
- Vendor Manager

**Compass**

Tier 1:
- CRO / Chief Revenue Officer
- VP Sales / SVP Sales
- Head of Sales / Head of Sales Operations
- VP Revenue Operations

Tier 2 (pick one):
- Sales Operations Manager
- Incentive Compensation Manager
- Regional Sales Head

**Loyalife**

Tier 1:
- VP Marketing / CMO / Chief Marketing Officer
- Chief Customer Officer / Chief Experience Officer
- Head of CX / Head of Retention / Head of Customer Marketing
- Head of Loyalty / Head of CRM

Tier 2 (pick one):
- CRM Manager / Retention Marketing Manager
- Digital Marketing Manager
- Customer Engagement Lead

---

### 6C — Personalized Pitch Angle

Write 2–3 sentences per product. Every pitch must include:
1. A warm-in line referencing the product the company currently uses
2. A specific company signal (B2C base size, sales team scale, channel partners, platform)
3. A concrete outcome or metric

Use these structures as the base — adapt with real company details, never copy-paste generic.
Every pitch ends with its CTA exactly as specified below.

**Empuls pitch (company is on Plum):**
"We're proud to be partnered with [Company] for your R&R programs — and reaching out
because there's a natural next step many of our clients take that delivers significantly
more impact. Several HR leaders we work with upgraded from a standalone rewards catalogue
to Empuls — our full employee engagement platform — and saw eNPS improve by 20+ points
within two quarters. Empuls connects recognition, pulse surveys, peer appreciation, and
milestone rewards in one place. No additional vendors, no new logins for employees.
Worth a 20-minute walkthrough tailored to [Company]'s size?"
CTA: Schedule a Call →

**Empuls add-on pitch (company already on Empuls — pitch unused modules):**
"We're glad to be powering [Company]'s employee engagement through Empuls — and there
are three add-on modules that activate natively into your existing setup without a new
vendor, new login for employees, or additional procurement cycle:
- Fitness Challenges — team wellness goals with automated reward milestones. Clients
  see 3x participation vs. standalone apps.
- L&D Incentives — points and rewards tied to course completions and certifications,
  directly within your LMS workflow.
- Referral Incentives — automated reward payouts across the full referral journey,
  from nomination through successful hire.
Which of these is most relevant to your priorities right now? Happy to show you a
focused 20-minute walkthrough."
CTA: Book a Walkthrough →

**Loyalife pitch (company is B2C):**
Warm-in line must reflect the actual current product. Use the correct version below:
- If current product is Empuls: "We're honored to be partnered with [Company] for your
  employee R&R programs — and in addition to that, we also work with companies like
  yours on the customer loyalty side, which is what prompted this note."
- If current product is Plum or Compass: "We're glad to be partnered with [Company]
  on [Plum rewards / sales incentives] — and wanted to connect on a separate
  opportunity on the customer side."
Then continue: "Loyalife is our white-labeled, API-first customer loyalty platform.
Your customers earn and redeem from a catalog of 10M+ rewards — flights, hotels,
gift cards, merchandise — across 50+ countries. Brands in [their industry] using
Loyalife have seen customer lifetime value grow by 25–35%, with most going live in
under 8 weeks. Given we're already a vendor at [Company], the commercial and
compliance path to getting started is meaningfully shorter than from scratch."
CTA: Book a Discovery Call →

**Compass pitch (company has large sales team):**
"We're glad to be partnered with [Company] for your R&R programs — and in addition
to that, we also offer a solution built specifically for sales leaders, which is what
I wanted to share with you. Compass replaces manual SPIFFs and spreadsheet-based
commission tracking with real-time leaderboards, automated payouts, and
behavior-specific incentive nudges — all visible to reps from any device. Sales
leaders using Compass report 20–30% improvement in quota attainment within two
quarters, with a significant reduction in incentive disputes and ops overhead.
Since [Company] already runs on Xoxoday infrastructure, the integration path is
materially faster than a cold deployment."
CTA: Book a Demo →

**Plum pitch (company is on Empuls — pitching Plum as the rewards catalog layer):**
"We're proud to power [Company]'s employee engagement through Empuls — and many
HR and admin leaders we work with add Plum as the rewards catalog that sits
alongside it. Given [Company]'s [headcount / multi-location setup / gifting volume],
Plum removes procurement overhead entirely — your team issues personalised digital
gifts in minutes from a single dashboard with full reporting and no MOQ."
CTA: Schedule a Call →

---

### 6D — Strategic Triggers

List 2–4 concrete, company-specific signals that make the pitch timely. Not generic.

Bad: "The company is growing."
Good: "Series D closed in 2024 signals active headcount expansion — employee
engagement investment typically follows within 1–2 quarters post-funding."

Other triggers to look for:
- Large B2C base with no current loyalty layer identified
- Own platform with no embedded rewards layer
- Large channel partner network with no structured incentive program
- Sales team above 200 with no automated commission tool visible
- Recent geographic expansion
- Industry where competitors actively use loyalty programs
- Headcount in growth stage with no R&R program signals

---

## Step 7 — Calculate Priority Score

Score 1–10. Round to nearest whole number.

**Base from fit ratings (existing columns):**
- Strong = +1.5 per product (4 products max = 6 points max)
- Moderate = +0.5 per product
- Weak = 0

**Bonuses:**
- B2C Customer Base column has any value = +1.5
- Own Platform = Yes = +1.0
- Channel Partner Network = populated = +0.5

**Caps and floors:**
- Score ceiling = 10
- Priority Tier already = High → minimum score is 7 (adjust upward if formula gives less)
- Priority Tier already = Low → cap at 5, unless 3+ Strong fits exist (then allow up to 7)

---

## Output format

Add these 9 columns to the RIGHT of all existing columns. Never modify existing columns.

| Col | Column Name | Content |
|---|---|---|
| 30 | Company Summary | 3–4 sentences per Step 2 |
| 31 | Sister Verticals / Divisions | Per Step 3 |
| 32 | Growth Stage | Single value from Step 4 definitions |
| 33 | Recommended Products | All eligible — comma-separated |
| 34 | Outreach Tracks | Each product paired with its target persona. Format: Empuls → VP HR / Head People Operations / Loyalife → CMO / Head of CX |
| 35 | Key Use Cases | Per product — tagged [PRODUCT NAME] |
| 36 | Ideal Buyer Personas | Per product — tagged [PRODUCT NAME] |
| 37 | Personalized Pitch Angle | Per product — tagged [PRODUCT NAME] |
| 38 | Strategic Triggers | 2–4 bullet points |
| 39 | Priority Score (1–10) | Numeric |

For columns 35, 36, 37 — always use this separator format:
[EMPULS] content
[PLUM] content
[LOYALIFE] content
[COMPASS] content

Only include tags for products that are in Recommended Products for that company.

---

## Edge cases

- Multi-product accounts (already on 2+ Xoxoday products): read
  references/cross-sell-logic.md section "Multi-product accounts."
- Own Platform = Yes: always note API Marketplace potential in Strategic Triggers
  even though API is not an active pitch product right now.
- No web presence found: write "Insufficient public information" in Company Summary
  and Sister Verticals, set Growth Stage to "Unknown", and complete all rule-based
  columns (Steps 5–7) using only existing Excel data.
