# Pattern: incremental cache for immutable child records

**The idea in one line:** records that cannot change after they are written only ever need fetching once, so make the expensive call once and detect change at the parent.

## When this applies

You repeatedly pull child records that hang off parent records, and fetching each child's body is its own API call:

| Parent | Children |
|---|---|
| CRM deal | notes, emails, call logs |
| Support ticket | replies, internal comments |
| Pull request | review comments, commits |
| Account | audit-log entries |

Two conditions make the repeated work avoidable:

1. **The children are immutable.** A logged call or a sent email never changes after it is recorded.
2. **The parent carries a last-modified timestamp** that moves when a child is added, so one cheap list call tells you which parents could possibly have anything new.

If both hold, a refresh costs one parent scan plus a body fetch for genuinely new children. Everything else comes from local storage at zero API cost.

## What it is worth

In the system this came from, a pipeline review was taking about six hours, and most of that was fetching engagement bodies that had already been fetched on the previous review. After caching, body-fetches dropped by about 90% on a normal refresh, and that is most of the gap between six hours and twenty minutes.

The test suite simulates the steady state directly: 100 parents, 5 children each, 3 parents change. A warm refresh costs over 95% less than the cold run.

## Use it

```python
from engagement_cache import EngagementCache, sync

cache = EngagementCache("cache.db")
plan = sync(cache,
            list_parents=api.list_parents,       # -> [(parent_id, last_modified), ...]
            list_child_ids=api.list_child_ids,   # -> [child_id, ...]
            fetch_children=api.fetch_children)   # -> [{"id": ..., "body": ...}, ...]

print(len(plan.fresh_parents), "parents served from cache with no API call")
rows = cache.children_of("deal-123")
```

Run the tests:

```bash
python test_engagement_cache.py
```

## Where it bites

- **It is only correct if the children really are immutable.** If a record can be edited after creation, you need an edit timestamp on the child and a different approach. Check this properly rather than assuming it, because "notes are append-only" is the kind of thing that is true until someone enables an edit button.
- **Deletion needs handling and is easy to miss.** Caching bodies forever is fine, but if a child is unlinked from its parent it must stop being returned. `store()` takes the full association list for exactly this reason, and there is a test for it.
- **Parent timestamps are not always trustworthy.** Some systems touch last-modified on unrelated field changes, which costs you a wasted association call but stays correct. The dangerous failure is the opposite: a system that adds a child *without* moving the parent timestamp. Verify that before relying on it, or add a periodic full refresh as a safety net.
- **The benefit depends on your refresh cadence.** Frequent reviews over mostly-unchanged parents is the best case. Quarterly reviews over a churning pipeline is close to the worst.
