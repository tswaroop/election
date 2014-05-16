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
    candidates = read_sql('SELECT CCODE, CANDICODE, CANDINAME, VOTES, ABBR, CANDI_STATUS, CANDI_ALLIANCE_INDIA_ID FROM dbo.ELECP_CANDMAST', con, coerce_float=False)
    candidates['CANDICODE'] = candidates['CANDICODE'].dropna().astype(int)
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
        'S31-1': 'U06-1',   # Lakshadweep
        'S32-1': 'U07-1',   # Puducherry
        'S33-1': 'U01-1',   # Andaman & Nicobar
        'S34-1': 'U02-1',   # Chandigarh
        'S35-1': 'U03-1',   # Dadra & Nagar Haveli
    }, inplace=True)

    # Replace alliance ID values with text (slow operations)
    candidates['CANDI_ALLIANCE_INDIA_ID'].replace({0: 'OTHER', 1: 'NDA', 2: 'UPA', 3: 'OTHER'}, inplace=True)

    # Take each constituency's data
    declared = candidates[candidates['CANDI_STATUS'].isin(['WON', 'LEADING'])].set_index('CCODE')
    awaited = candidates[~candidates['CANDI_STATUS'].isin(['WON', 'LEADING', 'TRAILING', 'LOST']) & (candidates['CANDICODE'] == 1)].set_index('CCODE')

    elections = pd.concat([declared, awaited], axis=0)[['ABBR', 'CANDI_ALLIANCE_INDIA_ID', 'VOTES', 'ID', 'CANDI_STATUS', 'CANDICODE']]
    elections.columns = ['ABBR', 'CANDI_ALLIANCE_INDIA_ID', 'WINNER VOTES', 'ID', 'STATUS', 'CANDICODE']

    elections['VOTES'] = candidates.sort(['CCODE', 'CANDICODE']).groupby('CCODE')['VOTES'].apply(lambda v: list(v))
    elections = elections.reset_index().rename(columns={'index': 'CONST_ID'})
    # Status: 0 = awaited, 1 = counting, 2 = finished
    elections['STATUS'] = elections.apply(lambda v: 2 if v['STATUS'] == 'WON' else 1 if v['STATUS'] == 'LEADING' else 0, axis=1)

    elections = elections[['ID', 'ABBR', 'CANDI_ALLIANCE_INDIA_ID', 'WINNER VOTES', 'STATUS', 'VOTES', 'CANDICODE']]

    # Create JSON structure
    now = datetime.datetime.now()
    summary = {
        'updated': now.strftime('%H:%M %p'),
        'map': json.loads(elections.to_json(orient='values'))
    }
    with open('2014-summary.json', 'w') as out:
        json.dump(summary, out, separators=(',', ':'))
    with open(now.strftime('2014-summary-%Y-%m-%d-%H-%M-%S.json'), 'w') as out:
        json.dump(summary, out, separators=(',', ':'))

    # If 2014-candidates.json was not present, regenerate it
    if not count:
        battles = pd.read_sql('SELECT TRN_CONSTI_ID, TRN_CANDI_CODE FROM CANDI_KEY_CONTEST', con, coerce_float=False).astype(str)
        battles.columns = ['CCODE', 'CANDICODE']
        battles['CANDICODE'] = battles['CANDICODE'].dropna().astype(int)
        battles['CCODE'] = battles['CCODE'].apply(lambda v: v.zfill(5))
        battles['BATTLE'] = 1

        battles = battles.set_index(['CCODE', 'CANDICODE'])
        candi_index = candidates.set_index(['CCODE', 'CANDICODE'])
        candi_index['BATTLE'] = battles['BATTLE']
        candi_index['BATTLE'] = candi_index['BATTLE'].fillna(0)
        candi_index['BATTLE'] = candi_index['BATTLE'].astype(int)
        candi_index.sort_index(inplace=True)
        cols = candi_index[['CANDINAME', 'ABBR', 'BATTLE']]
        names = {
            id: cols.ix[indices].values.tolist()
            for id, indices in candi_index.groupby(['ID']).groups.iteritems()
        }
        with open('2014-candidates.json', 'w') as out:
            json.dump(names, out, separators=(',', ':'), encoding='cp1252')

    by_status = elections.groupby(['STATUS'])['ID'].count()
    counting = elections[elections['STATUS'].isin([1,2])]
    by_party = counting.groupby(['ABBR'])['ID'].count()
    by_alliance = counting.groupby(['CANDI_ALLIANCE_INDIA_ID'])['ID'].count()
    return '{:0.2f}s. {:3d} = {:3d} FIN + {:3d} WIP + {:3d} TBD. NDA={:3d} UPA={:3d} CONG={:3d} BJP={:3d}. {:3d} candidates'.format(
        duration,
        len(elections),
        by_status.ix[2] if 2 in by_status else 0,
        by_status.ix[1] if 1 in by_status else 0,
        by_status.ix[0] if 0 in by_status else 0,
        by_alliance.ix['NDA'] if 'NDA'  in by_alliance else 0,
        by_alliance.ix['UPA'] if 'UPA'  in by_alliance else 0,
        by_party.ix['CONG']   if 'CONG' in by_party else 0,
        by_party.ix['BJP']    if 'BJP'  in by_party else 0,
        len(candidates),
    )

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
                msg = main(args, count)
                count += 1
                print count, datetime.datetime.now().strftime('%H:%M:%S'), msg
            except Exception, e:
                print traceback.format_exc(e)
            finally:
                sleep(args.refresh)
