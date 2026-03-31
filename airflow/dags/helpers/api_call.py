import requests
import math
import io
import os
from datetime import datetime
import pandas as pd

def fetch_page(url, params, check):
    if not check:
        print(f'Currently at page no: {math.ceil(params['offset'] / 5000) + 1}')
    r = requests.get(url, params = params, timeout = 60)
    r.raise_for_status()
    return r.json()

def api_call(endpoint):
    key = os.environ.get('EIA_API')
    url = endpoint['url']
    params = {
        "frequency": "hourly",
        "data[0]": "value",
        "start": endpoint['start_date'],
        "end": endpoint['end_date'],
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "offset": 0,
        "length": 5000,
        "api_key": key
    }
    first_page = fetch_page(url, params, True)
    num_records = first_page["response"]["total"]
    total = int(num_records)
    page_size = 5000
    num_pages = math.ceil(total / page_size)
    print(f'A total of {num_records} records are being fetched from {num_pages} pages. Time for some chai/coffee while the task finishes.')
    df = pd.DataFrame()
    num_pages = 0

    while True:
        data = fetch_page(url, params, False)['response']['data']
        if not data:
            break
        df = pd.concat([df, pd.DataFrame(data)])
        params["offset"] = params["offset"] + page_size

    df['ingestion_time'] = datetime.now()


    for column in df.columns:
        df = renamer(df, column)

    print(f'Total number of records shown by the API: {total}')
    print(f'Total number of reocrds returned by the API: {df.shape[0]}')

    if total != df.shape[0]:
        raise ValueError('Total number of records found is not equal to the number of written records.')
    else:
        buffer = io.BytesIO()
        df.to_parquet(buffer, index = False)
        buffer.seek(0)
        return(buffer)

def renamer(df, column):
    new_name = column.lower().replace('-', '_')
    return(df.rename(columns = {column: new_name}))
