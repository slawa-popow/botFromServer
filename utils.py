import pytz
from datetime import datetime

from config import Config

NOT_ALLOWED_CONTENT_TYPES_RECEIPT = [
    'text', 'audio', 'document', 'sticker', 'ideo',
    'video_note', 'voice', 'location', 'contact'
]

def is_today_delivery():
    tz = pytz.timezone(Config.TIMEZONE)
    now_datetime = datetime.now(tz)
    # 15:30 по МСК
    cutoff_time = datetime(now_datetime.year, now_datetime.month, now_datetime.day, 15, 30, 0, 0, tzinfo=tz)
    if now_datetime < cutoff_time:
        return True
    return False
