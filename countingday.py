"""
A script to create and sync counting day visualisations.
To be run every time the SQL server data changes.
May also be run at a fixed interval (e.g. 1 minute)

Usage: python countingday.py
"""

import os
import json
import datetime
import pyodbc
import pandas as pd
from pandas import read_sql
from time import time, sleep

def main(args, count):
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
        con = pyodbc.connect(dsn.format('{SQL Server Native Client 11.0}'), timeout=3, unicode_results=True)
    except pyodbc.Error:
        con = pyodbc.connect(dsn.format('{SQL Server}'), timeout=3, unicode_results=True)

    # Load latest candidate votes
    start_time = time()
    candidates = read_sql('SELECT * FROM dbo.ELECP_CANDMAST', con, coerce_float=False)
    duration = time() - start_time

    # Sanitize the values
    candidates['VOTES'] = candidates['VOTES'].fillna(0).astype(int)
    candidates['ID'] = candidates['CCODE'].dropna().astype(str).apply(lambda v: 'S%s-%d' % (v[:2], int(v[-2:])))
    candidates['ABBR'].replace({
      'INC(I)': 'CONG',
      'ADK': 'ADMK',
      'BLD': 'JNP',
      'INC': 'CONG',
      'SHS': 'SS',
      'JD(U)': 'JDU',
      'AITC': 'TMC',
      'JKN': 'NC',
      'MUL': 'IUML',
      'JD(S)': 'JDS',
      'BOPF': 'BPF',
      'KEC(M)': 'KECM',
    }, inplace=True)

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

    # Replace alliance ID values with text (slow operations)
    candidates['CANDI_ALLIANCE_INDIA_ID'].replace({0: 'OTHER', 1: 'NDA', 2: 'UPA', 3: 'OTHER'}, inplace=True)

    # Take the winners / leaders' data. Assumption: only 1 such row per constituency
    elections = candidates[candidates['CANDI_STATUS'].isin(['WON', 'LEADING'])].set_index('CCODE')[['CANDINAME', 'ABBR', 'CANDI_ALLIANCE_INDIA_ID', 'VOTES', 'ID', 'CANDI_STATUS']]
    elections.columns = ['WINNER', 'WINNER PARTY', 'WINNER ALLIANCE', 'WINNER VOTES', 'ID', 'STATUS']

    elections['VOTES'] = candidates.sort(['CCODE', 'CANDICODE']).groupby('CCODE')['VOTES'].apply(lambda v: list(v))
    elections = elections.reset_index().rename(columns={'index': 'CONST_ID'})
    # Status: 0 = awaited, 1 = counting, 2 = finished
    elections['STATUS'] = elections.apply(lambda v: 0 if v['WINNER VOTES'] <= 0 else 2 if v['STATUS'] == 'WON' else 1, axis=1)

    map_data = elections[['ID', 'WINNER PARTY', 'WINNER ALLIANCE', 'WINNER VOTES', 'STATUS', 'VOTES']]
    map_data = json.loads(map_data.to_json(orient='values'))

    # Create JSON structure
    now = datetime.datetime.now()
    summary = {
        'updated': now.strftime('%H:%M %p'),
        'map': map_data
    }
    with open('2014-summary.json', 'w') as out:
        json.dump(summary, out, separators=(',', ':'))
    with open(now.strftime('2014-summary-%Y-%m-%d-%H-%M-%S.json'), 'w') as out:
        json.dump(summary, out, separators=(',', ':'))

    # If 2014-candidates.json was not present, regenerate it
    if not count:
        candidates.sort(['ID', 'CANDICODE'], inplace=True)
        cols = candidates[['CANDINAME', 'ABBR']]
        names = {
            id: cols.ix[indices].values.tolist()
            for id, indices in candidates.groupby(['ID']).groups.iteritems()
        }
        with open('2014-candidates.json', 'w') as out:
            json.dump(names, out, separators=(',', ':'), encoding='cp1252')

    return duration

if __name__ == '__main__':
    import argparse
    import traceback

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help='SQL Server name', default='localhost')
    parser.add_argument('--db', help='Database name', default='ELEC_6MAY_6_20PM')
    parser.add_argument('--uid', help='SQL Server username')
    parser.add_argument('--pwd', help='SQL Server username')
    parser.add_argument('--refresh', help='Rerun after n seconds', type=int)
    args = parser.parse_args()

    count = 0
    if not args.refresh:
        main(args, count)
    else:
        while True:
            try:
                duration = main(args, count)
                count += 1
                print count, datetime.datetime.now().strftime('%H:%M:%S'), duration
            except Exception, e:
                print traceback.format_exc(e)
            finally:
                sleep(args.refresh)
