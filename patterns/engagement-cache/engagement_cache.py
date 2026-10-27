"""Incremental cache for immutable child records fetched from an expensive API.

The situation this is for: you repeatedly pull child records (notes, emails, call
logs, comments, audit entries) that hang off parent records (deals, tickets,
accounts). Fetching a child body is a separate API call and that is where the
time goes.

Two properties make the repeated work avoidable:

  1. The children are immutable. Once written, a logged note or a sent email
     never changes. So a child only ever needs fetching ONCE, ever.
  2. The parent carries a last-modified timestamp that moves when a child is
     added, so one cheap list call tells you which parents could possibly have
     new children.

Together those mean a refresh costs: one parent scan, plus a body fetch for
genuinely new children only. Parents whose timestamp has not moved are served
entirely from local storage with no API call at all.

This module is deliberately vendor-neutral and stdlib-only. You supply two
callables and it handles the bookkeeping:

    list_parents()        -> iterable of (parent_id, last_modified)
    list_child_ids(pid)   -> iterable of child_id for that parent
    fetch_children(ids)   -> iterable of dicts with at least {"id": ...}

Usage:

    cache = EngagementCache("cache.db")
    plan = cache.plan(list_parents())
    # plan.stale_parents  -> parents whose timestamp moved
    # plan.fresh_parents  -> served from cache, zero API cost
    for pid in plan.stale_parents:
        ids = list_child_ids(pid)
        missing = cache.missing(ids)          # only the ones we have never seen
        cache.store(pid, fetch_children(missing))
    cache.mark_synced(plan)
    rows = cache.children_of(parent_id)

Correctness note: this is only safe when children really are immutable. If a
record can be edited after creation, you need an edit timestamp on the child and
a different strategy. Deletion is handled: `children_of` reflects the
association list last seen for that parent, so a child that disappears from the
parent stops being returned even though its body stays cached.
"""

import json
import sqlite3
import time
from collections import namedtuple

SyncPlan = namedtuple("SyncPlan", "stale_parents fresh_parents seen")

SCHEMA = """
CREATE TABLE IF NOT EXISTS parents (
    parent_id     TEXT PRIMARY KEY,
    last_modified TEXT,
    last_synced   REAL
);
CREATE TABLE IF NOT EXISTS children (
    child_id  TEXT PRIMARY KEY,
    kind      TEXT,
    created   TEXT,
    body      TEXT
);
CREATE TABLE IF NOT EXISTS links (
    parent_id TEXT,
    child_id  TEXT,
    PRIMARY KEY (parent_id, child_id)
);
CREATE INDEX IF NOT EXISTS links_parent ON links (parent_id);
"""


class EngagementCache:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.stats = {"body_fetches": 0, "parents_scanned": 0, "parents_skipped": 0}

    # -- planning ---------------------------------------------------------

    def plan(self, parents):
        """Split parents into those that changed and those served from cache.

        `parents` is an iterable of (parent_id, last_modified). last_modified is
        compared as an opaque string, so any monotonic format works as long as
        it is used consistently.
        """
        known = {r["parent_id"]: r["last_modified"] for r in self.db.execute(
            "SELECT parent_id, last_modified FROM parents")}
        stale, fresh, seen = [], [], {}
        for pid, modified in parents:
            pid = str(pid)
            seen[pid] = modified
            if known.get(pid) != modified:
                stale.append(pid)
            else:
                fresh.append(pid)
        self.stats["parents_scanned"] += len(seen)
        self.stats["parents_skipped"] += len(fresh)
        return SyncPlan(stale_parents=stale, fresh_parents=fresh, seen=seen)

    def missing(self, child_ids):
        """Of these child IDs, which have we never fetched a body for?"""
        ids = [str(c) for c in child_ids]
        if not ids:
            return []
        have = set()
        # chunked so a long association list cannot blow the SQL variable limit
        for i in range(0, len(ids), 500):
            chunk = ids[i:i + 500]
            q = "SELECT child_id FROM children WHERE child_id IN (%s)" % ",".join("?" * len(chunk))
            have.update(r["child_id"] for r in self.db.execute(q, chunk))
        return [c for c in ids if c not in have]

    # -- writing ----------------------------------------------------------

    def store(self, parent_id, records, all_child_ids=None):
        """Cache child bodies and record which parent they hang off.

        `all_child_ids` is the full association list for the parent. Pass it so
        links to already-cached children are kept and links to children that
        have gone away are dropped. If omitted, only the supplied records link.
        """
        parent_id = str(parent_id)
        rows = list(records)
        self.stats["body_fetches"] += len(rows)
        with self.db:
            for r in rows:
                self.db.execute(
                    "INSERT OR REPLACE INTO children (child_id, kind, created, body) VALUES (?,?,?,?)",
                    (str(r["id"]), r.get("kind"), r.get("created"),
                     r.get("body") if isinstance(r.get("body"), str) else json.dumps(r.get("body"))))
            links = [str(c) for c in (all_child_ids if all_child_ids is not None
                                      else [r["id"] for r in rows])]
            self.db.execute("DELETE FROM links WHERE parent_id = ?", (parent_id,))
            self.db.executemany("INSERT OR IGNORE INTO links (parent_id, child_id) VALUES (?,?)",
                                [(parent_id, c) for c in links])

    def mark_synced(self, plan):
        """Record the observed timestamps so the next plan() can skip them."""
        now = time.time()
        with self.db:
            self.db.executemany(
                "INSERT OR REPLACE INTO parents (parent_id, last_modified, last_synced) VALUES (?,?,?)",
                [(pid, mod, now) for pid, mod in plan.seen.items()])

    # -- reading ----------------------------------------------------------

    def children_of(self, parent_id):
        return [dict(r) for r in self.db.execute(
            "SELECT c.child_id AS id, c.kind, c.created, c.body "
            "FROM links l JOIN children c ON c.child_id = l.child_id "
            "WHERE l.parent_id = ? ORDER BY c.created", (str(parent_id),))]

    def cached_child_count(self):
        return self.db.execute("SELECT COUNT(*) AS n FROM children").fetchone()["n"]

    def close(self):
        self.db.close()


def sync(cache, list_parents, list_child_ids, fetch_children):
    """Convenience wrapper tying the three callables together for one refresh."""
    plan = cache.plan(list_parents())
    for pid in plan.stale_parents:
        child_ids = [str(c) for c in list_child_ids(pid)]
        missing = cache.missing(child_ids)
        fetched = list(fetch_children(missing)) if missing else []
        cache.store(pid, fetched, all_child_ids=child_ids)
    cache.mark_synced(plan)
    return plan
