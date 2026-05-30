import os
import re
import time
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

SPEARFORGE_PROFILE = """
Spearforge Industrial and Engineering Solutions — Chennai, India
ISO 9001:2015 certified | Indian Railways Approved Vendor

TARGETING STRATEGY -- use in all project analysis:
- NEVER flag large conglomerates (Adani, RIL, NTPC, L&T, Tata) as direct targets.
  Vendor approval takes 12-18 months minimum.
- IDEAL Tier 1 targets: mid-size EPC contractors (200-2000 employees, no internal fabrication)
  Examples: Hartek Group, VIKRAN Engineering, InSolare, Oriano, Rays Power Infra
- IDEAL Tier 2 targets: electrical distributors/traders (20-200 employees, no factory)
  These source from Chinese imports currently -- that is Spearforge's entry angle.
- Always recommend the Tier 1 or Tier 2 sub-contractor, not the end client.
"""

# ================================================================
# GEMINI SETUP -- model priority list avoids deprecated names
# Dead as of June 2026: gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro
# ================================================================
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

DEAD_MODELS = {
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-001",
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-pro",
    "gemini-1.5-pro-001",
}

def find_best_model():
    PREFERRED = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]
    try:
        available = {
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        }
        for candidate in PREFERRED:
            if candidate in available:
                print(f"  Using model: {candidate}")
                return f"models/{candidate}"
        # Scan available for any live flash model
        for name in sorted(available):
            if "flash" in name and "latest" not in name and name not in DEAD_MODELS:
                print(f"  Fallback model: {name}")
                return f"models/{name}"
    except Exception as e:
        print(f"  Could not list models: {e}")
    # Hard fallback -- always a live model
    print("  Hard fallback: gemini-2.5-flash")
    return "models/gemini-2.5-flash"


# ================================================================
# PROMPTS
# ================================================================
def get_prompt_part1():
    today = datetime.now().strftime("%d %B %Y")
    return f"""You are the weekly intelligence analyst for Spearforge Industrial and Engineering Solutions.

COMPANY BACKGROUND:
Spearforge is an ISO 9001:2015 certified, Indian Railways Approved Vendor based in Chennai, India.
Products: Perforated/Ladder Cable Trays (IS:2062/1079), Electrical Enclosures (IP55/IP65/IP66, CPRI),
Solar Mounting Structures (IS:875 Part 3), Die Storage Racks, Supermarket Racks,
Electrical Junction Boxes, Cable Raceways.
Export markets: US, Europe, Middle East, UK.

Today is {today}. Show project values as Rs.X,XXX Cr (original currency in brackets).

CRITICAL RULES:
- Search EACH of the 5 trusted sources listed below for every project.
- If a project appears in MORE than one source, it is HIGH CONFIDENCE -- mark it.
- Include REAL projects only. Do not return N/A or placeholder entries.
- If value is not public, write "Value not disclosed" -- still include the project.
- Keep each field to ONE LINE maximum.
- For AWARDED projects, name who won and whether EPC or manufacturer.
- Start DIRECTLY with SECTION 1. Nothing before it.
- You MUST complete BOTH Section 1 and Section 2 in full. Do not stop early.

TRUSTED SOURCES (search all 5 for every project):
1. Mercom India (mercomindia.com) -- Solar, BESS, renewables
2. Economic Times Energy (economictimes.indiatimes.com) -- All sectors
3. Business Standard (business-standard.com) -- Infrastructure, energy
4. Construction World India (constructionworld.in) -- EPC awards
5. PV Magazine India (pv-magazine-india.com) -- Solar, storage

For global projects also search:
6. PV Tech (pvtech.org) -- Global solar and BESS
7. Recharge News (rechargenews.com) -- Global energy

MULTI-SOURCE RULE:
- VERIFIED_BY field: list ALL sources where you found this project.
- Found in 2+ sources: CONFIDENCE: High
- Found in 1 source: CONFIDENCE: Medium
- Cannot verify in any trusted source: skip the project.

==============================================================
SECTION 1 - TOP INDIAN PROJECTS
==============================================================
Find 6 major Indian projects from the past 10 days. Search for:
NTPC projects and awards, BESS tenders and awards, Solar EPC (SECI/NTPC/DISCOMs),
Metro rail (all cities), Data centres, Airport MEP, Retail/supermarket expansions,
Automotive/manufacturing plant expansions, major EPC contract awards.

For each use EXACTLY this format:
PROJECT: [Title]
VALUE: [Rs.X,XXX Cr] ([original currency])
CLIENT: [Name] | LOCATION: [City, State] | STATUS: [Tendered/Awarded/Announced]
WINNER: [Company -- EPC/Manufacturer] (if Awarded, else N/A)
PRODUCTS: [Specific Spearforge products that apply]
OPPORTUNITY: [One line -- which Tier 1 or Tier 2 EPC sub-contractor to approach and how]
VERIFIED_BY: [Source 1, Source 2, Source 3] | CONFIDENCE: [High/Medium]
---

==============================================================
SECTION 2 - TOP GLOBAL PROJECTS
==============================================================
Find 4 global projects (Middle East, Europe, US) from the past 10 days.
Priority: BESS, Solar EPC, Data centres, Industrial plants, Metro/Rail, Retail.

IMPORTANT: You MUST include all 4 global projects. Do not skip this section.

For each use EXACTLY this format:
PROJECT: [Title]
VALUE: [Rs.X,XXX Cr] ([original currency])
COUNTRY: [Country] | LOCATION: [City] | STATUS: [status] | CLIENT: [Name]
WINNER: [Company -- EPC/Manufacturer] (if Awarded, else N/A)
PRODUCTS: [Specific Spearforge products that apply]
OPPORTUNITY: [One line export angle]
VERIFIED_BY: [Source 1, Source 2] | CONFIDENCE: [High/Medium]
---

==============================================================
STRATEGIC ACTION
==============================================================
ACTION: [One critical thing Spearforge should do this week based on the projects above]
"""


