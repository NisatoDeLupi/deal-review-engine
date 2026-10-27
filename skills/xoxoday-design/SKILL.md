---
name: xoxoday-design
description: >
  Apply Xoxoday's brand look-and-feel to any deliverable — sales battle cards, pitch decks,
  PPTX presentations, one-pagers, internal reports, HTML pages. Use this skill whenever the
  user wants something "on-brand", "in Xoxoday style/colors", "branded", or mentions making a
  battle card, deck, slide, sales sheet, or competitor card for Xoxoday (or its products Plum,
  Empuls, Loyalife). It carries the full color system, typography, layout rules, voice, and
  ready-to-use code so the output looks like Xoxoday even with no other context.
---

# Xoxoday Design System

A self-contained brand kit for producing on-brand Xoxoday assets — primarily **battle cards** and
**PPTX decks**. Everything needed (colors, type, layout, voice, code) is in this skill; you do not
need any prior conversation context to use it.

> **Color accuracy note.** The hex values below are a *working palette* matched to Xoxoday's site
> and product brands (June 2026). They look correct and ship-ready, but are not lifted from the
> official brand file. Before external/customer-facing use, verify against the official kit at
> `https://www.xoxoday.com/downloads/xoxoday-brand-assets-usage-guidelines`. To replace a value,
> change it once in the palette table here and in `assets/pptx_theme.js` — everything else references it.

---

## 0. What Xoxoday is (context for shared use)

Xoxoday is an **AI-first enterprise platform for rewards, incentives, loyalty and payouts**. 5,000+
enterprises across 150+ countries run programs on it. Tagline energy: *"Make every relationship
rewarding."* Lead value: *"Human first."* The brand voice is **warm and human but enterprise-grade
and confident** — it celebrates outcomes, leans on proof (stats, logos), and avoids hype.

**Three products, one platform:**

- **Plum** — rewards, incentives & payouts (10M+ rewards, 150+ countries). Accent: plum/purple.
- **Empuls** — employee & sales engagement: recognition, rewards, surveys, commissions. Accent: gold/yellow.
- **Loyalife** — customer & channel loyalty, referrals, merchant offers.

Common audiences for these assets: enterprise buyers in HR, Sales, RevOps, Marketing, and Channel.

---

## 1. Color system

One hue dominates each layout; **ink + light neutrals carry ~70%**, coral is the single hero accent,
plum is secondary, gold is reserved for one standout number/label per view.

| Token | Name | Hex | Use |
|-------|------|-----|-----|
| `INK` | Plum Ink | `#1B1530` | Dark backgrounds, body text on light, titles |
| `PANEL` | Deep Plum | `#2A1E47` | Cards/panels on dark backgrounds |
| `CORAL` | Xoxoday Coral | `#F4593F` | **Hero accent** — kickers, rules, arrows, CTAs, emphasis |
| `CORALL` | Coral Light | `#FB7A63` | Secondary coral, hovers, soft fills |
| `PLUM` | Plum | `#7A3D9C` | Secondary panels, section breaks, alt headers |
| `GOLD` | Empuls Gold | `#FFBC2E` | Big stat numbers + one accent label per view (use sparingly) |
| `CLOUD` | Cloud | `#F6F4FA` | Light backgrounds (cool, faint plum tint — **never cream**) |
| `WHITE` | White | `#FFFFFF` | Cards on light |
| `SLATE` | Slate | `#6B6480` | Muted/secondary text on light |
| `ICE` | Ice | `#D9D2EA` | Muted/secondary text on dark |
| `MUTE` | Mute | `#9B92B5` | Footnotes, captions on dark |

Status colors (battle cards: win/loss/parity): win `#27B98A`, caution `#FFBC2E`, risk `#F4593F`.

**Dominance rule:** coral and gold never fight — gold appears at most once per slide/card, on a number.
Per product piece, you may swap the hero accent to that product's color (Plum → `#7A3D9C`, Empuls → `#FFBC2E`).

---

## 2. Typography

| Element | Font | Size (deck) | Size (battle card) |
|---------|------|-------------|--------------------|
| Display / title | **Trebuchet MS** bold (humanist sans — "human first") | 30–48 pt | 20–28 pt |
| Kicker / label | Trebuchet MS bold, UPPERCASE, letter-spaced | 12–13 pt | 9–11 pt |
| Body | **Calibri** | 13–17 pt | 9–11 pt |
| Caption / quote | Calibri italic | 12–14 pt | 8–10 pt |

