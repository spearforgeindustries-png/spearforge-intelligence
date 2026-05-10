import os
import re
import smtplib
import requests
import google.generativeai as genai
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ================================================================
# CONFIGURATION
# ================================================================
SENDER_EMAIL   = "vimal.dgv@gmail.com"
RECEIVER_EMAIL = "vimal.prakash@spearforgeindustries.com"
REPORT_SUBJECT = "Spearforge Weekly Intelligence Report"
USD_TO_INR     = 83.5  # Update weekly

# ================================================================
# STEP 1 — GEMINI SETUP
# ================================================================
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def find_best_model():
    try:
        for m in genai.list_models():
            if "flash" in m.name.lower() and "generateContent" in m.supported_generation_methods:
                print(f"  Found model: {m.name}")
                return m.name
    except Exception as e:
        print(f"  Could not list models: {e}")
    return "models/gemini-1.5-flash"


# ================================================================
# STEP 2 — PROMPT
# ================================================================
def get_prompt():
    today = datetime.now().strftime("%d %B %Y")
    return f"""You are the weekly intelligence analyst for Spearforge Industrial and Engineering Solutions.

COMPANY BACKGROUND:
Spearforge is an ISO 9001:2015 certified, Indian Railways Approved Vendor based in Chennai, Tamil Nadu, India.
Full product catalogue:
- Perforated Cable Trays (PCT) and Ladder Type Cable Trays (LCT) — IS:2062/1079, all finishes
- Electrical Enclosures (IP55/IP65/IP66, CPRI Certified, CRCA and SS, RAL 7035)
- Solar Mounting Structures (IS:875 Part 3, IEC 61215, HDG MS + Aluminium 6063-T5)
- Die Storage Racks (500kg to 10,000+kg per shelf, all-welded IS:2062 MS)
- Supermarket Racks (Centre Gondola, Wall-Side, End Cap, Heavy-Duty, CRC/GI sheet)
- Electrical Junction Boxes (MS/SS, IP55/IP66, custom sizes)
- Cable Raceways (floor and ceiling, single/dual compartment)
Export markets: US, Europe, Middle East.

Today is {today}. USD/INR: {USD_TO_INR}. Show values as Rs.X,XXX Cr (original currency in brackets).

RULES:
- Use Google Search. Real verified data from the past 10 days only.
- No fabrication. Skip any item without a verified source URL.
- Keep each field to ONE LINE maximum.
- For AWARDED projects, always name who won — EPC contractor or manufacturer, and their type.
- Never miss major NTPC, SECI, Indian Railways, Metro, Data Centre, BESS project news.

==============================================================
SECTION 1 - TOP INDIAN PROJECTS
==============================================================
Find 8 major Indian projects from the past 10 days. Cast a wide net — search for:
- NTPC projects (coal, solar, BESS, transmission) -- especially the 1200MW and any new awards
- BESS / Battery Energy Storage tenders and awards
- Solar EPC project awards and tenders (SECI, NTPC, state DISCOMs)
- Metro rail projects (all cities -- Chennai, Bangalore, Mumbai, Delhi, Hyderabad, Pune, Kochi)
- Data centre construction announcements
- Industrial plant / factory construction
- Airport MEP packages
- Retail / hypermarket / supermarket chain expansions (relevant for Supermarket Racks)
- Automotive plant expansions or new factories (relevant for Die Storage Racks)
- Any major EPC contract awards -- name the winner and whether EPC or manufacturer

For each use EXACTLY this format:
PROJECT: [Title]
VALUE: [Rs.X,XXX Cr] ([original currency])
CLIENT: [Owner/Client name] | LOCATION: [City, State] | STATUS: [Tendered/Awarded/Announced]
WINNER: [Company name -- EPC Contractor / Manufacturer / Developer] (only if Awarded, else write N/A)
PRODUCTS: [Specific Spearforge products that apply from catalogue above]
OPPORTUNITY: [One line -- what Spearforge should do and who to contact]
SOURCE: [Publication name] -- [https://full-url]
---

==============================================================
SECTION 2 - TOP GLOBAL PROJECTS
==============================================================
Find 5 major global projects from past 10 days -- Middle East, Europe, or US.
Priority: BESS, Solar EPC, Data centres, Industrial plants, Metro/Rail, Retail expansion.
For awarded projects, name who won and their type (EPC/manufacturer).

For each use EXACTLY this format:
PROJECT: [Title]
VALUE: [Rs.X,XXX Cr] ([original currency])
COUNTRY: [Country] | LOCATION: [City/Region] | STATUS: [status] | CLIENT: [Name]
WINNER: [Company name -- EPC / Manufacturer] (if Awarded, else N/A)
PRODUCTS: [Specific Spearforge products that apply]
OPPORTUNITY: [One line export angle and entry strategy]
SOURCE: [Publication name] -- [https://full-url]
---

==============================================================
SECTION 3 - RAW MATERIAL PRICES (Chennai market this week)
==============================================================
Search for current Chennai / South India steel prices from ANY of these sources:
SteelMint (steelmint.com), Steel360 (steel360.com), IndiaMart steel listings,
TradeIndia steel prices, Economic Times Commodities, Business Standard commodities,
or any Indian steel trader website. Search "MS HR sheet price Chennai 2026" and
"GI sheet price India May 2026" and "SS 304 sheet price India 2026".

For each material use EXACTLY this one-line format:
MATERIAL: [name and spec] | TONNE: [Rs.XX,XXX] | KG: [Rs.XX.XX] | CHANGE: [Rising/Falling/Stable X%] | SOURCE: [https://url]

Cover these materials:
MS HR Sheet 2mm, MS HR Sheet 3mm, MS CR Sheet 1.2mm, MS CR Sheet 1.6mm,
GI Sheet 1.2mm, GI Sheet 1.6mm, SS 304 Sheet 1.2mm, SS 304 Sheet 1.6mm, Aluminium 6063-T5

USD/INR IMPACT: [One line on how current rate affects Spearforge import-linked costs]

==============================================================
STRATEGIC ACTION
==============================================================
ACTION: [One critical thing Spearforge should do this week based on all the above intelligence]
"""