def get_prompt_part2():
    today = datetime.now().strftime("%d %B %Y")
    return f"""You are the raw material price analyst for Spearforge Industrial and Engineering Solutions,
a sheet metal manufacturer in Chennai, India.

Today is {today}.

SOURCES TO USE (priority order):
1. PRIMARY: SteelMint India (steelmint.com)
2. SECONDARY: Steel360 (steel360.com)
3. TERTIARY: IndiaMart / JSW / SAIL official notifications

Search: "MS HR sheet price Chennai {today[:4]}", "GI sheet price South India {today[:4]}",
"SS 304 sheet price India {today[:4]}", "aluminium extrusion price Chennai {today[:4]}".

For each material: use PRIMARY if available, cross-check SECONDARY, note source.
If prices differ, use the average.

YOU MUST include ALL 9 materials. Do not skip any.
If Chennai-specific price not found, use South India or national market price.

CRITICAL RULES:
- Do NOT add any introduction or summary text.
- Start DIRECTLY with SECTION 3. Nothing before it.
- SOURCE field: write only the source name (SteelMint / Steel360 / IndiaMart etc.) -- NO URLs.

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
# EXCHANGE RATES -- two live APIs, cross-verified
# ================================================================
FX_CURRENCIES = {
    "USD": {"name": "US Dollar",     "flag": "US"},
    "AED": {"name": "UAE Dirham",    "flag": "AE"},
    "EUR": {"name": "Euro",          "flag": "EU"},
    "GBP": {"name": "British Pound", "flag": "GB"},
    "SAR": {"name": "Saudi Riyal",   "flag": "SA"},
}

def fetch_exchange_rates():
    results = {}
    try:
        resp = requests.get("https://open.er-api.com/v6/latest/INR", timeout=10)
        data = resp.json()
        if data.get("result") == "success":
            raw = data.get("rates", {})
            for curr in FX_CURRENCIES:
                if curr in raw and raw[curr] != 0:
                    results[curr] = {
                        "rate":    round(1 / raw[curr], 4),
                        "source1": "Open Exchange Rates",
                        "rate1":   round(1 / raw[curr], 4),
                    }
            print(f"  FX Source 1: {len(results)} currencies fetched")
    except Exception as e:
        print(f"  FX Source 1 failed: {e}")

    try:
        resp2 = requests.get(
            "https://api.frankfurter.app/latest?from=INR&to=USD,EUR,GBP", timeout=10)
        data2 = resp2.json()
        raw2  = data2.get("rates", {}) if isinstance(data2, dict) else {}
        for curr in ["USD", "EUR", "GBP"]:
            if curr in raw2 and raw2[curr] != 0:
                rate2 = round(1 / raw2[curr], 4)
                if curr in results:
                    results[curr]["rate2"]    = rate2
                    results[curr]["source2"]  = "Frankfurter (ECB)"
                    results[curr]["rate"]     = round((results[curr]["rate1"] + rate2) / 2, 2)
                    results[curr]["verified"] = True
        print("  FX Source 2: cross-verified USD, EUR, GBP")
    except Exception as e:
        print(f"  FX Source 2 failed: {e}")

    return results


# ================================================================
# GEMINI API CALL -- with retry on 429 and safety guard on response
# ================================================================
def call_gemini(api_key, model_id, prompt, label=""):
    url = (f"https://generativelanguage.googleapis.com/v1beta"
           f"/models/{model_id}:generateContent?key={api_key}")
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools":    [{"google_search": {}}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192}
    }
    for attempt in range(4):
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code == 429:
            wait = 70 * (attempt + 1)
            print(f"  [{label}] Rate limit (429). Waiting {wait}s... (attempt {attempt+1}/4)")
            time.sleep(wait)
            continue
        if resp.status_code != 200:
            raise ValueError(f"Gemini error {resp.status_code}: {resp.text[:400]}")

        data          = resp.json()
        usage         = data.get("usageMetadata", {})
        input_tokens  = usage.get("promptTokenCount", 0)
        output_tokens = usage.get("candidatesTokenCount", 0)
        total_tokens  = usage.get("totalTokenCount", 0)
        print(f"  [{label}] {input_tokens:,} in | {output_tokens:,} out | {total_tokens:,} total")

        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError(
                f"[{label}] Gemini returned no candidates. "
                f"Possible safety block. Full response: {str(data)[:300]}")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts or "text" not in parts[0]:
            finish = candidates[0].get("finishReason", "unknown")
            raise ValueError(
                f"[{label}] Gemini candidate has no text. finishReason: {finish}")

        return parts[0]["text"], input_tokens, output_tokens, total_tokens

    raise ValueError(f"[{label}] Still rate-limited after 4 attempts.")


# ================================================================
# CLAUDE API CALL -- analysis and strategic writing
# ================================================================
def call_claude(prompt, label=""):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(f"  [{label}] No ANTHROPIC_API_KEY -- skipping Claude")
        return None
    headers = {
        "x-api-key":         api_key,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
    }
    payload = {
        "model":      "claude-sonnet-4-6",
        "max_tokens": 4000,
        "messages":   [{"role": "user", "content": prompt}]
    }
    for attempt in range(3):
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            json=payload, headers=headers, timeout=90)
        if resp.status_code == 529:
            wait = 30 * (attempt + 1)
            print(f"  [{label}] Claude overloaded. Waiting {wait}s...")
            time.sleep(wait)
            continue
        if resp.status_code != 200:
            print(f"  [{label}] Claude error {resp.status_code} -- using Gemini output as-is")
            return None
        data    = resp.json()
        tokens  = data.get("usage", {})
        in_tok  = tokens.get("input_tokens", 0)
        out_tok = tokens.get("output_tokens", 0)
        cost    = round((in_tok * 3 + out_tok * 15) / 1e6, 4)
        print(f"  [{label}] Claude: {in_tok}+{out_tok} tokens (~${cost})")
        return data["content"][0]["text"]
    return None


# ================================================================
# GENERATE REPORT
# ================================================================
FREE_TIER_LIMITS = {"rpm": 15, "rpd": 1500, "tpm": 1_000_000}

def generate_report():
    model_name = find_best_model()
    model_id   = model_name.replace("models/", "")
    api_key    = os.environ["GEMINI_API_KEY"]

    print("  Fetching live exchange rates...")
    fx_data = fetch_exchange_rates()

    print("  [Gemini] Call 1: Projects across 5 trusted sources...")
    part1, in1, out1, tot1 = call_gemini(api_key, model_id, get_prompt_part1(), "Projects")

    claude_enhanced = part1
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("  [Claude] Analysing projects for tier targeting...")
        claude_prompt = f"""You are a strategic analyst for Spearforge Industrial and Engineering Solutions.
{SPEARFORGE_PROFILE}

