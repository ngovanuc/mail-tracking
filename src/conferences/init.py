import os
from pymongo import MongoClient


# Connect to MongoDB on local machine
try:
    client = MongoClient("mongodb://localhost:27017/")
    print("Connected to MongoDB successfully.")
except Exception as e:
    raise Exception("Failed to connect to MongoDB.")

# Check mail_tracking_database
mail_tracking_database = "mail_tracking_database"
if mail_tracking_database in client.list_database_names():
    print(f"Database '{mail_tracking_database}' already exists.")
    mail_tracking_database = client.mail_tracking_database
else:
    mail_tracking_database = client.mail_tracking_database
    print(f"Database '{mail_tracking_database}' created successfully.")

# Create "conferences_collection"
conferences_collection = mail_tracking_database.conferences_collection
if "conferences_collection" not in mail_tracking_database.list_collection_names():
    conferences_collection = mail_tracking_database.conferences_collection
    print(f"Collection 'conferences_collection' created successfully.")
else:
    conferences_collection = mail_tracking_database.conferences_collection
    print(f"Collection 'conferences_collection' already exists.")
