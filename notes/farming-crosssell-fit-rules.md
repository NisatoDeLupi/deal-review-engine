---
name: farming-crosssell-fit-rules
description: Fit-rating thresholds and do-not-pitch list used for the Xoxoday farming cross-sell analysis in the ref-sheet 27-column format
type: project
---
Farming cross-sell analyses reuse the "Sales Opportunity Analysis" tab format from
SMB Focus Accounts Research.xlsx (27 columns, exact headers). Source accounts come from
the "2026 Plan" tab of the same workbook (Client Name / Product / Employee Size /
Cross Sell Potential / New Poc / YTD July-2026 Ach).

Fit thresholds settled on (2026-08-24 run, 58 accounts):
- Empuls: Strong = 500+ HC with a real HR function; Moderate = 200-500; Weak = <200 or
  competing product. Literal value "Empuls" = already an active customer, so the motion is
  add-on modules, not a new sale.
- Compass: Strong = sales team 200+; Moderate = 50-200 or a smaller genuinely
  commission-driven GTM (real estate brokers, equipment dealers, freight); Weak otherwise.
- Loyalife: Strong = 1M+ consumer base or a large channel network already issuing points;
  Moderate = small consumer base or a partner network with no points mechanic; Weak = pure B2B.
- API Marketplace: Strong = owns a customer/partner-facing platform AND issues points, or is
  itself a rewards operator; Moderate = owns a platform but the budget holder is their client.
- Opportunity Count = live COUNTIF of Moderate+Strong across K:N.
- Priority Tier: High = count 3+, or count 2 with a Strong fit plus an active trigger
  (funding, launch cycle, merger, in-flight deal); Medium = count 2 or a single Strong at
  500+ HC; Low = count 1 or 0.
- Tier reflects merit, not CRM state. CRM "Disqualified" goes in the Sales Disqualified
  column so High-tier disqualified rows read as deliberate re-test candidates.

Do not pitch (competitive overlap): Account_224 (sells competing employee-experience software),
Account_036 (competes with Loyalife - treat as Plum catalog-supply partner),
ZIZO Technologies (competes with Empuls recognition and Compass gamification - Plum API only).

Treat as distribution partnerships rather than accounts: i-exceed (Account_020 powers banks in
90+ countries), Account_136 (route into Account_185/Account_264/Account_158/Account_034), Account_224 (OEM rewards),
Account_036 (89 client loyalty programs).

Why: CRM employee-size buckets are unreliable — six of 58 were materially wrong
(Thryve ~4x understated, Account_200 ~10x understated, GCX ~4x overstated, ISB counted
students as employees). How to apply: always web-verify headcount before quoting seats,
and record the correction in the Comments column.
