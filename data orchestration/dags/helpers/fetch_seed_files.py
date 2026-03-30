import pandas as pd

def renamer(name):
    return '_'.join(
        name.lower()
            .replace('/', '_or_')
            .replace('.', '')
            .split()
    )

def build_utc_offset_table(start, end, labels, mapping):
    # Create a UTC hourly range
    utc_range = pd.date_range(start, end, freq='d', tz='UTC')
    dfs = []

    for label in labels:
        local = utc_range.tz_convert(mapping[label])

        # Compute UTC offset in hours (including DST)
        offsets = pd.Series(local).map(lambda x: x.utcoffset().total_seconds() / 3600)

        df = pd.DataFrame({
            'utc_time': utc_range.date,
            'timezone': label,
            'utc_offset_hours': offsets
        })

        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

def make_csv():
    df = pd.ExcelFile('/tmp/eia_930_reference_tables.xlsx')
    ba = pd.read_excel(df, 'BAs')
    regions = pd.read_excel(df, 'Regions')
    ba_subregions = pd.read_excel(df, 'BA Subregions')
    ba_connections = pd.read_excel(df, 'BA Connections')
    es = pd.read_excel(df, 'Energy Sources')

    dataframes = {
        "balancing_authorities": ba,
        "regions": regions,
        "ba_subregions": ba_subregions,
        "ba_connections": ba_connections,
        "energy_sources": es
    }

    for name, df in dataframes.items():
        df.rename(columns = renamer, inplace = True)
        df.to_csv(f"/opt/airflow/dbt/seeds/{name}.csv", index = False)

    tz_labels = ['Central', 'Pacific', 'Arizona', 'Eastern', 'Mountain']

    tz_map = {
        'Eastern': 'America/New_York',
        'Central': 'America/Chicago',
        'Mountain': 'America/Denver',
        'Pacific': 'America/Los_Angeles',
        'Arizona': 'America/Phoenix'
    }

    utc_offset_df = build_utc_offset_table('2019-01-01', '2030-12-31', tz_labels, tz_map)
    utc_offset_df.to_csv('/opt/airflow/dbt/seeds/utc_offset.csv', index = False)