# Engagement cache — fewer HubSpot pulls per review

This augments the **hubspot-deal-review** workflow with a local SQLite cache of
notes, emails, and calls so each review pulls only what changed since the last
one.

## The core idea

Logged engagements are **immutable and append-only**. A note, email, or call
body never changes after it is recorded. Therefore **each engagement ID only
needs to be fetched from HubSpot once, ever.**

After the first cached review, a later review pulls only:

1. **Deals whose `hs_lastmodifieddate` changed** since the last sync (a single
   cheap deal-list scan tells us this — "stale" deals).
2. **Within those stale deals, only the engagement IDs not already cached** —
   i.e. genuinely new notes/emails/calls.

Unchanged ("fresh") deals are served entirely from the cache with **zero**
HubSpot calls. In practice the first review pays full cost; every review after
that drops body-fetches by ~90%+.

## Where things live

```
Deal Review/
  scripts/engagement_cache.py     ← the sync helper (stdlib only)
  cache/engagements.db            ← created on first run; the persistent cache
  docs/engagement_cache.md        ← this file
```

The `.db` file lives in the workspace folder so it persists across sessions.
Delete it (or pass `--full-refresh` to `plan`) to force a clean re-pull.

## Schema

- **deals** — `deal_id` (PK), `dealname`, `hs_lastmodifieddate`, `last_synced_at`.
  The `hs_lastmodifieddate` is the change-detection key.
- **engagements** — `engagement_id` (PK), `type` (note/email/call), `timestamp`,
  `body`, `metadata` (JSON: subject, direction, disposition, duration, from/to,
  recording_url, etc.), `fetched_at`. One row per engagement, body stored once.
- **deal_engagements** — `(deal_id, engagement_id)` link table, so an engagement
  shared by multiple deals stores its body once but links to each deal.
- **meta** — `schema_version`, `last_sync_at`.

## CLI

All commands take `--db <path to cache/engagements.db>`. Input defaults to stdin,
output to stdout; override with `--in` / `--out`.

| Command | Purpose |
|---|---|
| `init` | Create schema (idempotent; also auto-run by every command). |
| `plan --in deals.json` | Split current deals into `stale` (changed/new) vs `fresh` (unchanged). Add `--full-refresh` to force all stale. |
| `need-bodies --in associations.json` | From the associations of stale deals, return the `fetch` list = engagement IDs with no cached body yet. |
| `ingest --deals d.json --associations a.json --engagements e.json` | Upsert deals, link associations, store newly fetched bodies, stamp sync time. |
| `export [--deals filter.json]` | Cached engagements grouped per deal into `{notes,emails,calls}` for building the report. |
| `stats` | Counts + last sync time. |

### JSON shapes

```jsonc
// deals.json
[{"deal_id":"123","hs_lastmodifieddate":"2026-06-01T10:00:00Z","dealname":"Acme"}]

// associations.json  (discovered for stale deals only)
[{"deal_id":"123","engagement_id":"e9","type":"note"}]

// engagements.json  (bodies fetched ONLY for the need-bodies "fetch" list)
[{"engagement_id":"e9","type":"note","timestamp":"2026-05-30T09:00:00Z",
  "body":"...","metadata":{"subject":"...","direction":"OUTGOING"}}]
```

`type` is one of `note`, `email`, `call`. Suggested `metadata` per type:
- **note**: `{ "owner_id": "..." }`
- **email**: `{ "subject", "direction", "status", "from_email", "to_email" }`
- **call**: `{ "title", "duration_ms", "direction", "disposition", "recording_url" }`

## How the review workflow uses it (drop-in for SKILL.md Steps 2.5 & 3)

```
DB="<workspace>/cache/engagements.db"
PY="python <workspace>/scripts/engagement_cache.py --db $DB"

# Step 2.5 — after pulling the deal list (Step 2), write deals.json, then:
$PY plan --in deals.json --out plan.json
#   -> stale[] need refresh; fresh[] are served from cache.

# Step 3 — for STALE deals only:
#   1. pull HubSpot associations (note/email/call IDs) -> associations.json
$PY need-bodies --in associations.json --out need.json
#   2. fetch bodies from HubSpot ONLY for need.json -> "fetch" list -> engagements.json
$PY ingest --deals deals.json --associations associations.json --engagements engagements.json

# Build the report from the full cached view (stale + fresh together):
$PY export --deals deals.json --out engagements_by_deal.json
```

Net effect: association pulls happen only for stale deals; body fetches happen
only for never-before-seen engagement IDs; fresh deals cost nothing.

## SKILL.md changes to make this permanent

The skill file is in a read-only app folder, so paste these edits into
`hubspot-deal-review/SKILL.md` when you can edit it:

1. **New "Step 2.5: Load & sync the engagement cache"** between Steps 2 and 3 —
   run `plan` to classify deals stale vs fresh.
2. **Rewrite Step 3** to: pull associations for stale deals only → `need-bodies`
   → fetch only the `fetch` list → `ingest` → `export` for the full view.
3. **Reference pointer** under "Reference files": this doc + `scripts/engagement_cache.py`.
4. **Critical reminder**: "Never refetch a cached engagement body — bodies are
   immutable. Only deals with a changed `hs_lastmodifieddate` and engagement IDs
   absent from the cache get pulled. Use `--full-refresh` to force a clean pull."
