# Case study: an AI deal-review engine

**Problem:** a pipeline review across a sales team took most of a working day, so it happened late, partially, or not at all.

**Result:** 6 hours to 20 minutes. Adopted beyond my own book into enterprise hunting, farming and revenue operations.

---

## What a pipeline review actually costs

The expensive part of a deal review is not judgement, it is reading. For each open deal someone has to reconstruct what happened from notes, emails and call logs, decide whether the stage is honest, decide what should happen next, write that somewhere the rep will see it, and create a task so it does not evaporate. Multiply by a team's open pipeline and the review is a day's work. Done monthly, it slips.

The parts that are mechanical are the reading, the scoring and the writing back. The part that needs a human is the judgement call on each deal, and that judgement is much cheaper once someone has laid out the evidence.

## Shape of the system

Five skills. A router that classifies an incoming request, and four segment workflows that each handle one slice of the pipeline:

| Skill | Segment | Fires on |
|---|---|---|
| router | orchestrator | request names no segment, spans several, or is a bare record ID |
| active | open pipeline | "pipeline review", "are reps following up", "hygiene check", "QBR prep" |
| dormant | deals parked at the dormant stage | "dormant", "passive pipeline" |
| closed-lost | lost deals worth re-engaging | "revive lost", "closed lost" |
| contact | companies with no deal object at all | "who should I approach", "contact revival" |

They are split by scope deliberately. The segments ask genuinely different questions: an open deal is a hygiene and next-action question, a lost deal is a re-engagement question, a company with no deal is a targeting question. Collapsing them into one skill produced vague output for all four.

Every segment follows the same six steps:

```
confirm scope -> pull from the CRM -> score -> build the review workbook
             -> gated writeback -> verify against the CRM
```

## Three decisions that made it work

### Read all three engagement types, not just notes

The first version read notes only, because notes are what a CRM review is nominally about. It produced confidently wrong summaries for a particular kind of rep: the ones who do their actual selling over email and never log a note. Pulling emails and calls as well changed the picture on a meaningful share of deals.

The general lesson: when a system summarises human work, find out where that work is actually recorded before deciding what to read. The answer is usually "not in the place designed for it".

### Cache what cannot change

Logged notes, emails and calls are immutable. Once written, the body never changes. So each engagement only ever needs fetching once, and a later review needs to pull only:

1. parents whose last-modified timestamp moved since the last sync, and
2. within those, only the child IDs not already cached.

Everything else is served from local storage with no API call at all. This cut body-fetches by about 90% after the first run and is most of the 6-hours-to-20-minutes gap. It is written up as a standalone module in [patterns/engagement-cache](patterns/engagement-cache/).

### Make the writeback gated, batched and visible

Bulk writes into a CRM are the part that can go badly wrong, and the failure mode is not a crash, it is quiet corruption that someone discovers three weeks later.

The rules the system enforces:

- **Workbook first.** The review is produced as a file and reviewed by a human before anything is written.
- **Test before bulk.** One or two records are written and checked before the full batch.
- **Batches are capped.** Write calls are chunked, because partial failure of a large batch is very hard to unwind.
- **One note and two tasks per deal**, with a defined owner and due dates offset so the rep acts first and the manager reviews afterwards.
- **A stop request is never overridden.** If a contact has asked not to be contacted, no score and no tier overrides that. It generates a note and no outreach task.
- **Exclusions are written down.** Any record the system skipped appears in the output with the reason. Silent filtering is how a review quietly stops covering a third of the pipeline.

### Retargeting is configuration, not a rewrite

Each skill carries a run-configuration block holding the rep in scope and their CRM owner ID. Pointing the review at a different rep is two values. Nothing about a specific person is baked into the logic, which is the only reason it could spread from my own book to other teams without me rewriting it each time.

## What it is made of

Roughly: a router plus four segment definitions, a shared reference layer describing the CRM's own quirks (which fields mean what, which stage IDs are terminal, which queries silently drop rows), workbook generators, the cache, and a backfill runner for historical slices.

The reference layer turned out to be as important as the code. Most of the early failures were not logic errors, they were the CRM behaving differently from its documentation: association queries that return results for one record type and silently nothing for another, properties that do not appear in a property-search index but can be requested directly, aggregate queries that cap out at a row limit without saying so. Each of those cost a session to find and a line to write down.

## Honest limitations

- **The scoring is a playbook, not a model.** It applies stage-based rules I wrote. It does not learn from outcomes, and I would not claim it predicts anything.
- **It depends on reps logging activity.** It reads more surfaces than a human reviewer bothers to, which helps, but a deal worked entirely over a channel the CRM never sees is still invisible to it.
- **"Revived deals" is a small number honestly counted.** Three to four dormant deals returned to active in a month. I have not attempted to claim the revenue, because attribution over that gap is not something I can defend.
- **The 90% fetch reduction is measured on my own usage pattern**, where reviews are frequent and most deals are unchanged between them. A team reviewing once a quarter would see less benefit.
