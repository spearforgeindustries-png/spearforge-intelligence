# ================================================================
# SPEARFORGE INTELLIGENCE REPORT — PROMPT CONFIGURATION
# Drop this file into your GitHub repo and import REPORT_PROMPT
# into your existing automation script.
#
# Usage in your existing code:
#   from spearforge_prompt import REPORT_PROMPT, build_html_email
#   (replace your current prompt variable with REPORT_PROMPT)
# ================================================================

from datetime import datetime

# Current USD to INR rate — update weekly or fetch dynamically
# Your automation can replace this by fetching from an FX API
USD_TO_INR = 83.5  # approximate — update as needed


def get_report_prompt(usd_to_inr=USD_TO_INR):
    today = datetime.now().strftime("%d %B %Y")

    return f"""You are the weekly intelligence analyst for Spearforge Industrial and Engineering Solutions.

COMPANY BACKGROUND:
Spearforge is an ISO 9001:2015 certified, Indian Railways Approved Vendor based in Chennai, Tamil Nadu, India.
They manufacture precision sheet metal products from their facility at Ayapakkam, Chennai.

FULL PRODUCT CATALOGUE (use this to assess project relevance):
1. Perforated Cable Trays (PCT Series) — Widths 50mm–1000mm, thickness 1.0–2.5mm, HR/SS/Pre-Galvanized sheet.
   Profiles: Straight Tyre Fold, Return Flange Inside/Outside, C-Type Inside/Outside. Finishes: PG, HG, EG, SS, PC, PA.
2. Ladder Type Cable Trays (LCT Series) — Widths 100mm–900mm, IS:2062/1079, MS or GI Sheet, IS:2629/4759 galvanizing.
3. Cable Tray Accessories (PCA/LCA) — 90° bends, reducers, raisers, tees, intersection curved/cornered. All finishes.
4. Cable Raceways — Floor & Ceiling, single/dual compartment, PG or powder-coated, IT/ITeS/Telecom/Healthcare use.
5. Electrical Junction Boxes — MS/SS, IP55/IP66, custom sizes 100×100×70 to 400×300×150mm+, HDG/powder/enamel finish.
6. Supermarket Racks (SMR Series) — Centre Gondola, Wall-Side, End Cap, Mini-Mart, Vegetable & Fruit, Heavy-Duty.
   CRC/GI sheet, 16–18 gauge, heights 1500/1800/2100mm, powder-coated RAL.
7. Die Storage Racks (DSR Series) — 500kg to 10,000+kg/shelf, all-welded IS:2062 MS, roll-out conveyor shelves.
8. Solar Mounting Structures (SMB Series) — HDG MS + Aluminium 6063-T5, IS:875 Part 3, IEC 61215 compatible.
   Pitched Roof, Flat Roof Ballasted, Trapezoidal Clamp, Ground Mount, East-West Dual Tilt, Carport. 25yr life.
9. Electrical Enclosures (ECB Series) — IP55/IP65/IP66, CRCA & SS, CPRI Certified. Wall-mounted, terminal boxes,
   floor-standing Form 1. Sizes 200×200×150 to 1200×1400×400mm. Foamed-in PU gasket, RAL 7035 powder coat.

CURRENCY: Today is {today}. Use USD/INR rate of {usd_to_inr}. Show all values in INR crores (Cr) as primary,
with original currency in brackets. Example: ₹4,175 Cr ($500M).

YOUR TASK: Search the web and produce a structured intelligence report with FOUR sections below.
Only include data you can verify with a real source URL. Do NOT fabricate projects, prices, or sources.
If you cannot find a real source URL, skip that item entirely.

==============================================================
SECTION 1 — TOP INDIAN PROJECTS (past 10 days)
==============================================================
Find 6–10 major Indian infrastructure, energy, or industrial projects that are:
- Announced, tendered, or awarded in the past 10 days
- Directly relevant to Spearforge's product catalogue above

For EACH project include:
- Project name and description
- Project value in ₹ Cr (convert if in USD using rate above)
- Location (state/city)
- Status: Announced | Tendered | Awarded | Under Construction
- Issuing authority or client name
- Which SPECIFIC Spearforge products apply and why (reference catalogue above)
- Verified source name and full URL

Priority sectors: Indian Railways infrastructure, BESS/battery storage, Solar EPC,
Data centres, Industrial plant construction, Airport MEP, Smart city infrastructure.

==============================================================
SECTION 2 — TOP GLOBAL PROJECTS (past 10 days)
==============================================================
Find 4–6 major global infrastructure or energy projects that are:
- Announced, tendered, or awarded in the past 10 days
- Relevant to export opportunities for Spearforge
- Located in: Middle East (UAE, Saudi Arabia, Qatar, Oman), Europe, or US

For EACH project include:
- Project name and description
- Project value in ₹ Cr AND original currency (e.g. ₹8,350 Cr / $1B)
- Country and city/region
- Status: Announced | Tendered | Awarded | Under Construction
- Client or issuing authority
- Which SPECIFIC Spearforge products apply and why (reference catalogue above)
- Verified source name and full URL

Priority sectors: BESS, Solar EPC, Data centres, Industrial plants,
Railway/metro infrastructure, Oil & gas facility upgrades.

==============================================================
SECTION 3 — RAW MATERIAL PRICES (Chennai market, this week)
==============================================================
Search SteelMint (steelmint.com), Steel360 (steel360.com), and Indian steel trader
websites for CURRENT Chennai / South India market prices for these materials:

1. MS Hot Rolled (HR) Sheet — 2mm thickness
2. MS Hot Rolled (HR) Sheet — 3mm thickness
3. MS Cold Rolled (CR) Sheet — 1.2mm thickness
4. MS Cold Rolled (CR) Sheet — 1.6mm thickness
5. GI Sheet / Pre-Galvanized Sheet — 1.2mm
6. GI Sheet / Pre-Galvanized Sheet — 1.6mm
7. Stainless Steel Sheet 304 — 1.2mm
8. Stainless Steel Sheet 304 — 1.6mm
9. Aluminium 6063-T5 Extrusion (per kg)
10. MS Structural Steel (IS:2062) — per tonne

For EACH material show:
- Price per TONNE in ₹
- Price per KG in ₹ (= per tonne ÷ 1000)
- Week-on-week change: Rising ↑ | Falling ↓ | Stable →
- Source name and URL

Also show current USD/INR rate and its impact on import-linked materials.

==============================================================
SECTION 4 — INDIAN RAILWAYS TENDERS (IREPS)
==============================================================
Search the IREPS website (ireps.gov.in) for open tenders published in the past 14 days
that are relevant to Spearforge's product catalogue.

Search for tenders related to:
- Cable trays and cable management systems
- Electrical enclosures and junction boxes
- Battery boxes and underslung water tanks (Spearforge is approved vendor)
- Berth frames and coach fittings
- Welded structural fabrication
- Sheet metal components for rolling stock
- Solar mounting for railway stations
- Supermarket/display racks for railway canteens

For EACH tender found:
- Tender number (exact IREPS tender ID)
- Description
- Issuing Railway / Zone / Unit
- Estimated value in ₹
- Submission deadline
- Which Spearforge product applies
- Direct IREPS tender URL

Also note: Spearforge is already an approved vendor for MS/SS battery boxes,
coat hooks, underslung water tanks, and berth frames. Flag any tenders in these
categories as HIGH PRIORITY.

==============================================================
OUTPUT FORMAT: Respond ONLY with valid JSON. No markdown, no backticks, no preamble.
==============================================================

{{
  "reportDate": "{today}",
  "usdInrRate": {usd_to_inr},
  "indianProjects": [
    {{
      "rank": 1,
      "title": "Project name",
      "description": "2-3 sentence description",
      "valueInr": "₹X,XXX Cr",
      "location": "City, State",
      "status": "Tendered | Awarded | Announced | Under Construction",
      "client": "Client or authority name",
      "spearforgeProducts": "Specific products from catalogue that apply",
      "spearforgeAngle": "Why this matters and what opportunity it creates",
      "sourceName": "Publication or portal name",
      "sourceUrl": "https://full-verified-url"
    }}
  ],
  "globalProjects": [
    {{
      "rank": 1,
      "title": "Project name",
      "description": "2-3 sentence description",
      "valueInr": "₹X,XXX Cr",
      "valueOriginal": "$X B / €X M / AED X B",
      "country": "Country",
      "location": "City/Region",
      "status": "Tendered | Awarded | Announced | Under Construction",
      "client": "Client or authority name",
      "spearforgeProducts": "Specific products from catalogue that apply",
      "spearforgeAngle": "Export opportunity and entry strategy",
      "sourceName": "Publication name",
      "sourceUrl": "https://full-verified-url"
    }}
  ],
  "rawMaterials": [
    {{
      "material": "Material name and spec",
      "pricePerTonne": "₹XX,XXX",
      "pricePerKg": "₹XX.XX",
      "weekChange": "Rising ↑ | Falling ↓ | Stable →",
      "changePercent": "+X.X% | -X.X% | 0%",
      "sourceName": "Source name",
      "sourceUrl": "https://url"
    }}
  ],
  "usdInrImpact": "One line on how current USD/INR rate affects Spearforge import-linked costs",
  "railwayTenders": [
    {{
      "priority": "HIGH | MEDIUM | LOW",
      "tenderNumber": "Exact IREPS tender ID",
      "description": "Tender description",
      "issuingUnit": "Railway zone / division / unit",
      "estimatedValue": "₹X Lakhs / ₹X Cr",
      "deadline": "DD MMM YYYY",
      "spearforgeProduct": "Matching product from catalogue",
      "isApprovedVendorCategory": true,
      "tenderUrl": "https://ireps.gov.in/..."
    }}
  ],
  "weeklySignal": "One critical strategic action Spearforge should take this week based on all the above"
}}"""


