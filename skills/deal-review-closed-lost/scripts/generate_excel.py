"""
Closed Lost Revival Scoring — Excel Generator
Mirrors the two-sheet structure of the Dormant Deal Revival Excel.
Usage: python scripts/generate_excel.py '<json_payload>' output.xlsx

JSON payload schema:
{
  "meta": {
    "owner": "AE Name",
    "pipeline": "Pipeline Name",
    "date": "DD-Mon-YYYY",
    "total_deals": 10
  },
  "deals": [
    {
      "rank": 1,
      "deal_name": "...",
      "record_id": "...",
      "hs_link": "...",
      "amount": 500000,
      "drop_reason_field": "...",
      "filter1_score": 20,
      "classification": "Internal",
      "classification_confidence": "Confirmed",
      "competitor": "Not named",
      "deepest_stage": "4 - Proposal",
      "filter2_score": 20,
      "last_meaningful_activity": "2026-03-15",
      "filter3_score": 15,
      "filter4_score": 16,
      "associated_contacts": 2,
      "filter5_score": 7,
      "total_score": 78,
      "priority_tier": "🔥 HIGH",
      "re_engagement_date": "Jan 2027",
      "timeline_basis": "Pre-renewal window",
      "recommended_next_step": "...",
      "key_concerns": "...",
      "evidence_reference": "...",
      "data_flag": "None",
      "months_dormant": 3.2,
      "contact_person": "...",
      "conversation_signal_summary": "..."
    }
  ],
  "excluded": [
    {
      "deal_name": "...",
      "record_id": "...",
      "reason": "DATE FILTER | last meaningful activity on or before 1 Dec 2024"
    }
  ],
  "flagged": [
    {
      "deal_name": "...",
      "record_id": "...",
      "reason": "MULTI-AE SAME COMPANY | coordinate before outreach"
    }
  ]
}
"""

import sys
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ── Colour palette (matches dormant deals Excel exactly) ──────────────────────
DARK_NAVY   = "1F3864"   # Row 1 banner background
MID_BLUE    = "2E75B6"   # Header row background
LIGHT_BLUE  = "4472C4"   # Secondary header (intent / contact quality cols)
SCORE_NAVY  = "1F497D"   # Total score cell background
WHITE       = "FFFFFFFF"
ROW_TINT    = "FFEBF3FB" # Alternating row tint (light blue)
ROW_WHITE   = "FFFFFFFF"

# Tier colours  (fill, font)
TIER_HIGH    = ("C8E6C9", "C00000")   # green fill, dark red text
TIER_MEDIUM  = ("C8E6C9", "ED7D31")   # green fill, orange text
TIER_LOW     = ("FFFFF9C4"[2:], "BF8F00")  # yellow fill, gold text  # note: strip alpha
TIER_ARCHIVE = ("D9D9D9", "808080")   # grey fill, grey text
TIER_EXCL    = ("D9D9D9", "808080")

TIER_MAP = {
    "🔥 HIGH":   TIER_HIGH,
    "⚡ MEDIUM": TIER_MEDIUM,
    "📋 LOW":    TIER_LOW,
    "🗄 ARCHIVE": TIER_ARCHIVE,
}

def hex_fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def make_font(bold=False, color="FF000000", size=10, name="Arial"):
    return Font(bold=bold, color=color, size=size, name=name)

def center_align(wrap=False):
    return Alignment(horizontal="center", vertical="center", wrap_text=wrap)

def left_align(wrap=False):
    return Alignment(horizontal="left", vertical="center", wrap_text=wrap)

def thin_border():
    side = Side(style="thin", color="FFBFBFBF")
    return Border(left=side, right=side, top=side, bottom=side)


# ── Sheet 1: Scoring Methodology ─────────────────────────────────────────────

