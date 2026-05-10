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
# STEP 1 -- GEMINI SETUP
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
# STEP 2 -- PROMPT
# ================================================================
def get_prompt_part1():
    """Exchange rates + Indian Projects + Global Projects"""
    today = datetime.now().strftime("%d %B %Y")
    return f"""You are the weekly intelligence analyst for Spearforge Industrial and Engineering Solutions.

COMPANY BACKGROUND:
Spearforge is an ISO 9001:2015 certified, Indian Railways Approved Vendor based in Chennai, Tamil Nadu, India.
Full product catalogue:
- Perforated Cable Trays (PCT) and Ladder Type Cable Trays (LCT) -- IS:2062/1079, all finishes
- Electrical Enclosures (IP55/IP65/IP66, CPRI Certified, CRCA and SS, RAL 7035)
- Solar Mounting Structures (IS:875 Part 3, IEC 61215, HDG MS + Aluminium 6063-T5)
- Die Storage Racks (500kg to 10,000+kg per shelf, all-welded IS:2062 MS)
- Supermarket Racks (Centre Gondola, Wall-Side, End Cap, Heavy-Duty, CRC/GI sheet)
- Electrical Junction Boxes (MS/SS, IP55/IP66, custom sizes)
- Cable Raceways (floor and ceiling, single/dual compartment)
Export markets: US, Europe, Middle East, UK.

Today is {today}. Show project values as Rs.X,XXX Cr (original currency in brackets).

CRITICAL RULES:
- Use Google Search actively. Search multiple queries to find projects.
- Include real projects you find — do not return N/A or placeholder entries.
- If you cannot find 6 Indian projects, include however many you find — even 2 or 3 is fine.
- If a source name is not clear, write "Industry News" — do not write N/A.
- Keep each field to ONE LINE maximum.
- For AWARDED projects, name who won and whether EPC or manufacturer.
- Search specifically for: NTPC awards, BESS India, Solar tenders SECI, Metro rail India,
  Data centre India 2026, Retail expansion India, Automotive plant India.
- If project value is not publicly available, write "Value not disclosed" -- still include the project.
- Do NOT return N/A entries. If genuinely nothing found for a section, write one line:
  NOTE: No major projects found this week for this category.
- Start your response DIRECTLY with SECTION 0. Nothing before it.

==============================================================
SECTION 0 - EXCHANGE RATES
==============================================================
Search Google Finance or xe.com for today's live rates.

RATE: USD | [rate] | [+/-X% vs last week] | [impact on Spearforge US exports]
RATE: AED | [rate] | [+/-X% vs last week] | [impact on Spearforge UAE exports]
RATE: EUR | [rate] | [+/-X% vs last week] | [impact on Spearforge Europe exports]
RATE: GBP | [rate] | [+/-X% vs last week] | [impact on Spearforge UK exports]
RATE: SAR | [rate] | [+/-X% vs last week] | [impact on Spearforge Saudi exports]

==============================================================
SECTION 1 - TOP INDIAN PROJECTS
==============================================================
Find 6 major Indian projects from past 10 days. Search for:
NTPC projects and awards, BESS tenders and awards, Solar EPC (SECI/NTPC/DISCOMs),
Metro rail (all cities), Data centres, Airport MEP, Retail/supermarket expansions,
Automotive/manufacturing plant expansions, any major EPC contract awards.

For each use EXACTLY this format:
PROJECT: [Title]
VALUE: [Rs.X,XXX Cr] ([original currency])
CLIENT: [Name] | LOCATION: [City, State] | STATUS: [Tendered/Awarded/Announced]
WINNER: [Company -- EPC/Manufacturer] (if Awarded, else N/A)
PRODUCTS: [Specific Spearforge products that apply]
OPPORTUNITY: [One line on what Spearforge should do]
SOURCE: [Publication name only]
---

==============================================================
SECTION 2 - TOP GLOBAL PROJECTS
==============================================================
Find 4 global projects (Middle East, Europe, US) from past 10 days.
Priority: BESS, Solar EPC, Data centres, Industrial plants, Metro/Rail, Retail.

For each use EXACTLY this format:
PROJECT: [Title]
VALUE: [Rs.X,XXX Cr] ([original currency])
COUNTRY: [Country] | LOCATION: [City] | STATUS: [status] | CLIENT: [Name]
WINNER: [Company -- EPC/Manufacturer] (if Awarded, else N/A)
PRODUCTS: [Specific Spearforge products that apply]
OPPORTUNITY: [One line export angle]
SOURCE: [Publication name only]
---

==============================================================
STRATEGIC ACTION
==============================================================
ACTION: [One critical thing Spearforge should do this week]
"""