# ================================================================
# STEP 3 — CALL GEMINI WITH GOOGLE SEARCH GROUNDING
# ================================================================
def generate_report():
    model_name = find_best_model()
    model_id   = model_name.replace("models/", "")
    api_key    = os.environ["GEMINI_API_KEY"]
    url        = (f"https://generativelanguage.googleapis.com/v1beta"
                  f"/models/{model_id}:generateContent?key={api_key}")

    prompt = get_prompt()
    print(f"  Calling Gemini REST API ({model_id}) with Google Search grounding...")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools":    [{"google_search": {}}],
        "generationConfig": {
            "temperature":     0.1,
            "maxOutputTokens": 8192
        }
    }

    resp = requests.post(url, json=payload, timeout=120)

    if resp.status_code != 200:
        raise ValueError(f"Gemini API error {resp.status_code}: {resp.text[:400]}")

    data     = resp.json()
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    print(f"  Gemini responded ({len(raw_text)} chars)")
    return raw_text


# ================================================================
# STEP 4 — BUILD HTML EMAIL FROM PLAIN TEXT
# ================================================================
def build_html_from_text(text):
    today = datetime.now().strftime("%d %B %Y")

    SECTIONS = {
        "SECTION 1": {"color": "#1565c0", "icon": "IN", "label": "Top Indian Projects"},
        "SECTION 2": {"color": "#2e7d32", "icon": "GL", "label": "Top Global Projects"},
        "SECTION 3": {"color": "#c9a227", "icon": "RM", "label": "Raw Material Prices -- Chennai Market"},
    }

    current_color   = "#c9a227"
    current_section = ""
    html_body       = ""
    in_strategic    = False

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        # Skip separator lines
        if re.match(r'^[=\-]{4,}$', line):
            continue

        # Section headers
        matched = False
        for key, cfg in SECTIONS.items():
            if key in line.upper():
                current_color   = cfg["color"]
                current_section = key
                in_strategic    = False
                html_body += f"""<tr><td style="padding:20px 24px 8px;background:#fafbfd;">
  <div style="font-size:11px;font-weight:700;color:{cfg['color']};text-transform:uppercase;
    letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid {cfg['color']};">
    {cfg['label']}</div></td></tr>"""
                matched = True
                break
        if matched:
            continue

        # Strategic Action header
        if "STRATEGIC ACTION" in line.upper():
            in_strategic  = True
            current_color = "#c9a227"
            html_body += """<tr><td style="background:#1a2744;padding:16px 24px 4px;">
  <div style="font-size:10px;font-weight:700;color:#c9a227;text-transform:uppercase;
    letter-spacing:2px;margin-bottom:6px;">Strategic Action This Week</div>"""
            continue

        # ACTION line
        if line.startswith("ACTION:"):
            content = line.replace("ACTION:", "").strip()
            html_body += f"""<div style="font-size:14px;color:#ffffff;font-weight:600;
  line-height:1.6;padding-bottom:12px;">{content}</div></td></tr>"""
            in_strategic = False
            continue

        # Divider
        if line == "---":
            html_body += """<tr><td style="padding:0 24px;">
  <hr style="border:none;border-top:1px solid #eef0f5;margin:4px 0;"></td></tr>"""
            continue

        # PROJECT
        if line.startswith("PROJECT:"):
            content = line.split(":", 1)[1].strip()
            html_body += f"""<tr><td style="padding:14px 24px 2px;">
  <div style="font-size:15px;font-weight:700;color:#1a2744;">{content}</div></td></tr>"""
            continue

        # VALUE
        if line.startswith("VALUE:"):
            content = line.replace("VALUE:", "").strip()
            html_body += f"""<tr><td style="padding:2px 24px 4px;">
  <div style="font-size:18px;font-weight:800;color:{current_color};">{content}</div></td></tr>"""
            continue

        # CLIENT / COUNTRY / RAILWAY UNIT
        if any(line.startswith(k) for k in ["CLIENT:", "COUNTRY:", "RAILWAY UNIT:"]):
            html_body += f"""<tr><td style="padding:2px 24px;">
  <div style="font-size:12px;color:#666;">{line}</div></td></tr>"""
            continue

        # WINNER
        if line.startswith("WINNER:"):
            content = line.replace("WINNER:", "").strip()
            if content and content != "N/A":
                html_body += f"""<tr><td style="padding:4px 24px;">
  <div style="font-size:12px;background:#fff0f0;border-left:3px solid #c0392b;
    padding:6px 12px;border-radius:0 4px 4px 0;">
    <strong style="color:#c0392b;">Contract Winner:</strong> {content}</div></td></tr>"""
            continue

        # PRODUCTS
        if line.startswith("PRODUCTS:"):
            content = line.replace("PRODUCTS:", "").strip()
            html_body += f"""<tr><td style="padding:6px 24px 2px;">
  <div style="background:#f8f9fc;border-left:3px solid {current_color};
    padding:8px 12px;border-radius:0 4px 4px 0;font-size:12px;color:#444;">
    <strong style="color:{current_color};">Spearforge Products:</strong> {content}</div></td></tr>"""
            continue

        # OPPORTUNITY
        if line.startswith("OPPORTUNITY:"):
            content = line.replace("OPPORTUNITY:", "").strip()
            html_body += f"""<tr><td style="padding:2px 24px 8px;">
  <div style="font-size:12px;color:#444;background:#fffbf0;
    border-left:3px solid #c9a227;padding:6px 12px;border-radius:0 4px 4px 0;">
    <strong style="color:#c9a227;">Opportunity:</strong> {content}</div></td></tr>"""
            continue

        # SOURCE / URL
        if line.startswith("SOURCE:") or line.startswith("URL:"):
            url_match  = re.search(r'https?://\S+', line)
            label_part = re.sub(r'https?://\S+', '', line)
            label_part = re.sub(r'^(SOURCE:|URL:)', '', label_part).replace("--", "").strip()
            if url_match:
                link = url_match.group().rstrip(")")
                html_body += f"""<tr><td style="padding:2px 24px 10px;">
  <a href="{link}" style="font-size:11px;color:{current_color};
    font-weight:700;text-decoration:none;">Source: {label_part if label_part else link[:50]}</a></td></tr>"""
            else:
                html_body += f"""<tr><td style="padding:2px 24px 10px;">
  <div style="font-size:11px;color:#888;">{line}</div></td></tr>"""
            continue

        # MATERIAL rows (Section 3)
        if line.startswith("MATERIAL:"):
            parts    = [p.strip() for p in line.split("|")]
            mat_name = parts[0].replace("MATERIAL:", "").strip()
            tonne    = next((p.replace("TONNE:", "").strip() for p in parts if "TONNE:" in p), "—")
            kg       = next((p.replace("KG:", "").strip() for p in parts if "KG:" in p), "—")
            change   = next((p.replace("CHANGE:", "").strip() for p in parts if "CHANGE:" in p), "—")
            src_raw  = next((p.replace("SOURCE:", "").strip() for p in parts if "SOURCE:" in p), "#")
            clr      = "#c0392b" if "Rising" in change else ("#27ae60" if "Falling" in change else "#546e7a")
            html_body += f"""<tr>
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;font-size:12px;
    color:#333;font-weight:600;">{mat_name}</td>
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;font-size:13px;
    font-weight:800;color:#1a2744;">{tonne}</td>
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;font-size:12px;
    font-weight:700;color:#333;">{kg}</td>
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;font-size:12px;
    color:{clr};font-weight:700;">{change}</td>
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;">
    <a href="{src_raw}" style="font-size:11px;color:#c9a227;
      font-weight:700;text-decoration:none;">View</a></td></tr>"""
            continue

        # USD/INR IMPACT
        if line.startswith("USD/INR IMPACT:"):
            content = line.replace("USD/INR IMPACT:", "").strip()
            html_body += f"""<tr><td style="padding:10px 24px;background:#f9f9f9;
  border-top:1px solid #eef0f5;" colspan="5">
  <div style="font-size:12px;color:#555;">
    <strong>USD/INR Impact:</strong> {content}</div></td></tr>"""
            continue

        # DESCRIPTION / PRODUCT MATCH / APPROVED VENDOR
        if any(line.startswith(k) for k in ["DESCRIPTION:", "PRODUCT MATCH:", "APPROVED VENDOR:"]):
            key, _, val = line.partition(":")
            approved = ("YES" in val.upper() and "APPROVED" in key.upper())
            style    = "color:#c0392b;font-weight:700;" if approved else "color:#555;"
            prefix   = "APPROVED VENDOR CATEGORY  " if approved else ""
            html_body += f"""<tr><td style="padding:2px 24px;">
  <div style="font-size:12px;{style}">
    <strong>{key}:</strong> {prefix}{val.strip()}</div></td></tr>"""
            continue

        # Everything else
        if len(line) > 3 and not line.startswith("=="):
            html_body += f"""<tr><td style="padding:2px 24px;">
  <div style="font-size:12px;color:#777;">{line}</div></td></tr>"""

    # Material table header
    mat_header = """<tr><td style="padding:0;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr style="background:#1a2744;">
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Material</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Per Tonne</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Per KG</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Week Change</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Source</th>
</tr>"""

    first_mat = html_body.find('<tr>\n  <td style="padding:8px 14px;border-bottom')
    if first_mat != -1:
        html_body = html_body[:first_mat] + mat_header + html_body[first_mat:]
        last_mat  = html_body.rfind('style="font-size:11px;color:#c9a227;\n      font-weight:700;text-decoration:none;">View</a></td></tr>')
        if last_mat != -1:
            close_pos = last_mat + len('style="font-size:11px;color:#c9a227;\n      font-weight:700;text-decoration:none;">View</a></td></tr>')
            html_body = html_body[:close_pos] + "</table></td></tr>" + html_body[close_pos:]

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f2f8;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f8;padding:24px 0;">
<tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0"
  style="background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 4px 24px rgba(26,39,68,0.12);">