Gemini found these projects this week:
---
{part1}
---

Enhance ONLY the OPPORTUNITY field for each project with a commercially realistic recommendation:
1. Never recommend approaching Adani, RIL, NTPC, L&T, Tata directly.
2. Identify the mid-size EPC sub-contractor who will execute this and name them.
3. If Chinese imports are involved, flag as "SUPPLY CHAIN DE-RISK opportunity".
4. Include: WHO to approach (company + job title), HOW (LinkedIn/email), WHAT angle.

Return the FULL text back with only the OPPORTUNITY fields changed. Keep everything else identical."""
        enhanced = call_claude(claude_prompt, "Claude-Analysis")
        if enhanced:
            claude_enhanced = enhanced
            print("  [Claude] Enhancement complete")
        time.sleep(5)
    else:
        print("  [Claude] Skipped -- ANTHROPIC_API_KEY not set")

    print("  Waiting 12s before materials call...")
    time.sleep(12)

    print("  [Gemini] Call 2: Raw material prices...")
    part2, in2, out2, tot2 = call_gemini(api_key, model_id, get_prompt_part2(), "Materials")

    total_in  = in1 + in2
    total_out = out1 + out2
    total_all = tot1 + tot2
    print(f"\n  TOKENS: {total_all:,} this run | ~{total_all*4:,}/month")

    generate_report.last_stats = {
        "model":          model_id,
        "input_tokens":   total_in,
        "output_tokens":  total_out,
        "total_tokens":   total_all,
        "calls":          2,
        "monthly_tokens": total_all * 4,
        "monthly_calls":  8,
        "rpd_limit":      FREE_TIER_LIMITS["rpd"],
        "tpm_limit":      FREE_TIER_LIMITS["tpm"],
    }
    generate_report.fx_data = fx_data
    return claude_enhanced + "\n" + part2

generate_report.last_stats = {}
generate_report.fx_data    = {}


# ================================================================
# EMAIL HTML BUILDERS
# ================================================================
def build_token_panel(stats):
    if not stats:
        return ""
    pct_rpd = round((stats["monthly_calls"] / stats["rpd_limit"]) * 100, 1)
    bar_w   = min(int(pct_rpd * 2), 200)
    bar_clr = "#27ae60" if pct_rpd < 50 else "#e67e22" if pct_rpd < 80 else "#c0392b"
    return f"""
