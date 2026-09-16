import calendar
from datetime import date


MONTH_NAMES = {name.lower(): index for index, name in enumerate(calendar.month_name) if name}


def month_range(year: int, month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def infer_month_range(message: str, today: date) -> tuple[date, date, str]:
    """Resolve a tiny, explicit subset of time expressions for Stage 1."""
    text = message.lower()

    for month_name, month_number in MONTH_NAMES.items():
        if month_name in text:
            year = today.year
            start, end = month_range(year, month_number)
            return start, end, f"{calendar.month_name[month_number]} {year}"

    if "last month" in text:
        if today.month == 1:
            year, month = today.year - 1, 12
        else:
            year, month = today.year, today.month - 1
        start, end = month_range(year, month)
        return start, end, f"{calendar.month_name[month]} {year}"

    start, end = month_range(today.year, today.month)
    return start, min(end, today), f"{calendar.month_name[today.month]} {today.year}"
