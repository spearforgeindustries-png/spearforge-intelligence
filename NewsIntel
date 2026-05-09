import os
import google.generativeai as genai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. SETUP GEMINI WITH SEARCH GROUNDING
# This allows the AI to search the live web for Chennai steel prices and tenders.
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# We use the 'google_search' tool to ensure real-time data accuracy
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=[{"google_search": {}}] 
)

# 2. THE BUSINESS INTELLIGENCE PROMPT
# Specifically tuned for the Spearforge Catalogue (PCT, LCT, ECB, SMB series)
prompt = """
Generate a professional weekly newsletter for Spearforge Industries, Chennai.
Today is Friday morning. Act as an Industrial Market Analyst.

1. RAW MATERIAL RATES (CHENNAI MARKET):
   - Find current market rates in INR/Kg for:
     * MS HR Sheet (Thickness: 1.6mm to 3.0mm) - used for PCT/LCT Cable Trays.
     * GI Sheet (Thickness: 1.2mm to 2.0mm).
     * SS 304 Sheet.
   - Present these in a clean table with a 'Weekly Trend' column.

2. PROJECT LEADS & TENDERS:
   - Search for active tenders or project news in:
     * Chennai Metro Phase 2 (Electrical/MEP packages).
     * Indian Railways (Southern Railway traction or gantry steel).
     * NTPC / SECI (BESS and Solar Mounting structures).
   - For each lead, provide a 'Product Match' (e.g., LCT Series, ECB Enclosure) and a 'How to Reach' action path.

3. VISUAL STYLE:
   - Use professional Markdown.
   - Header: 🛡️ SPEARFORGE | Weekly Intelligence Digest.
   - Include a 'Strategic Goal of the Week' section at the end.
"""

def run_newsletter_automation():
    try:
        # Generate the content using Google Search grounding
        print("Searching for latest Chennai market data and tenders...")
        response = model.generate_content(prompt)
        newsletter_markdown = response.text

        # 3. EMAIL DELIVERY SETUP
        # Change 'your-email@gmail.com' to the Gmail you are using to SEND the report.
        sender_email = "vimal.dgv@gmail.com" 
        receiver_email = "vimal.prakash@spearforgeindustries.com"
        
        # This password comes from your GitHub Secrets (GMAIL_APP_PASSWORD)
        app_password = os.environ["GMAIL_APP_PASSWORD"]

        msg = MIMEMultipart()
        msg['From'] = f"Spearforge Automation <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = "🛡️ Spearforge Weekly Intelligence | Chennai & Global Projects"

        # Attach the AI-generated content
        msg.attach(MIMEText(newsletter_markdown, 'plain'))

        # Send via Gmail SMTP
        print(f"Connecting to Gmail to send report to {receiver_email}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print("Success! Newsletter delivered to Vimal.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    run_newsletter_automation()
