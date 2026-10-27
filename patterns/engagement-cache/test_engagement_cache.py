"""Tests for the engagement cache.

The claim being tested is the one that matters commercially: a second refresh
over mostly-unchanged data costs almost no API calls. Run with:

    python test_engagement_cache.py
"""

import sys

from engagement_cache import EngagementCache, sync


class FakeAPI:
    """Stands in for a CRM. Counts every call so the tests can assert on cost."""

    def __init__(self):
        # parent -> (last_modified, [child ids])
        self.parents = {
            "d1": ["2026-01-01", ["c1", "c2"]],
            "d2": ["2026-01-01", ["c3"]],
            "d3": ["2026-01-01", ["c4", "c5", "c6"]],
        }
        self.calls = {"list_parents": 0, "list_child_ids": 0, "fetch_bodies": 0}

    def list_parents(self):
        self.calls["list_parents"] += 1
        return [(pid, v[0]) for pid, v in self.parents.items()]

    def list_child_ids(self, pid):
        self.calls["list_child_ids"] += 1
        return list(self.parents[pid][1])

    def fetch_children(self, ids):
        ids = list(ids)
        self.calls["fetch_bodies"] += len(ids)
        return [{"id": i, "kind": "note", "created": "2026-01-01",
                 "body": "body of %s" % i} for i in ids]

    # -- mutations a real CRM would produce -------------------------------

    def add_child(self, pid, cid, modified):
        self.parents[pid][1].append(cid)
        self.parents[pid][0] = modified

    def remove_child(self, pid, cid, modified):
        self.parents[pid][1].remove(cid)
        self.parents[pid][0] = modified


RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def main():
    api = FakeAPI()
    cache = EngagementCache()

    # --- first run: everything is cold -----------------------------------
    plan = sync(cache, api.list_parents, api.list_child_ids, api.fetch_children)
    check("first run treats all parents as stale", len(plan.stale_parents) == 3,
          "stale=%d" % len(plan.stale_parents))
    check("first run fetches every body", api.calls["fetch_bodies"] == 6,
          "fetched=%d" % api.calls["fetch_bodies"])
    check("children are readable back", len(cache.children_of("d3")) == 3)
    check("bodies survive the round trip",
          cache.children_of("d2")[0]["body"] == "body of c3")

    # --- second run: nothing changed -------------------------------------
    before = api.calls["fetch_bodies"]
    plan = sync(cache, api.list_parents, api.list_child_ids, api.fetch_children)
    check("unchanged parents are all fresh", len(plan.fresh_parents) == 3,
          "fresh=%d" % len(plan.fresh_parents))
    check("unchanged refresh costs zero body fetches",
          api.calls["fetch_bodies"] == before,
          "fetched %d extra" % (api.calls["fetch_bodies"] - before))
    check("unchanged refresh costs zero association calls",
          api.calls["list_child_ids"] == 3,
          "association calls=%d" % api.calls["list_child_ids"])
    check("cache still serves the data", len(cache.children_of("d1")) == 2)

    # --- third run: one parent gains one child ---------------------------
    api.add_child("d1", "c7", "2026-02-01")
    before = api.calls["fetch_bodies"]
    plan = sync(cache, api.list_parents, api.list_child_ids, api.fetch_children)
    check("only the changed parent is stale", plan.stale_parents == ["d1"],
          "stale=%s" % plan.stale_parents)
    check("only the genuinely new child is fetched",
          api.calls["fetch_bodies"] - before == 1,
          "fetched=%d" % (api.calls["fetch_bodies"] - before))
    check("the new child is linked", len(cache.children_of("d1")) == 3)
    check("previously cached siblings were not refetched",
          cache.cached_child_count() == 7, "cached=%d" % cache.cached_child_count())

    # --- fourth run: a child is unlinked from its parent -----------------
    api.remove_child("d3", "c5", "2026-03-01")
    before = api.calls["fetch_bodies"]
    sync(cache, api.list_parents, api.list_child_ids, api.fetch_children)
    check("unlinked child stops being returned",
          [c["id"] for c in cache.children_of("d3")] == ["c4", "c6"],
          "got=%s" % [c["id"] for c in cache.children_of("d3")])
    check("unlinking costs no fetches", api.calls["fetch_bodies"] == before)
    check("the body is still cached, just not linked", cache.cached_child_count() == 7)

    # --- the headline claim ----------------------------------------------
    # A realistic steady state: 100 parents, 5 children each, 3 parents change.
    api2, cache2 = FakeAPI(), EngagementCache()
    api2.parents = {"p%d" % i: ["v1", ["p%dc%d" % (i, j) for j in range(5)]]
                    for i in range(100)}
    sync(cache2, api2.list_parents, api2.list_child_ids, api2.fetch_children)
    cold = api2.calls["fetch_bodies"]
    for i in range(3):
        api2.add_child("p%d" % i, "p%dc_new" % i, "v2")
    before = api2.calls["fetch_bodies"]
    sync(cache2, api2.list_parents, api2.list_child_ids, api2.fetch_children)
    warm = api2.calls["fetch_bodies"] - before
    reduction = 1 - (warm / float(cold))
    check("steady-state refresh is >95% cheaper than a cold run", reduction > 0.95,
          "cold=%d warm=%d reduction=%.1f%%" % (cold, warm, reduction * 100))

    # --- report -----------------------------------------------------------
    width = max(len(n) for n, _, _ in RESULTS)
    failed = 0
    for name, ok, detail in RESULTS:
        if not ok:
            failed += 1
        print("%s %s %s" % ("PASS" if ok else "FAIL", name.ljust(width),
                            ("  <- " + detail) if detail and not ok else ""))
    print("\n%d passed, %d failed" % (len(RESULTS) - failed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