<tr><td style="padding:16px 24px;background:#f9f9f9;border-top:1px solid #eef0f5;">
  <div style="font-size:10px;font-weight:700;color:#1a2744;text-transform:uppercase;
    letter-spacing:2px;margin-bottom:10px;">API Usage This Run</div>
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="width:50%;vertical-align:top;padding-right:10px;">
      <div style="padding:8px 10px;background:#fff;border:1px solid #eee;border-radius:4px;margin-bottom:6px;">
        <div style="font-size:9px;color:#888;text-transform:uppercase;">Model</div>
        <div style="font-size:12px;font-weight:700;color:#1a2744;">{stats["model"]}</div>
      </div>
      <div style="padding:8px 10px;background:#fff;border:1px solid #eee;border-radius:4px;">
        <div style="font-size:9px;color:#888;text-transform:uppercase;">This Run</div>
        <div style="font-size:12px;font-weight:700;color:#1a2744;">{stats["total_tokens"]:,} tokens &nbsp;·&nbsp; {stats["calls"]} calls</div>
        <div style="font-size:10px;color:#888;">In: {stats["input_tokens"]:,} | Out: {stats["output_tokens"]:,}</div>
      </div>
    </td>
    <td style="width:50%;vertical-align:top;padding-left:10px;">
      <div style="padding:8px 10px;background:#fff;border:1px solid #eee;border-radius:4px;margin-bottom:6px;">
        <div style="font-size:9px;color:#888;text-transform:uppercase;">Monthly (4 runs)</div>
        <div style="font-size:12px;font-weight:700;color:#1a2744;">~{stats["monthly_tokens"]:,} tokens</div>
      </div>
      <div style="padding:8px 10px;background:#fff;border:1px solid #eee;border-radius:4px;">
        <div style="font-size:9px;color:#888;text-transform:uppercase;margin-bottom:4px;">Free Tier RPD: {stats["rpd_limit"]:,}</div>
        <div style="background:#eee;border-radius:4px;height:8px;width:200px;">
          <div style="background:{bar_clr};height:8px;border-radius:4px;width:{bar_w}px;"></div>
        </div>
        <div style="font-size:10px;color:{bar_clr};font-weight:700;margin-top:4px;">
          {stats["monthly_calls"]} / {stats["rpd_limit"]:,} requests &nbsp;·&nbsp; {pct_rpd}% used ✓</div>
      </div>
    </td>
  </tr></table>
