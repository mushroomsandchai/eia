# Counts number of parquet files in the bucket.
# This package assumes we're only using the bucket for API records from EIA.

from google.cloud import storage
import os

def count():
    bucket_name = os.environ.get('BUCKET_NAME')
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    blobs = client.list_blobs(bucket_name)
    parquet_files = [b for b in blobs if b.name.endswith(".parquet")]
    print(f"Total number of parquet files: {len(parquet_files)}")
    return(len(parquet_files))