def get_prompt_part2():
    """Raw material prices only"""
    today = datetime.now().strftime("%d %B %Y")
    return f"""You are the raw material price analyst for Spearforge Industrial and Engineering Solutions,
a sheet metal manufacturer in Chennai, India.

Today is {today}.

Search for current Chennai / South India steel prices from SteelMint, Steel360,
IndiaMart, TradeIndia, Economic Times Commodities, Business Standard commodities,
or any Indian steel trader website.
Search: "MS HR sheet price Chennai 2026", "GI sheet price India May 2026",
"SS 304 price India 2026", "aluminium extrusion price India 2026".

YOU MUST include ALL 9 materials. Do not skip any.
If exact Chennai price is not found, use closest South India or national market price.

CRITICAL RULES:
- Do NOT add any introduction or summary text.
- Start your response DIRECTLY with SECTION 3. Nothing before it.
- SOURCE field: website/publication name only. No URLs.

==============================================================
SECTION 3 - RAW MATERIAL PRICES (Chennai market this week)
==============================================================
For each material use EXACTLY this one-line format:
MATERIAL: [name] | TONNE: [Rs.XX,XXX] | KG: [Rs.XX.XX] | CHANGE: [Rising/Falling/Stable X%] | SOURCE: [name only]

ALL 9 materials are mandatory:
1. MS HR Sheet 2mm
2. MS HR Sheet 3mm
3. MS CR Sheet 1.2mm
4. MS CR Sheet 1.6mm
5. GI Sheet 1.2mm
6. GI Sheet 1.6mm
7. SS 304 Sheet 1.2mm
8. SS 304 Sheet 1.6mm
9. Aluminium 6063-T5 Extrusion

USD/INR IMPACT: [One line on how current USD/INR rate affects Spearforge import costs]
"""


# ================================================================
# STEP 3 -- CALL GEMINI WITH GOOGLE SEARCH GROUNDING
# Two separate calls so neither gets truncated
# ================================================================
def call_gemini(api_key, model_id, prompt, label=""):
    url = (f"https://generativelanguage.googleapis.com/v1beta"
           f"/models/{model_id}:generateContent?key={api_key}")
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
    data = resp.json()

    # Extract token usage from response metadata
    usage         = data.get("usageMetadata", {})
    input_tokens  = usage.get("promptTokenCount", 0)
    output_tokens = usage.get("candidatesTokenCount", 0)
    total_tokens  = usage.get("totalTokenCount", 0)

    print(f"  [{label}] Input: {input_tokens:,} | Output: {output_tokens:,} | Total: {total_tokens:,} tokens")

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return text, input_tokens, output_tokens, total_tokens


# Gemini 1.5 Flash free tier limits (as of May 2026)
FREE_TIER_LIMITS = {
    "rpm":  15,          # Requests per minute
    "rpd":  1500,        # Requests per day
    "tpm":  1_000_000,   # Tokens per minute
    "tpd":  None,        # No daily token limit on free tier
}


def generate_report():
    model_name = find_best_model()
    model_id   = model_name.replace("models/", "")
    api_key    = os.environ["GEMINI_API_KEY"]

    print(f"  Using model: {model_id}")

    print("  Call 1: Exchange rates + Projects...")
    part1, in1, out1, tot1 = call_gemini(api_key, model_id, get_prompt_part1(), "Part 1")

    print("  Call 2: Raw material prices...")
    part2, in2, out2, tot2 = call_gemini(api_key, model_id, get_prompt_part2(), "Part 2")

    # Weekly token summary
    total_in    = in1  + in2
    total_out   = out1 + out2
    total_all   = tot1 + tot2
    calls_week  = 2
    calls_month = calls_week * 4   # ~4 Fridays/month
    tokens_month = total_all * 4

    print(f"\n  TOKEN SUMMARY THIS RUN:")
    print(f"    Input tokens  : {total_in:,}")
    print(f"    Output tokens : {total_out:,}")
    print(f"    Total tokens  : {total_all:,}")
    print(f"    API calls     : {calls_week} (this run)")
    print(f"  MONTHLY PROJECTION (4 runs):")
    print(f"    Est. tokens/month : {tokens_month:,}")
    print(f"    Est. calls/month  : {calls_month}")
    print(f"    Free tier RPD     : {FREE_TIER_LIMITS['rpd']:,} (you use {calls_month})")
    print(f"    Free tier TPM     : {FREE_TIER_LIMITS['tpm']:,}")

    # Store token stats for email footer
    generate_report.last_stats = {
        "model":         model_id,
        "input_tokens":  total_in,
        "output_tokens": total_out,
        "total_tokens":  total_all,
        "calls":         calls_week,
        "monthly_tokens": tokens_month,
        "monthly_calls":  calls_month,
        "rpd_limit":     FREE_TIER_LIMITS["rpd"],
        "tpm_limit":     FREE_TIER_LIMITS["tpm"],
    }

    return part1 + "\n" + part2


