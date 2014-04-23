"""
Converts a denormalized CSV file into a normalized CSV file with reference data.

For example, if a CSV file looks like this:

    First,Second
    Alpha,Gamma
    Alpha,Gamma
    Alpha,Delta
    Beta,Gamma
    Beta,Delta

... this will be converted into a transaction file:

    First,Second
    A,A
    A,A
    A,B
    B,A
    B,B

... and a transaction file:

"""
import pandas as pd

KEY = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_='

def baseN(num):
    b = len(KEY)
    return ((num == 0) and KEY[0]) or (baseN(num // b).lstrip(KEY[0]) + KEY[num % b])

def normalize(source, target, reference, ratio, columns):
    data = pd.read_csv(source, dtype=object)
    N = ratio * len(data)
    ref = []
    for column in columns or data.columns:
        vals = data[column].value_counts()
        n = len(vals)
        if n <= N:
            values = pd.Series(pd.np.arange(n)).apply(baseN).values
            lookup = pd.Series(values, index=vals.index, name='value')
            data[column].replace(lookup.to_dict(), inplace=True)
            ref_df = lookup.reset_index()
            ref_df['column'] = column
            ref.append(ref_df)
    data.to_csv(target, index=False)
    pd.concat(ref, ignore_index=True).to_csv(reference, index=False)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Normalize a CSV file into transaction & reference files.')
    parser.add_argument('source', help='Input CSV file')
    parser.add_argument('target', help='Output CSV file')
    parser.add_argument('reference', help='Metadata CSV file')
    parser.add_argument('--ratio', type=float, default=0.005,
        help='Normalize if %% unique values are below this ratio')
    parser.add_argument('--columns', nargs='*', help='Columns to normalize')

    args = parser.parse_args()

    normalize(args.source, args.target, args.reference, args.ratio, args.columns)
