"""
A script to create and sync counting day visualisations.
To be run every time the SQL server data changes.
May also be run at a fixed interval (e.g. 1 minute)

Usage: python countingday.py
"""

import json
import datetime
import argparse
import pyodbc
import pandas as pd
from pandas import read_sql

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

    # Load latest candidate votes
    candidates = read_sql('SELECT * FROM dbo.ELECP_CANDMAST', con, coerce_float=False)

    # Summarise by constituency
    candidates['VOTES'] = candidates['VOTES'].fillna(0).astype(int)
    candidates['ID'] = candidates['CCODE'].dropna().astype(str).apply(lambda v: 'S%s-%d' % (v[:2], int(v[-2:])))

    # Map Nielsen's Union Territory codes to ECI Union Territory codes
    candidates['ID'].replace({
        'S29-1': 'U04-1',   # Daman & Diu
        'S30-1': 'U05-1',   # NCT of Delhi
        'S30-2': 'U05-2',
        'S30-3': 'U05-3',
        'S30-4': 'U05-4',
        'S30-5': 'U05-5',
        'S30-6': 'U05-6',
        'S30-7': 'U05-7',
        'S32-1': 'U07-1',   # Puducherry
        'S34-1': 'U02-1',   # Chandigarh
        'S35-1': 'U03-1',   # Dadra & Nagar Haveli
        'S31-1': 'U06-1',   # Lakshadweep
        'S33-1': 'U01-1',   # Andaman & Nicobar
    }, inplace=True)

    const_wise = candidates.groupby('CCODE')
    candidates['#'] = const_wise['VOTES'].transform(lambda v: v.rank(ascending=False, method='first'))
    candidates['CANDI_ALLIANCE_INDIA_ID'].replace({0: 'OTHER', 1: 'NDA', 2: 'UPA', 3: 'OTHER'}, inplace=True)
    winners = candidates[candidates['#'] == 1].set_index('CCODE')[['CANDINAME', 'ABBR', 'CANDI_ALLIANCE_INDIA_ID', 'VOTES', 'ID']]
    runners = candidates[candidates['#'] == 2].set_index('CCODE')[['CANDINAME', 'ABBR', 'CANDI_ALLIANCE_INDIA_ID', 'VOTES', 'RNO']]
    winners.columns = ['WINNER', 'WINNER PARTY', 'WINNER ALLIANCE', 'WINNER VOTES', 'ID']
    runners.columns = ['RUNNER', 'RUNNER PARTY', 'RUNNER ALLIANCE', 'RUNNER VOTES', 'STATUS']

    # Save the results
    elections = pd.concat([
        winners,
        runners], axis=1)
    elections = elections.reset_index().rename(columns={'index': 'CONST_ID'})
    elections['STATUS'] = elections.apply(lambda v: 2 if v['STATUS'] == '99' else 1 if v['WINNER VOTES'] > 0 else 0, axis=1)

    map_data = elections[['ID', 'WINNER PARTY', 'WINNER ALLIANCE', 'WINNER VOTES', 'STATUS']]
    map_data = json.loads(map_data.to_json(orient='values'))

    # Create JSON structure
    summary = {
        'updated': datetime.datetime.now().strftime('%H:%M %p'),
        'map': map_data
    }
    with open('2014-summary.json', 'w') as out:
        json.dump(summary, out, separators=(',', ':'))

if __name__ == '__main__':
    main()
