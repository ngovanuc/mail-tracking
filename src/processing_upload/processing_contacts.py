import os
import uuid
import pandas as pd

from src.conferences.init import mail_tracking_database
from src.conferences.init import conferences_collection

def process_uploaded_excel(excel_filepath, conference_name) -> list:
    """
    Processes an uploaded Excel file to extract contact information.

    Args:
        excel_filepath (str): The path to the Excel file.
        conference_name (str): The name of the conference.

    Returns:
        list: A list of processed contact dictionaries.
    """
    """Open an excel file and read all contact. Excel file mush have at least two columns:
        - "Name": Contain full name of contact (First column)
        - "Email": Contain email of contact (Second column)

    The information for each contact is:
        {
            "_id": ObjectId("60c72b2f9b1e8d3f4c8b4567"),
            "name": "AI Conference 2023",
            "location": "San Francisco, CA",
            "date": "2023-09-15",
            "description": "A conference about the latest advancements in AI.",
            "link_conference": "https://www.example.com/ai-conference-2023",
            "template_link": null,
            "recipients": [
                {
                "name": "Nguyễn Văn A",
                "email": "a@example.com",
                "status": {
                    "sent": false,
                    "date_sent": null,
                    "opened": false,
                    "clicked": false,
                    "date_clicked": null,
                    "failed": false,
                    "unsubscribed": false,
                    "responded": false
                }
                },
                # Add more recipients as needed,
            ]
        }
    """
    print(f"Processing uploaded excel file: {excel_filepath} for conference: {conference_name}")
    df = pd.read_excel(excel_filepath)
    processed_contacts = []
    for index, row in df.iterrows():
        contact_name = row[0]
        contact_email = row[1]
        contact_info = {
            "name": contact_name,
            "email": contact_email,
            "status": {
                "sent": False,
                "date_sent": None,
                "opened": False,
                "date_opened": None,
                "clicked": False,
                "date_clicked": None,
                "failed": False,
                "unsubscribed": False,
                "responded": False
            },
            "tracking_id": uuid.uuid4()
        }
        processed_contacts.append(contact_info)

    return processed_contacts