<tr><td style="background:linear-gradient(135deg,#1a2744 0%,#243560 100%);padding:28px 32px;">
  <div style="color:#c9a227;font-size:10px;font-weight:700;letter-spacing:3px;
    text-transform:uppercase;margin-bottom:8px;">Spearforge Industrial &amp; Engineering Solutions</div>
  <div style="color:#fff;font-size:24px;font-weight:800;margin-bottom:6px;">Weekly Intelligence Report</div>
  <div style="color:#8a9dc0;font-size:13px;">{today} &nbsp;&middot;&nbsp;
    USD/INR: <strong style="color:#c9a227;">Rs.{USD_TO_INR}</strong></div>
</td></tr>

<table width="100%" cellpadding="0" cellspacing="0">
  {html_body}
</table>

<tr><td style="padding:20px 28px;background:#1a2744;text-align:center;">
  <div style="font-size:11px;color:#8a9dc0;line-height:1.9;">
    Auto-generated by Spearforge Intel Bot &nbsp;&middot;&nbsp; Every Friday 7:00 AM IST<br>
    enquiries@spearforgeindustries.com &nbsp;&middot;&nbsp; Chennai, Tamil Nadu, India<br>
    <span style="color:#c9a227;font-weight:700;">"Global Precision. Industrial Excellence."</span>
  </div>
