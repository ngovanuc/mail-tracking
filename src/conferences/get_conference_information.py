from src.conferences.init import conferences_collection
import datetime


async def get_conference_information(conference):
    """
    Retrieves detailed information about a specific conference.

    Args:
        conference (dict): The conference details.

    Returns:
        dict: A dictionary containing analysis of the conference's recipients and status.
    """
    recipients = conference.get("recipients", [])
    total_recipients = len(recipients)
    def count(key, default):
        return sum(1 for r in recipients if r.get("status", {}).get(key, default))
    analysis = {
        "total_recipients": total_recipients,
        "total_sent": conference.get("total_sent", 0),
        "total_opened": conference.get("total_opened", 0),
        "total_clicked": conference.get("total_clicked", 0),
        "total_failed": conference.get("total_failed", 0),
        "total_unsubscribed": conference.get("total_unsubscribed", 0),
    }
    for k in analysis:
        if k != "total_recipients":
            analysis[k] = min(analysis[k], total_recipients)
    return analysis


async def mail_sent_this_week(conference_name: str):
    """
    Calculates the number of emails sent for a conference during the current week.

    Args:
        conference_name (str): The name of the conference.

    Returns:
        list: A list of integers representing the number of emails sent each day of the week.
    """
    conference = conferences_collection.find_one({"name": conference_name})
    if not conference:
        return [0, 0, 0, 0, 0, 0, 0]

    recipients = conference.get("recipients", [])
    now = datetime.datetime.now()
    start_of_week = now - datetime.timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    mail_sent_per_day = [0] * 7  # Monday to Sunday

    for r in recipients:
        sent_time = r.get("status", {}).get("date_sent")
        if sent_time:
            # sent_time is assumed to be a datetime object
            if isinstance(sent_time, str):
                sent_time = datetime.datetime.fromisoformat(sent_time)
            if start_of_week <= sent_time < start_of_week + datetime.timedelta(days=7):
                day_index = (sent_time.weekday())  # Monday=0, Sunday=6
                mail_sent_per_day[day_index] += 1

    # return mail_sent_per_day
    # mail_sent_per_day = [10, 100, 200, 300, 350, 400, 500] # Giả lập
    return mail_sent_per_day


async def ratio_report(analysis: dict):
    total_recipients = analysis.get("total_recipients", 0)
    if total_recipients == 0:
        return [0.0, 0.0, 0.0, 0.0, 0.0]
    return [
        round((analysis.get("total_sent", 0) / total_recipients) * 100, 2),         # Sent rate
        round((analysis.get("total_opened", 0) / total_recipients) * 100, 2),       # Open rate
        round((analysis.get("total_clicked", 0) / total_recipients) * 100, 2),      # Click rate
        round((analysis.get("total_failed", 0) / total_recipients) * 100, 2),       # Failed rate
        round((analysis.get("total_unsubscribed", 0) / total_recipients) * 100, 2)  # Unsubscribed rate
    ]