generate_report.last_stats = {}


def build_token_panel(stats):
    if not stats:
        return ""
    pct_rpd = round((stats["monthly_calls"] / stats["rpd_limit"]) * 100, 1)
    bar_w   = min(int(pct_rpd * 2), 200)
    bar_clr = "#27ae60" if pct_rpd < 50 else "#e67e22" if pct_rpd < 80 else "#c0392b"
    return f"""
<tr><td style="padding:16px 24px;background:#f9f9f9;border-top:1px solid #eef0f5;">
  <div style="font-size:10px;font-weight:700;color:#1a2744;text-transform:uppercase;
    letter-spacing:2px;margin-bottom:12px;">API Token Usage This Run</div>
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td style="width:50%;padding-right:12px;vertical-align:top;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="padding:6px 10px;background:#fff;border:1px solid #eee;border-radius:4px;margin-bottom:4px;">
              <div style="font-size:9px;color:#888;text-transform:uppercase;">Model</div>
              <div style="font-size:12px;font-weight:700;color:#1a2744;">{stats["model"]}</div>
            </td>
          </tr>
          <tr><td style="padding:4px 0;"></td></tr>
          <tr>
            <td style="padding:6px 10px;background:#fff;border:1px solid #eee;border-radius:4px;">
              <div style="font-size:9px;color:#888;text-transform:uppercase;">This Run</div>
              <div style="font-size:12px;font-weight:700;color:#1a2744;">
                {stats["total_tokens"]:,} tokens &nbsp;·&nbsp; {stats["calls"]} API calls</div>
              <div style="font-size:10px;color:#888;margin-top:2px;">
                Input: {stats["input_tokens"]:,} &nbsp;|&nbsp; Output: {stats["output_tokens"]:,}</div>
            </td>
          </tr>
        </table>
      </td>
      <td style="width:50%;padding-left:12px;vertical-align:top;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="padding:6px 10px;background:#fff;border:1px solid #eee;border-radius:4px;margin-bottom:4px;">
              <div style="font-size:9px;color:#888;text-transform:uppercase;">Monthly Projection (4 runs)</div>
              <div style="font-size:12px;font-weight:700;color:#1a2744;">
                ~{stats["monthly_tokens"]:,} tokens &nbsp;·&nbsp; {stats["monthly_calls"]} calls</div>
            </td>
          </tr>
          <tr><td style="padding:4px 0;"></td></tr>
          <tr>
            <td style="padding:6px 10px;background:#fff;border:1px solid #eee;border-radius:4px;">
              <div style="font-size:9px;color:#888;text-transform:uppercase;margin-bottom:4px;">
                Free Tier Usage (Requests/Day limit: {stats["rpd_limit"]:,})</div>
              <div style="background:#eee;border-radius:4px;height:8px;width:200px;">
                <div style="background:{bar_clr};height:8px;border-radius:4px;width:{bar_w}px;"></div>
              </div>
              <div style="font-size:10px;color:{bar_clr};font-weight:700;margin-top:4px;">
                {stats["monthly_calls"]} / {stats["rpd_limit"]:,} requests/day &nbsp;·&nbsp; {pct_rpd}% used</div>
              <div style="font-size:10px;color:#888;margin-top:2px;">
                TPM limit: {stats["tpm_limit"]:,} &nbsp;·&nbsp; Well within free tier ✓</div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</td></tr>"""
