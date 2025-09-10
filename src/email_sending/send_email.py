import os
import time
import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from src.conferences.init import mail_tracking_database
from src.conferences.init import conferences_collection

def login_to_smtp(gmail, app_password):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail, app_password)
        print("Logged in to SMTP server successfully.")
        return server
    except Exception as e:
        print(f"Failed to login to SMTP server: {e}")
        return None
    

def send(conference, contacts, gmail, app_password):
    html_template_filepath = conference.get("html_template_filepath")
    try:
        with open(html_template_filepath, 'r', encoding='utf-8') as file:
            html_template = file.read()
    except Exception as e:
        yield f"data: Error reading HTML template file: {e}\n\n"
        return

    server = login_to_smtp(gmail, app_password)
    if not server:
        yield "data: Failed to login to SMTP server.\n\n"
        return

    success_count = 0
    failed_count = 0
    attempt_count = 0
    idx = 0
    while idx < len(contacts) and attempt_count <= 3:
        try:
            server.noop()
        except Exception as e:
            yield f"data: SMTP server connection lost: {e}. Attempting to reconnect...\n\n"
            server = login_to_smtp(gmail, app_password)
            if not server:
                attempt_count += 1
                time.sleep(5)
                continue

        name = contacts[idx]["name"]
        email = contacts[idx]["email"]

        msg = MIMEMultipart()
        msg["From"] = gmail
        msg["To"] = email
        msg["Subject"] = conference.get("subject")
        html_message = html_template.replace("{{name}}", name)

        try:
            msg.attach(MIMEText(html_message, "html"))
            server.send_message(msg)
            success_count += 1
            # Update collection
            conferences_collection.update_one(
                {"_id": conference["_id"], "recipients.email": email},
                {"$set": {
                    "recipients.$.status.sent": True,
                    "recipients.$.status.date_sent": str(datetime.datetime.now())
                }}
            )
            yield f"data: Sent to {email} successfully.\n\n"
        except Exception as e:
            failed_count += 1

            # Update sent
            conferences_collection.update_one(
                {"_id": conference["_id"], "recipients.email": email},
                {"$set": {
                    "recipients.$.status.sent": True,
                    "recipients.$.status.date_sent": str(datetime.datetime.now())
                }}
            )
            # Update failed
            conferences_collection.update_one(
                {"_id": conference["_id"], "recipients.email": email},
                {"$set": {
                    "recipients.$.status.failed": True
                }}
            )
            yield f"data: Failed to send to {email}: {e}\n\n"

        idx += 1
        time.sleep(3)

    yield f"data: Finished sending. Success: {success_count}, Failed: {failed_count}\n\n"

    # Update sending information to collection
    conferences_collection.update_one(
        {"_id": conference["_id"]},
        {"$set": {
            "total_sent": conference.get("total_sent") + success_count,
            "total_failed": conference.get("total_failed") + failed_count
        }}
    )
    server.quit()
