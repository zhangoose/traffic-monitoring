from datetime import datetime
from pytz import UTC


def utc_now():
    """
    `now` returns a timezone aware date time in UTC 
    """
    return datetime.utcnow().replace(tzinfo=UTC)