METHODOLOGY_ROWS = [
    ["CLOSED LOST REVIVAL SCORING — METHODOLOGY"],
    ["Scoring system for the configured AE / pipeline | Pipeline: Closed Lost | Purpose: Identify deals worth re-engaging"],
    [],
    ["SCORING MODEL: ONE DIMENSION — REVIVAL WORTHINESS (100 pts)"],
    ["This system scores whether a Closed Lost deal is worth re-engaging, when to re-engage, and how."],
    [],
    ["FILTER-BY-FILTER SCORING BREAKDOWN"],
    ["Filter", "What it measures & why", "Max Points", "Data Source"],
    ["1. Drop Reason Classification",
     "WHY did the deal close lost? Internal shifts (budget deferred, timing, no response) = revivable. External rejections (competitor chosen, disqualified, product mismatch) = low chance. The single strongest signal.",
     25, "HubSpot: notes, call logs, emails — three-step data pull required"],
    ["2. Deepest Pipeline Stage Reached",
     "HOW FAR did the deal get? Negotiation = highest proven intent. Prospect = no real engagement.",
     25, "HubSpot: deal stage field"],
    ["3. Recency of Last Meaningful Activity",
     "WHEN was the last real conversation? Recent = easier to re-open. Score decays with time. Blank/admin calls do not count.",
     20, "HubSpot: notes, call logs — last dated entry with substantive content"],
    ["4. Deal Amount (₹)",
     "IS IT WORTH IT? ₹5L+ justifies effort. ₹0 = unqualified, scores 0.",
     20, "HubSpot: amount field"],
    ["5. Associated Contacts",
     "HOW BROAD was the org engagement? 2+ contacts = discussion was happening internally. 0 = ghost record.",
     10, "HubSpot: num_associated_contacts"],
    [],
    ["DROP REASON CLASSIFICATION — INTERNAL vs EXTERNAL"],
    ["Classification", "Score Range /25", "Examples", "Re-engagement Logic"],
    ["INTERNAL", "18–22",
     "Budget deferred | Plan dropped | Internal restructuring | Tech delay | No response (went quiet)",
     "Re-engage 6 months from last activity, or per explicit timeline in notes"],
    ["EXTERNAL", "2–8",
     "Named competitor | Product fit rejection | Disqualified | Bad CS experience | Firm price rejection",
     "Re-engage 10 months from last activity (before assumed 1-yr competitor contract expires)"],
    ["DATA MISSING", "0", "No notes, no calls, no emails found anywhere", "BLANK — AE must set manually"],
    ["DATA VAGUE", "10 (hold)", "Activity exists but reason cannot be determined", "BLANK — AE must set manually"],
    [],
    ["DETAILED SCORING BRACKETS"],
    ["Filter", "Condition / Bracket", "Score", "Max", "Logic"],
    ["1. Drop Reason", "Explicit timeline given (revisit Q2, next FY)", "22", "25", "Client signalled intent to return"],
    ["", "Clear internal reason, no timeline", "20", "", "Not a rejection — timing/priority shift"],
    ["", "Implies internal shift, not explicit", "18", "", "Likely timing, cannot confirm"],
    ["", "Lost on commercial grounds (price/terms) — fit was there", "8", "", "Revivable if terms change"],
    ["", "Lost on product/feature fit", "5", "", "Revivable only if product evolved"],
    ["", "Explicit rejection / disqualified / CS exit", "3", "", "Low revival potential"],
    ["", "Multiple compounding external reasons", "2", "", "Very low revival potential"],
    ["", "DATA VAGUE — reason unclear", "10 (hold)", "", "Manual review needed"],
    ["", "DATA MISSING — no activity found", "0", "", "AE must review account manually"],
    ["2. Deepest Stage", "5 - Negotiation", "25", "25", "Reviewing contracts — highest proven intent"],
    ["", "4 - Proposal", "20", "", "Formal offer shared — real engagement"],
    ["", "3 - Opportunity", "15", "", "Meetings happened, need confirmed"],
    ["", "2 - Qualified / Need Analysis", "10", "", "Some qualification, no proposal"],
    ["", "1 - Prospect", "5", "", "Initial outreach only"],
    ["", "Pre-prospect / Unknown / Not logged", "0", "", "No evidence of engagement"],
    ["3. Recency", "Within 3 months", "20", "20", "Very recent — context fresh, easy to re-open"],
    ["", "3–6 months ago", "15", "", "Moderate gap — re-establish with reference"],
    ["", "6–12 months ago", "10", "", "Noticeable gap — may need reintroduction"],
    ["", "12–18 months ago", "5", "", "Cold — significant effort needed"],
    ["", "18+ months ago", "0", "", "Very cold — treat as near-new outreach"],
    ["4. Deal Amount", "₹5,00,000 and above", "20", "20", "High value — effort worthiness clear"],
    ["", "₹3,00,000–₹4,99,999", "16", "", "Meaningful — worth structured follow-up"],
    ["", "₹1,00,000–₹2,99,999", "12", "", "Moderate — worth 2–3 attempts"],
    ["", "₹25,000–₹99,999", "8", "", "Low-moderate — light follow-up only"],
    ["", "₹1–₹24,999", "4", "", "Very low — only strategic/referral accounts"],
    ["", "₹0 (unfilled / placeholder)", "0", "", "No commercial basis confirmed"],
    ["5. Contacts", "3 or more", "10", "10", "Org-wide discussion was happening"],
    ["", "2 contacts", "7", "", "Cross-functional interest shown"],
    ["", "1 contact", "4", "", "Single thread — fragile"],
    ["", "0 contacts", "0", "", "Ghost record — cannot be worked"],
    [],
    ["PRIORITY TIERS"],
    ["Tier", "Score Range", "Action"],
    ["🔥 HIGH", "70–100", "Re-engage this month"],
    ["⚡ MEDIUM", "45–69", "Re-engage this quarter"],
    ["📋 LOW", "25–44", "Revisit in 6 months or on external trigger"],
    ["🗄 ARCHIVE", "Below 25", "Do not pursue"],
    [],
    ["WHAT THIS SYSTEM WILL NOT DO"],
    ["— Score CAM, farming, cross-sell, or upsell deals (direct-sales / hunting pipeline only)"],
    ["— Score deals where last meaningful activity is on or before 1 December 2024"],
    ["— Score a deal superseded by a Confirmed & Signed or Closed Won deal at the same company"],
    ["— Infer a drop reason from general knowledge or other deals"],
    ["— Fabricate a re-engagement date when data is insufficient"],
    ["— Override a DO NOT CONTACT flag based on score"],
    ["— Score Empuls Gifting deals (deprioritised per internal policy)"],
]

