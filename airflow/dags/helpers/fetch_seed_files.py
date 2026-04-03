import pandas as pd

def renamer(name):
    return '_'.join(
        name.lower()
            .replace('/', '_or_')
            .replace('.', '')
            .split()
    )

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