"""
Tạo mới user cho hệ thống bằng cách thủ công, phương pháp này sử dụng tài khoản Google đang hiệu lực
để tạo mới một user trong hệ thống Mail Tracking API.

Yêu cầu:
    - Tài khoản đã được đăng nhập trên trình duyệt bất kỳ trên thiết bị này.
    - Nhập đúng tài khoản Google muốn gửi thư bằng email.
    - Nhập mật khẩu tài khoản Google.
    - Vào cài đặt tài khoản Google, tạo mật khẩu ứng dụng và nhập vào đây.

Lưu ý:
    - File này chạy hoàn toàn độc lập với dự án.
    - Thông tin tài khoản được lưu vào MongoDB database.
    - Mật khẩu và Mật khẩu ứng dụng đã được hash bằng Argon2 trước khi lưu vào database.
"""

import os

from argon2 import PasswordHasher

# from src.authentication.init import mail_tracking_database
# from src.authentication.init import users_collection
from init import mail_tracking_database, users_collection


ph = PasswordHasher()


# Get account information from user
gmail_account = str(input("Enter Gmail address: "))
gmail_password = str(input("Enter Gmail password: "))
app_password = str(input("Enter App password: "))

# Enter Gmail address:
# Enter Gmail password:
# Enter App password:

# Checking gmail account if already exist
if users_collection.find_one({"gmail_account": gmail_account}):
    print("[LOG] Gmail account already exists.")
    exit()

if gmail_account == "" or gmail_password == "" or app_password == "":
    print("[LOG] All fields are required.")
    exit()

print("[LOG] Creating a new user...")

# Hash the passwords
hashed_password = ph.hash(gmail_password)
hashed_app_password = ph.hash(app_password)

# Store the user information into the database
user_data = {
    "gmail_account": gmail_account,
    "gmail_password": hashed_password,
    "app_password": hashed_app_password,
}

users_collection.insert_one(user_data)
print(f"[LOG] User created successfully in {users_collection}.")