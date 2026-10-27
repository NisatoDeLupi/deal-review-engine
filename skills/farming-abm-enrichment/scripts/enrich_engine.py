"""
enrich_engine.py — rule-based engine for the Xoxoday Farming ABM Enrichment skill.

This module implements the deterministic parts of the enrichment workflow
described in the skill's SKILL.md (Steps 4–7) and references/cross-sell-logic.md.

It is invoked during Phase 1 of a run, when the rule-based columns are populated
in a single pass across all rows before any LLM work begins.

Public helpers that callers typically use:
  - determine_growth_stage(headcount, divisions_count=0) -> str
  - recommend_products(row) -> list[str]
  - build_outreach_tracks(recs, addon_pitch) -> str
  - persona_block(product) -> str        # Tier 1 / Tier 2 personas
  - priority_score(row) -> int           # 1..10
  - build_enrichment(row, company, custom_summary, custom_divisions,
                     custom_growth_override=None) -> dict
      Returns a dict with keys: summary, divisions, growth, recs, tracks,
      use_cases, personas, pitch, triggers, score — i.e. the full set of
      9 new columns for a single row. `custom_summary` and `custom_divisions`
      come from Phase 2 (AI judgment); everything else is computed here.
  - write_batch(out_path, sheet_name, batch_results) -> int
      Writes a list of (row_num, enrichment_dict) into columns 30..39 of the
      named sheet and saves the workbook. Use this at the end of every
      Phase-2 batch so partial progress is durable.

The row dict passed to these helpers should be the header->value mapping read
from openpyxl, with the exact header strings from the source workbook
(including the "B2C Customer Base\n(Loyalife Scope)" newline).
"""
from __future__ import annotations
import re
from typing import Dict, Any, List, Optional


def lower_bound(headcount):
    if headcount is None:
        return 0
    s = str(headcount).replace(",", "")
    m = re.search(r"(\d+)", s)
    return int(m.group(1)) if m else 0


def is_b2c(b2c_val):
    if b2c_val is None:
        return False
    s = str(b2c_val).strip()
    if s == "" or s.lower() in ("no", "none", "n/a"):
        return False
    return True


def channel_present(chan_val):
    if chan_val is None:
        return False
    s = str(chan_val).strip().lower()
    if s == "" or s in ("no", "none", "n/a"):
        return False
    return True


def own_platform_yes(plat_val):
    if plat_val is None:
        return False
    s = str(plat_val).strip().lower()
    return s.startswith("yes")


def normalize_product(prod_val):
    if prod_val is None:
        return []
    s = str(prod_val).strip()
    products = []
    for p in ["Empuls", "Plum", "Compass", "Loyalife"]:
        if p.lower() in s.lower():
            products.append(p)
    return products


def fit_strong(val):
    return val is not None and str(val).strip().lower() == "strong"

def fit_moderate(val):
    return val is not None and str(val).strip().lower() == "moderate"


def determine_growth_stage(headcount, divisions_count=0):
    hc = lower_bound(headcount)
    if hc >= 50000 or divisions_count >= 3:
        return "Conglomerate"
    if hc >= 5000:
        return "Enterprise"
    if hc >= 2000:
        return "Mid-Market"
    if hc >= 800:
        return "Scale-up"
    if hc >= 200:
        return "Growth"
    if hc > 0 and hc < 200:
        return "Startup"
    return "Unknown"


def recommend_products(row):
    current = normalize_product(row.get("Product Currently Used"))
    hc = lower_bound(row.get("Est. Headcount"))
    sales_size = lower_bound(row.get("Sales Team Size"))
    b2c = is_b2c(row.get("B2C Customer Base\n(Loyalife Scope)"))
    channel = channel_present(row.get("Channel Partner Network"))
    compass_fit = row.get("Compass Fit")
    loyalife_fit = row.get("Loyalife Fit")
    recs = set()

    if "Plum" in current:
        if hc >= 500: recs.add("Empuls")
        if b2c: recs.add("Loyalife")
        if hc < 500 and not b2c: recs.add("Empuls")
        if sales_size >= 200: recs.add("Compass")

    if "Empuls" in current:
        recs.add("Plum")
        if b2c: recs.add("Loyalife")
        if sales_size >= 200: recs.add("Compass")

    if "Compass" in current:
        if hc >= 500: recs.add("Empuls")
        else: recs.add("Plum")
        if b2c:
            recs.add("Plum"); recs.add("Loyalife")
            if hc >= 500: recs.add("Empuls")

    if "Loyalife" in current:
        if hc >= 500: recs.add("Empuls")
        recs.add("Plum")
        if sales_size >= 200: recs.add("Compass")

    if channel: recs.add("Loyalife")
    if fit_strong(loyalife_fit): recs.add("Loyalife")
    if sales_size >= 200 or fit_strong(compass_fit) or fit_moderate(compass_fit):
        recs.add("Compass")

    for p in current:
        recs.discard(p)

    order = ["Empuls", "Plum", "Compass", "Loyalife"]
    return [p for p in order if p in recs]


