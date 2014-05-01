from collections import OrderedDict
#from donation.common import prev_days, prev_wtd, prev_mtd, prev_ytd
import stats
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

# Title of the application
title = 'Party Donation'

# Date column
date = ''


# Transaction data file
data_file = 'data.csv'

# Transformations for transaction data file.
# Just return data if no transformations are required.
def data_setup(data):
    # data[date] = stats.to_date(data[date], dayfirst=True)
    data['Amount'] /= 1E7;
    return data

# Reference data file and its transformations
reference_file = 'reference.csv'
def reference_setup(ref):
    return ref.set_index('column')

# Group by columns
groups = 'Party,Donor Type,Donor Name'.split(',')

# Columns that act as dropdown filters
filters = ['Financial Year']

# Maximum entries in the treemap
MAX_ENTRIES = 500

# Maximum font size in treemap
MAX_FONT = 100

# Treemap aspect ratio
aspect = 2

# Outliers to be removed on either side of colour data
outliers = 0.05

# What are the allowed date periods
periods = OrderedDict((
    ('Year',  prev_days(365)),
))

# What is the size based on?
sizes = OrderedDict((
    # Title                       fieldname, aggregation, display format
    ('Amount Donated',       ('Amount', 'sum', '{:,.2f} cr')),

))

# Colour is based on ratio of two sizes (see sizes variable)
# Optionally prefixed by 'Prev' to indicate previous period
colors = OrderedDict((
    # Title                       numerator, denominator, display format
    ('Amount',        ('Amount Donated', 'Amount Donated', '{:,.2f}')),
))
