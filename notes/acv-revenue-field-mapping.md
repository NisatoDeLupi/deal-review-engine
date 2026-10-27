---
name: acv-revenue-field-mapping
description: How Xoxoday's GMV / SaaS / Net Revenue metrics map onto HubSpot deal properties, and the net revenue formula. Read before any deal-value, cohort, or pipeline-value analysis.
type: reference
---

# HubSpot deal value fields (confirmed by Abhimanyu, 31 Aug 2026)

| Business term | HubSpot property | HubSpot label |
|---|---|---|
| GMV | `potential_acv____` | Variable ACV ($) |
| SaaS (part 1) | `booked_acv____` | Fixed ACV ($) |
| SaaS (part 2) | `one_time_setup_fee____` | Total One Time Setup Fee ($) |
| Gross ACV | `total_acv` | Gross ACV $ — equals Fixed + Variable |

**SaaS = Fixed ACV + One-time ACV**
**Net Revenue = 5% x GMV + SaaS**

Why: this is the company's own revenue definition — only 5% of gross merchandise value is
recognised as revenue, while SaaS billing is recognised in full. HubSpot surfaces the result
as "Total Net Booking Revenue $" on the deal record.

How to apply: **all `*_acv____` properties are stored in USD regardless of the deal's own
`deal_currency_code`**, so they can be summed across deals directly — do NOT convert them.
The `amount` property, by contrast, is in the deal's native currency and must never be summed
raw. When a threshold is quoted in lakhs/crores, convert the USD ACV at ~90 INR/USD.

Do not confuse these with `total_gmv` / `total_saas`, which are separate INR-denominated
billing fields with different semantics ("Total SaaS + Total Stores").

Related: [[new-logos-smb-cohort-run]]
