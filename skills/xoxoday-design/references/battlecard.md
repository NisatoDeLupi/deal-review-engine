# Battle card — structure & build guide

The Xoxoday battle card is a **long-form comparison battlebook** (multi-page document / PDF), not a
one-page sheet. It walks a buyer from positioning -> proof -> an exhaustive feature-by-feature
comparison -> social proof. Use this exact section order. Brand styling (colors, type) comes from
`SKILL.md`; this file governs **document structure**. Template: `assets/battlecard_template.html`.

## Section order (top -> bottom)

1. **Title + hook.** "Xoxoday vs {{Competitor}}" with a one-line hook in a tinted band, e.g.
   *"Similar is not identical: most solutions in this space seem identical; experienced first-hand,
   they're worlds apart."*

2. **"Choose a platform that's right for you"** - two "About" blocks:
   - **About Xoxoday** - 1 short positioning paragraph, then a **capability equation**:
     `Xoxoday = Rewards & Recognition + Surveys & Feedback + Social Intranet + Global Rewards Catalog + Perks & Benefits + People Analytics + Agentic AI`.
   - **About {{Competitor}}** - 1 paragraph (frame them honestly as foundational), then their shorter
     equation: `{{Competitor}} = ... + ... + ...`.
   - **Bridge line:** "While both share similarities, Xoxoday goes deeper - here's how."

3. **"Secure, scalable, purpose-built for global brands"** - 5-6 differentiator blocks, each a bold
   heading + 2-3 line paragraph. Default set: **Truly Global . Industry-Leading Value .
   Enterprise-Ready . Highly Configurable . Efficient Onboarding . Global Support**.

4. **AI capabilities across modules** - short intro, then a bullet list (bold lead-in + one line each):
   Agentic AI, AI skill mapping, trends/survival analysis, analytics co-pilot, recognition nudges,
   content moderation, sentiment analysis, etc.

5. **Global catalog showcase** (optional but recommended) - headline + a 3xN grid of reward-category
   cards (Gift Cards, Experiences, Travel, Merchandise, Prepaid, Charity, Swag, Top-ups, Financial).

6. **The feature comparison table** - the core. Columns: **Feature | What it does | Xoxoday | {{Competitor}}**.
   Rows are grouped under full-width **category band** rows. Use the category set that fits the deal;
   the standard library is:
   *Recognition & Rewards . Reward Catalogs . Perks & Benefits . Surveys . Social Intranet .
   Sales Incentive Management . Employee Profile . Community Groups . User Access Settings .
   AI Capabilities . Reports . Security & Compliance . Enterprise Capabilities . Integration.*
   - **Cell legend:** `check` full support . `cross` not available . **Limited** partial . **No info** unknown.
   - You may annotate a cell (e.g. *"Available on Xoxoday Compass"*) in small text under the check.
   - Be honest: include rows where the competitor wins or matches (check/check). Credibility comes from a
     fair table that still tilts clearly in our favor.
   - **Footnote under the table:** *"All comparisons are based on open-source data."*

7. **"Don't just take our word for it"** - a logo wall of recognizable customers (see `brand.md`).

8. **"Last words..."** - a short, candid closing paragraph: own that we're biased, then state the
   confident POV (UX, modern interface, infra, product vision) and the partnership promise.

9. **Awards / recognition** (optional) - a row of G2-style badges (Momentum Leader, High Performer, etc.).

## Content prompts (fill per competitor)
- Their honest one-paragraph positioning + capability equation (what they actually do).
- The 5-6 differentiators where we structurally win (map to the section-3 blocks).
- For each table category: which features are check/cross/Limited for the competitor (cite open-source data).
- 3-4 marquee customer logos relevant to this buyer's industry.
- The closing "last words" paragraph in Xoxoday's voice.

## Style rules
- Honest comparison only. Mark unknowns **No info** rather than guessing; mark anything unverified `[verify]`.
- Category bands use a soft brand tint with bold colored label; keep the table airy (don't cram).
- `check` in win-green, `cross` in risk-coral (or muted), **Limited** in caution-gold/slate. One accent system; no rainbow.
- This is a multi-page document - let it breathe across pages; don't shrink type below 9 pt to force fit.
- Footer on every page: `www.xoxoday.com` + page number (matches the source document convention).

## Build steps
1. Copy `assets/battlecard_template.html`; fill the `{{placeholders}}` and repeat table rows/bands as needed.
2. Pull positioning, differentiators, proof and logos from `references/brand.md`; competitor specifics
   from the user or open-source research.
3. Render to PDF for sharing: open in a browser -> Print -> Save as PDF (A4 portrait), or use a headless
   converter. Run the `references/qa.md` checklist before sending.

> Need a quick one-pager instead of the full book? Keep sections 1, 3 (condensed to 4 bullets),
> a trimmed table of ~8 marquee rows, and 8 (last words). Same order, fewer rows.
