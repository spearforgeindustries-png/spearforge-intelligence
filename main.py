import os
import google.generativeai as genai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. SETUP GEMINI AI
# Using the newer Gemini 3 Flash model to bypass the 404 error
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def run_automation():
    print("Step 1: Connecting to Gemini 3 Flash...")
    
    try:
        # Switching to 'gemini-3-flash' which is the current stable standard
        model = genai.GenerativeModel('gemini-3-flash')
        
        prompt = """
        Generate a professional weekly newsletter for Spearforge Industries, Chennai.
        Date: May 10, 2026.

        Provide a table for Chennai Raw Material Rates (INR/Kg):
        - MS HR Sheet (1.6mm - 3.0mm)
        - GI Sheet (1.2mm - 2.0mm)
        - SS 304 Sheet
        
        Include a section on Chennai Metro Phase 2 & Southern Railway project leads.
        """

        # Generate content
        response = model.generate_content(prompt)
        newsletter_markdown = response.text
        print("Step 2: Content generated successfully.")

        # 2. EMAIL DELIVERY
        sender_email = "vimal.dgv@gmail.com" 
        receiver_email = "spearforgeindustries@gmail.com"
        app_password = os.environ["GMAIL_APP_PASSWORD"]

        msg = MIMEMultipart()
        msg['From'] = f"Spearforge Intelligence <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = "🛡️ Spearforge Weekly Intelligence Report"
        msg.attach(MIMEText(newsletter_markdown, 'plain'))

        print(f"Step 3: Sending email to {receiver_email}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print("Final Step: Success! Newsletter delivered.")

    except Exception as e:
        # This will now tell us if the model name was the issue
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_automation()
