import os
import getpass
import pymongo
from pymongo import MongoClient


# Connect to MongoDB on local machine
client = MongoClient("mongodb://localhost:27017/")
if client:
    print("Connected to MongoDB successfully.")
else:
    raise Exception("Failed to connect to MongoDB.")

# Create mail tracking database
mail_tracking_database = "mail_tracking_database"
if mail_tracking_database in client.list_database_names():
    print(f"Database '{mail_tracking_database}' already exists.")
    mail_tracking_database = client.mail_tracking_database
else:
    mail_tracking_database = client.mail_tracking_database
    print(f"Database '{mail_tracking_database}' created successfully.")

# Create username and password collection
users_collection = "users_collection"
if users_collection in mail_tracking_database.list_collection_names():
    print(f"Collection '{users_collection}' already exists.")
    users_collection = mail_tracking_database.users_collection
else:
    users_collection = mail_tracking_database.users_collection
    print(f"Collection '{users_collection}' created successfully.")