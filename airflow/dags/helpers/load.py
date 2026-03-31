# Uploads a file to the bucket.
def upload_blob(buffer, destination_blob_name):
    from google.cloud import storage
    import os

    bucket_name = os.environ.get('BUCKET_NAME')
    buffer.seek(0)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(buffer, content_type='application/octet-stream')

    print(f"Buffer uploaded to {destination_blob_name}.")

# Loads a table to data warehouse using files in the datalake.
def load_table(type, start_date = None, end_date = None, interval = 'daily'):
    from google.cloud import bigquery
    import os
    
    # Writes an external table in big query.
    project = os.environ.get('PROJECT')
    dataset = os.environ.get('DATASET')
    table_id = f'{project}.{dataset}.landing_{type}'

    client = bigquery.Client()

    bucket = os.environ.get('BUCKET_NAME')
    job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.PARQUET,
                )

    if interval == 'daily':
        from helpers.fetch_uris import uri

        uris = uri(bucket, type, start_date, end_date)
        load_job = client.load_table_from_uri(
            source_uris = uris,
            destination = table_id,
            job_config = job_config
        )
    elif interval == 'batch_load':
        load_job = client.load_table_from_uri(
            source_uris = f'gs://{bucket}/api/{type}/*.parquet',
            destination = table_id,
            job_config = job_config
        )

    load_job.result()

    destination_table = client.get_table(table_id)
    print(f"Loaded {destination_table.num_rows} rows.")
