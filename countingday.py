"""
A script to create and sync counting day visualisations.
To be run every time the SQL server data changes.
May also be run at a fixed interval (e.g. 1 minute)

Usage: python countingday.py

Creates the following files:

2014-constituency.csv:
    - CONST_ID
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
import datetime
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
    parser.add_argument('--server', help='SQL Server name', default='localhost')
    parser.add_argument('--db', help='Database name', default='ELEC_6MAY_6_20PM')
    parser.add_argument('--time', help='Simulation real time 0.0-1.0', type=float, default=1.0)
    parser.add_argument('--uid', help='SQL Server username')
    parser.add_argument('--pwd', help='SQL Server username')
    args = parser.parse_args()

    # Connect to SQL Server
    dsn = ('DRIVER={:s};' +
          'SERVER={:s};'.format(args.server) +
          'DATABASE={:s};'.format(args.db) +
          'WSID={:s};'.format(args.server) +
          'APP=PyCountingDay;')
    if not args.uid:
        dsn += 'Trusted_Connection=Yes'
    else:
        dsn += 'UID={:s};PWD={:s};'.format(args.uid, args.pwd)

    try:
        con = pyodbc.connect(dsn.format('{SQL Server Native Client 11.0}'))
    except pyodbc.Error:
        con = pyodbc.connect(dsn.format('{SQL Server}'))

    # Load constituency master
    constituencies = read_sql('SELECT * FROM dbo.CONST_MST', con, coerce_float=False)
    constituencies['CONST_ID'] = constituencies['CONST_ID'].astype(str)
    constituencies = constituencies.set_index('CONST_ID')

    # Load latest candidate votes
    candidates = read_sql('SELECT * FROM dbo.ELECP_CANDMAST', con, coerce_float=False)

    # Mimic VOTES at an earlier point in time
    if args.time < 1:
        candidates = simulate(candidates, args.time)

    # Summarise by constituency
    candidates['VOTES'] = candidates['VOTES'].fillna(0).astype(int)
    candidates['ID'] = candidates['CCODE'].astype(str).apply(lambda v: 'S' + v[:2] + '-' + v[-2:])
    const_wise = candidates.groupby('CCODE')
    candidates['#'] = const_wise['VOTES'].transform(lambda v: v.rank(ascending=False, method='first'))
    candidates['CANDI_ALLIANCE_INDIA_ID'].replace({0: 'OTHER', 1: 'NDA', 2: 'UPA', 3: 'OTHER'}, inplace=True)
    winners = candidates[candidates['#'] == 1].set_index('CCODE')[['CANDINAME', 'ABBR', 'CANDI_ALLIANCE_INDIA_ID', 'VOTES', 'ID']]
    runners = candidates[candidates['#'] == 2].set_index('CCODE')[['CANDINAME', 'ABBR', 'CANDI_ALLIANCE_INDIA_ID', 'VOTES', 'RNO']]
    winners.columns = ['WINNER', 'WINNER PARTY', 'WINNER ALLIANCE', 'WINNER VOTES', 'ID']
    runners.columns = ['RUNNER', 'RUNNER PARTY', 'RUNNER ALLIANCE', 'RUNNER VOTES', 'FINISHED']

    # Save the results
    elections = pd.concat([
        winners,
        runners], axis=1)
    elections = elections.reset_index().rename(columns={'index': 'CONST_ID'})
    elections['FINISHED'] = elections['FINISHED'].apply(lambda v: 1 if v == '99' else 0)

    elections.to_csv('2014-constituency.txt'.format(args.time * 100), index=False, float_format='%.0f', sep='\t')

    alliances = elections.pivot_table(cols='FINISHED', rows='WINNER ALLIANCE', values='WINNER', aggfunc='count').fillna(0)
    alliances.rename(columns={0: 'leading', 1: 'won'}, inplace=True)
    if alliances['won']['NDA'] + alliances['leading']['NDA'] > alliances['won']['UPA'] + alliances['leading']['UPA']:
        alliances = alliances.reindex(['NDA', 'OTHER', 'UPA'])
    else:
        alliances = alliances.reindex(['UPA', 'OTHER', 'NDA'])
    alliances['all'] = alliances['leading'] + alliances['won']
    alliances = alliances.reset_index().rename(columns={'index': 'name'})
    alliances_dict = json.loads(alliances.reset_index().to_json(orient='records'))

    parties = elections.pivot_table(cols='FINISHED', rows=['WINNER ALLIANCE', 'WINNER PARTY'], values='WINNER', aggfunc='count').fillna(0)
    parties.rename(columns={0: 'leading', 1: 'won'}, inplace=True)
    parties['all'] = parties['leading'] + parties['won']
    parties.sort('all', ascending=False, inplace=True)
    for row in alliances_dict:
        subset = parties.ix[row['name']].astype(int).reset_index()
        subset.rename(columns={'WINNER PARTY': 'name'}, inplace=True)
        row['parties'] = json.loads(subset.head(5)  .to_json(orient='records'))

    map_data = elections[['ID', 'WINNER PARTY', 'WINNER ALLIANCE', 'WINNER VOTES', 'FINISHED']]
    map_data = json.loads(map_data.to_json(orient='values'))

    # Create JSON structure
    summary = {
        'updated': datetime.datetime.now().strftime('%H:%M %p'),
        'constituencies': {
            'finished': sum(elections['FINISHED'] == 1),
            'counting': sum((elections['FINISHED'] != 1) & (elections['WINNER VOTES'] > 0)),
            'awaited': sum((elections['FINISHED'] != 1) & (elections['WINNER VOTES'] == 0)),
            'total': len(elections),
        },
        'alliances': alliances_dict,
        'party_maxall': parties['all'].max(),
        'map': map_data
    }
    with open('2014-summary.json', 'w') as out:
        json.dump(summary, out, separators=(',', ':'))

if __name__ == '__main__':
    main()
