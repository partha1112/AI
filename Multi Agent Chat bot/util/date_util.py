from datetime import date, timedelta
from typing import Optional


def parse_relative_period(user_message: str) -> Optional[tuple[str, str]]:
    lowered = user_message.lower()
    if not any(term in lowered for term in [
        "transaction",
        "transactions",
        "spending",
        "expense",
        "expenses",
        "payment",
        "payments",
        "transfer",
        "transfers",
    ]):
        return None

    today = date.today()
    if "last week" in lowered:
        current_week_start = today - timedelta(days=today.weekday() + 1)
        last_week_start = current_week_start - timedelta(days=7)
        last_week_end = current_week_start - timedelta(days=1)
        return last_week_start.strftime("%Y-%m-%d"), last_week_end.strftime("%Y-%m-%d")

    if "last month" in lowered:
        first_of_current_month = date(today.year, today.month, 1)
        last_month_end = first_of_current_month - timedelta(days=1)
        last_month_start = date(last_month_end.year, last_month_end.month, 1)
        return last_month_start.strftime("%Y-%m-%d"), last_month_end.strftime("%Y-%m-%d")

    if "last" in lowered and "day" in lowered:
        for token in lowered.split():
            if token.isdigit():
                days = int(token)
                end_date = today - timedelta(days=1)
                start_date = end_date - timedelta(days=days - 1)
                return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    if "last" in lowered and "month" in lowered:
        for token in lowered.split():
            if token.isdigit():
                months = int(token)
                end_month = today.month - 1 if today.month > 1 else 12
                end_year = today.year if today.month > 1 else today.year - 1
                start_month = end_month - months + 1
                start_year = end_year
                while start_month <= 0:
                    start_month += 12
                    start_year -= 1
                start_date = date(start_year, start_month, 1)
                end_date = date(end_year, end_month, 1) - timedelta(days=1)
                return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    return None


def resolve_transaction_dates(user_message: str) -> dict[str, str] | None:
    parsed = parse_relative_period(user_message)
    if parsed is None:
        return None

    start_date, end_date = parsed
    return {
        "start_date": start_date,
        "end_date": end_date,
        "explanation": "Resolved from relative period using the current date.",
    }
