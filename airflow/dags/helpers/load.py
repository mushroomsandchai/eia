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
    from google.cloud import bigquery, storage
    import os
    
    # Writes an external table in big query.
    project = os.environ.get('PROJECT')
    dataset = os.environ.get('DATASET')
    bucket = os.environ.get('BUCKET_NAME')

    table_id = f'{project}.{dataset}.landing_{type}'

    if type == 'generation':
        cluster = ['respondent', 'fueltype']
    elif type == 'interchange':
        cluster = ['fromba', 'toba']
    elif type == 'demand_forecast':
        cluster = ['respondent', 'type']
    elif type == 'demand_by_subregion':
        cluster = ['parent', 'subba']

    client = bigquery.Client()
    storage_client = storage.Client()
    gcpbucket = storage_client.bucket(bucket)
    
    job_config = bigquery.LoadJobConfig(
                        source_format = bigquery.SourceFormat.PARQUET,
                        time_partitioning = bigquery.TimePartitioning(
                            type_ = bigquery.TimePartitioningType.DAY,
                            field = 'partition_date',
                            expiration_ms = None,
                        ),
                        clustering_fields = cluster,
                        write_disposition = bigquery.WriteDisposition.WRITE_APPEND,
                    )

    if interval == 'daily':
        from helpers.fetch_uris import uri

        if type == 'demand_forecast':
            from datetime import timedelta
            end_date = end_date + timedelta(days = 1)
        uris = uri(bucket, type, start_date, end_date)
        
        for u in uris:
            blob = gcpbucket.blob(u)

            if blob:
                load_job = client.load_table_from_uri(
                    source_uris = u,
                    destination = table_id,
                    job_config = job_config
                )

    elif interval == 'batch_load':
        source_uri = f'gs://{bucket}/api/{type}/*.parquet'

        blob = gcpbucket.blob(source_uri)

        if blob:
            load_job = client.load_table_from_uri(
                source_uris = source_uri,
                destination = table_id,
                job_config = job_config
            )