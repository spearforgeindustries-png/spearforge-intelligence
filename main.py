import os
import google.generativeai as genai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. SETUP GEMINI AI
# Configure the API Key from GitHub Secrets
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use the direct model string to avoid 404 errors
model = genai.GenerativeModel('gemini-1.5-flash')

def run_automation():
    print("Step 1: Starting AI content generation...")
    
    prompt = """
    Generate a professional weekly newsletter for Spearforge Industries, Chennai.
    Current Date: May 10, 2026.

    Please include:
    1. RAW MATERIAL RATES (Chennai Market):
       - MS HR Sheet (1.6mm to 3.0mm) for PCT/LCT Series.
       - GI Sheet (1.2mm to 2.0mm).
       - SS 304 Sheet.
       (Present this in a clear Markdown Table).

    2. PROJECT UPDATES & TENDERS:
       - Summarize any new tenders for Chennai Metro Phase 2 (Electrical/MEP).
       - Look for Southern Railway steel procurement news.

    Format the output with bold headings and a professional tone.
    """

    try:
        # Generate the newsletter content
        # Note: We removed the tools/search part to ensure it doesn't crash on v1beta
        response = model.generate_content(prompt)
        newsletter_markdown = response.text
        print("Step 2: Newsletter content generated successfully.")

        # 3. EMAIL DELIVERY SETUP
        sender_email = "vimal.dgv@gmail.com" 
        receiver_email = "spearforgeindustries@gmail.com"
        
        # Read the 16-digit App Password from GitHub Secrets
        app_password = os.environ["GMAIL_APP_PASSWORD"]

        msg = MIMEMultipart()
        msg['From'] = f"Spearforge Market Intelligence <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = "🛡️ Spearforge Weekly Intelligence | Market & Project Report"

        msg.attach(MIMEText(newsletter_markdown, 'plain'))

        print(f"Step 3: Connecting to Gmail as {sender_email}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print(f"Final Step: Success! Newsletter delivered to {receiver_email}.")

    except Exception as e:
        # This will print the specific error in GitHub logs if it fails
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_automation()
