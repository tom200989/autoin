import shutil
import stat
import subprocess
import os
import time

from minio import Minio
from minio.error import S3Error

endpoint = 'minio.ecoflow.com:9000'
access_key = 'EQS4J84JGJCDYNENIMT1'
secret_key = '8Vgk11c9bDOpZPTJMexPLrxZpzEOqro+jZyAUh+a'
bucket_name = 'rnd-app-and-device-logs'
minio_config = 'minio_config.json'

minio_motherbox_root = 'autocase/android/motherbox/'  # motherbox的根目录 (注意, 要加一个`/`结尾,可能会有重复的前缀目录, 也会被搜索出来)
minio_boxhelper_root = 'autocase/android/boxhelper/'  # boxhelper的根目录 (注意, 要加一个`/`结尾,可能会有重复的前缀目录, 也会被搜索出来)

# 定义要打包的项目路径列表
project_paths = {  #
    'motherbox.exe': r'D:\project\python\autoin\case\motherbox',  # 母盒
    'boxhelper.exe': r'D:\project\python\autoin\case\boxhelper',  # 母盒辅助器
}

def __upload_minio(*args):
    minio_motherbox_x, motherbox_zip, minio_boxhelper_x, boxhelper_zip = args

    try:
        client = Minio(endpoint, access_key=access_key, secret_key=secret_key, )
        result = client.fput_object(bucket_name=bucket_name, object_name=minio_motherbox_x, file_path=motherbox_zip, num_parallel_uploads=1)
        print(f"正在上传{result.object_name}")
        result2 = client.fput_object(bucket_name=bucket_name, object_name=minio_boxhelper_x, file_path=boxhelper_zip, num_parallel_uploads=1)
        print(f"正在上传{result2.object_name}")
        time.sleep(1)
        print('上传完成')
    except Exception as err:
        print(err)

def __need_version():
    """
    压缩包版本号
    :return:
    """
    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=True)
    objects = client.list_objects(bucket_name, prefix=minio_motherbox_root, recursive=True)
    versions = []
    for obj in objects:
        versions.append(int(str(obj.object_name).split('/')[-2]))

    if len(versions) > 0:
        cur_max_version = max(versions)
        print('当前minio中最新版本号:', cur_max_version)
        print('将使用版本号:', cur_max_version + 1)
        return str(cur_max_version + 1)
    else:
        print('当前minio中无版本号')
        print('将使用版本号:1000')
        return '1000'

def del_rw(action, name, exc):
    """
    切换文件夹权限(管理员)
    :param action:
    :param name:
    :param exc:
    """
    os.chmod(name, stat.S_IWRITE)
    try:
        # 先解除占用
        # unoccupied(name)
        # 再删除文件夹
        os.remove(name)
    except Exception as error:
        print('文件夹被进程占用, 正在强制删除: ', error)
        os.popen(f'rd /s /q {name}')  # 如果当前文件夹被占用, 则强制删除

# ---------------------------------------------- 流程 ----------------------------------------------
def pack():
    # 为每个项目执行打包命令
    for project_fun, project_path in project_paths.items():
        try:
            print('即将打包:', project_fun)
            # 切换到项目目录
            print('切换到项目目录:', project_path)
            os.chdir(project_path)
            print('正在删除build文件夹')
            build_path = os.path.join(project_path, 'build')
            if os.path.exists(build_path) and os.path.isdir(build_path):
                shutil.rmtree(build_path, onerror=del_rw)
                print('build文件夹已删除')

            print('开始打包...')
            # 执行打包命令
            result = subprocess.run(['python', 'setup.py', 'build'], check=True)

            # 打印结果
            if result.returncode == 0:
                print(f'{project_path} 打包成功！')
            else:
                print(f'{project_path} 打包失败！返回码：{result.returncode}')

        except Exception as e:
            print(f'在项目 {project_path} 打包时出错：{e}')

    print('所有项目打包完成')

def zip_upload():
    """
    压缩并上传
    :return:
    """
    # 获取motherbox的minio当前版本
    zip_version = __need_version()
    # 压缩motherbox
    print('正在压缩motherbox')
    motherbox_build = os.path.join(project_paths['motherbox.exe'], 'build')
    motherbox_zip = os.path.join(project_paths['motherbox.exe'], f'motherbox_{zip_version}.zip')
    motherbox_without_ext,_ = os.path.splitext(motherbox_zip) # 去掉后缀
    shutil.make_archive(motherbox_without_ext, 'zip', motherbox_build)
    # 压缩boxhelper
    print('正在压缩boxhelper')
    boxhelper_build = os.path.join(project_paths['boxhelper.exe'], 'build')
    boxhelper_zip = os.path.join(project_paths['boxhelper.exe'], f'boxhelper.zip')
    boxhelper_without_ext,_ = os.path.splitext(boxhelper_zip) # 去掉后缀
    shutil.make_archive(boxhelper_without_ext, 'zip', boxhelper_build)
    # 返回需要上传到minio的参数
    minio_motherbox_x = minio_motherbox_root + f'{zip_version}/motherbox_{zip_version}.zip'
    minio_boxhelper_x = minio_boxhelper_root + f'boxhelper.zip'
    need_upload = minio_motherbox_x, motherbox_zip, minio_boxhelper_x, boxhelper_zip
    # 上传到minio
    __upload_minio(*need_upload)
    # 删除压缩包
    print(f'正在删除压缩包:{str(motherbox_zip)}')
    os.remove(motherbox_zip)
    print(f'正在删除压缩包:{str(boxhelper_zip)}')
    os.remove(boxhelper_zip)

""" ----------------------------------------------- pack ----------------------------------------------- """

# 执行打包
pack()
# 执行压缩并上传
zip_upload()
