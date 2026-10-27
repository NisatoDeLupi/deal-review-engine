# SKILL.md patch — cache-aware deal review

Paste-ready edits for `hubspot-deal-review/SKILL.md` (read-only app folder, so
applied here as a patch). Three changes: add Step 2.5, replace Step 3, and add a
reference pointer + critical reminder.

Paths below assume the workspace project folder:
- `DB` = `<project>/cache/engagements.db`
- `PY` = `python <project>/scripts/engagement_cache.py --db $DB`

---

## 1. INSERT a new step between Step 2 and Step 3

### Step 2.5: Load & sync the engagement cache

This project keeps a local SQLite cache of every note, email, and call ever
pulled (`<project>/cache/engagements.db`, managed by
`scripts/engagement_cache.py`). Engagement bodies are immutable, so a cached
engagement is never refetched. Use the cache to pull only what changed.

Write the deals from Step 2 to `deals.json`
(`[{"deal_id","hs_lastmodifieddate","dealname"}]`), then classify them:

    $PY plan --in deals.json --out plan.json

`plan.json` gives `stale` (new or `hs_lastmodifieddate` changed → must refresh)
and `fresh` (unchanged → served entirely from cache, zero pulls). Report the
split back to the user, e.g. "62 of 85 deals unchanged — pulling engagements for
23." To force a clean re-pull of everything, add `--full-refresh`.

---

## 2. REPLACE Step 3 entirely with:

### Step 3: Delta-fetch engagements (cache-aware)

Fetch from HubSpot only for **stale** deals; serve **fresh** deals from cache.

1. **Associations — stale deals only.** For each `stale` deal, use
   `HubSpot:get_crm_objects` with `associations: ["notes","emails","calls"]` to
   list engagement IDs. Build `associations.json`:
   `[{"deal_id","engagement_id","type"}]`. (Skip fresh deals — their links are
   already cached.)

2. **Bodies — new IDs only.** Identify which of those engagement IDs have no
   cached body yet:

       $PY need-bodies --in associations.json --out need.json

   Fetch bodies from HubSpot **only** for `need.json`'s `fetch` list. Already-
   cached IDs (re-associated or unchanged) are skipped — this is where most of
   the saving comes from. Fetch the same fields as before:
   - **Notes** — `hs_note_body`
   - **Emails** — `hs_email_text`/`hs_email_html`, `hs_email_subject`,
     `hs_email_direction`, `hs_email_status`, `hs_email_from_email`,
     `hs_email_to_email`, `hs_timestamp`
   - **Calls** — `hs_call_body`, `hs_call_title`, `hs_call_duration`,
     `hs_call_direction`, `hs_call_disposition`, `hs_timestamp`,
     `hs_call_recording_url`

   Build `engagements.json`:
   `[{"engagement_id","type","timestamp","body","metadata":{...}}]`.

3. **Ingest.** Persist deals, links, and new bodies:

       $PY ingest --deals deals.json --associations associations.json --engagements engagements.json

4. **Export the full view.** Get cached + new engagements for all deals to drive
   classification and the report:

       $PY export --deals deals.json --out engagements_by_deal.json

Then classify each deal's engagements into AE Deal Summary / Manager Notes /
Email Trail / Call Activity exactly as before — but now reading from
`engagements_by_deal.json` rather than live API responses. The hidden-risk
signals (0 emails+calls in 30 days, outbound-only ghosting, 60-day call gaps,
unlogged email commitments) are computed from the same cached data.

---

## 3. ADD under "Reference files" → "Local references"

- `scripts/engagement_cache.py` — SQLite engagement cache helper. Run at
  Step 2.5 (`plan`) and Step 3 (`need-bodies`, `ingest`, `export`).
- `docs/engagement_cache.md` — cache design, schema, and CLI. Read once before
  the first cache-aware run.

## 4. ADD to "Critical reminders"

- **Never refetch a cached engagement body.** Bodies are immutable and append-
  only. Only deals with a changed `hs_lastmodifieddate` and engagement IDs absent
  from the cache get pulled from HubSpot. The first review pays full cost; later
  reviews should pull a small fraction. Use `plan --full-refresh` only when you
  deliberately want a clean re-pull.
