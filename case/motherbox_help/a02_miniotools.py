from minio import Minio
from minio.error import S3Error
from zboxtools import *

def check_minio_connect():
    """
    检查minio连接
    :return:
    """
    tmp_print('<noprint>', '正在检查minio连接...')
    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=True)
    try:
        buckets = client.list_buckets()
        tmp_print('<noprint>', f'minio连接成功, bucket名: {str(buckets[0])}')
        return True, str(buckets[0]), client
    except S3Error as e:
        tmp_print('<noprint>', f'连接失败, {e}')
        return False, str(e), None

def list_minio_objs(obj_prefix):
    """
    从minio中获取指定前缀的object列表
    :param obj_prefix: object前缀
    :return: object列表
    """
    try:
        client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=True)
        objects = client.list_objects(bucket_name, prefix=obj_prefix, recursive=True)
        obj_names = []
        for obj in objects:
            obj_names.append(obj.object_name)
        return obj_names
    except Exception as e:
        tmp_print('<noprint>', f'minio获取列表[{obj_prefix}]失败, {e}')
        return None

def download_obj(local_path, obj_name):
    """
    从minio下载文件
    :param local_path:  本地路径
    :param obj_name:  object名称
    """
    try:
        client = Minio(endpoint, access_key=access_key, secret_key=secret_key, )
        client.fget_object(bucket_name, obj_name, local_path)
        tmp_print(f"正在下载 {bucket_name} 到 {local_path}")
    except Exception as err:
        tmp_print(f'下载文件[{obj_name}]失败, {err}')

def get_motherbox_version(obj_prefix):
    """
    获取minio的box版本号
    :param obj_prefix: object前缀
    :return: box版本号
    """
    versions = []
    obj_names = list_minio_objs(obj_prefix)
    if obj_names is None: return None
    for objn in obj_names:
        versions.append(str(objn).split('/')[-2])
    new_version = max(versions)
    tmp_print('<noprint>', f'最新版本: {new_version}')
    return int(new_version)

# get_motherbox_version('autocase/android/motherbox/')