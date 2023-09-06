
from minio import Minio
from minio.error import S3Error

def check_minio_connect():

    endpoint = 'minio.ecoflow.com:9000'
    access_key = 'EQS4J84JGJCDYNENIMT1'
    secret_key = '8Vgk11c9bDOpZPTJMexPLrxZpzEOqro+jZyAUh+a'

    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=True)
    try:
        buckets = client.list_buckets()
        return True, str(buckets[0])
    except S3Error as e:
        return False, str(e)