</td></tr>

</table></td></tr></table>
</body></html>"""


# ================================================================
# STEP 5 — SEND EMAIL
# ================================================================
def send_email(html_body, today):
    app_password   = os.environ["GMAIL_APP_PASSWORD"]
    msg            = MIMEMultipart("alternative")
    msg["From"]    = f"Spearforge Intel Bot <{SENDER_EMAIL}>"
    msg["To"]      = RECEIVER_EMAIL
    msg["Subject"] = f"{REPORT_SUBJECT} -- {today}"
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, app_password)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    print(f"  Email sent to {RECEIVER_EMAIL}")


# ================================================================
# MAIN
# ================================================================
def run_automation():
    today = datetime.now().strftime("%d %B %Y")
    print(f"\n{'='*60}")
    print(f"  Spearforge Intel Bot -- {today}")
    print(f"{'='*60}")
    try:
        print("\nStep 1: Generating report with live web search...")
        raw_response = generate_report()

        print("Step 2: Building HTML email...")
        html_body = build_html_from_text(raw_response)

        print("Step 3: Sending email...")
        send_email(html_body, today)

        print(f"\n  SUCCESS -- Report delivered to {RECEIVER_EMAIL}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n  ERROR: {e}")
        try:
            app_password = os.environ["GMAIL_APP_PASSWORD"]
            msg = MIMEMultipart()
            msg["From"]    = SENDER_EMAIL
            msg["To"]      = RECEIVER_EMAIL
            msg["Subject"] = f"Spearforge Intel Bot -- Error {today}"
            msg.attach(MIMEText(f"Report failed:\n\n{str(e)}", "plain"))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SENDER_EMAIL, app_password)
                server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        except Exception:
            pass
        raise


if __name__ == "__main__":
    run_automation()