</td></tr>"""


def build_fx_table(fx_data):
    if not fx_data:
        return ""
    rows = ""
    for curr, info in FX_CURRENCIES.items():
        if curr not in fx_data:
            continue
        d        = fx_data[curr]
        rate     = d.get("rate", "N/A")
        src1     = d.get("source1", "Open Exchange Rates")
        src2     = d.get("source2", "")
        verified = d.get("verified", False)
        rate1    = d.get("rate1", rate)
        rate2    = d.get("rate2", "")
        sources  = src1 + (f" + {src2}" if src2 else "")
        v_badge  = ('<span style="color:#27ae60;font-weight:700;font-size:10px;">CROSS-VERIFIED</span>'
                    if verified else
                    '<span style="color:#888;font-size:10px;">Single source</span>')
        rows += f"""<tr style="border-bottom:1px solid #eef0f5;">
  <td style="padding:10px 14px;font-size:13px;font-weight:700;color:#1a2744;width:10%;">{info['flag']} {curr}</td>
  <td style="padding:10px 14px;font-size:11px;color:#555;width:16%;">{info['name']}</td>
  <td style="padding:10px 14px;font-size:16px;font-weight:800;color:#37474f;width:14%;">Rs.{rate}</td>
  <td style="padding:10px 14px;font-size:12px;color:#555;width:12%;">Rs.{rate1}</td>
  <td style="padding:10px 14px;font-size:12px;color:#555;width:12%;">{"Rs."+str(rate2) if rate2 else "—"}</td>
  <td style="padding:10px 14px;width:12%;">{v_badge}</td>
  <td style="padding:10px 14px;font-size:11px;color:#888;">{sources}</td>
</tr>"""

    return f"""<tr><td style="padding:20px 24px 10px;background:#fafbfd;">
  <div style="font-size:11px;font-weight:700;color:#37474f;text-transform:uppercase;
    letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid #37474f;">
    Exchange Rates — Live (Direct API Feed)</div>
