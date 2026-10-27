# Deal review engine

The AI deal-review system I built and ran on Xoxoday's HubSpot portal: a router, four pipeline-segment review skills, the scripts behind them, and the notes I kept on where HubSpot behaves differently from its documentation.

It took a pipeline review from about 6 hours to about 20 minutes, and it was picked up beyond my own book by enterprise hunting, farming and revenue operations. The full write-up, including what it does not do, is in the [case study](CASE_STUDY.md).

I specified it, made the calls on scoring and writeback rules, and own it. Claude was the implementation tool. These are Claude skills (Markdown instructions plus Python helpers), run inside Claude with a HubSpot connector, not a standalone application.

## How a review runs

```
confirm scope (rep + stages) -> pull from HubSpot -> score against the stage playbook
  -> Excel review workbook -> human approves -> test 1-2 deals -> gated bulk writeback -> verify
```

Every deal gets one manager note plus two tasks: the rep acts at T+1, the manager checks at T+5. Nothing is written to the CRM before a person has signed off the workbook. Do-not-contact is never overridden by a score, and anything skipped is listed with the reason.

## What is in here

| Path | What it is |
|---|---|
| `skills/deal-review-router/` | Classifies a request (deal ID, company ID, "review everything") and hands it to the right segment |
| `skills/deal-review-active/` | Open-pipeline review: the main `SKILL.md`, the HubSpot reference (stage IDs, field map, roster format) and the next-action patterns used when writing recommendations |
| `skills/deal-review-dormant/` | Deals parked in the dormant stage, with its scoring rubric and data-pull method |
| `skills/deal-review-closed-lost/` | Lost deals worth re-engaging, plus the Excel generator |
| `skills/deal-review-contact/` | Companies with no deal object: who to approach and why it never converted |
| `skills/contact-revival-scorer/`, `skills/closed-lost-revival-scoring/` | Earlier standalone versions of the revival scoring, kept because the rubrics differ |
| `skills/farming-abm-enrichment/` | Cross-sell fit scoring for existing customers, with the enrichment engine |
| `skills/xoxoday-design/` | Brand skill so every workbook, battlecard and deck comes out on-brand (built from Xoxoday's public brand pages) |
| `scripts/engagement_cache.py` | SQLite cache for notes, emails and calls. They never change once logged, so each is fetched once. This is most of the 6-hours-to-20-minutes gap |
| `scripts/build_review.py`, `build_rows.py`, `build_wb.py` | Turn scored deals into the review workbook |
| `docs/` | The skill-family overview, the cache design and a patch note |
| `notes/` | The working memory from the project: HubSpot association quirks, ACV field mapping, deal-to-company resolution, sandbox limits |
| `patterns/engagement-cache/` | The cache idea rewritten as a standalone, CRM-neutral module with tests: `python patterns/engagement-cache/test_engagement_cache.py` |
| `CASE_STUDY.md`, `LESSONS.md` | The write-up, and what I learned about letting AI write to a production CRM |

## Running it

You need Claude with a HubSpot connector that has write access, a local folder connected so the scripts can run, and Python 3.10+ with `openpyxl`. Set the rep name and owner ID in each skill's Run Configuration block. Nothing about a specific rep is baked into the logic, so pointing it at someone else is two values.

## What was changed for publication

This is the real working code, not a rewrite, with identifying details swapped out:

- Colleagues are role tokens: `SDR_A`, `AE_07`, `Person_03`. The same person has the same token across all three of these repos.
- Customer and prospect companies are `Account_NNN`. Deal names and contact names are removed.
- HubSpot owner, deal, company and stage IDs are replaced with stable synthetic IDs (they start with 9), so lookups still line up. The portal ID is `1234567`.
- Emails are `<email>`.
- No CRM data, caches or past review workbooks are included. A third-party library of general sales-skill documents that sat alongside the project is not included either.

Related: [sdr-analytics-suite](https://github.com/NisatoDeLupi/sdr-analytics-suite) · [icp-routing-engine](https://github.com/NisatoDeLupi/icp-routing-engine)

Abhimanyu Singh Shekhawat · [linkedin.com/in/abhimanyu-singh-shekhawat](https://www.linkedin.com/in/abhimanyu-singh-shekhawat) · [github.com/NisatoDeLupi](https://github.com/NisatoDeLupi)
