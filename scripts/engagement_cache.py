#!/usr/bin/env python3
"""
engagement_cache.py — local SQLite cache for HubSpot deal-review engagements.

Why this exists
---------------
The deal-review workflow used to re-pull every note/email/call body from HubSpot
on every run. Engagement bodies are immutable and append-only: once a note,
email, or call is logged its body never changes. So each engagement ID only ever
needs to be fetched ONCE. After the first review, later reviews fetch only:
  * deals whose hs_lastmodifieddate changed since the last sync, and
  * within those, only the engagement IDs not already cached.

Everything else is served from this cache with zero HubSpot pulls.

An association link table (deal_engagements) means a single engagement shared by
multiple deals stores its body once and is linked to each deal.

Stdlib only (sqlite3, json, argparse). No third-party dependencies.

Commands
--------
  init        Create the schema (idempotent). Safe to run every time.
  plan        Given the current deal list, report which deals are stale
              (need an association + body refresh) vs fresh (serve from cache).
  need-bodies Given the associations discovered for stale deals, report which
              engagement IDs have no cached body yet (the only bodies to fetch).
  ingest      Upsert deals, link associations, and store newly fetched bodies.
              Updates the sync metadata.
  export      Dump cached engagements grouped per deal (for building the report).
  stats       Print cache counts.

All commands take --db PATH (the SQLite file, e.g. the workspace cache folder).
Input JSON uses --in (default stdin); output uses --out (default stdout).

JSON shapes
-----------
deals.json        : [{"deal_id":"123","hs_lastmodifieddate":"2026-06-01T...","dealname":"Acme"}]
associations.json : [{"deal_id":"123","engagement_id":"e9","type":"note"}]
engagements.json  : [{"engagement_id":"e9","type":"note","timestamp":"...","body":"...",
                      "metadata":{...type-specific fields...}}]

plan output       : {"stale":["123",...],"fresh":["456",...],
                     "counts":{"total":N,"stale":S,"fresh":F}}
need-bodies output: {"fetch":["e9",...],"cached":["e1",...],
                     "counts":{"associations":A,"to_fetch":T,"already_cached":C}}
export output     : {"123":{"notes":[...],"emails":[...],"calls":[...]}, ...}
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

SCHEMA_VERSION = "1"

DDL = """
CREATE TABLE IF NOT EXISTS deals (
    deal_id              TEXT PRIMARY KEY,
    dealname             TEXT,
    hs_lastmodifieddate  TEXT,
    last_synced_at       TEXT
);

CREATE TABLE IF NOT EXISTS engagements (
    engagement_id  TEXT PRIMARY KEY,
    type           TEXT NOT NULL,            -- note | email | call
    timestamp      TEXT,
    body           TEXT,
    metadata       TEXT,                     -- JSON: subject, direction, disposition, etc.
    fetched_at     TEXT
);

CREATE TABLE IF NOT EXISTS deal_engagements (
    deal_id        TEXT NOT NULL,
    engagement_id  TEXT NOT NULL,
    PRIMARY KEY (deal_id, engagement_id)
);

CREATE INDEX IF NOT EXISTS idx_de_deal ON deal_engagements (deal_id);
CREATE INDEX IF NOT EXISTS idx_de_eng  ON deal_engagements (engagement_id);

