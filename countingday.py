"""
A script to create and sync counting day visualisations.
To be run every time the SQL server data changes.
May also be run at a fixed interval (e.g. 1 minute)

Usage: python countingday.py

Creates the following files:

2014-constituency-results.csv:
    - CONST_ID
    - STATE
    - PC
    - WINNER TIME
    - WINNER
    - WINNER PARTY
    - WINNER VOTES 1
    - RUNNER TIME
    - RUNNER
    - RUNNER PARTY
    - RUNNER VOTES 2
"""

import argparse
import pyodbc
import pandas as pd
from pandas import read_sql

parser = argparse.ArgumentParser()
parser.add_argument('--server', help='Server name', default='localhost')
parser.add_argument('--db', help='Database name', default='ELECTIONS_2014')
args = parser.parse_args()

con = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};' +
        'SERVER={:s};'.format(args.server) +
        'DATABASE={:s};'.format(args.db) +
        'WSID={:s};'.format(args.server) +
        'APP=PyCountingDay;' +
        'Trusted_Connection=Yes')
constituencies = read_sql('SELECT * FROM dbo.CONST_MST', con, coerce_float=False)
constituencies['CONST_ID'] = constituencies['CONST_ID'].astype(str)
constituencies = constituencies.set_index('CONST_ID')

candidates = read_sql('SELECT * FROM dbo.ELECA_CANDMAST', con, coerce_float=False)
const_wise = candidates.groupby('CCODE')
candidates['#'] = const_wise['VOTES'].transform(lambda v: v.rank(ascending=False, method='first'))
candidates['TIME'] = const_wise['CANDI_UPDATE_TIME'].transform('max')
winners = candidates[candidates['#'] == 1].set_index('CCODE')[['CANDINAME', 'ABBR', 'VOTES']]
runners = candidates[candidates['#'] == 2].set_index('CCODE')[['CANDINAME', 'ABBR', 'VOTES', 'TIME']]
winners.columns = ['WINNER', 'WINNER PARTY', 'WINNER VOTES']
runners.columns = ['RUNNER', 'RUNNER PARTY', 'RUNNER VOTES', 'UPDATED']

result = pd.concat([
    constituencies[['CONST_NAME_LANG2', 'CONST_NAME_LANG1']],
    winners,
    runners], axis=1)
result = result.reset_index().rename(columns={
    'CONST_NAME_LANG2': 'STATE',
    'CONST_NAME_LANG1': 'PC',
    'index': 'CONST_ID',
})
result.to_csv('2014-constituency-results.csv', index=False, float_format='%.0f')
