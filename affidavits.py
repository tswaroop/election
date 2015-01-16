"""
Rename STATE and PC in affidavit.csv based on PC.csv

Usage: python affidavits.py
"""

import pandas as pd

affidavits = pd.read_csv('affidavits.csv')
pc = pd.read_csv('pc.csv').set_index(['ST_CODE', 'PC_CODE'])

affidavits['STATE'] = affidavits.apply(
    lambda row: pc.ix[row['ST_CODE'], row['PC_CODE']]['STATE'], axis=1)
affidavits['PC'] = affidavits.apply(
    lambda row: pc.ix[row['ST_CODE'], row['PC_CODE']]['PC'], axis=1)

affidavits.to_csv('affidavits.csv', index=False)
