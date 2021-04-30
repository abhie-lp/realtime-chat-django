"""Function to handle timestamps"""

from datetime import datetime, timedelta
from django.contrib.humanize.templatetags.humanize import naturalday


def humanize_or_normal(timestamp: datetime) -> str:
    """
    Format the timestamp of the chat

    1. Today or yesterday:
        - today at 12:45 AM
        - yesterday at 12:30 PM
    2. Other:
        - 24/04/2021
    """
    today = datetime.now()

    # Check if timestamp date ins in today or yesterday
    if timestamp.date() in (today.date(), (today - timedelta(1)).date()):
        str_time = timestamp.strftime("%I:%M %p").strip("0")
        ts = f"{naturalday(timestamp)} at {str_time}"
    else:
        ts = timestamp.strftime("%d/%m/%Y")
    return ts
