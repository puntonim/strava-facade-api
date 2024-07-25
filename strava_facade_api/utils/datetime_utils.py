from datetime import datetime, time, timezone


def now_utc() -> datetime:
    """
    Time in UTC, timezone-aware.
    """
    return datetime.now(tz=timezone.utc)


def now() -> datetime:
    """
    Time in the current timezone, timezone-aware.
    """
    return datetime.now().astimezone()


def is_naive(d: datetime | time):
    # Docs: https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
    if d.tzinfo is None or d.tzinfo.utcoffset(None) is None:
        return True
    return False
