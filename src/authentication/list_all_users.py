"""
Liệt kê tất cả các tài khoản người dùng đã đăng ký trong hệ thống.
"""

# from src.authentication.init import mail_tracking_database
# from src.authentication.init import user_collection
from init import mail_tracking_database, users_collection


print("[LOG] List of all user account:")
for user in users_collection.find():
    print(f" - {user['gmail_account']}")
    print(f" - {user['gmail_password']}")
    print(f" - {user['app_password']}\n")