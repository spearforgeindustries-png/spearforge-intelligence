import os
import google.generativeai as genai
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. SETUP GEMINI AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def find_best_model():
    try:
        for m in genai.list_models():
            if 'flash' in m.name.lower() and 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        pass
    return 'models/gemini-1.5-flash'

def run_automation():
    target_model = find_best_model()
    model = genai.GenerativeModel(target_model)
    today_date = datetime.now().strftime("%B %d, 2026")

    print(f"Step 1: Compiling Global Intel Report for {today_date}...")
    
    # INTEL-SPECIFIC PROMPT
    prompt = f"""
    ROLE: Strategic Intelligence Analyst for Spearforge Industries.
    DATE: {today_date}.
    
    TASK: Provide a Global & Domestic Intelligence Report for the following categories. 
    CRITICAL: For every major point, you MUST list the 'SOURCE' (e.g., News portal, Govt Website, or Market Index).

    1. RAW MATERIAL INTELLIGENCE (Global & India):
       - LME (London Metal Exchange) trends for Steel and Nickel.
       - Domestic India HR/GI/SS price shifts and why they are happening.
       - SOURCE: Mention specific indices like SteelMint, JPC, or LME.

    2. MAJOR GLOBAL INFRASTRUCTURE (Relevant to Enclosures/Cable Trays):
       - Identify 2 major Data Center, Renewable Energy, or Metro projects announced this week in the Middle East, Europe, or SE Asia.
       - Why it matters to Spearforge: (e.g., demand for electrical containment systems).
       - SOURCE: News link or portal name.

    3. MAJOR INDIAN PROJECTS (Beyond Chennai):
       - High-speed rail, new airports, or large-scale industrial corridors (NICDC) updates.
       - Identify specific MEP (Mechanical, Electrical, Plumbing) tender trends.
       - SOURCE: PIB, Tenders.gov.in, or news outlets.

    FORMAT: Use a "Briefing" style. Use bold bullet points and a 'Sources' section at the bottom of each category.
    """

    try:
        response = model.generate_content(prompt)
        newsletter_markdown = response.text

        # 2. EMAIL DELIVERY
        sender_email = "vimal.dgv@gmail.com" 
        receiver_email = "spearforgeindustries@gmail.com"
        app_password = os.environ["GMAIL_APP_PASSWORD"]

        msg = MIMEMultipart()
        msg['From'] = f"Spearforge Intel <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🛡️ GLOBAL INTEL REPORT | {today_date}"
        msg.attach(MIMEText(newsletter_markdown, 'plain'))

        print("Step 2: Dispatching Intelligence...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print(f"🚀 Success! Intel report dispatched.")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_automation()
