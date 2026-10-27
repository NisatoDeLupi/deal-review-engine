---
name: sandbox-tmp-not-writable
description: "Linux sandbox /tmp is read-only; write scratch files to $HOME instead, and beware stale /tmp files from older sessions"
type: project
---

In the Cowork Linux sandbox, `/tmp` is NOT writable (`Permission denied`, files owned by `nobody`), but stale files from earlier sessions can still be *readable* there. On 2026-08-17 the deal-review cache sync wrote `deals.json` from a leftover `/tmp/deals.tsv` dated 2026-08-14 after the heredoc write silently failed, producing a bogus "0 stale / 114 fresh" plan.

**Why:** bash's `cat > /tmp/x` failure only prints to stderr; the next command reads the old file and looks like it worked.

**How to apply:** write scratch files to `$HOME` (`/sessions/<name>/`), which is writable, or straight into the project folder. Assert on freshness after generating input files (e.g. check `max(hs_lastmodifieddate)` is recent, and that the row count matches the API `total`). Also note: `rm` is not permitted inside the mounted project folder. See [[hubspot-engagement-association-mapping]].