def empuls_addon_applicable(row):
    return "Empuls" in normalize_product(row.get("Product Currently Used"))


PERSONAS = {
    "Empuls": (["CHRO / Chief People Officer", "VP HR / VP People Operations", "Head HR / Head Employee Experience", "Director HR / Director Employee Engagement"],
               ["Employee Engagement Manager / Total Rewards Manager"]),
    "Plum": (["Head of Rewards / Head of R&R", "Head HR / VP HR (employee gifting)", "Head of Admin / Head of Procurement", "Head of Partnerships / VP Partnerships"],
             ["HR Manager / Admin Manager"]),
    "Compass": (["CRO / Chief Revenue Officer", "VP Sales / SVP Sales", "Head of Sales / Head of Sales Operations", "VP Revenue Operations"],
                ["Sales Operations Manager / Incentive Compensation Manager"]),
    "Loyalife": (["CMO / VP Marketing", "Chief Customer Officer / Chief Experience Officer", "Head of CX / Head of Retention", "Head of Loyalty / Head of CRM"],
                 ["CRM Manager / Retention Marketing Manager"]),
}


def persona_block(product):
    t1, t2 = PERSONAS[product]
    return "Tier 1: " + " | ".join(t1) + " || Tier 2: " + t2[0]


OUTREACH_PERSONA_SHORT = {
    "Empuls": "VP HR / Head People Operations",
    "Plum": "Head HR / Head Admin / Head Procurement",
    "Compass": "VP Sales / CRO / Head Sales Ops",
    "Loyalife": "CMO / Head of CX / Head of Loyalty",
}


def build_outreach_tracks(recs, addon_pitch):
    tracks = [f"{p} -> {OUTREACH_PERSONA_SHORT[p]}" for p in recs]
    if addon_pitch:
        tracks.append("Empuls Add-On Modules -> HRBP / L&D Head / TA Lead")
    return " / ".join(tracks)


def pitch_empuls(company, current):
    return (f"We're proud to be partnered with {company} for your R&R programs - and reaching out because there's a natural next step many of our clients take that delivers significantly more impact. Several HR leaders we work with upgraded from a standalone rewards catalogue to Empuls - our full employee engagement platform - and saw eNPS improve by 20+ points within two quarters. Empuls connects recognition, pulse surveys, peer appreciation, and milestone rewards in one place. No additional vendors, no new logins for employees. Worth a 20-minute walkthrough tailored to {company}'s size? CTA: Schedule a Call ->")


def pitch_empuls_addon(company):
    return (f"We're glad to be powering {company}'s employee engagement through Empuls - and there are three add-on modules that activate natively into your existing setup without a new vendor, new login for employees, or additional procurement cycle: (1) Fitness Challenges - team wellness goals with automated reward milestones, 3x participation vs. standalone apps; (2) L&D Incentives - points and rewards tied to course completions and certifications, directly within your LMS; (3) Referral Incentives - automated reward payouts across the full referral journey from nomination through successful hire. Which of these is most relevant to your priorities right now? Happy to show you a focused 20-minute walkthrough. CTA: Book a Walkthrough ->")


def pitch_loyalife(company, current, industry=""):
    if "Empuls" in current:
        warm = f"We're honored to be partnered with {company} for your employee R&R programs - and in addition to that, we also work with companies like yours on the customer loyalty side, which is what prompted this note."
    else:
        kind = "Plum rewards" if "Plum" in current else "sales incentives"
        warm = f"We're glad to be partnered with {company} on {kind} - and wanted to connect on a separate opportunity on the customer side."
    ind = f" in {industry}" if industry else ""
    return (f"{warm} Loyalife is our white-labeled, API-first customer loyalty platform. Your customers earn and redeem from a catalog of 10M+ rewards - flights, hotels, gift cards, merchandise - across 50+ countries. Brands{ind} using Loyalife have seen customer lifetime value grow by 25-35%, with most going live in under 8 weeks. Given we're already a vendor at {company}, the commercial and compliance path to getting started is meaningfully shorter than from scratch. CTA: Book a Discovery Call ->")


def pitch_compass(company, current):
    return (f"We're glad to be partnered with {company} for your R&R programs - and in addition to that, we also offer a solution built specifically for sales leaders, which is what I wanted to share with you. Compass replaces manual SPIFFs and spreadsheet-based commission tracking with real-time leaderboards, automated payouts, and behavior-specific incentive nudges - all visible to reps from any device. Sales leaders using Compass report 20-30% improvement in quota attainment within two quarters, with a significant reduction in incentive disputes and ops overhead. Since {company} already runs on Xoxoday infrastructure, the integration path is materially faster than a cold deployment. CTA: Book a Demo ->")