CREATE TABLE IF NOT EXISTS meta (
    key    TEXT PRIMARY KEY,
    value  TEXT
);
"""


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _dir_supports_unlink(db_path):
    """Some workspace mounts allow create/overwrite but forbid unlink. SQLite's
    WAL and rollback-journal modes both need to delete sidecar files, so on such
    mounts they fail with "disk I/O error" AND leave an undeletable hot-journal
    that corrupts later opens. Detect unlink support with a throwaway probe in
    the db's directory (never touching the db itself) so we can pick a safe
    journal mode up front."""
    d = os.path.dirname(os.path.abspath(db_path)) or "."
    probe = os.path.join(d, ".ec_unlink_probe")
    try:
        with open(probe, "w") as fh:
            fh.write("x")
        os.unlink(probe)
        return True
    except OSError:
        return False


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # WAL is best on local disk; MEMORY is the only safe mode on mounts that
    # forbid file deletion (it creates no on-disk journal/wal sidecars).
    if _dir_supports_unlink(db_path):
        conn.execute("PRAGMA journal_mode=WAL;")
    else:
        conn.execute("PRAGMA journal_mode=MEMORY;")
    return conn


def read_json(args):
    if getattr(args, "in_file", None):
        with open(args.in_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return json.load(sys.stdin)


def emit(args, obj):
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    out_file = getattr(args, "out_file", None)
    if out_file:
        with open(out_file, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text + "\n")


def _load_optional(path):
    if not path:
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def cmd_init(conn, args):
    conn.executescript(DDL)
    conn.execute(
        "INSERT INTO meta(key, value) VALUES('schema_version', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (SCHEMA_VERSION,),
    )
    conn.commit()
    return {"status": "ok", "schema_version": SCHEMA_VERSION}


def cmd_plan(conn, args):
    """Decide which deals are stale (changed or new) vs fresh (unchanged)."""
    deals = read_json(args)
    cached = {
        r["deal_id"]: r["hs_lastmodifieddate"]
        for r in conn.execute("SELECT deal_id, hs_lastmodifieddate FROM deals")
    }
    stale, fresh = [], []
    for d in deals:
        did = str(d["deal_id"])
        lm = d.get("hs_lastmodifieddate")
        if args.full_refresh or did not in cached or cached[did] != lm:
            stale.append(did)
        else:
            fresh.append(did)
    return {
        "stale": stale,
        "fresh": fresh,
        "counts": {"total": len(deals), "stale": len(stale), "fresh": len(fresh)},
    }


def cmd_need_bodies(conn, args):
    """Given associations for stale deals, return engagement IDs lacking a body."""
    assocs = read_json(args)
    have = {r["engagement_id"] for r in conn.execute("SELECT engagement_id FROM engagements")}
    fetch, cached_ids, seen = [], [], set()
    for a in assocs:
        eid = str(a["engagement_id"])
        if eid in seen:
            continue
        seen.add(eid)
        (cached_ids if eid in have else fetch).append(eid)
    return {
        "fetch": fetch,
        "cached": cached_ids,
        "counts": {
            "associations": len(seen),
            "to_fetch": len(fetch),
            "already_cached": len(cached_ids),
        },
    }


def cmd_ingest(conn, args):
    """Upsert deals, link associations, store new engagement bodies."""
    deals = _load_optional(args.deals)
    assocs = _load_optional(args.associations)
    engs = _load_optional(args.engagements)
    ts = now_iso()
    deal_n = assoc_n = eng_n = 0

    for d in deals:
        conn.execute(
            "INSERT INTO deals(deal_id, dealname, hs_lastmodifieddate, last_synced_at) "
            "VALUES(?,?,?,?) "
            "ON CONFLICT(deal_id) DO UPDATE SET "
            "  dealname=excluded.dealname, "
            "  hs_lastmodifieddate=excluded.hs_lastmodifieddate, "
            "  last_synced_at=excluded.last_synced_at",
            (str(d["deal_id"]), d.get("dealname"), d.get("hs_lastmodifieddate"), ts),
        )
        deal_n += 1

    for e in engs:
        conn.execute(
            "INSERT INTO engagements(engagement_id, type, timestamp, body, metadata, fetched_at) "
            "VALUES(?,?,?,?,?,?) "
            "ON CONFLICT(engagement_id) DO UPDATE SET "
            "  type=excluded.type, timestamp=excluded.timestamp, "
            "  body=excluded.body, metadata=excluded.metadata",
            (
                str(e["engagement_id"]),
                e.get("type"),
                e.get("timestamp"),
                e.get("body"),
                json.dumps(e.get("metadata", {}), ensure_ascii=False),
                ts,
            ),
        )
        eng_n += 1

    for a in assocs:
        conn.execute(
            "INSERT OR IGNORE INTO deal_engagements(deal_id, engagement_id) VALUES(?,?)",
            (str(a["deal_id"]), str(a["engagement_id"])),
        )
        assoc_n += 1

    conn.execute(
        "INSERT INTO meta(key, value) VALUES('last_sync_at', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (ts,),
    )
    conn.commit()
    return {
        "status": "ok",
        "deals_upserted": deal_n,
        "associations_linked": assoc_n,
        "engagements_stored": eng_n,
        "synced_at": ts,
    }


def cmd_export(conn, args):
    """Group cached engagements per deal into notes/emails/calls."""
    deal_filter = None
    if args.deals:
        raw = _load_optional(args.deals)
        deal_filter = {str(d["deal_id"]) if isinstance(d, dict) else str(d) for d in raw}

    rows = conn.execute(
        "SELECT de.deal_id AS deal_id, e.engagement_id, e.type, e.timestamp, e.body, e.metadata "
        "FROM deal_engagements de JOIN engagements e ON e.engagement_id = de.engagement_id "
        "ORDER BY e.timestamp"
    )
    out = {}
    bucket = {"note": "notes", "email": "emails", "call": "calls"}
    for r in rows:
        did = r["deal_id"]
        if deal_filter is not None and did not in deal_filter:
            continue
        deal_obj = out.setdefault(did, {"notes": [], "emails": [], "calls": []})
        item = {
            "engagement_id": r["engagement_id"],
            "timestamp": r["timestamp"],
            "body": r["body"],
            "metadata": json.loads(r["metadata"]) if r["metadata"] else {},
        }
        deal_obj[bucket.get(r["type"], r["type"] + "s")].append(item)
    return out


def cmd_stats(conn, args):
    def scalar(q):
        return conn.execute(q).fetchone()[0]

    by_type = {
        r["type"]: r["n"]
        for r in conn.execute("SELECT type, COUNT(*) AS n FROM engagements GROUP BY type")
    }
    last_sync = conn.execute("SELECT value FROM meta WHERE key='last_sync_at'").fetchone()
    return {
        "deals": scalar("SELECT COUNT(*) FROM deals"),
        "engagements": scalar("SELECT COUNT(*) FROM engagements"),
        "associations": scalar("SELECT COUNT(*) FROM deal_engagements"),
        "engagements_by_type": by_type,
        "last_sync_at": last_sync[0] if last_sync else None,
        "schema_version": SCHEMA_VERSION,
    }


COMMANDS = {
    "init": cmd_init,
    "plan": cmd_plan,
    "need-bodies": cmd_need_bodies,
    "ingest": cmd_ingest,
    "export": cmd_export,
    "stats": cmd_stats,
}


def build_parser():
    p = argparse.ArgumentParser(description="HubSpot deal-review engagement cache")
    p.add_argument("--db", required=True, help="Path to the SQLite cache file")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create schema (idempotent)")

    sp = sub.add_parser("plan", help="Stale vs fresh deals from current deal list")
    sp.add_argument("--in", dest="in_file", help="deals.json (default stdin)")
    sp.add_argument("--out", dest="out_file", help="output file (default stdout)")
    sp.add_argument("--full-refresh", action="store_true", help="Treat all deals as stale")

    sn = sub.add_parser("need-bodies", help="Engagement IDs lacking cached bodies")
    sn.add_argument("--in", dest="in_file", help="associations.json (default stdin)")
    sn.add_argument("--out", dest="out_file", help="output file (default stdout)")

    si = sub.add_parser("ingest", help="Store deals, associations, bodies")
    si.add_argument("--deals", help="deals.json")
    si.add_argument("--associations", help="associations.json")
    si.add_argument("--engagements", help="engagements.json (newly fetched bodies)")
    si.add_argument("--out", dest="out_file", help="output file (default stdout)")

    se = sub.add_parser("export", help="Cached engagements grouped per deal")
    se.add_argument("--deals", help="optional deal filter (deals.json or [ids])")
    se.add_argument("--out", dest="out_file", help="output file (default stdout)")

    sub.add_parser("stats", help="Cache counts")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    conn = connect(args.db)
    try:
        # Ensure schema exists for every command so a fresh DB never errors.
        conn.executescript(DDL)
        result = COMMANDS[args.command](conn, args)
        emit(args, result)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
