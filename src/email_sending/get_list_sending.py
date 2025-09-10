from typing import Dict, List, Any

def contacts_to_send(conference) -> List[dict]:
    """Lấy danh sách 100 liên hệ chưa được gửi thư."""
    recipients = conference.get("recipients", [])
    contacts = [contact for contact in recipients if not contact["status"]["sent"]]
    return contacts[:100]