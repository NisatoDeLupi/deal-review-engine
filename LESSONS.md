# What I learned building this

## On letting AI write to production systems

**Never share scratch state across parallel writers.** My first bulk CRM write created 20 duplicate tasks. Two sub-agents were working in parallel and shared a scratch directory, so each believed it owned the same queue and both wrote. The fix was a file-per-call pattern where every write has its own named payload and nothing is inferred from shared state. The next run, larger than the first, produced zero duplicates.

I neutralised the duplicates rather than deleting them, which was the right call: deleting them would have destroyed the evidence of what had actually happened.

**Gate every write behind a human-readable artifact.** The deliverable is the review sheet, not the write. A person approves the sheet, and only then does anything touch the system of record. This costs a round trip and has repeatedly been worth it.

**Test on one or two records before the batch.** Obvious, routinely skipped, and the one time it is skipped is the time the field mapping is wrong.

**Cap batch sizes.** Partial failure of a large batch is very hard to unwind, because you often cannot tell which half succeeded.

**Write exclusions down.** Any record the system skipped should appear in the output with a reason. Silent filtering is how a review quietly stops covering a third of the pipeline and nobody notices for two months.

**Stop rather than guess.** The meeting allocator ships with its owner map blank and refuses to run until someone fills it. A wrong owner is slow and political to unwind; an error message costs thirty seconds. Any component that assigns work to a human should prefer failing loudly over assigning plausibly.



## On building with an LLM as the implementation tool

**Write the rules of record down, with dates and attribution.** Every decision that shapes behaviour lives in a file with the date it was made and the reasoning. Six months later nobody remembers why a category is excluded, and a reconstruction is not the same as a record. Mine held through three separate attempts to widen a filter, each of which had a plausible case.

**Derive rules from decisions, not from definitions.** Encoding a tidy written profile did not survive contact with real data, because the written version was a neat summary of a messier judgement. Qualifying 65 real rows by hand and deriving the rules from those decisions worked. Measuring the result against those same rows gave an agreement rate worth reporting.

**Keep the disagreements.** Two of the 65 still disagree. Tuning them away would have produced a rounder number and destroyed the only honest signal about where the boundary is.

**Mark what the machine proposed versus what a human ratified.** A provenance field distinguishing the two, checked before anyone quotes a row, prevents a draft becoming policy by being read twice.

**Most early failures are environmental, not logical.** Association queries that return results for one record type and silently nothing for another. Fields that do not appear in a search index but can be requested directly. Aggregates that cap at a row limit without saying so. Each cost a session to find and one line to write down, and the written-down version is what stopped the next person losing the same session.

**Split skills by scope, not by topic.** One company deserves research and a brief. A list of 300 deserves one consistent rule applied 300 times. A booked meeting deserves an ownership decision. Collapsing those into one skill because they are all "about accounts" produced output that was vague for all three.

**Retargeting should be configuration.** Putting the person-specific values in a run-configuration block, with nothing about a named individual in the logic, is the only reason the tool spread to other teams without being rewritten each time.
