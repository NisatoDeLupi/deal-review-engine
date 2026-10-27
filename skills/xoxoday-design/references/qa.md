# Pre-delivery visual QA checklist

Always render and look before shipping. For PPTX: convert to PDF, then to images, and inspect.

```bash
# PPTX → PDF → JPGs (LibreOffice + poppler)
soffice --headless --convert-to pdf deck.pptx
pdftoppm -jpeg -r 110 deck.pdf slide
```

Check every slide/card for:

- [ ] **Title fits on intended line(s)** — long titles wrapping into the subtitle is the #1 defect.
      Drop title size or shorten copy if it wraps unexpectedly.
- [ ] **No overflow** — text inside its box; nothing cut at edges or spilling past bounds.
- [ ] **No overlap** — text not running through shapes/rings; cards not touching (<0.3" gap).
- [ ] **Contrast** — light text only on dark, dark text only on light. No coral text on plum.
- [ ] **Accent discipline** — one hero accent; gold used at most once per view, on a number.
- [ ] **Margins** — ≥0.5" from slide edges; consistent gaps (pick 0.3" or 0.5", keep it).
- [ ] **Brand tag + motif present** on content slides; logo correct variant for background.
- [ ] **No placeholder text** — grep for `{{`, `xxx`, `lorem`, `TODO`, `[verify]`.
- [ ] **Claims verified** — stats/quotes are real and current.

Fix the real issues in one pass; don't chase sub-pixel nudges.
