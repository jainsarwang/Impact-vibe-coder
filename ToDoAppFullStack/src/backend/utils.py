from datetime import datetime, date

def is_overdue(due_date: datetime) -> bool:
    if not due_date:
        return False
    return due_date.date() < date.today()


def is_due_today(due_date: datetime) -> bool:
    if not due_date:
        return False
    return due_date.date() == date.today()


def is_upcoming(due_date: datetime) -> bool:
    if not due_date:
        return False
    return due_date.date() > date.today()