def build_html_from_text(text):
    today = datetime.now().strftime("%d %B %Y")

    SECTIONS = {
        "SECTION 0": {"color": "#37474f", "icon": "FX", "label": "Exchange Rates -- Live"},
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

        # ---- PRE-PROCESSING: Normalize Gemini output variations ----
        # Strip leading numbers like "1. " "12. " that Gemini adds to lists
        line = re.sub(r'^\d+\.\s+', '', line)
        # Strip bold markdown ** from both ends but keep content
        line = re.sub(r'^\*\*(.+)\*\*$', r'\1', line)
        line = re.sub(r'^\*\*', '', line)
        # If line contains "| TONNE:" it's a material row — add prefix if missing
        if "| TONNE:" in line and not line.startswith("MATERIAL:"):
            line = "MATERIAL: " + line
        # If line contains "| LOCATION:" or "| STATUS:" it's a project CLIENT line
        if ("| LOCATION:" in line or "| STATUS:" in line) and not any(
                line.startswith(k) for k in ["CLIENT:", "COUNTRY:", "RAILWAY UNIT:"]):
            line = "CLIENT: " + line

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

        # Skip junk intro lines Gemini sometimes adds
        if ("Weekly Intelligence Report" in line
                or "Spearforge Industrial" in line
                or line.startswith("Date:") or line.startswith("USD/INR:")
                or line.startswith("*Date") or line.startswith("*USD")):
            continue

        # RATE lines (Section 0 -- Exchange Rates)
        if line.startswith("RATE:"):
            parts    = [p.strip() for p in line.replace("RATE:", "").split("|")]
            currency = parts[0] if len(parts) > 0 else ""
            rate     = parts[1] if len(parts) > 1 else ""
            change   = parts[2] if len(parts) > 2 else ""
            impact   = parts[3] if len(parts) > 3 else ""
            chg_color = ("#c0392b" if "+" in change else
                         "#27ae60" if "-" in change else "#546e7a")
            CURRENCY_FLAGS = {
                "USD": "🇺🇸", "AED": "🇦🇪", "EUR": "🇪🇺",
                "GBP": "🇬🇧", "SAR": "🇸🇦"
            }
            flag = CURRENCY_FLAGS.get(currency, "")
            html_body += f"""<tr style="border-bottom:1px solid #eef0f5;">
  <td style="padding:10px 14px;font-size:13px;font-weight:700;color:#1a2744;width:12%;">
    {flag} {currency}</td>
  <td style="padding:10px 14px;font-size:15px;font-weight:800;color:#37474f;width:18%;">
    Rs.{rate}</td>
  <td style="padding:10px 14px;font-size:12px;font-weight:700;color:{chg_color};width:15%;">
    {change}</td>
  <td style="padding:10px 14px;font-size:12px;color:#555;">{impact}</td>
</tr>"""
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

        # PROJECT — also catches "Project Name:" or bare project titles in Section 1/2
        # Skip N/A placeholder entries Gemini returns when it finds nothing
        if line.startswith("PROJECT:") or line.startswith("Project Name:"):
            content = re.split(r':\s*', line, 1)[1].strip() if ':' in line else line
            if (content.strip().upper() == "N/A"
                    or "no major" in content.lower()
                    or "no additional" in content.lower()
                    or "not found" in content.lower()
                    or "no projects" in content.lower()):
                # Skip this entire project block by flagging it
                current_color = current_color  # keep color unchanged
                continue
            html_body += f"""<tr><td style="padding:14px 24px 2px;">
  <div style="font-size:15px;font-weight:700;color:#1a2744;">{content}</div></td></tr>"""
            continue

        # VALUE
        if line.startswith("VALUE:"):
            content = line.replace("VALUE:", "").strip()
            if not content or content.upper() == "N/A":
                content = "Value not disclosed"
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

        # SOURCE / URL -- show as plain text only, no links (avoids 404 errors)
        if line.startswith("SOURCE:") or line.startswith("URL:"):
            content = line.replace("SOURCE:", "").replace("URL:", "").strip()
            # Remove any URLs Gemini added despite instructions
            content = re.sub(r'https?://\S+', '', content).replace("--", "").strip()
            if content:
                html_body += f"""<tr><td style="padding:2px 24px 10px;">
  <div style="font-size:11px;color:#888;">&#128240; Source: {content}</div></td></tr>"""
            continue

        # MATERIAL rows (Section 3)
        if line.startswith("MATERIAL:"):
            parts    = [p.strip() for p in line.split("|")]
            mat_name = parts[0].replace("MATERIAL:", "").strip()
            tonne    = next((p.replace("TONNE:", "").strip() for p in parts if "TONNE:" in p), "--")
            kg       = next((p.replace("KG:", "").strip() for p in parts if "KG:" in p), "--")
            change   = next((p.replace("CHANGE:", "").strip() for p in parts if "CHANGE:" in p), "--")
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

    # Exchange rate table header injection
    fx_header = """<tr><td style="padding:0;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr style="background:#37474f;">
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;width:12%;">Currency</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;width:20%;">Rate to INR</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;width:15%;">Week Change</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Export Impact for Spearforge</th>
</tr>"""
    first_rate = html_body.find('<tr style="border-bottom:1px solid #eef0f5;">\n  <td style="padding:10px 14px;font-size:13px;font-weight:700;color:#1a2744;width:12%;">')
    if first_rate != -1:
        html_body = html_body[:first_rate] + fx_header + html_body[first_rate:]
        last_rate  = html_body.rfind('width:12%;">')
        if last_rate != -1:
            close_pos = html_body.find('</tr>', last_rate) + 5
            html_body = html_body[:close_pos] + "</table></td></tr>" + html_body[close_pos:]

    # Material table header injection
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
  <div style="color:#8a9dc0;font-size:13px;">{today} &nbsp;&middot;&nbsp; Auto-generated every Friday 7:00 AM IST</div>
</td></tr>

<table width="100%" cellpadding="0" cellspacing="0">
  {html_body}
</table>

{build_token_panel(generate_report.last_stats)}

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
# STEP 5 -- SEND EMAIL
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
