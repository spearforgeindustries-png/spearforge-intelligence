import os
import google.generativeai as genai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. SETUP GEMINI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Simplified model setup to avoid the 'google_search' error
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

def run_automation():
    # 2. THE BUSINESS INTELLIGENCE PROMPT
    # We ask the AI to use its internal knowledge of recent market trends
    prompt = """
    Generate a professional weekly newsletter for Spearforge Industries, Chennai.
    Focus on the following data points for May 2026:

    1. RAW MATERIAL RATES (Estimate based on current Chennai Market trends):
       - MS HR Sheet (1.6mm to 3.0mm) for PCT/LCT Series.
       - GI Sheet (1.2mm to 2.0mm).
       - SS 304 Sheet.
       (Present in a clean table with weekly trends).

    2. PROJECT LEADS:
       - Summary of ongoing Chennai Metro Phase 2 & Southern Railway projects.
       - Provide a 'Product Match' for Spearforge (e.g., LCT Ladder Trays or ECB Enclosures).

    Format with professional Markdown headers and a 'Strategic Goal' section.
    """

    try:
        print("Generating newsletter content...")
        response = model.generate_content(prompt)
        newsletter_markdown = response.text

        # 3. EMAIL DELIVERY SETUP
        sender_email = "vimal.dgv@gmail.com" 
        receiver_email = "spearforgeindustries@gmail.com"
        app_password = os.environ["GMAIL_APP_PASSWORD"]

        msg = MIMEMultipart()
        msg['From'] = f"Spearforge Automation <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = "🛡️ Spearforge Weekly Intelligence | Market & Project Report"

        msg.attach(MIMEText(newsletter_markdown, 'plain'))

        print(f"Connecting to Gmail as {sender_email}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print("Success! Newsletter delivered to Vimal.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    run_automation()
