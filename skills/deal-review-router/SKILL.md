---
name: deal-review-router
compatibility: Requires HubSpot MCP connector to be active. Will not function without it.
description: >
  Orchestrator for the deal-review family. Use this FIRST whenever a review/scoring request does not
  name its segment, spans more than one segment, or asks to "review everything". Triggers: "review my
  pipeline", "review my deals", "score my accounts", "who should I chase/contact", "run the deal
  review", "do a full review", "review everything", "which of these should I work", or a bare HubSpot
  deal/company ID (or list) with no stage/segment stated. This skill decides which segment applies —
  active pipeline, dormant, closed lost, or no-deal contact-level — and hands off to the matching
  skill (deal-review-active / deal-review-dormant / deal-review-closed-lost / deal-review-contact).
  If the user already names the segment clearly, that specific skill triggers directly and this
  router is not needed. This router does not score deals itself; it classifies and dispatches.
---

# Deal Review — Router / Orchestrator

One review workflow, four segments, one entry point. This skill classifies an incoming request into
the correct segment and hands off to the matching sub-skill. It does not pull, score, or write back
itself — the sub-skill it selects does that.

## The four segments

| Segment | Skill to load | Object | Stage / filter | Deliverables |
|---------|---------------|--------|----------------|--------------|
| Active pipeline | `deal-review-active` | Open deal | Prospect → Negotiation (not closed) | Excel + notes + AE task + manager task |
| Passive / dormant | `deal-review-dormant` | Deal | `dealstage = 900000070` (Stage 8) | Excel + revival note + re-engagement task |
| Closed lost | `deal-review-closed-lost` | Deal | `dealstage = 900000056` (Stage 9) | Excel + revival note + re-engagement task |
| Contact-level (no deal) | `deal-review-contact` | Company with **no** deal object | `NOT_HAS_PROPERTY num_associated_deals` | 5-sheet Excel (+ ledger) + signal note + approach task |

Confirmed & Signed (`9000000002`) and Closed Won (`9000000001`) are **not review targets** — they are
excluded by every segment.

Note: `deal-review-active` is an alias for the existing **`hubspot-deal-review`** skill (in `Skills/`);
load that skill when routing to the active segment.

---

## Routing decision tree

Work top to bottom. Stop at the first rule that matches.

### 1. Did the user explicitly name the segment?

If the request clearly names one segment, route there without further checks:

| Signal in the request | Route to |
|-----------------------|----------|
| "open deals", "pipeline review", "are reps calling", "pipeline hygiene", "QBR", "AE accountability" | `deal-review-active` |
| "dormant", "passive pipeline", "stage 8", "revive dormant" | `deal-review-dormant` |
| "closed lost", "revive lost", "stage 9", "why did we lose" | `deal-review-closed-lost` |
| "no-deal companies", "who should I approach", "contacts to reach", "company never converted", "contact revival" | `deal-review-contact` |

### 2. No segment named, but an ID or record was given

Resolve by looking at the record itself — do not guess:

- **A deal ID (or list of deal IDs):** fetch `dealstage` for each via `search_crm_objects`
  (`objectType: "deals"`). Route each deal by its stage:
  - `900000070` → `deal-review-dormant`
  - `900000056` → `deal-review-closed-lost`
  - any open pipeline stage (Prospect…Negotiation) → `deal-review-active`
  - `9000000002` / `9000000001` → out of scope; report and drop.
- **A company ID (or list):** fetch `num_associated_deals`.
  - No associated deal → `deal-review-contact`.
  - Has associated deal(s) → resolve each deal by stage as above (a company can have deals in
    different segments; split accordingly).

### 3. No segment named and no ID — infer from intent, then confirm

Map the verb/goal to a segment, then confirm scope with the user before pulling:

- "who do I chase / who's gone quiet / re-engage" + deals exist → dormant or closed-lost (ask which pipeline, or run both).
- "who should I reach out to / net-new / never bought" → contact.
- "how's my pipeline / are deals moving" → active.

If still ambiguous, ask ONE clarifying question naming the four segments rather than guessing.

### 4. Multi-segment or "review everything"

If the request spans segments (mixed ID list, or "review my whole book / everything"):

1. Split the universe by segment using rules 1–2.
2. Run each relevant sub-skill on its subset, in this order: `deal-review-active` →
   `deal-review-dormant` → `deal-review-closed-lost` → `deal-review-contact`.
3. Each sub-skill produces its **own** Excel and its own writeback — do not merge scoring models
   (active = discipline/activity axes; dormant/closed-lost = 100-pt tiers; contact = verdict/tier).
   A combined run therefore yields up to four workbooks. Offer a short roll-up summary across them
   at the end (counts and top actions per segment).

---

## Handoff protocol

Once the segment is decided:

1. State the routing decision in one line: `Routing to <skill> — <reason (stage ID / no-deal / named)>.`
2. Load that skill (invoke it) and follow its Step 0 / scope-confirmation.
3. Pass through any scope the user already gave (AE/owner, batch size, writeback yes/no, test-first)
   so the sub-skill does not re-ask what is already known.
4. For a mixed batch, hand off one subset at a time and keep a running note of which IDs went where,
   so nothing is double-processed or dropped.

---

## Shared conventions (all four segments honour these)

The router enforces consistency so every segment behaves the same way on the cross-cutting rules:

- **Owner scoping is per run — nothing is hardcoded to one AE.** Every segment skill has a Run
  Configuration block. Collect the AE name + HubSpot owner ID from the user or the request and pass
  it through; never assume a default owner, confirm before pulling, and never mix owners in one
  batch silently.
- **Writeback is gated.** Build the Excel first, present it, and confirm before any HubSpot write.
  Always offer a 1–2 record test before the full batch.
- **Writeback mechanics are identical everywhere:** `manage_crm_objects` capped at 10 objects/batch;
  @mentions only via `<span data-mention-id="...">`; no emojis in notes/tasks; post note + task for
  a record together and sequence by priority.
- **DO NOT CONTACT / stop-request is never overridden** by score or tier, in any segment. Note only,
  no outreach task.
- **Exclusions are always written visibly** — never silently skip a record.

---

## Disambiguation quick-reference

- Has a deal object? → one of the three deal skills (by stage). No deal object? → `deal-review-contact`.
- Stage 8 = dormant. Stage 9 = closed lost. Open = active. Won/Signed = out of scope.
- Bare "score these deals" with no stage → **fetch the stage, then route** (rule 2). Do not assume dormant vs closed-lost.
- A company with deals in two stages → split; route each deal to its stage's skill.

---

## Worked examples

- *"Score these deals"* + 6 deal IDs → fetch each `dealstage`; 4 are `900000056` → `deal-review-closed-lost`, 2 are `900000070` → `deal-review-dormant`. Run both, two workbooks.
- *"Who should I approach at these accounts?"* + company IDs → fetch `num_associated_deals`; no-deal companies → `deal-review-contact`; any with a deal → split out to the deal skills.
- *"Review my whole hunting book"* → rule 4: run active, then dormant, then closed-lost, then contact; four workbooks + a roll-up.
- *"Are my reps actually calling their open deals?"* → named active-pipeline intent → `deal-review-active`.
