import re

re_slug = re.compile(r'[^A-Za-z0-9_]+')

def slug(s):
    return re_slug.sub('-', s)

def pc_setup(data):
    data['VOTES'] = data['VOTES'].astype(float)
    data['AGE'] = data['AGE'].astype(float)
    data['COUNT'] = 1

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
    elections['WINNING PARTY'] = winners['PARTY'].min()

    return data, elections
