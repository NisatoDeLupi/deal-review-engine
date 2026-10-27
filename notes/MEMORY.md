# Claude learnings index (Deal Review project memory)

Operational gotchas Claude recorded across Deal Review sessions. Load these into a new Claude project's memory so the next setup doesn't relearn them.

- [HubSpot engagement association mapping](hubspot-engagement-association-mapping.md) — NOTE queries return deal associations, EMAIL/CALL don't; per-deal createdate-filtered workaround for the cache sync; standard review scope owners/stages
- [Backfill: pause schedule during manual runs](backfill-manual-run-pause-schedule.md) — disable fullreview-backfill task while manually running slices; re-enable when done
- [Fetch email bodies in a subagent](email-body-fetch-via-subagent.md) — EMAIL body batches overflow or flood the main context; delegate to a subagent that writes JSON and reports counts
- [Sandbox /tmp is not writable](sandbox-tmp-not-writable.md) — write scratch to $HOME; stale /tmp files silently poisoned a cache-sync plan
- [Farming cross-sell fit rules](farming-crosssell-fit-rules.md) — Empuls/Compass/Loyalife/API rating thresholds, tier logic, do-not-pitch list, CRM headcount buckets are unreliable
- [ACV / GMV / SaaS field mapping](acv-revenue-field-mapping.md) — Variable ACV=GMV, Fixed+One-time=SaaS, NetRev=5%xGMV+SaaS; all *_acv____ props are USD and safe to sum, `amount` is not
- [Tool-result overflow files are readable](tool-result-overflow-files-readable.md) — oversized MCP results land in .claude/.../tool-results/; parse them from the sandbox instead of re-querying
- [Deal-to-company resolution](deal-company-resolution.md) — DEAL search can't return associations; resolve one company at a time in subagents, deal names often don't match the company
