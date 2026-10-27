---
name: backfill-manual-run-pause-schedule
description: Pause the fullreview-backfill scheduled task whenever manually running slices
type: feedback
---

When Abhimanyu is manually running the deal-review-fullreview-backfill slices, pause (disable) the `deal-review-fullreview-backfill` scheduled task so automatic 15-min runs don't collide with manual ones. Re-enable it only when he says he's done running manually.

**Why:** Concurrent auto + manual runs on the same queue/DB risk clobbering progress and duplicate work.
**How to apply:** On "I'm running this manually" (or similar), call update_scheduled_task enabled:false; when he says to resume, enabled:true. Relates to [[hubspot-engagement-association-mapping]].