def build_methodology_sheet(ws):
    ws.title = "Scoring Methodology"
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 55
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 45

    for i, row_data in enumerate(METHODOLOGY_ROWS, start=1):
        if not row_data:
            continue
        for j, val in enumerate(row_data, start=1):
            cell = ws.cell(row=i, column=j, value=val)
            cell.alignment = left_align(wrap=True)
            cell.font = make_font()

        first_val = str(row_data[0]) if row_data else ""

        # Row 1: dark navy banner
        if i == 1:
            ws.merge_cells(f"A1:D1")
            cell = ws["A1"]
            cell.fill = hex_fill(DARK_NAVY)
            cell.font = make_font(bold=True, color=WHITE, size=12)
            cell.alignment = center_align()
            ws.row_dimensions[1].height = 24

        # Row 2: subtitle
        elif i == 2:
            ws.merge_cells(f"A2:D2")
            cell = ws["A2"]
            cell.fill = hex_fill(MID_BLUE)
            cell.font = make_font(color=WHITE)
            cell.alignment = center_align()

        # Section headers (all-caps rows)
        elif first_val.isupper() and len(row_data) == 1:
            ws.merge_cells(f"A{i}:D{i}")
            cell = ws.cell(row=i, column=1)
            cell.fill = hex_fill(DARK_NAVY)
            cell.font = make_font(bold=True, color=WHITE)
            cell.alignment = left_align()

        # Sub-header rows (multiple columns, first is a label like "Filter")
        elif len(row_data) >= 3 and first_val in ("Filter", "Classification", "Tier", "Condition / Bracket"):
            for j in range(1, len(row_data) + 1):
                c = ws.cell(row=i, column=j)
                c.fill = hex_fill(MID_BLUE)
                c.font = make_font(bold=True, color=WHITE)
                c.alignment = center_align(wrap=True)

        # Bullet rows (start with —)
        elif first_val.startswith("—"):
            ws.merge_cells(f"A{i}:D{i}")


# ── Sheet 2: Scored Deals ─────────────────────────────────────────────────────

SCORED_COLS = [
    ("Rank", 5),
    ("Deal Name", 18),
    ("Pipeline", 18),
    ("Amount (₹)", 14),
    ("Drop Reason\n(HubSpot field)", 16),
    ("Filter 1\nScore /25", 10),
    ("Classification", 16),
    ("Classification\nConfidence", 14),
    ("Competitor(s)", 14),
    ("Deepest\nStage", 14),
    ("Filter 2\nScore /25", 10),
    ("Last Meaningful\nActivity Date", 14),
    ("Filter 3\nScore /20", 10),
    ("Filter 4\nScore /20", 10),
    ("Associated\nContacts", 10),
    ("Filter 5\nScore /10", 10),
    ("TOTAL\nSCORE /100", 14),
    ("Priority\nTier", 12),
    ("Closed Lost\nRank", 10),
    ("Re-engagement\nDate", 14),
    ("Timeline\nBasis", 18),
    ("Recommended\nNext Step", 30),
    ("Key\nConcerns", 30),
    ("Evidence\nReference", 22),
    ("Data Flag", 14),
    ("Months\nDormant", 10),
    ("Contact\nPerson", 18),
    ("HubSpot Link", 30),
    ("Conversation\nSignal Summary", 42),
]