</td></tr>
<tr><td style="padding:0;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr style="background:#37474f;">
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Code</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Currency</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Rate (Avg)</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Source 1</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Source 2 (ECB)</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Status</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Data Source</th>
</tr>
{rows}
</table>
</td></tr>"""


def build_html_from_text(text, fx_data=None):
    today = datetime.now().strftime("%d %B %Y")

    SECTIONS = {
        "SECTION 1": {"color": "#1565c0", "label": "Top Indian Projects"},
        "SECTION 2": {"color": "#2e7d32", "label": "Top Global Projects"},
        "SECTION 3": {"color": "#c9a227", "label": "Raw Material Prices — Chennai Market"},
    }

    current_color = "#c9a227"
    html_body     = ""
    in_strategic  = False

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        line = re.sub(r'^\d+\.\s+', '', line)
        line = re.sub(r'^\*\*(.+)\*\*$', r'\1', line)
        line = re.sub(r'^\*\*', '', line)
        if "| TONNE:" in line and not line.startswith("MATERIAL:"):
            line = "MATERIAL: " + line
        if ("| LOCATION:" in line or "| STATUS:" in line) and not any(
                line.startswith(k) for k in ["CLIENT:", "COUNTRY:", "RAILWAY UNIT:"]):
            line = "CLIENT: " + line

        if re.match(r'^[=\-]{4,}$', line):
            continue

        matched = False
        for key, cfg in SECTIONS.items():
            if key in line.upper():
                current_color = cfg["color"]
                in_strategic  = False
                html_body += f"""<tr><td style="padding:20px 24px 8px;background:#fafbfd;">
  <div style="font-size:11px;font-weight:700;color:{cfg['color']};text-transform:uppercase;
    letter-spacing:2px;padding-bottom:10px;border-bottom:3px solid {cfg['color']};">
    {cfg['label']}</div></td></tr>"""
                matched = True
                break
        if matched:
            continue

        if any(x in line for x in [
            "Weekly Intelligence Report", "Spearforge Industrial",
            "Date:", "*Date", "*USD", "USD/INR:"
        ]):
            continue

        if "STRATEGIC ACTION" in line.upper():
            in_strategic  = True
            current_color = "#c9a227"
            html_body += """<tr><td style="background:#1a2744;padding:16px 24px 4px;">
  <div style="font-size:10px;font-weight:700;color:#c9a227;text-transform:uppercase;
    letter-spacing:2px;margin-bottom:6px;">Strategic Action This Week</div>"""
            continue

        if line.startswith("ACTION:"):
            content = line.replace("ACTION:", "").strip()
            html_body += f"""<div style="font-size:14px;color:#fff;font-weight:600;
  line-height:1.6;padding-bottom:12px;">{content}</div></td></tr>"""
            in_strategic = False
            continue

        if line == "---":
            html_body += """<tr><td style="padding:0 24px;">
  <hr style="border:none;border-top:1px solid #eef0f5;margin:4px 0;"></td></tr>"""
            continue

        if line.startswith("PROJECT:") or line.startswith("Project Name:"):
            content = re.split(r':\s*', line, 1)[1].strip() if ':' in line else line
            skip_words = ["n/a", "no major", "no additional", "not found", "no projects",
                          "no global", "no international"]
            if any(w in content.lower() for w in skip_words):
                continue
            html_body += f"""<tr><td style="padding:14px 24px 2px;">
  <div style="font-size:15px;font-weight:700;color:#1a2744;">{content}</div></td></tr>"""
            continue

        if line.startswith("VALUE:"):
            content = line.replace("VALUE:", "").strip()
            if not content or content.upper() == "N/A":
                content = "Value not disclosed"
            html_body += f"""<tr><td style="padding:2px 24px 4px;">
  <div style="font-size:18px;font-weight:800;color:{current_color};">{content}</div></td></tr>"""
            continue

        if any(line.startswith(k) for k in ["CLIENT:", "COUNTRY:", "RAILWAY UNIT:"]):
            html_body += f"""<tr><td style="padding:2px 24px;">
  <div style="font-size:12px;color:#666;">{line}</div></td></tr>"""
            continue

        if line.startswith("WINNER:"):
            content = line.replace("WINNER:", "").strip()
            if content and content != "N/A":
                html_body += f"""<tr><td style="padding:4px 24px;">
  <div style="font-size:12px;background:#fff0f0;border-left:3px solid #c0392b;
    padding:6px 12px;border-radius:0 4px 4px 0;">
    <strong style="color:#c0392b;">Contract Winner:</strong> {content}</div></td></tr>"""
            continue

        if line.startswith("PRODUCTS:"):
            content = line.replace("PRODUCTS:", "").strip()
            html_body += f"""<tr><td style="padding:6px 24px 2px;">
  <div style="background:#f8f9fc;border-left:3px solid {current_color};
    padding:8px 12px;border-radius:0 4px 4px 0;font-size:12px;color:#444;">
    <strong style="color:{current_color};">Spearforge Products:</strong> {content}</div></td></tr>"""
            continue

        if line.startswith("OPPORTUNITY:"):
            content = line.replace("OPPORTUNITY:", "").strip()
            html_body += f"""<tr><td style="padding:2px 24px 8px;">
  <div style="font-size:12px;color:#444;background:#fffbf0;
    border-left:3px solid #c9a227;padding:6px 12px;border-radius:0 4px 4px 0;">
    <strong style="color:#c9a227;">Opportunity:</strong> {content}</div></td></tr>"""
            continue

        if line.startswith("VERIFIED_BY:"):
            parts      = line.replace("VERIFIED_BY:", "").split("|")
            sources    = parts[0].strip() if parts else ""
            confidence = parts[1].replace("CONFIDENCE:", "").strip() if len(parts) > 1 else "Medium"
            is_high    = "High" in confidence
            badge_clr  = "#27ae60" if is_high else "#e67e22"
            badge_txt  = "HIGH CONFIDENCE — Multiple Sources" if is_high else "Medium Confidence — Single Source"
            html_body += f"""<tr><td style="padding:4px 24px 10px;">
  <div style="display:inline-block;background:{badge_clr}20;border:1px solid {badge_clr};
    border-radius:3px;padding:3px 10px;">
    <span style="color:{badge_clr};font-size:10px;font-weight:700;">{badge_txt}</span>
    <span style="color:#666;font-size:10px;"> — {sources}</span>
  </div></td></tr>"""
            continue

        if line.startswith("SOURCE:") or line.startswith("URL:"):
            content = line.replace("SOURCE:", "").replace("URL:", "").strip()
            content = re.sub(r'https?://\S+', '', content).strip()
            if content:
                html_body += f"""<tr><td style="padding:2px 24px 10px;">
  <div style="font-size:11px;color:#888;">📰 Source: {content}</div></td></tr>"""
            continue

        if line.startswith("MATERIAL:"):
            parts    = [p.strip() for p in line.split("|")]
            mat_name = parts[0].replace("MATERIAL:", "").strip()
            tonne    = next((p.replace("TONNE:", "").strip() for p in parts if "TONNE:" in p), "--")
            kg       = next((p.replace("KG:", "").strip() for p in parts if "KG:" in p), "--")
            change   = next((p.replace("CHANGE:", "").strip() for p in parts if "CHANGE:" in p), "--")
            src_name = next((p.replace("SOURCE:", "").strip() for p in parts if "SOURCE:" in p), "")
            src_name = re.sub(r'https?://\S+', '', src_name).strip()
            clr      = "#c0392b" if "Rising" in change else ("#27ae60" if "Falling" in change else "#546e7a")
            html_body += f"""<tr class="mat-row">
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;font-size:12px;color:#333;font-weight:600;">{mat_name}</td>
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;font-size:13px;font-weight:800;color:#1a2744;">{tonne}</td>
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;font-size:12px;font-weight:700;color:#333;">{kg}</td>
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;font-size:12px;color:{clr};font-weight:700;">{change}</td>
  <td style="padding:8px 14px;border-bottom:1px solid #eef0f5;font-size:11px;color:#1a2744;font-weight:700;">{src_name}</td>
</tr>"""
            continue

        if line.startswith("USD/INR IMPACT:"):
            content = line.replace("USD/INR IMPACT:", "").strip()
            html_body += f"""</table></td></tr>
<tr><td style="padding:10px 24px;background:#f9f9f9;border-top:1px solid #eef0f5;">
  <div style="font-size:12px;color:#555;"><strong>USD/INR Impact:</strong> {content}</div></td></tr>"""
            continue

        if len(line) > 3 and not line.startswith("=="):
            html_body += f"""<tr><td style="padding:2px 24px;">
  <div style="font-size:12px;color:#777;">{line}</div></td></tr>"""

    mat_header = """<tr><td style="padding:0;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr style="background:#1a2744;">
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Material</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Per Tonne</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Per KG</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Week Change</th>
  <th style="padding:10px 14px;text-align:left;font-size:9px;color:#c9a227;font-weight:700;text-transform:uppercase;">Source</th>
</tr>"""
    first_mat = html_body.find('<tr class="mat-row">')
    if first_mat != -1:
        html_body = html_body[:first_mat] + mat_header + html_body[first_mat:]

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f2f8;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f8;padding:24px 0;">
<tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0"
  style="background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 4px 24px rgba(26,39,68,0.12);">

