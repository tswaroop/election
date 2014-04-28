"""
A script to create and sync counting day visualisations.
To be run every time the SQL server data changes.
May also be run at a fixed interval (e.g. 1 minute)

Usage: python countingday.py

Creates the following files:

2014-constituency.csv:
    - CONST_ID
    - STATE
    - PC
    - WINNER
    - WINNER PARTY
    - WINNER VOTES
    - RUNNER
    - RUNNER PARTY
    - RUNNER VOTES
    - FINISHED
    - TIME
"""

import json
import argparse
import pyodbc
import pandas as pd
from pandas import read_sql

def simulate(candidates, time):
    """Simulate candidates at an earlier point in time"""
    power = ((candidates['CCODE'] + candidates['CANDICODE']).astype(int) % 10).astype(float)
    power[power > 5] = 1. / (power[power > 5] - 5)
    start = (candidates['CCODE'].astype(int) % 50) / 60.
    end = (start + (candidates['CCODE'].astype(int) % 20) / 60.).clip_upper(1.)

    votes = candidates['VOTES']
    not_started = time < start
    votes[not_started] = 0

    not_finished = time < end
    in_progress = (time >= start) & not_finished
    factor = ((time - start[in_progress]) / (end[in_progress] - start[in_progress])) ** power[in_progress]
    votes[in_progress] = votes[in_progress] * factor
    candidates['VOTES'] = votes

    candidates['RNO'][not_finished] = ''
    return candidates

def main():
    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help='Server name', default='localhost')
    parser.add_argument('--db', help='Database name', default='ELECTIONS_2014')
    parser.add_argument('--time', help='Simulation real time 0.0-1.0', type=float, default=1.0)
    args = parser.parse_args()

    # Connect to SQL Server
    con = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};' +
            'SERVER={:s};'.format(args.server) +
            'DATABASE={:s};'.format(args.db) +
            'WSID={:s};'.format(args.server) +
            'APP=PyCountingDay;' +
            'Trusted_Connection=Yes')

    # Load constituency master
    constituencies = read_sql('SELECT * FROM dbo.CONST_MST', con, coerce_float=False)
    constituencies['CONST_ID'] = constituencies['CONST_ID'].astype(str)
    constituencies = constituencies.set_index('CONST_ID')

    # Load latest candidate votes
    candidates = read_sql('SELECT * FROM dbo.ELECA_CANDMAST', con, coerce_float=False)

    # Mimic VOTES at an earlier point in time
    candidates = simulate(candidates, args.time)

    # Summarise by constituency
    const_wise = candidates.groupby('CCODE')
    candidates['#'] = const_wise['VOTES'].transform(lambda v: v.rank(ascending=False, method='first'))
    candidates['TIME'] = const_wise['CANDI_UPDATE_TIME'].transform('max')
    winners = candidates[candidates['#'] == 1].set_index('CCODE')[['CANDINAME', 'ABBR', 'CANDI_ALLIANCE_ID', 'VOTES']]
    runners = candidates[candidates['#'] == 2].set_index('CCODE')[['CANDINAME', 'ABBR', 'CANDI_ALLIANCE_ID', 'VOTES', 'RNO', 'TIME']]
    winners.columns = ['WINNER', 'WINNER PARTY', 'WINNER ALLIANCE', 'WINNER VOTES']
    runners.columns = ['RUNNER', 'RUNNER PARTY', 'RUNNER ALLIANCE', 'RUNNER VOTES', 'FINISHED', 'UPDATED']

    # Save the results
    elections = pd.concat([
        constituencies[['CONST_NAME_LANG2', 'CONST_NAME_LANG1']],
        winners,
        runners], axis=1)
    elections = elections.reset_index().rename(columns={
        'CONST_NAME_LANG2': 'STATE',
        'CONST_NAME_LANG1': 'PC',
        'index': 'CONST_ID',
    })
    elections.to_csv('2014-constituency.csv'.format(args.time * 100), index=False, float_format='%.0f')

    # Create JSON structure
    summary = {
        'updated': candidates['TIME'].max().strftime('%H:%M, %a %d-%b'),
        'constituencies': {
            'total': len(constituencies),
            'finished': sum(elections['FINISHED'] == '99'),
            'counting': sum((elections['FINISHED'] != '99') & (elections['WINNER VOTES'] > 0)),
            'awaited': sum((elections['FINISHED'] != '99') & (elections['WINNER VOTES'] == 0)),
        },
        'alliances': [
            { 'name': 'NDA',   'won': 5, 'leading': 3},
            { 'name': 'UPA',   'won': 3, 'leading': 1},
            { 'name': 'Other', 'won': 1, 'leading': 1},
        ],
    }
    with open('2014-summary.json', 'w') as out:
        json.dump(summary, out)

if __name__ == '__main__':
    main()