def pitch_plum(company, current):
    return (f"We're proud to power {company}'s employee engagement through Empuls - and many HR and admin leaders we work with add Plum as the rewards catalog that sits alongside it. Given {company}'s headcount and gifting volume, Plum removes procurement overhead entirely - your team issues personalised digital gifts in minutes from a single dashboard with full reporting and no MOQ. CTA: Schedule a Call ->")


def use_cases_empuls(row, company):
    hc_text = row.get("Est. Headcount") or "the company"
    industry = row.get("Industry / Vertical") or "operations"
    return (f"(1) Run continuous recognition + peer appreciation across {hc_text} employees in {industry} to replace ad-hoc, manager-driven R&R cycles. (2) Quarterly pulse surveys with anonymous feedback to detect engagement drift before attrition spikes. (3) Service milestone, birthday and wedding anniversary automation tied to the existing Plum catalog.")


def use_cases_plum(row, company):
    industry = row.get("Industry / Vertical") or "operations"
    return (f"(1) Replace gift-voucher procurement with a self-serve, no-MOQ digital catalog for HR and Admin teams. (2) Festival, R&R, joining bonus and referral payouts on a single platform with full audit trail. (3) Vendor and partner gifting from the same wallet - relevant for {industry} channel programs.")


def use_cases_compass(row, company):
    sales = row.get("Sales Team Size") or "the sales team"
    return (f"(1) Automate commission calculation and SPIFF payouts for {sales} sales reps - eliminating the spreadsheet + manual reconciliation cycle. (2) Real-time leaderboards tied to daily/weekly quota nudges visible on rep mobile devices. (3) Region and product-line-specific incentive plans with on-the-fly modeling for sales leadership.")


def use_cases_loyalife(row, company):
    b2c = row.get("B2C Customer Base\n(Loyalife Scope)")
    industry = row.get("Industry / Vertical") or ""
    b2c_text = f"{b2c} consumer base" if b2c else "growing consumer base"
    return (f"(1) White-labeled points + tier loyalty program for {company}'s {b2c_text} - earn on transactions, redeem from 10M+ global catalog. (2) Channel/partner loyalty layer with structured incentive tiers for the existing distribution network. (3) API-first integration with the existing {industry} platform - no separate front-end build required.")


def strategic_triggers(row, company, recs):
    triggers = []
    hc = lower_bound(row.get("Est. Headcount"))
    sales = lower_bound(row.get("Sales Team Size"))
    b2c = is_b2c(row.get("B2C Customer Base\n(Loyalife Scope)"))
    channel = channel_present(row.get("Channel Partner Network"))
    plat = own_platform_yes(row.get("Own Platform? (Relevant for API Usecase as well as Loyalty)"))
    current = normalize_product(row.get("Product Currently Used"))
    industry = (row.get("Industry / Vertical") or "")

    if hc >= 500:
        triggers.append(f"Headcount {row.get('Est. Headcount')} crosses the Empuls threshold - structured engagement ROI typically realized at this scale")
    if hc < 500 and "Plum" in current:
        triggers.append("Sub-500 headcount - frame Empuls as a 'start small, scale up' deployment alongside existing Plum usage")
    if b2c:
        triggers.append(f"B2C base of {row.get('B2C Customer Base' + chr(10) + '(Loyalife Scope)')} - immediate Loyalife opportunity with no current loyalty layer identified")
    if channel:
        triggers.append("Channel partner network signals opportunity for a structured partner incentive program via Loyalife")
    if plat and channel:
        triggers.append("Own platform + channel partners - flag API Marketplace as a future conversation (not actively pitched today)")
    elif plat:
        triggers.append("Own platform - API Marketplace becomes a relevant future conversation")
    if sales >= 200:
        triggers.append(f"Sales team of {row.get('Sales Team Size')} - Compass automates the SPIFF/commission layer that typically runs on spreadsheets at this size")
    if "Empuls" in current:
        triggers.append("Already on Empuls - Fitness, L&D and Referral add-on modules can be activated natively without a new procurement cycle")
    if industry.lower().startswith("it") or "saas" in industry.lower():
        triggers.append("IT/SaaS vertical - L&D Incentives and Referral Incentives add-ons typically show the strongest engagement uplift")

    if not triggers:
        triggers.append("Existing Xoxoday vendor relationship shortens commercial and compliance cycle for any add-on product")

    return " | ".join(triggers[:4])


