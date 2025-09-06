from src.conferences.init import mail_tracking_database
from src.conferences.init import conferences_collection


def load_conferences():
    conferences = conferences_collection.find()
    return list(conferences)
