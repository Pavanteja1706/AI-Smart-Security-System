import smtplib
from email.message import EmailMessage
import os
from datetime import datetime

STATUS_FILE = "email_status.txt"

def update_email_status(message):
    with open(STATUS_FILE, "w") as f:
        f.write(message)

def send_email_alert(image_path):
    sender_email = "youremailid@gmail.com"
    sender_password = "your google account app password"
    receiver_email = "youremailid@gmail.com"

    try:
        msg = EmailMessage()
        msg["Subject"] = f"AI Security Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.set_content("An unknown person was detected by your AI Security System. See attached image.")

        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(image_path)
                msg.add_attachment(
                    file_data,
                    maintype="image",
                    subtype="jpeg",
                    filename=file_name
                )

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        update_email_status("Sent successfully")
        print("Email alert sent successfully.")

    except Exception as e:
        update_email_status(f"Failed: {str(e)}")
        print("Email alert failed:", e)
