from typing import Dict, List, Any
from datetime import datetime

def is_same_day(date_str: str) -> bool:
    """Kiểm tra xem date_str có phải là ngày hôm nay không."""
    if not date_str:
        return False
    try:
        date = datetime.fromisoformat(date_str)
        return date.date() == datetime.today().date()
    except Exception:
        return False

def contacts_to_send(conference) -> List[dict]:
    """
    Retrieves a list of up to 100 contacts that have not been sent emails.

    Args:
        conference (dict): The conference details.

    Returns:
        List[dict]: A list of contact dictionaries to send emails to.
    """
    last_sent_time_str = conference.get("last_sent_time")
    last_sent_count = conference.get("last_sent_count", 0)
    if is_same_day(last_sent_time_str) or last_sent_count == 400:
        return [], "Đã hoàn thành gửi mail cho hôm nay!"

    recipients = conference.get("recipients", [])
    contacts = [contact for contact in recipients if not contact["status"]["sent"]]
    return contacts[:100], "Hãy thư cho những liên hệ dưới đây!"