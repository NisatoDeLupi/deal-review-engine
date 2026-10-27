---
name: tool-result-overflow-files-readable
description: Oversized MCP tool results are persisted to disk under .claude/projects/.../tool-results/ and the Linux sandbox can read them with python
type: reference
---

When an MCP tool result is too large to return inline, the harness writes the full JSON to
`<session outputs>/.claude/projects/<encoded-session-path>/tool-results/<toolu_id>.json`.
The Linux sandbox can read those files, so a giant HubSpot response does not need re-querying —
parse the persisted file with python instead.

Matters for HubSpot engagement pulls: `search_crm_objects` on NOTE/EMAIL/CALL auto-includes
`hs_body_preview`, so even an IDs-only query (properties `["hs_timestamp"]`) overflows on deals with
long histories. Collect the `id` values out of the persisted file rather than narrowing properties,
which does not help.

Related: [[hubspot-engagement-association-mapping]], [[email-body-fetch-via-subagent]]
