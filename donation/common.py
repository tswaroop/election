import pandas as pd
from pandas.tseries.offsets import DateOffset, MonthBegin, YearBegin

def prev_days(days):
    def fn(date):
        prev_end_time = start_time = date - DateOffset(days=days)
        prev_start_time = date - DateOffset(days=2 * days)
        return prev_start_time, prev_end_time, start_time
    return fn

def prev_wtd(date):
    start_time = date - DateOffset(days=date.weekday() or 7)
    prev_end_time = date - DateOffset(days=7)
    prev_start_time = prev_end_time - DateOffset(days=prev_end_time.weekday() or 7)
    return prev_start_time, prev_end_time, start_time

def prev_mtd(date):
    start_time = date - MonthBegin()
    prev_end_time = (start_time - DateOffset(days=1)).replace(day=date.day)
    prev_start_time = prev_end_time - MonthBegin()
    return prev_start_time, prev_end_time, start_time

def prev_ytd(date):
    start_time = date - YearBegin()
    prev_end_time = (start_time - DateOffset(days=1)).replace(day=date.day, month=date.month)
    prev_start_time = prev_end_time - YearBegin()
    return prev_start_time, prev_end_time, start_time