<tr><td style="background:linear-gradient(135deg,#1a2744 0%,#243560 100%);padding:28px 32px;">
  <div style="color:#c9a227;font-size:10px;font-weight:700;letter-spacing:3px;
    text-transform:uppercase;margin-bottom:8px;">Spearforge Industrial &amp; Engineering Solutions</div>
  <div style="color:#fff;font-size:24px;font-weight:800;margin-bottom:6px;">Weekly Intelligence Report</div>
  <div style="color:#8a9dc0;font-size:13px;">{today} &nbsp;&middot;&nbsp; Auto-generated every Friday 3:00 PM IST</div>
</td></tr>

<tr><td>
<table width="100%" cellpadding="0" cellspacing="0">
  {build_fx_table(fx_data or {})}
  {html_body}
</table>
</td></tr>

{build_token_panel(generate_report.last_stats)}

<tr><td style="padding:20px 28px;background:#1a2744;text-align:center;">
  <div style="font-size:11px;color:#8a9dc0;line-height:1.9;">
    Auto-generated by Spearforge Intel Bot &nbsp;&middot;&nbsp; Every Friday 3:00 PM IST<br>
    enquiries@spearforgeindustries.com &nbsp;&middot;&nbsp; Chennai, Tamil Nadu, India<br>
    <span style="color:#c9a227;font-weight:700;">"Global Precision. Industrial Excellence."</span>
  </div>
