---
name: deal-company-resolution
description: How to reliably map HubSpot deals back to their company when working from an account list. Read before any batch pull of deals for a named set of accounts.
type: project
---

# Resolving deals for a list of companies

`search_crm_objects` on DEAL with `associatedWith IN [many company ids]` returns the deals but
**does not say which company each deal belongs to**, and the deal name is not a reliable proxy.

Why it matters: on the New Logos SMB run (31 Aug 2026) several deals carried names with no
relation to their company — Account_198 held `Account_035_Marketplace API`,
Account_052 held `API Integration - Account_011`, Account_126 held
`Account_248_Empuls`, Account_177 held `Survey Module - Account_176 technologies`.
Name-matching would have silently mis-assigned pipeline value.

How to apply: search **one company at a time** with `associatedWith EQUAL [single id]`, and
fan the work out across subagents that write JSON to disk and report only counts and doubtful
matches. Roughly 20 companies per subagent keeps each one inside its context budget.

Companies routinely hold several deals, including dormant ones from earlier years. Pick the
won/signed deal, tie-breaking on most recent `createdate`. Note that in the Direct Sales -
Active Pipeline the internal stage value `closedlost` is **labelled "7 - Closed won"** — do not
filter it out as a loss. Won/signed stage ids seen in this portal: `9000000002`, `900000074`,
`90000041`, `900000063`, `9000000029`, `9000000011`, `900000068`, `closedlost`.

Company name matching: `name IN [...]` is exact-match and missed ~11% of a 64-name list
(legal-entity suffixes, casing, trailing spaces). Fall back to `CONTAINS_TOKEN "Prefix*"`,
up to 5 filterGroups per call.

Related: [[acv-revenue-field-mapping]]
