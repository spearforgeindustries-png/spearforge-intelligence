import os
import google.generativeai as genai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. AI SETUP
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash', tools=[{"google_search": {}}])

def run_automation():
    # 2. PROMPT FOR SPEARFORGE CATALOGUE
    prompt = """
    Generate a professional weekly newsletter for Spearforge Industries, Chennai.
    Show Raw Material rates in INR/Kg for:
    - 2.5mm - 3.0mm MS HR (for LCT Series)
    - 1.6mm - 2.0mm MS HR (for PCT Series)
    - 1.2mm - 1.6mm GI Sheet (for Pre-Galv PCT)
    Search for Chennai Metro Phase 2 & Southern Railway tenders.
    """

    try:
        response = model.generate_content(prompt)
        newsletter_text = response.text

        # 3. EMAIL DELIVERY
        sender_email = "vimal.dgv@gmail.com" 
        receiver_email = "vimal.prakash@spearforgeindustries.com"
        app_password = os.environ["GMAIL_APP_PASSWORD"]

        msg = MIMEMultipart()
        msg['From'] = f"Spearforge Intelligence <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = "🛡️ Spearforge Weekly Digest"
        msg.attach(MIMEText(newsletter_text, 'plain'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print("Success! Sent to Vimal.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_automation()