</td></tr>

</table>
</td></tr></table>
</body></html>"""


# ================================================================
# SEND EMAIL
# ================================================================
def send_email(html_body, today):
    app_password   = os.environ["GMAIL_APP_PASSWORD"]
    msg            = MIMEMultipart("alternative")
    msg["From"]    = f"Spearforge Intel Bot <{SENDER_EMAIL}>"
    msg["To"]      = RECEIVER_EMAIL
    msg["Subject"] = f"{REPORT_SUBJECT} — {today}"
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
    print(f"  Spearforge Intel Bot — {today}")
    print(f"{'='*60}")
    try:
        print("\nStep 1: Generating report...")
        raw_response = generate_report()

        print("Step 2: Building HTML email...")
        html_body = build_html_from_text(raw_response, generate_report.fx_data)

        print("Step 3: Sending email...")
        send_email(html_body, today)

        print(f"\n  SUCCESS — Report delivered to {RECEIVER_EMAIL}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n  ERROR: {e}")
        try:
            app_password = os.environ["GMAIL_APP_PASSWORD"]
            msg = MIMEMultipart()
            msg["From"]    = SENDER_EMAIL
            msg["To"]      = RECEIVER_EMAIL
            msg["Subject"] = f"Spearforge Intel Bot — Script Error {today}"
            msg.attach(MIMEText(
                f"The weekly newsletter script failed:\n\n{str(e)}\n\n"
                "Check GitHub Actions logs for the full traceback.", "plain"))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SENDER_EMAIL, app_password)
                server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        except Exception:
            pass
        raise


if __name__ == "__main__":
    run_automation()
