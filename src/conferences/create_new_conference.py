from src.conferences.init import conferences_collection


def create_new_conference(conference_information: dict):
    """Example of a conference document:
        {
            "_id": ObjectId("60c72b2f9b1e8d3f4c8b4567"),
            "name": "AI Conference 2023",
            "location": "San Francisco, CA",
            "date": "2023-09-15",
            "description": "A conference about the latest advancements in AI.",
            "link_conference": "https://www.example.com/ai-conference-2023",
            "template_filepath": null,
            "poster_filepath": null,
            "recipients": [
                {
                "name": "Nguyễn Văn A",
                "email": "a@example.com",
                "status": {
                    "sent": false,
                    "date_sent": null,
                    "opened": false,
                    "clicked": false,
                    "failed": false,
                    "unsubscribed": false,
                    "responded": false
                }
                },
                # Add more recipients as needed,
            ],
            "total_sent": 0,
            "total_opened": 0,
            "total_clicked": 0,
            "total_failed": 0,
            "total_unsubscribed": 0,
            "total_responded": 0
        }
    """
    result = conferences_collection.insert_one(conference_information)
    print(f"[LOG] Conference created successfully in {conferences_collection}.")
    return result.inserted_id