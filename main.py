import os
import json
import re
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google import genai
from google.genai import types as genai_types

# ================================================================
# CONFIGURATION
# ================================================================
SENDER_EMAIL    = "vimal.dgv@gmail.com"
RECEIVER_EMAIL  = "vimal.prakash@spearforgeindustries.com"
REPORT_SUBJECT  = "Spearforge Weekly Intelligence Report"
USD_TO_INR      = 83.5   # Update weekly or fetch dynamically

# ================================================================
# STEP 1 — GEMINI CLIENT SETUP (google-genai package)
# ================================================================
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
GEMINI_MODEL ="gemini-1.5-flash-001"

# ================================================================
# STEP 2 — PROMPT (full Spearforge catalogue context)
# ================================================================
def get_prompt():
    today = datetime.now().strftime("%d %B %Y")
    return f"""You are the weekly intelligence analyst for Spearforge Industrial and Engineering Solutions.

COMPANY BACKGROUND:
Spearforge is an ISO 9001:2015 certified, Indian Railways Approved Vendor based in Chennai, Tamil Nadu, India.
They manufacture precision sheet metal products from their facility at Ayapakkam, Chennai.

FULL PRODUCT CATALOGUE (use this to assess project relevance):
1. Perforated Cable Trays (PCT Series) — Widths 50mm-1000mm, thickness 1.0-2.5mm, HR/SS/Pre-Galvanized sheet.
   Profiles: Straight Tyre Fold, Return Flange Inside/Outside, C-Type Inside/Outside. Finishes: PG, HG, EG, SS, PC, PA.
2. Ladder Type Cable Trays (LCT Series) — Widths 100mm-900mm, IS:2062/1079, MS or GI Sheet, IS:2629/4759 galvanizing.
3. Cable Tray Accessories (PCA/LCA) — 90 degree bends, reducers, raisers, tees, intersection curved/cornered.
4. Cable Raceways — Floor and Ceiling, single/dual compartment, PG or powder-coated, IT/ITeS/Telecom/Healthcare.
5. Electrical Junction Boxes — MS/SS, IP55/IP66, custom sizes 100x100x70 to 400x300x150mm, HDG/powder/enamel finish.
6. Supermarket Racks (SMR Series) — Centre Gondola, Wall-Side, End Cap, Mini-Mart, Heavy-Duty. CRC/GI sheet, powder-coated RAL.
7. Die Storage Racks (DSR Series) — 500kg to 10,000+kg/shelf, all-welded IS:2062 MS, roll-out conveyor shelves.
8. Solar Mounting Structures (SMB Series) — HDG MS + Aluminium 6063-T5, IS:875 Part 3, IEC 61215. Pitched Roof,
   Flat Roof Ballasted, Ground Mount, East-West Dual Tilt, Carport. 25-year service life.
9. Electrical Enclosures (ECB Series) — IP55/IP65/IP66, CRCA and SS, CPRI Certified. Wall-mounted, terminal boxes,
   floor-standing Form 1. Sizes 200x200x150 to 1200x1400x400mm. Foamed-in PU gasket, RAL 7035 powder coat.

CURRENCY: Today is {today}. USD/INR rate is {USD_TO_INR}.
Show all values in INR crores (Cr) as primary, original currency in brackets.
Example: Rs.4,175 Cr ($500M).

CRITICAL RULES:
- Use Google Search to find REAL, CURRENT data from the past 10 days only
- Do NOT fabricate projects, prices, or sources
- If you cannot find a real verified URL for a project, skip it entirely
- Only include items you found via actual web search results

YOUR TASK: Produce a structured intelligence report with FOUR sections.

==============================================================
SECTION 1 - TOP INDIAN PROJECTS (past 10 days)
==============================================================
Find 5-8 major Indian infrastructure, energy, or industrial projects:
- Announced, tendered, or awarded in the past 10 days
- Directly relevant to Spearforge products above

Priority sectors: Indian Railways, BESS/battery storage, Solar EPC,
Data centres, Industrial plant construction, Airport MEP, Smart city.

For each project include: title, description, value in INR Cr,
location, status, client, which specific Spearforge products apply
and why, source name, verified source URL.

==============================================================
SECTION 2 - TOP GLOBAL PROJECTS (past 10 days)
==============================================================
Find 4-6 major global projects relevant to Spearforge exports:
- Middle East (UAE, Saudi Arabia, Qatar, Oman)
- Europe or US

Priority: BESS, Solar EPC, Data centres, Industrial plants,
Railway/metro infrastructure.

For each: title, description, value in INR Cr AND original currency,
country, location, status, client, specific Spearforge products,
export opportunity angle, source name, verified URL.

==============================================================
SECTION 3 - RAW MATERIAL PRICES (Chennai market, this week)
==============================================================
Search SteelMint (steelmint.com) and Steel360 (steel360.com) for
CURRENT Chennai / South India market prices for:

1. MS Hot Rolled (HR) Sheet - 2mm
2. MS Hot Rolled (HR) Sheet - 3mm
3. MS Cold Rolled (CR) Sheet - 1.2mm
4. MS Cold Rolled (CR) Sheet - 1.6mm
5. GI Sheet / Pre-Galvanized - 1.2mm
6. GI Sheet / Pre-Galvanized - 1.6mm
7. Stainless Steel Sheet 304 - 1.2mm
8. Stainless Steel Sheet 304 - 1.6mm
9. Aluminium 6063-T5 Extrusion
10. MS Structural Steel IS:2062

For each: price per tonne in INR, price per kg in INR,
week-on-week change direction, source name, source URL.

Also: current USD/INR rate and its impact on import costs.

==============================================================
SECTION 4 - INDIAN RAILWAYS TENDERS (IREPS)
==============================================================
Search ireps.gov.in for open tenders published in past 14 days for:
- Cable trays and cable management systems
- Electrical enclosures and junction boxes
- Battery boxes and underslung water tanks (Spearforge approved vendor)
- Berth frames and coach fittings (Spearforge approved vendor)
- Coat hooks for coaches (Spearforge approved vendor)
- Welded structural fabrication
- Sheet metal components for rolling stock
- Solar mounting for railway stations

NOTE: Spearforge is already an approved vendor for MS/SS battery boxes,
coat hooks, underslung water tanks, and berth frames. Flag these HIGH PRIORITY.

For each tender: exact IREPS tender number, description, issuing Railway zone/unit,
estimated value in INR, submission deadline, matching Spearforge product,
whether it is an approved vendor category, direct IREPS tender URL.

==============================================================
OUTPUT: Respond with ONLY valid JSON. No markdown, no backticks, no explanation.
==============================================================

{{
  "reportDate": "{today}",
  "usdInrRate": {USD_TO_INR},
  "indianProjects": [
    {{
      "rank": 1,
      "title": "Project name",
      "description": "2-3 sentence description",
      "valueInr": "Rs.X,XXX Cr",
      "location": "City, State",
      "status": "Tendered | Awarded | Announced | Under Construction",
      "client": "Client or authority name",
      "spearforgeProducts": "Specific products from catalogue",
      "spearforgeAngle": "Why this matters and the opportunity",
      "sourceName": "Publication or portal name",
      "sourceUrl": "https://verified-url"
    }}
  ],
  "globalProjects": [
    {{
      "rank": 1,
      "title": "Project name",
      "description": "2-3 sentence description",
      "valueInr": "Rs.X,XXX Cr",
      "valueOriginal": "$X B or EUR X M or AED X B",
      "country": "Country",
      "location": "City/Region",
      "status": "Tendered | Awarded | Announced | Under Construction",
      "client": "Client name",
      "spearforgeProducts": "Specific products from catalogue",
      "spearforgeAngle": "Export opportunity and entry strategy",
      "sourceName": "Publication name",
      "sourceUrl": "https://verified-url"
    }}
  ],
  "rawMaterials": [
    {{
      "material": "Material name and spec",
      "pricePerTonne": "Rs.XX,XXX",
      "pricePerKg": "Rs.XX.XX",
      "weekChange": "Rising | Falling | Stable",
      "changePercent": "+X.X% or -X.X% or 0%",
      "sourceName": "Source name",
      "sourceUrl": "https://url"
    }}
  ],
  "usdInrImpact": "One line on how current rate affects Spearforge costs",
  "railwayTenders": [
    {{
      "priority": "HIGH | MEDIUM | LOW",
      "tenderNumber": "Exact IREPS tender ID",
      "description": "Tender description",
      "issuingUnit": "Railway zone / division / unit",
      "estimatedValue": "Rs.X Lakhs or Rs.X Cr",
      "deadline": "DD MMM YYYY",
      "spearforgeProduct": "Matching product",
      "isApprovedVendorCategory": true,
      "tenderUrl": "https://ireps.gov.in/..."
    }}
  ],
  "weeklySignal": "One critical strategic action Spearforge should take this week"
}}"""