def priority_score(row):
    score = 0.0
    e_fit = row.get("Empuls (Identify accounts on Plum or Empuls Gifting)")
    c_fit = row.get("Compass Fit")
    l_fit = row.get("Loyalife Fit")
    api_fit = row.get("API Marketplace Fit")
    for f in (e_fit, c_fit, l_fit, api_fit):
        if f is None:
            continue
        s = str(f).strip().lower()
        if s == "strong": score += 1.5
        elif s == "moderate": score += 0.5

    if is_b2c(row.get("B2C Customer Base\n(Loyalife Scope)")): score += 1.5
    if own_platform_yes(row.get("Own Platform? (Relevant for API Usecase as well as Loyalty)")): score += 1.0
    if channel_present(row.get("Channel Partner Network")): score += 0.5
    score = min(score, 10.0)

    tier = (row.get("Priority Tier") or "").strip().lower()
    strong_count = sum(1 for f in (e_fit, c_fit, l_fit, api_fit) if f and str(f).strip().lower() == "strong")
    if tier == "high": score = max(score, 7.0)
    if tier == "low":
        cap = 7.0 if strong_count >= 3 else 5.0
        score = min(score, cap)

    # Floor at 1 — SKILL.md states scores are 1–10
    return max(int(round(score)), 1)


def build_enrichment(row, company, custom_summary, custom_divisions, custom_growth_override=None):
    current = normalize_product(row.get("Product Currently Used"))
    industry = row.get("Industry / Vertical") or ""
    recs = recommend_products(row)
    addon = empuls_addon_applicable(row)
    tracks = build_outreach_tracks(recs, addon)
    growth = custom_growth_override or determine_growth_stage(row.get("Est. Headcount"))

    use_case_parts = []; persona_parts = []; pitch_parts = []
    for p in recs:
        if p == "Empuls":
            use_case_parts.append(f"[EMPULS] {use_cases_empuls(row, company)}")
            persona_parts.append(f"[EMPULS] {persona_block('Empuls')}")
            pitch_parts.append(f"[EMPULS] {pitch_empuls(company, current)}")
        elif p == "Plum":
            use_case_parts.append(f"[PLUM] {use_cases_plum(row, company)}")
            persona_parts.append(f"[PLUM] {persona_block('Plum')}")
            pitch_parts.append(f"[PLUM] {pitch_plum(company, current)}")
        elif p == "Compass":
            use_case_parts.append(f"[COMPASS] {use_cases_compass(row, company)}")
            persona_parts.append(f"[COMPASS] {persona_block('Compass')}")
            pitch_parts.append(f"[COMPASS] {pitch_compass(company, current)}")
        elif p == "Loyalife":
            use_case_parts.append(f"[LOYALIFE] {use_cases_loyalife(row, company)}")
            persona_parts.append(f"[LOYALIFE] {persona_block('Loyalife')}")
            pitch_parts.append(f"[LOYALIFE] {pitch_loyalife(company, current, industry)}")

    if addon:
        use_case_parts.append("[EMPULS ADD-ONS] Fitness Challenges, L&D Incentives, Referral Incentives - activate natively into the existing Empuls deployment with no new vendor or login.")
        persona_parts.append("[EMPULS ADD-ONS] Tier 1: HRBP | L&D Head | TA Lead || Tier 2: Culture Manager / Engagement Manager")
        pitch_parts.append(f"[EMPULS ADD-ONS] {pitch_empuls_addon(company)}")

    return {
        "summary": custom_summary,
        "divisions": custom_divisions,
        "growth": growth,
        "recs": ", ".join(recs) if recs else "Deepen existing usage",
        "tracks": tracks if tracks else "No new cross-sell tracks - deepen existing usage",
        "use_cases": "\n\n".join(use_case_parts) if use_case_parts else "No new product use cases - deepen existing usage",
        "personas": "\n\n".join(persona_parts) if persona_parts else "N/A - already on relevant products",
        "pitch": "\n\n".join(pitch_parts) if pitch_parts else "N/A - already on relevant products",
        "triggers": strategic_triggers(row, company, recs),
        "score": priority_score(row),
    }


def write_batch(out_path, sheet_name, batch_results):
    """batch_results: list of (row_num, enrichment_dict)"""
    import openpyxl
    from openpyxl.styles import Alignment
    wb = openpyxl.load_workbook(out_path)
    ws = wb[sheet_name]
    wrap = Alignment(wrap_text=True, vertical="top")
    # New columns 30-39
    col_keys = ["summary", "divisions", "growth", "recs", "tracks", "use_cases", "personas", "pitch", "triggers", "score"]
    for row_num, enr in batch_results:
        for i, k in enumerate(col_keys):
            c = ws.cell(row=row_num, column=30 + i, value=enr[k])
            c.alignment = wrap
    wb.save(out_path)
    return len(batch_results)