# ================================================================
# HTML EMAIL BUILDER
# Call build_html_email(data) where data = parsed JSON from above
# ================================================================

def build_html_email(data):
    today = data.get("reportDate", "")
    usd_inr = data.get("usdInrRate", "")
    signal = data.get("weeklySignal", "")
    usd_impact = data.get("usdInrImpact", "")

    # --- Indian Projects ---
    indian_html = ""
    for p in data.get("indianProjects", []):
        indian_html += f"""
        <tr>
          <td style="padding:18px 24px;border-bottom:1px solid #eef0f5;vertical-align:top;">
            <div style="margin-bottom:8px;">
              <span style="background:#1565c0;color:#fff;font-size:10px;font-weight:700;
                padding:2px 10px;border-radius:2px;text-transform:uppercase;letter-spacing:1px;
                margin-right:8px;">#{p.get('rank','')} {p.get('status','')}</span>
            </div>
            <div style="font-size:15px;font-weight:700;color:#1a2744;margin-bottom:4px;">{p.get('title','')}</div>
            <div style="font-size:13px;color:#555;line-height:1.6;margin-bottom:8px;">{p.get('description','')}</div>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
              <tr>
                <td style="padding:6px 12px;background:#f0f7ff;border-radius:4px 0 0 4px;width:50%;">
                  <div style="font-size:10px;color:#888;text-transform:uppercase;letter-spacing:1px;">Project Value</div>
                  <div style="font-size:16px;font-weight:800;color:#1565c0;">{p.get('valueInr','')}</div>
                </td>
                <td style="width:8px;"></td>
                <td style="padding:6px 12px;background:#f5f5f5;border-radius:0 4px 4px 0;width:50%;">
                  <div style="font-size:10px;color:#888;text-transform:uppercase;letter-spacing:1px;">Client / Authority</div>
                  <div style="font-size:13px;font-weight:600;color:#333;">{p.get('client','')}</div>
                  <div style="font-size:11px;color:#888;">📍 {p.get('location','')}</div>
                </td>
              </tr>
            </table>
            <div style="background:#fffbf0;border-left:3px solid #c9a227;padding:10px 14px;
              border-radius:0 4px 4px 0;margin-bottom:8px;">
              <div style="font-size:10px;font-weight:700;color:#c9a227;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:4px;">Spearforge Products → {p.get('spearforgeProducts','')}</div>
              <div style="font-size:13px;color:#444;line-height:1.5;">{p.get('spearforgeAngle','')}</div>
            </div>
            <a href="{p.get('sourceUrl','#')}" style="font-size:11px;color:#1565c0;
              font-weight:700;text-decoration:none;">↗ {p.get('sourceName','View Source')}</a>
          </td>
        </tr>"""

    # --- Global Projects ---
    global_html = ""
    for p in data.get("globalProjects", []):
        global_html += f"""
        <tr>
          <td style="padding:18px 24px;border-bottom:1px solid #eef0f5;vertical-align:top;">
            <div style="margin-bottom:8px;">
              <span style="background:#2e7d32;color:#fff;font-size:10px;font-weight:700;
                padding:2px 10px;border-radius:2px;text-transform:uppercase;letter-spacing:1px;
                margin-right:8px;">#{p.get('rank','')} {p.get('country','')}</span>
              <span style="font-size:11px;color:#888;">{p.get('status','')}</span>
            </div>
            <div style="font-size:15px;font-weight:700;color:#1a2744;margin-bottom:4px;">{p.get('title','')}</div>
            <div style="font-size:13px;color:#555;line-height:1.6;margin-bottom:8px;">{p.get('description','')}</div>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
              <tr>
                <td style="padding:6px 12px;background:#f0fff4;border-radius:4px 0 0 4px;width:50%;">
                  <div style="font-size:10px;color:#888;text-transform:uppercase;letter-spacing:1px;">Value (INR)</div>
                  <div style="font-size:16px;font-weight:800;color:#2e7d32;">{p.get('valueInr','')}</div>
                  <div style="font-size:11px;color:#888;">{p.get('valueOriginal','')}</div>
                </td>
                <td style="width:8px;"></td>
                <td style="padding:6px 12px;background:#f5f5f5;border-radius:0 4px 4px 0;width:50%;">
                  <div style="font-size:10px;color:#888;text-transform:uppercase;letter-spacing:1px;">Client</div>
                  <div style="font-size:13px;font-weight:600;color:#333;">{p.get('client','')}</div>
                  <div style="font-size:11px;color:#888;">📍 {p.get('location','')}</div>
                </td>
              </tr>
            </table>
            <div style="background:#f0fff4;border-left:3px solid #2e7d32;padding:10px 14px;
              border-radius:0 4px 4px 0;margin-bottom:8px;">
              <div style="font-size:10px;font-weight:700;color:#2e7d32;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:4px;">Spearforge Products → {p.get('spearforgeProducts','')}</div>
              <div style="font-size:13px;color:#444;line-height:1.5;">{p.get('spearforgeAngle','')}</div>
            </div>
            <a href="{p.get('sourceUrl','#')}" style="font-size:11px;color:#2e7d32;
              font-weight:700;text-decoration:none;">↗ {p.get('sourceName','View Source')}</a>
          </td>
        </tr>"""

    # --- Raw Materials Table ---
    materials_rows = ""
    for m in data.get("rawMaterials", []):
        trend = m.get("weekChange", "Stable →")
        if "Rising" in trend:
            color = "#c0392b"
        elif "Falling" in trend:
            color = "#27ae60"
        else:
            color = "#546e7a"
        materials_rows += f"""
        <tr style="border-bottom:1px solid #eef0f5;">
          <td style="padding:10px 14px;font-size:13px;color:#333;font-weight:600;
            border-bottom:1px solid #eef0f5;">{m.get('material','')}</td>
          <td style="padding:10px 14px;font-size:14px;font-weight:800;color:#1a2744;
            border-bottom:1px solid #eef0f5;">{m.get('pricePerTonne','')}</td>
          <td style="padding:10px 14px;font-size:13px;font-weight:700;color:#444;
            border-bottom:1px solid #eef0f5;">{m.get('pricePerKg','')}</td>
          <td style="padding:10px 14px;border-bottom:1px solid #eef0f5;">
            <span style="color:{color};font-weight:700;font-size:13px;">{trend}</span>
            <span style="font-size:11px;color:#888;margin-left:6px;">{m.get('changePercent','')}</span>
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #eef0f5;">
            <a href="{m.get('sourceUrl','#')}" style="font-size:11px;color:#c9a227;
              font-weight:700;text-decoration:none;">{m.get('sourceName','')}</a>
          </td>
        </tr>"""

    # --- Railway Tenders ---
    railway_html = ""
    for t in data.get("railwayTenders", []):
        priority = t.get("priority", "LOW")
        p_color = {"HIGH": "#c0392b", "MEDIUM": "#e67e22", "LOW": "#27ae60"}.get(priority, "#546e7a")
        approved = "⭐ APPROVED VENDOR CATEGORY" if t.get("isApprovedVendorCategory") else ""
        railway_html += f"""
        <tr>
          <td style="padding:16px 24px;border-bottom:1px solid #eef0f5;">
            <div style="margin-bottom:6px;">
              <span style="background:{p_color};color:#fff;font-size:10px;font-weight:700;
                padding:2px 10px;border-radius:2px;text-transform:uppercase;letter-spacing:1px;
                margin-right:8px;">{priority} PRIORITY</span>
              {"<span style='font-size:11px;color:#c9a227;font-weight:700;'>" + approved + "</span>" if approved else ""}
            </div>
            <div style="font-size:14px;font-weight:700;color:#1a2744;margin-bottom:4px;">{t.get('description','')}</div>
            <div style="font-size:11px;color:#888;font-family:monospace;margin-bottom:8px;">
              Tender No: {t.get('tenderNumber','')}
            </div>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:8px;">
              <tr>
                <td style="width:33%;padding:6px 10px;background:#f9f9f9;border-radius:4px;margin-right:4px;">
                  <div style="font-size:10px;color:#888;text-transform:uppercase;">Issuing Unit</div>
                  <div style="font-size:12px;font-weight:600;color:#333;">{t.get('issuingUnit','')}</div>
                </td>
                <td style="width:4px;"></td>
                <td style="width:33%;padding:6px 10px;background:#f9f9f9;border-radius:4px;">
                  <div style="font-size:10px;color:#888;text-transform:uppercase;">Est. Value</div>
                  <div style="font-size:12px;font-weight:700;color:#1a2744;">{t.get('estimatedValue','')}</div>
                </td>
                <td style="width:4px;"></td>
                <td style="width:33%;padding:6px 10px;background:#fff0f0;border-radius:4px;">
                  <div style="font-size:10px;color:#888;text-transform:uppercase;">Deadline</div>
                  <div style="font-size:12px;font-weight:700;color:#c0392b;">{t.get('deadline','')}</div>
                </td>
              </tr>
            </table>
            <div style="font-size:12px;color:#555;margin-bottom:8px;">
              🔧 <strong>Product match:</strong> {t.get('spearforgeProduct','')}
            </div>
            <a href="{t.get('tenderUrl','https://ireps.gov.in')}"
              style="font-size:11px;color:#7b1fa2;font-weight:700;text-decoration:none;">
              View on IREPS →</a>
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f0f2f8;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f8;padding:24px 0;">
<tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0"
  style="background:#fff;border-radius:10px;overflow:hidden;
  box-shadow:0 4px 24px rgba(26,39,68,0.12);">

  <!-- HEADER -->
  <tr><td style="background:linear-gradient(135deg,#1a2744 0%,#243560 100%);padding:28px 32px;">
    <div style="color:#c9a227;font-size:10px;font-weight:700;letter-spacing:3px;
      text-transform:uppercase;margin-bottom:8px;">Spearforge Industrial & Engineering Solutions</div>
    <div style="color:#fff;font-size:24px;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;">
      Weekly Intelligence Report</div>
    <div style="color:#8a9dc0;font-size:13px;">{today} &nbsp;·&nbsp;
      USD/INR: <strong style="color:#c9a227;">₹{usd_inr}</strong></div>
  </td></tr>

  <!-- WEEKLY SIGNAL -->
  <tr><td style="background:#fffbf0;border-top:3px solid #c9a227;padding:16px 28px;">
    <div style="font-size:10px;font-weight:700;color:#c9a227;text-transform:uppercase;
      letter-spacing:2px;margin-bottom:6px;">📡 This Week's Strategic Action</div>
    <div style="font-size:14px;color:#333;line-height:1.7;font-weight:600;">{signal}</div>
  </td></tr>

  <!-- SECTION 1: INDIAN PROJECTS -->
  <tr><td style="padding:20px 24px 8px;background:#fafbfd;">
    <div style="font-size:12px;font-weight:700;color:#1565c0;text-transform:uppercase;
      letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid #1565c0;">
      🇮🇳 Top Indian Projects</div>
  </td></tr>
  <table width="100%" cellpadding="0" cellspacing="0">{indian_html}</table>

  <!-- SECTION 2: GLOBAL PROJECTS -->
  <tr><td style="padding:20px 24px 8px;background:#fafbfd;">
    <div style="font-size:12px;font-weight:700;color:#2e7d32;text-transform:uppercase;
      letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid #2e7d32;">
      🌍 Top Global Projects</div>
  </td></tr>
  <table width="100%" cellpadding="0" cellspacing="0">{global_html}</table>

  <!-- SECTION 3: RAW MATERIALS -->
  <tr><td style="padding:20px 24px 8px;background:#fafbfd;">
    <div style="font-size:12px;font-weight:700;color:#c9a227;text-transform:uppercase;
      letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid #c9a227;">
      📊 Raw Material Prices — Chennai Market</div>
  </td></tr>
  <tr><td style="padding:0 0 0 0;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr style="background:#1a2744;">
        <th style="padding:10px 14px;text-align:left;font-size:10px;color:#c9a227;
          font-weight:700;text-transform:uppercase;letter-spacing:1px;">Material</th>
        <th style="padding:10px 14px;text-align:left;font-size:10px;color:#c9a227;
          font-weight:700;text-transform:uppercase;letter-spacing:1px;">Per Tonne</th>
        <th style="padding:10px 14px;text-align:left;font-size:10px;color:#c9a227;
          font-weight:700;text-transform:uppercase;letter-spacing:1px;">Per KG</th>
        <th style="padding:10px 14px;text-align:left;font-size:10px;color:#c9a227;
          font-weight:700;text-transform:uppercase;letter-spacing:1px;">Week Change</th>
        <th style="padding:10px 14px;text-align:left;font-size:10px;color:#c9a227;
          font-weight:700;text-transform:uppercase;letter-spacing:1px;">Source</th>
      </tr>
      {materials_rows}
    </table>
  </td></tr>
  <tr><td style="padding:10px 24px;background:#f9f9f9;border-bottom:1px solid #eef0f5;">
    <div style="font-size:12px;color:#555;">💱 <strong>USD/INR Impact:</strong> {usd_impact}</div>
  </td></tr>

  <!-- SECTION 4: RAILWAY TENDERS -->
  <tr><td style="padding:20px 24px 8px;background:#fafbfd;">
    <div style="font-size:12px;font-weight:700;color:#7b1fa2;text-transform:uppercase;
      letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid #7b1fa2;">
      🚆 Indian Railways Tenders — IREPS
      <span style="font-size:10px;font-weight:400;color:#888;margin-left:8px;text-transform:none;">
        ⭐ = Approved vendor category</span></div>
  </td></tr>
  <table width="100%" cellpadding="0" cellspacing="0">{railway_html}</table>

  <!-- FOOTER -->
  <tr><td style="padding:18px 28px;background:#1a2744;text-align:center;">
    <div style="font-size:11px;color:#8a9dc0;line-height:1.8;">
      Auto-generated by Spearforge Intel Bot · Every Friday 7:00 AM IST<br>
      enquiries@spearforgeindustries.com · Chennai, Tamil Nadu, India<br>
      <span style="color:#c9a227;font-weight:700;">"Global Precision. Industrial Excellence."</span>
    </div>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""
