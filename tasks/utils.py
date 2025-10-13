#recurrence utilities

from datetime import date
from dateutil.relativedelta import relativedelta

def get_next_yearly_date(current_date: date) -> date:
    return current_date + relativedelta(years=1)

def get_next_quarter_dates(start_date: date):
    # returns the next quarter start dates for the remainder of the year
    quarters = []
    month = ((start_date.month - 1) // 3) * 3 + 1
    # find next quarter start
    next_q_month = month + 3
    next_q = date(start_date.year, ((next_q_month - 1) % 12) + 1, start_date.day)
    if next_q.month <= start_date.month:
        next_q = next_q + relativedelta(years=1)
    quarters.append(next_q)
    return quarters

def get_next_term_dates(start_date: date):
    # Example: split academic year into three terms of 4 months each (approx)
    terms = []
    terms.append(start_date + relativedelta(months=4))
    terms.append(start_date + relativedelta(months=8))
    return terms

#status comparison helper
def status_changed(old_instance, new_instance):
    """
    Return True if status changed between two Activity instances.
    """
    return getattr(old_instance, 'status', None) != getattr(new_instance, 'status', None)
