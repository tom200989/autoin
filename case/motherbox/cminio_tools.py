import urllib3
from minio import Minio
from minio.error import S3Error
from ctmp_tools import *
from cprogress import Progress

def check_minio_connect():
    """
    检查minio连接
    :return:
    """
    tmp_print('正在检查minio连接...')
    client = Minio(endpoint,  #
                   access_key=access_key,  #
                   secret_key=secret_key,  #
                   secure=True,  #
                   http_client=urllib3.PoolManager(timeout=2)  #
                   )
    try:
        tmp_print('正在连接minio...')
        buckets = client.list_buckets()
        tmp_print(f'minio连接成功, bucket名: {str(buckets[0])}')
        return True, str(buckets[0]), client
    except Exception as e:
        if 'timed out' in str(e):
            tmp_print(f'连接超时, {e}')
        else:
            tmp_print(f'连接失败, {e}')
        return False, str(e), None

def download_obj(local_path, obj_name, progress=None):
    """
    从minio下载文件
    :param local_path:  本地路径
    :param obj_name:  object名称
    :param progress:  进度条
    """
    try:
        # 创建目录
        local_dir = os.path.dirname(local_path)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        client = Minio(endpoint, access_key=access_key, secret_key=secret_key, )
        client.fget_object(bucket_name, obj_name, local_path, progress=Progress())
        tmp_print(f"正在下载 {bucket_name} 到 {local_path}")
        return True
    except Exception as err:
        tmp_print(f'下载文件[{obj_name}]失败, {err}')
        return False

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
        tmp_print(f'minio获取列表[{obj_prefix}]失败, {e}')
        return None

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
        versions.append(int(str(objn).split('/')[-2]))
    new_version = max(versions)
    tmp_print(f'最新版本: {new_version}')
    return int(new_version)
