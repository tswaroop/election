import pandas as pd
import re
import layout
from collections import OrderedDict

NONE_COLOR = '#a0a0a0'

re_slug = re.compile(r'[^A-Za-z0-9_]+')

def slug(s):
    return re_slug.sub('-', str(s))

def pc_setup(data):
    data['VOTES'] = data['VOTES'].astype(float)
    data['AGE'] = data['AGE'].astype(float)
    data['COUNT'] = 1

    # Merge some parties for practicality
    data['PARTY'].replace({
      'INC(I)': 'INC',
      'ADK': 'ADMK',
      'BLD': 'JNP',
    }, inplace=True)

    # These elections had very few seats. Merge them with the previous year
    data['YEAR'].replace({
      '1985': '1984',
      '1992': '1991',
    }, inplace=True)

    electionwise = data.groupby(['YEAR', 'STATE', 'PC'])
    winners = data[data['#'] == '1'].groupby(['YEAR', 'STATE', 'PC'])
    women = data[data['SEX'] == 'F'].groupby(['YEAR', 'STATE', 'PC'])

    elections = data.pivot_table(
        rows=['YEAR', 'STATE', 'PC'],
        cols='#',
        values='VOTES')
    elections['VOTES'] = elections.sum(axis=1)
    elections['CANDIDATES'] = electionwise['COUNT'].sum()
    elections['MARGIN'] = elections['1'] - elections['2']
    elections['MARGIN %'] = elections['MARGIN'] / elections['VOTES'].astype(float)
    elections['WIN %'] = elections['1'] / elections['VOTES'].astype(float)
    elections['AGE'] = winners['AGE'].mean()
    elections['YOUNGEST CANDIDATE'] = electionwise['AGE'].min()
    elections['OLDEST CANDIDATE'] = electionwise['AGE'].max()
    elections['WOMEN'] = women['COUNT'].sum()
    elections['WOMEN %'] = elections['WOMEN'] / elections['CANDIDATES'].astype(float)
    elections['WINNER'] = winners['NAME'].min()
    elections['PARTY'] = winners['PARTY'].min()

    return data, elections

def ac_setup(data):
    data['VOTES'] = data['VOTES'].astype(float)
    data['AGE'] = data['AGE'].astype(float)
    data['COUNT'] = 1
    return data

R = 0.1
def latlong_setup(latlong):
    latlong['X'] = latlong['Y'] = pd.np.empty(len(latlong))
    for state, indices in latlong.groupby('ST_NAME').groups.iteritems():
        xy = layout.unpack(latlong.ix[indices][['LONG', 'LAT']], [R] * len(indices), gravity=0, factor=.99)
        latlong['X'][indices] = xy[:,0]
        latlong['Y'][indices] = xy[:,1]
    return latlong

metric_names = OrderedDict((
  ('MARGIN',     'Margin'),
  ('MARGIN %',   'Margin %'),
  ('CANDIDATES', 'Candidates'),
  ('AGE',        'Winner age'),
  ('WOMEN %',    'Women %'),
  ('VOTES',      'Voters'),
  ('WIN %',      'Winner %'),
  ('CONSTANT',   'Constant size'),
))