DEAL_FIELDS = [
    "rank", "deal_name", "pipeline", "amount",
    "drop_reason_field",
    "filter1_score", "classification", "classification_confidence",
    "competitor", "deepest_stage",
    "filter2_score", "last_meaningful_activity",
    "filter3_score", "filter4_score",
    "associated_contacts", "filter5_score",
    "total_score", "priority_tier", "rank",   # rank repeated for "Closed Lost Rank"
    "re_engagement_date", "timeline_basis",
    "recommended_next_step", "key_concerns",
    "evidence_reference", "data_flag",
    "months_dormant", "contact_person", "hs_link",
    "conversation_signal_summary",
]

def build_scored_sheet(ws, meta, deals, excluded, flagged):
    ws.title = "Scored Deals"

    # Row 1: banner
    last_col = get_column_letter(len(SCORED_COLS))
    ws.merge_cells(f"A1:{last_col}1")
    banner_text = (
        f"CLOSED LOST REVIVAL SCORE — {meta.get('owner','').upper()}  |  "
        f"{meta.get('pipeline','')}  |  "
        f"{meta.get('total_deals','')} Deals  |  "
        f"Scoring v1: 5 Filters out of 100  |  "
        f"{meta.get('date','')}"
    )
    cell = ws["A1"]
    cell.value = banner_text
    cell.fill = hex_fill(DARK_NAVY)
    cell.font = make_font(bold=True, color=WHITE, size=11)
    cell.alignment = center_align()
    ws.row_dimensions[1].height = 22

    # Row 2: headers
    for col_idx, (col_name, col_width) in enumerate(SCORED_COLS, start=1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = col_width
        cell = ws.cell(row=2, column=col_idx, value=col_name)
        cell.fill = hex_fill(MID_BLUE)
        cell.font = make_font(bold=True, color=WHITE, size=9)
        cell.alignment = center_align(wrap=True)
        cell.border = thin_border()
    ws.row_dimensions[2].height = 36
    ws.freeze_panes = "A3"

    # Data rows
    for row_offset, deal in enumerate(deals):
        row_num = 3 + row_offset
        row_fill = ROW_TINT if row_offset % 2 == 0 else ROW_WHITE
        ws.row_dimensions[row_num].height = 100

        for col_idx, field in enumerate(DEAL_FIELDS, start=1):
            val = deal.get(field, "")
            cell = ws.cell(row=row_num, column=col_idx, value=val)
            cell.alignment = left_align(wrap=True)
            cell.font = make_font(size=9)
            cell.border = thin_border()

            # Rank col: bold, tinted
            if col_idx == 1:
                cell.fill = hex_fill(ROW_TINT)
                cell.font = make_font(bold=True, size=9)
                cell.alignment = center_align()

            # Total score: navy bg, white text
            elif col_idx == 17:
                cell.fill = hex_fill(SCORE_NAVY)
                cell.font = make_font(bold=True, color=WHITE, size=10)
                cell.alignment = center_align()

            # Priority tier: coloured by tier
            elif col_idx == 18:
                tier_str = str(val)
                colors = TIER_MAP.get(tier_str, TIER_ARCHIVE)
                cell.fill = hex_fill(colors[0])
                cell.font = make_font(bold=True, color=colors[1], size=9)
                cell.alignment = center_align(wrap=True)

            else:
                cell.fill = hex_fill(row_fill)

    # Excluded/Flagged block (appended below scored deals)
    if excluded or flagged:
        next_row = 3 + len(deals) + 1
        ws.merge_cells(f"A{next_row}:{last_col}{next_row}")
        hdr = ws.cell(row=next_row, column=1, value="EXCLUDED & FLAGGED DEALS")
        hdr.fill = hex_fill(DARK_NAVY)
        hdr.font = make_font(bold=True, color=WHITE)
        hdr.alignment = center_align()
        next_row += 1

        for item in (excluded or []) + (flagged or []):
            ws.merge_cells(f"A{next_row}:{last_col}{next_row}")
            label = f"{item.get('deal_name','')} | Record ID: {item.get('record_id','')} | {item.get('reason','')}"
            cell = ws.cell(row=next_row, column=1, value=label)
            cell.fill = hex_fill("D9D9D9")
            cell.font = make_font(color="808080", size=9)
            cell.alignment = left_align(wrap=True)
            ws.row_dimensions[next_row].height = 28
            next_row += 1


# ── Sheet 3: Summary ──────────────────────────────────────────────────────────

def build_summary_sheet(ws, deals, excluded, flagged):
    ws.title = "Summary & Flags"
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 50

    ws.merge_cells("A1:C1")
    ws["A1"].value = "CLOSED LOST BATCH SUMMARY"
    ws["A1"].fill = hex_fill(DARK_NAVY)
    ws["A1"].font = make_font(bold=True, color=WHITE, size=12)
    ws["A1"].alignment = center_align()
    ws.row_dimensions[1].height = 22

    for col, label in zip(["A", "B", "C"], ["Priority Tier", "Count", "What it means"]):
        cell = ws[f"{col}2"]
        cell.value = label
        cell.fill = hex_fill(MID_BLUE)
        cell.font = make_font(bold=True, color=WHITE)
        cell.alignment = center_align(wrap=True)
    ws.row_dimensions[2].height = 18

    tier_desc = {
        "🔥 HIGH":    "Re-engage this month — timing is right, deal had real depth",
        "⚡ MEDIUM":  "Plan a re-engagement sequence this quarter",
        "📋 LOW":     "Revisit in 6 months or on external trigger",
        "🗄 ARCHIVE": "Do not pursue — no active re-engagement value",
    }
    tier_counts = {t: 0 for t in tier_desc}
    for d in deals:
        t = d.get("priority_tier", "")
        if t in tier_counts:
            tier_counts[t] += 1

    for row_idx, (tier, desc) in enumerate(tier_desc.items(), start=3):
        colors = TIER_MAP.get(tier, TIER_ARCHIVE)
        ws.cell(row=row_idx, column=1, value=tier).font = make_font(bold=True, color=colors[1])
        ws.cell(row=row_idx, column=1).fill = hex_fill(colors[0])
        ws.cell(row=row_idx, column=2, value=tier_counts[tier]).alignment = center_align()
        ws.cell(row=row_idx, column=3, value=desc)

    # Counts
    r = 3 + len(tier_desc) + 1
    stats = [
        ("Deals scored", len(deals)),
        ("Deals excluded (Date Filter / Superseded)", len([e for e in (excluded or []) if "DATE FILTER" in e.get("reason","") or "SUPERSEDED" in e.get("reason","")])),
        ("Deals flagged (Multi-AE / Other)", len([f for f in (flagged or []) if "MULTI-AE" in f.get("reason","")])),
        ("Data Missing flags", len([d for d in deals if "MISSING" in d.get("data_flag","")])),
        ("Data Vague flags", len([d for d in deals if "VAGUE" in d.get("data_flag","")])),
        ("DO NOT CONTACT flags", len([d for d in deals if "DO NOT CONTACT" in d.get("recommended_next_step","")])),
    ]
    for label, count in stats:
        ws.cell(row=r, column=1, value=label).font = make_font(bold=True)
        ws.cell(row=r, column=2, value=count).alignment = center_align()
        r += 1


# ── Main ──────────────────────────────────────────────────────────────────────

def generate(payload: dict, output_path: str):
    meta     = payload.get("meta", {})
    deals    = payload.get("deals", [])
    excluded = payload.get("excluded", [])
    flagged  = payload.get("flagged", [])

    wb = Workbook()
    # Rename default sheet and add others
    ws1 = wb.active
    ws2 = wb.create_sheet()
    ws3 = wb.create_sheet()

    build_methodology_sheet(ws1)
    build_scored_sheet(ws2, meta, deals, excluded, flagged)
    build_summary_sheet(ws3, deals, excluded, flagged)

    # Reorder: Scored Deals first, then Methodology, then Summary
    wb.move_sheet(ws2, offset=-1)

    wb.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_excel.py '<json>' output.xlsx")
        sys.exit(1)
    payload = json.loads(sys.argv[1])
    generate(payload, sys.argv[2])
