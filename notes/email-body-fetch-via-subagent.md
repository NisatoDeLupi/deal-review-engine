---
name: email-body-fetch-via-subagent
description: Fetch HubSpot EMAIL bodies inside a subagent that writes JSON to disk; inline batches blow the main context
type: feedback
---

When backfilling the engagement cache, delegate EMAIL body fetching (`get_crm_objects` with `hs_email_text`) to a subagent that writes a single JSON file and reports only counts.

**Why:** Email bodies carry long quoted threads. A batch of 10 either errors past the token cap (auto-saved to a `.txt`) or, worse, returns inline and consumes ~30k tokens of the main context in one call. Batches of 8 still overflow regularly.

**How to apply:** Give the subagent the ID list, the property list, batch size 10, the output path, and an explicit "report counts only, no email content" instruction. Tell it that auto-saved tool-result files are reachable in the sandbox by mapping the Windows prefix `...\local_<id>\.claude\` to `/sessions/<session>/mnt/.claude/` (specifically `.../projects/<slug>/<session>/tool-results/`). Batches of 10 reliably overflow, which is the *desired* outcome — the subagent parses them straight off disk with python and no body ever enters any context, which is cheaper than staging via heredoc. Calls and notes are small enough to fetch inline (a 29-call batch is fine). Also have the subagent write per-batch part files and concatenate at the end, so a crash mid-slice loses only one batch. See [[hubspot-engagement-association-mapping]].

Two schema gotchas seen in practice: `hs_call_duration` is unpopulated on this portal's calls (always null), and some emails lack `hs_email_status` or `hs_email_subject` — the cache consumer must tolerate nulls.
