# Deal Review — Skill Family

One review workflow across the whole sales motion, split into four pipeline **segments** plus a
**router** that dispatches to the right one. Every skill follows the same shape: confirm scope →
executable HubSpot pull → score → Excel workbook → gated HubSpot writeback → verify.

Nothing is hardcoded to a single AE. Each skill carries a **Run Configuration** block where the AE
name and HubSpot owner ID are set per run, so any AE in the org can be scored by changing those two
values. Pipeline stage IDs are the only fixed HubSpot values — they are org-level constants shared
across all AEs, not per-run settings.

## Skills

| Skill | Segment | Object | Fires when |
|-------|---------|--------|-----------|
| `deal-review-router` | — (orchestrator) | any | Request doesn't name a segment, spans several, is "review everything", or is a bare ID |
| `deal-review-active` | Open pipeline | Open deal | "pipeline review", "are reps calling", "hygiene", "QBR" |
| `deal-review-dormant` | Passive / dormant | Deal @ Stage 8 | "dormant", "passive pipeline", "stage 8" |
| `deal-review-closed-lost` | Closed lost | Deal @ Stage 9 | "closed lost", "revive lost", "stage 9" |
| `deal-review-contact` | Contact-level (no deal) | Company with no deal object | "who should I approach", "no-deal companies", "contact revival" |

`deal-review-active` is an **alias for the existing `hubspot-deal-review` skill** (in `Skills/`) — it
is not renamed here to avoid breaking the shared/installed copy. The other four skills live in this
folder. When the segment is unclear, start at `deal-review-router` — it classifies by fact (look up
`dealstage` for a deal ID, `num_associated_deals` for a company ID) and hands off.

That active skill is already org-usable: it takes an AE scope list and reads owner IDs from the team
roster in `Skills/hubspot_reference.md`, so no single AE is baked into its logic.

## Per-run configuration (set in each skill's Run Configuration block)

| Setting | Meaning |
|---------|---------|
| AE in scope (`<AE>`) | The account executive being reviewed — display name |
| Owner ID (`<owner_id>`) | That AE's HubSpot owner ID — used in the pull filter and as the @mention/task owner on writeback |
| Pipeline | The sales pipeline (default: Direct Sales — Hunting) |
| Create-date window start | Start of the active scoring window (default: `2024-12-02`) |
| HubSpot portal | Org-level portal ID (contact skill only) |

To run for a different AE, change `AE in scope` and `Owner ID`. Everything else holds.

## Org-level constants (shared across all AEs — not per-run)

Pipeline stage IDs (Direct Sales):

| Stage ID | Stage | Reviewed by |
|----------|-------|-------------|
| open stages | Prospect → Negotiation | `deal-review-active` |
| `900000070` | 8 — Dormant | `deal-review-dormant` |
| `900000056` | 9 — Closed Lost | `deal-review-closed-lost` |
| `9000000002` | 6 — Confirmed & Signed | out of scope (never reviewed) |
| `9000000001` | 7 — Closed Won | out of scope (never reviewed) |

Writeback mechanics (identical in every skill):

- `manage_crm_objects` is capped at **10 objects per batch**.
- @mentions only via `<span data-mention-id="<owner_id>">` — never plain `@Name`.
- No emojis in notes or tasks.
- Writeback is **gated**: build and present the Excel first, confirm, offer a 1–2 record test before the full batch.
- **DO NOT CONTACT / stop-request is never overridden** by score or tier — note only, no outreach task.
- Exclusions are always written visibly; never silently skip a record.

## Folder layout

```
Deal Review/
├── README.md                    (this file)
├── deal-review-router/          SKILL.md
├── deal-review-dormant/         SKILL.md + references/
├── deal-review-closed-lost/     SKILL.md + references/ + scripts/generate_excel.py
├── deal-review-contact/         SKILL.md + references/
└── _deprecated/                 superseded / stray files (kept because this mount can't delete)
```

## Notes

- `deal-review-closed-lost/scripts/generate_excel.py` is the shared 3-sheet workbook generator for
  the 5-filter closed-lost model. `deal-review-dormant` builds its own 6-filter workbook via the
  `xlsx` skill (a 6-filter shared generator can be added later if wanted).
- `_deprecated/` holds files that could not be deleted on this mount (an old `.orig`, a mis-placed
  generator, test scratch). Safe to delete manually from Explorer.
