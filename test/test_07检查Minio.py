from minio import Minio
from minio.error import S3Error

def check_minio_connection(endpoint, access_key, secret_key):
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=True
    )

    try:
        # 检查是否可以列出存储桶
        buckets = client.list_buckets()
        print("MinIO 连接成功，可用的存储桶如下:")
        for bucket in buckets:
            print(bucket.name)
        return True
    except Exception as e:
        print(f"连接MinIO时出错: {e}")
        return False

# 使用实际的Endpoint、Access Key和Secret Key替换以下占位符
endpoint = 'minio.ecoflow.com:9000'
access_key = 'EQS4J84JGJCDYNENIMT1'
secret_key = '8Vgk11c9bDOpZPTJMexPLrxZpzEOqro+jZyAUh+a'

check_minio_connection(endpoint, access_key, secret_key)
