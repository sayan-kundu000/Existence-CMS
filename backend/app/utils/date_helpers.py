import re
from datetime import datetime
from typing import Optional

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}


def parse_month_year(date_str: str) -> Optional[datetime]:
    """
    Parses date strings such as 'Aug 2020', 'August 2020', '08/2020', '2020-08', or '2020'.
    Returns datetime object set to the 1st of that month, or None if unparseable.
    """
    if not date_str or not date_str.strip():
        return None

    clean = date_str.strip().lower()

    # Case 1: "Aug 2020" or "August 2020"
    match_named = re.match(r'^([a-z]+)\s+([0-9]{4})$', clean)
    if match_named:
        month_name = match_named.group(1)
        year = int(match_named.group(2))
        month = MONTH_MAP.get(month_name)
        if month:
            return datetime(year, month, 1)

    # Case 2: "2020-08" or "2020/08"
    match_iso = re.match(r'^([0-9]{4})[-/]([0-9]{1,2})$', clean)
    if match_iso:
        year = int(match_iso.group(1))
        month = int(match_iso.group(2))
        if 1 <= month <= 12:
            return datetime(year, month, 1)

    # Case 3: "08/2020" or "8/2020"
    match_slash = re.match(r'^([0-9]{1,2})[-/]([0-9]{4})$', clean)
    if match_slash:
        month = int(match_slash.group(1))
        year = int(match_slash.group(2))
        if 1 <= month <= 12:
            return datetime(year, month, 1)

    # Case 4: Year only "2020"
    match_year = re.match(r'^([0-9]{4})$', clean)
    if match_year:
        return datetime(int(match_year.group(1)), 1, 1)

    return None


def validate_date_order(start_str: str, end_str: Optional[str]) -> bool:
    """
    Validates that ending date does not precede starting date.
    Returns True if valid or if either date cannot be parsed into a strict comparator.
    Raises ValueError if end_date precedes start_date.
    """
    if not start_str or not end_str:
        return True

    start_dt = parse_month_year(start_str)
    end_dt = parse_month_year(end_str)

    if start_dt and end_dt:
        if end_dt < start_dt:
            raise ValueError(f"Ending date ({end_str}) cannot precede starting date ({start_str}).")

    return True
