from datetime import datetime, timedelta

def uri(bucket, type, start_date, end_date):
    current_date = start_date
    uris = []

    while current_date <= end_date:
        uris.append(f'gs://{bucket}/api/{type}/{current_date.strftime("%Y")}/{current_date.strftime("%m")}/{current_date.strftime("%d")}.parquet')
        current_date += timedelta(days=1)

    return uris