# ================================================================
# STEP 3 — CALL GEMINI WITH GOOGLE SEARCH GROUNDING
# ================================================================
def generate_report():
    prompt = get_prompt()
    print("  Calling Gemini with Google Search grounding...")

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())],
            temperature=0.1,
            max_output_tokens=4000,
        )
    )

    raw_text = response.text
    print(f"  Gemini responded ({len(raw_text)} chars)")
    return raw_text


# ================================================================
# STEP 4 — PARSE JSON RESPONSE
# ================================================================
def parse_response(raw_text):
    # Strip any accidental markdown fences
    clean = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.IGNORECASE)
    clean = re.sub(r'^```\s*',     '', clean,            flags=re.IGNORECASE)
    clean = re.sub(r'```\s*$',     '', clean)
    clean = clean.strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Try extracting just the JSON object if there's surrounding text
        match = re.search(r'\{[\s\S]*\}', clean)
        if match:
            return json.loads(match.group())
        raise ValueError("Could not parse JSON from Gemini response. Raw output:\n" + raw_text[:500])


# ================================================================
# STEP 5 — BUILD HTML EMAIL
# ================================================================
def build_html_email(data):
    today        = data.get("reportDate", datetime.now().strftime("%d %B %Y"))
    usd_inr      = data.get("usdInrRate", USD_TO_INR)
    signal       = data.get("weeklySignal", "")
    usd_impact   = data.get("usdInrImpact", "")

    # ---- Indian Projects ----
    indian_html = ""
    for p in data.get("indianProjects", []):
        indian_html += f"""
        <tr>
          <td style="padding:18px 24px;border-bottom:1px solid #eef0f5;vertical-align:top;">
            <div style="margin-bottom:8px;">
              <span style="background:#1565c0;color:#fff;font-size:10px;font-weight:700;
                padding:2px 10px;border-radius:2px;text-transform:uppercase;letter-spacing:1px;
                margin-right:8px;">#{p.get('rank','')} &nbsp;{p.get('status','')}</span>
              <span style="font-size:11px;color:#888;">&#128205; {p.get('location','')}</span>
            </div>
            <div style="font-size:15px;font-weight:700;color:#1a2744;margin-bottom:6px;">{p.get('title','')}</div>
            <div style="font-size:13px;color:#555;line-height:1.6;margin-bottom:10px;">{p.get('description','')}</div>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
              <tr>
                <td style="padding:8px 12px;background:#f0f7ff;border-radius:4px;width:48%;">
                  <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:1px;">Project Value</div>
                  <div style="font-size:18px;font-weight:800;color:#1565c0;">{p.get('valueInr','')}</div>
                </td>
                <td style="width:4%;"></td>
                <td style="padding:8px 12px;background:#f5f5f5;border-radius:4px;width:48%;">
                  <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:1px;">Client / Authority</div>
                  <div style="font-size:13px;font-weight:600;color:#333;">{p.get('client','')}</div>
                </td>
              </tr>
            </table>
            <div style="background:#fffbf0;border-left:3px solid #c9a227;padding:10px 14px;
              border-radius:0 4px 4px 0;margin-bottom:8px;">
              <div style="font-size:9px;font-weight:700;color:#c9a227;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:4px;">SPEARFORGE PRODUCTS &#8594; {p.get('spearforgeProducts','')}</div>
              <div style="font-size:13px;color:#444;line-height:1.5;">{p.get('spearforgeAngle','')}</div>
            </div>
            <a href="{p.get('sourceUrl','#')}" style="font-size:11px;color:#1565c0;
              font-weight:700;text-decoration:none;">&#8599; {p.get('sourceName','View Source')}</a>
          </td>
        </tr>"""

    # ---- Global Projects ----
    global_html = ""
    for p in data.get("globalProjects", []):
        global_html += f"""
        <tr>
          <td style="padding:18px 24px;border-bottom:1px solid #eef0f5;vertical-align:top;">
            <div style="margin-bottom:8px;">
              <span style="background:#2e7d32;color:#fff;font-size:10px;font-weight:700;
                padding:2px 10px;border-radius:2px;text-transform:uppercase;letter-spacing:1px;
                margin-right:8px;">#{p.get('rank','')} &nbsp;{p.get('country','')}</span>
              <span style="font-size:11px;color:#888;">{p.get('status','')}</span>
            </div>
            <div style="font-size:15px;font-weight:700;color:#1a2744;margin-bottom:6px;">{p.get('title','')}</div>
            <div style="font-size:13px;color:#555;line-height:1.6;margin-bottom:10px;">{p.get('description','')}</div>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
              <tr>
                <td style="padding:8px 12px;background:#f0fff4;border-radius:4px;width:48%;">
                  <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:1px;">Value (INR)</div>
                  <div style="font-size:18px;font-weight:800;color:#2e7d32;">{p.get('valueInr','')}</div>
                  <div style="font-size:11px;color:#888;">{p.get('valueOriginal','')}</div>
                </td>
                <td style="width:4%;"></td>
                <td style="padding:8px 12px;background:#f5f5f5;border-radius:4px;width:48%;">
                  <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:1px;">Client</div>
                  <div style="font-size:13px;font-weight:600;color:#333;">{p.get('client','')}</div>
                  <div style="font-size:11px;color:#888;">&#128205; {p.get('location','')}</div>
                </td>
              </tr>
            </table>
            <div style="background:#f0fff4;border-left:3px solid #2e7d32;padding:10px 14px;
              border-radius:0 4px 4px 0;margin-bottom:8px;">
              <div style="font-size:9px;font-weight:700;color:#2e7d32;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:4px;">SPEARFORGE PRODUCTS &#8594; {p.get('spearforgeProducts','')}</div>
              <div style="font-size:13px;color:#444;line-height:1.5;">{p.get('spearforgeAngle','')}</div>
            </div>
            <a href="{p.get('sourceUrl','#')}" style="font-size:11px;color:#2e7d32;
              font-weight:700;text-decoration:none;">&#8599; {p.get('sourceName','View Source')}</a>
          </td>
        </tr>"""

    # ---- Raw Materials Table ----
    materials_rows = ""
    for m in data.get("rawMaterials", []):
        trend = m.get("weekChange", "Stable")
        color = "#c0392b" if "Rising" in trend else ("#27ae60" if "Falling" in trend else "#546e7a")
        arrow = "&#8593;" if "Rising" in trend else ("&#8595;" if "Falling" in trend else "&#8594;")
        materials_rows += f"""
        <tr>
          <td style="padding:10px 14px;font-size:13px;color:#333;font-weight:600;
            border-bottom:1px solid #eef0f5;">{m.get('material','')}</td>
          <td style="padding:10px 14px;font-size:14px;font-weight:800;color:#1a2744;
            border-bottom:1px solid #eef0f5;">{m.get('pricePerTonne','')}</td>
          <td style="padding:10px 14px;font-size:13px;font-weight:700;color:#333;
            border-bottom:1px solid #eef0f5;">{m.get('pricePerKg','')}</td>
          <td style="padding:10px 14px;border-bottom:1px solid #eef0f5;">
            <span style="color:{color};font-weight:700;">{arrow} {trend}</span>
            <span style="font-size:11px;color:#888;margin-left:6px;">{m.get('changePercent','')}</span>
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #eef0f5;">
            <a href="{m.get('sourceUrl','#')}" style="font-size:11px;color:#c9a227;
              font-weight:700;text-decoration:none;">{m.get('sourceName','')}</a>
          </td>
        </tr>"""

    # ---- Railway Tenders ----
    railway_html = ""
    for t in data.get("railwayTenders", []):
        priority  = t.get("priority", "LOW")
        p_color   = {"HIGH": "#c0392b", "MEDIUM": "#e67e22", "LOW": "#27ae60"}.get(priority, "#546e7a")
        approved  = t.get("isApprovedVendorCategory", False)
        railway_html += f"""
        <tr>
          <td style="padding:16px 24px;border-bottom:1px solid #eef0f5;">
            <div style="margin-bottom:8px;">
              <span style="background:{p_color};color:#fff;font-size:10px;font-weight:700;
                padding:2px 10px;border-radius:2px;text-transform:uppercase;margin-right:8px;">
                {priority} PRIORITY</span>
              {'<span style="font-size:11px;color:#c9a227;font-weight:700;">&#11088; APPROVED VENDOR CATEGORY</span>' if approved else ''}
            </div>
            <div style="font-size:14px;font-weight:700;color:#1a2744;margin-bottom:4px;">{t.get('description','')}</div>
            <div style="font-size:11px;color:#888;font-family:monospace;margin-bottom:10px;">
              Tender No: {t.get('tenderNumber','')}</div>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
              <tr>
                <td style="padding:7px 12px;background:#f9f9f9;border-radius:4px;width:32%;">
                  <div style="font-size:9px;color:#888;text-transform:uppercase;">Issuing Unit</div>
                  <div style="font-size:12px;font-weight:600;color:#333;">{t.get('issuingUnit','')}</div>
                </td>
                <td style="width:2%;"></td>
                <td style="padding:7px 12px;background:#f9f9f9;border-radius:4px;width:32%;">
                  <div style="font-size:9px;color:#888;text-transform:uppercase;">Est. Value</div>
                  <div style="font-size:13px;font-weight:700;color:#1a2744;">{t.get('estimatedValue','')}</div>
                </td>
                <td style="width:2%;"></td>
                <td style="padding:7px 12px;background:#fff0f0;border-radius:4px;width:32%;">
                  <div style="font-size:9px;color:#888;text-transform:uppercase;">Deadline</div>
                  <div style="font-size:13px;font-weight:700;color:#c0392b;">{t.get('deadline','')}</div>
                </td>
              </tr>
            </table>
            <div style="font-size:12px;color:#555;margin-bottom:8px;">
              &#128296; <strong>Product match:</strong> {t.get('spearforgeProduct','')}
            </div>
            <a href="{t.get('tenderUrl','https://ireps.gov.in')}"
              style="font-size:11px;color:#7b1fa2;font-weight:700;text-decoration:none;">
              View on IREPS &#8594;</a>
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
      text-transform:uppercase;margin-bottom:8px;">
      Spearforge Industrial &amp; Engineering Solutions</div>
    <div style="color:#fff;font-size:24px;font-weight:800;letter-spacing:-0.5px;margin-bottom:6px;">
      Weekly Intelligence Report</div>
    <div style="color:#8a9dc0;font-size:13px;">
      {today} &nbsp;&middot;&nbsp;
      USD/INR: <strong style="color:#c9a227;">Rs.{usd_inr}</strong>
    </div>
  </td></tr>

  <!-- WEEKLY SIGNAL -->
  <tr><td style="background:#fffbf0;border-top:3px solid #c9a227;padding:16px 28px;">
    <div style="font-size:9px;font-weight:700;color:#c9a227;text-transform:uppercase;
      letter-spacing:2px;margin-bottom:6px;">&#128225; This Week's Strategic Action</div>
    <div style="font-size:14px;color:#333;line-height:1.7;font-weight:600;">{signal}</div>
  </td></tr>

  <!-- SECTION 1: INDIAN PROJECTS -->
  <tr><td style="padding:20px 24px 10px;background:#fafbfd;">
    <div style="font-size:11px;font-weight:700;color:#1565c0;text-transform:uppercase;
      letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid #1565c0;">
      &#127470;&#127475; Top Indian Projects</div>
  </td></tr>
  <table width="100%" cellpadding="0" cellspacing="0">{indian_html}</table>

  <!-- SECTION 2: GLOBAL PROJECTS -->
  <tr><td style="padding:20px 24px 10px;background:#fafbfd;">
    <div style="font-size:11px;font-weight:700;color:#2e7d32;text-transform:uppercase;
      letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid #2e7d32;">
      &#127758; Top Global Projects</div>
  </td></tr>
  <table width="100%" cellpadding="0" cellspacing="0">{global_html}</table>

  <!-- SECTION 3: RAW MATERIALS -->
  <tr><td style="padding:20px 24px 10px;background:#fafbfd;">
    <div style="font-size:11px;font-weight:700;color:#c9a227;text-transform:uppercase;
      letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid #c9a227;">
      &#128202; Raw Material Prices &mdash; Chennai Market</div>
  </td></tr>
  <tr><td>
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr style="background:#1a2744;">
        <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Material</th>
        <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Per Tonne</th>
        <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Per KG</th>
        <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Week Change</th>
        <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Source</th>
      </tr>
      {materials_rows}
    </table>
  </td></tr>
  <tr><td style="padding:10px 24px 16px;background:#f9f9f9;">
    <div style="font-size:12px;color:#555;">
      &#128178; <strong>USD/INR Impact:</strong> {usd_impact}</div>
  </td></tr>

  <!-- SECTION 4: RAILWAY TENDERS -->
  <tr><td style="padding:20px 24px 10px;background:#fafbfd;">
    <div style="font-size:11px;font-weight:700;color:#7b1fa2;text-transform:uppercase;
      letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid #7b1fa2;">
      &#128646; Indian Railways Tenders &mdash; IREPS
      <span style="font-size:9px;font-weight:400;color:#888;margin-left:8px;
        text-transform:none;">&#11088; = Approved vendor category</span>
    </div>
  </td></tr>
  <table width="100%" cellpadding="0" cellspacing="0">{railway_html}</table>

  <!-- FOOTER -->
  <tr><td style="padding:20px 28px;background:#1a2744;text-align:center;">
    <div style="font-size:11px;color:#8a9dc0;line-height:1.9;">
      Auto-generated by Spearforge Intel Bot &nbsp;&middot;&nbsp; Every Friday 7:00 AM IST<br>
      enquiries@spearforgeindustries.com &nbsp;&middot;&nbsp; Chennai, Tamil Nadu, India<br>
      <span style="color:#c9a227;font-weight:700;">"Global Precision. Industrial Excellence."</span>
    </div>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""


# ================================================================
# STEP 6 — SEND HTML EMAIL VIA GMAIL
# ================================================================
def send_email(html_body, today):
    sender_email   = SENDER_EMAIL
    receiver_email = RECEIVER_EMAIL
    app_password   = os.environ["GMAIL_APP_PASSWORD"]

    msg             = MIMEMultipart("alternative")
    msg["From"]     = f"Spearforge Intel Bot <{sender_email}>"
    msg["To"]       = receiver_email
    msg["Subject"]  = f"{REPORT_SUBJECT} — {today}"

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    print(f"  Email sent to {receiver_email}")


# ================================================================
# MAIN
# ================================================================
def run_automation():
    today = datetime.now().strftime("%d %B %Y")
    print(f"\n{'='*60}")
    print(f"  Spearforge Intel Bot — {today}")
    print(f"{'='*60}")

    try:
        # Step 1: Generate report via Gemini + Google Search
        print("\nStep 1: Generating report with live web search...")
        raw_response = generate_report()

        # Step 2: Parse JSON
        print("Step 2: Parsing response...")
        data = parse_response(raw_response)
        indian_count  = len(data.get("indianProjects", []))
        global_count  = len(data.get("globalProjects", []))
        material_count = len(data.get("rawMaterials", []))
        tender_count  = len(data.get("railwayTenders", []))
        print(f"  Found: {indian_count} Indian projects, {global_count} global projects, "
              f"{material_count} materials, {tender_count} railway tenders")

        # Step 3: Build HTML email
        print("Step 3: Building HTML email...")
        html_body = build_html_email(data)

        # Step 4: Send
        print("Step 4: Sending email...")
        send_email(html_body, today)

        print(f"\n  SUCCESS — Report delivered to {RECEIVER_EMAIL}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n  ERROR: {e}")
        # Send plain text error notification
        try:
            app_password = os.environ["GMAIL_APP_PASSWORD"]
            msg = MIMEMultipart()
            msg["From"]    = SENDER_EMAIL
            msg["To"]      = RECEIVER_EMAIL
            msg["Subject"] = f"Spearforge Intel Bot — Error {today}"
            msg.attach(MIMEText(f"The weekly intelligence report failed:\n\n{str(e)}", "plain"))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SENDER_EMAIL, app_password)
                server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
            print("  Error notification sent.")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    run_automation()
