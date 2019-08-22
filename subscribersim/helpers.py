import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def get_seconds_a_year_from_now():
    """Returns the number of seconds a year from now"""
    NOW = datetime.now()
    THEN = NOW + relativedelta(months=+12)
    return datetime_to_time(THEN) - datetime_to_time(NOW)


def get_seconds_in_current_year(datetimeobj):
    """Returns the number of seconds in a given year"""
    NOW = datetimeobj
    THEN = NOW + relativedelta(months=+12)
    return datetime_to_time(THEN) - datetime_to_time(NOW)


def get_seconds_difference(then, now):
    """Returns the number of seconds between two datetime objects"""
    return datetime_to_time(then) - datetime_to_time(now)


def time_to_datetime(tim):
    """Returns a rounded datetime object given a time object"""
    return datetime.fromtimestamp(round(tim))


def datetime_to_time(datetim):
    """Returns a rounded time object given a datetime object"""
    now_time = time.mktime(datetim.timetuple())
    return round(now_time)


def datetime_now():
    """Returns a round datetime object for current timestamp"""
    return time_to_datetime(time.time())


def datetime_get_last_event(customer):
    """Returns a datetime object representing the last event timestamp"""
    return customer.events[-1][0]


def datetime_months_hence(prev, months):
    """Returns a rounded datetime object months from the current timestamp"""
    dt = prev + relativedelta(months=+months)
    tim = datetime_to_time(dt)
    return time_to_datetime(tim)
