import os
import google.generativeai as genai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. SETUP GEMINI AI
# Configure the API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def run_automation():
    print("Step 1: Starting AI content generation...")
    
    # We use the most basic model call to avoid versioning errors
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Generate a professional weekly newsletter for Spearforge Industries, Chennai.
        Date: May 10, 2026.

        Include:
        1. RAW MATERIAL RATES (Chennai Market):
           - MS HR Sheet (1.6mm to 3.0mm) 
           - GI Sheet (1.2mm to 2.0mm)
           - SS 304 Sheet
        2. PROJECT UPDATES:
           - Chennai Metro Phase 2 & Southern Railway news.

        Format with bold headings and tables.
        """

        # Using the standard generate_content call
        response = model.generate_content(prompt)
        newsletter_markdown = response.text
        print("Step 2: Newsletter content generated successfully.")

        # 2. EMAIL DELIVERY SETUP
        sender_email = "vimal.dgv@gmail.com" 
        receiver_email = "spearforgeindustries@gmail.com"
        app_password = os.environ["GMAIL_APP_PASSWORD"]

        msg = MIMEMultipart()
        msg['From'] = f"Spearforge Market Intelligence <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = "🛡️ Spearforge Weekly Intelligence Report"

        msg.attach(MIMEText(newsletter_markdown, 'plain'))

        print(f"Step 3: Connecting to Gmail...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print(f"Final Step: Success! Sent to {receiver_email}.")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_automation()
