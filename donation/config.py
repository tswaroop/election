from collections import OrderedDict
from common import prev_days, prev_wtd, prev_mtd, prev_ytd
import stats

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
    return data

# Reference data file and its transformations
reference_file = 'reference.csv'
def reference_setup(ref):
    return ref.set_index('column')

# Group by columns
groups = 'Party,Type,Name'.split(',')

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
    ('# Amount',       ('Amount', 'sum', '{:,.0f}')),

))

# Colour is based on ratio of two sizes (see sizes variable)
# Optionally prefixed by 'Prev' to indicate previous period
colors = OrderedDict((
    # Title                       numerator, denominator, display format
    ('Amount',        ('# Amount', '# Amount', '{:,.2f}')),
))
