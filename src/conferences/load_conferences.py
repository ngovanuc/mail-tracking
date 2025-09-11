from src.conferences.init import mail_tracking_database
from src.conferences.init import conferences_collection


def load_conferences():
    """
    Loads all conferences from the database.

    Returns:
        list: A list of conference documents.
    """
    conferences = conferences_collection.find()
    return list(conferences)
