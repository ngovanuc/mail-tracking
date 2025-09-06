from src.conferences.init import conferences_collection


def get_conference_information(conference):
    # Total recipients
    if conference.get("recipients") is None or len(conference.get("recipients")) == 0:
        total_recipients = 0
    else:
        total_recipients = len(conference.get("recipients", []))

    # Total sent
    if total_recipients == 0:
        total_sent = 0
    else:
        total_sent = sum(1 for r in conference.get("recipients", []) if r.get("status") == "sent")

    # Total opened
    if total_recipients == 0:
        total_opened = 0
    else:
        total_opened = sum(1 for r in conference.get("recipients", []) if r.get("status") == "opened")

    # Total clicked
    if total_recipients == 0:
        total_clicked = 0
    else:
        total_clicked = sum(1 for r in conference.get("recipients", []) if r.get("status") == "clicked")

    # Total failed
    if total_recipients == 0:
        total_failed = 0
    else:
        total_failed = sum(1 for r in conference.get("recipients", []) if r.get("status") == "failed")

    # Unsubscribed
    if total_recipients == 0:
        total_unsubscribed = 0
    else:
        total_unsubscribed = sum(1 for r in conference.get("recipients", []) if r.get("status") == "unsubscribed")
    # total_unsubscribed = sum(1 for r in conference.get("recipients", []) if r.get("status") == "unsubscribed")

    analysis = {
        "total_recipients": total_recipients,
        "total_sent": total_sent,
        "total_opened": total_opened,
        "total_clicked": total_clicked,
        "total_failed": total_failed,
        "total_unsubscribed": total_unsubscribed    
    }

    return analysis