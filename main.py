import os
import google.generativeai as genai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. SETUP GEMINI AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def find_best_model():
    """Automatically finds the correct model name to avoid 404 errors."""
    try:
        for m in genai.list_models():
            # Looks for any 'flash' model that supports generating content
            if 'flash' in m.name.lower() and 'generateContent' in m.supported_generation_methods:
                print(f"✅ Found working model: {m.name}")
                return m.name
    except Exception as e:
        print(f"Could not list models: {e}")
    # Fallback to a very safe default if listing fails
    return 'models/gemini-1.5-flash'

def run_automation():
    # Automatically get the right name (e.g., models/gemini-3.1-flash-lite)
    target_model = find_best_model()
    model = genai.GenerativeModel(target_model)

    print("Step 1: Generating content...")
    prompt = "Generate a weekly newsletter for Spearforge Industries, Chennai. Include raw material rates for MS HR, GI, and SS 304 sheets. Also, list Chennai Metro Phase 2 tenders."

    try:
        response = model.generate_content(prompt)
        newsletter_markdown = response.text

        # 2. EMAIL DELIVERY
        sender_email = "vimal.dgv@gmail.com" 
        receiver_email = "spearforgeindustries@gmail.com"
        app_password = os.environ["GMAIL_APP_PASSWORD"]

        msg = MIMEMultipart()
        msg['From'] = f"Spearforge Intelligence <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = "🛡️ Spearforge Weekly Intelligence"
        msg.attach(MIMEText(newsletter_markdown, 'plain'))

        print(f"Step 2: Sending email to {receiver_email}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print("🚀 Success! Newsletter delivered.")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_automation()