Two families only. If Trebuchet MS is unavailable, fall back to Arial/Helvetica bold; keep Calibri (or Account_054) for body.

---

## 3. Layout & motif

- **Sandwich structure:** dark `INK` for title / section-divider / closing; light `CLOUD` for content.
- **Cards:** white on light, `PANEL` on dark, soft shadow, **6 px `CORAL` edge-bar** on the left (or top).
- **Repeated motif:** thin concentric rings (coral / plum / gold) bleeding off corners of dark slides.
- **Engagement motif (decks):** a `PLUM` pill with a `CORAL` "?" badge marks every audience question.
- **Brand tag:** small muted `XOXODAY · <deck name>` wordmark, bottom-right of content slides.
- **Whitespace:** ≥0.5" margins; 0.3–0.5" between blocks. Let it breathe.
- **Proof first:** lead with numbers and recognizable logos where you can — it's core to the brand.

### Avoid (AI-slop / off-brand tells)
- No underline accent rules beneath titles.
- No full-width colored header/footer bars or side ribbons.
- No cream/beige backgrounds (`#FFF8E1`, `#FAF0E6`, etc.) — use `CLOUD` or white.
- No text-only slides — every view carries a visual (card grid, stat, icon, motif).
- Don't let gold compete with coral; don't use more than two fonts.
- Never stretch/recolor/rotate the Xoxoday logo; keep clear space around it.

---

## 4. Logos & assets

Pull official SVGs from these paths (verify current URLs against the brand kit):

- Xoxoday primary: `https://www.xoxoday.com/Xoxoday/Logos/Xoxoday Primary.svg`
- Xoxoday all-white (for dark bg): `https://www.xoxoday.com/Xoxoday/Logos/Xoxoday All White.svg`
- Empuls (white+yellow): `https://www.xoxoday.com/Empuls/Logos/Empuls-White-Yellow.svg`
- Plum (all white): `https://www.xoxoday.com/Plum/Logos/Plum All White.svg`
- Loyalife (white): `https://www.xoxoday.com/Loyalife/Logos/Loyalife-White-Logo.svg`

On dark backgrounds use the white logo; on light use the primary. If a logo file isn't to hand,
set a text wordmark "XOXODAY" in Trebuchet MS bold with 2 pt letter-spacing as a stand-in.

---

## 5. Build recipes

### A) PPTX deck
1. Read `assets/pptx_theme.js` — it exports the palette + helpers (`titleSlide`, `sectionKicker`,
   `card`, `statCard`, `askRoom`, `rings`, `brandTag`). Require it in a pptxgenjs build script.
2. Use `LAYOUT_WIDE` (13.33×7.5). Sandwich: dark title → light content → dark close.
3. One idea per slide; every slide gets the rings motif (dark) or a card grid (light) + brand tag.
4. Render to PDF and eyeball for overflow before delivering (see `references/qa.md`).

Minimal usage is documented at the top of `assets/pptx_theme.js`.

### B) Battle card (comparison battlebook)
Read `references/battlecard.md` for the full structure and the HTML template
(`assets/battlecard_template.html`) that already carries the palette and type. The Xoxoday battle
card is a **long-form, multi-page comparison document** ("Xoxoday vs <Competitor>"), in this order:
title + hook → "Choose a platform" About blocks with capability equations → differentiator blocks →
AI capabilities → catalog showcase → the big **feature comparison table** (category bands + ✓ / ✗ /
Limited / No-info cells, "based on open-source data" footnote) → customer-logo trust wall → candid
"Last words" → awards. Be honest in the table (include ✓/✓ matches); render to PDF (A4 portrait).
A trimmed one-pager variant is described at the end of `references/battlecard.md`.

---

## 6. References in this skill
- `references/brand.md` - extended brand voice, messaging pillars, product one-liners, do/don'ts.
- `references/battlecard.md` - comparison-battlebook structure, section order, and the HTML template guide.
- `references/qa.md` - pre-delivery visual QA checklist.
- `assets/pptx_theme.js` - reusable pptxgenjs palette + slide helpers.
- `assets/battlecard_template.html` - branded long-form comparison-battlebook template.

*Sources: xoxoday.com . xoxoday.com/about . xoxoday.com/downloads/xoxoday-brand-assets-usage-guidelines (June 2026).*
