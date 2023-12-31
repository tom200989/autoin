
import platform
import shutil
import stat
import subprocess
import os
import sys
import time
import tempfile

import psutil
import urllib3
from minio import Minio
from minio.error import S3Error
from case.motherbox.ctmp_tools import motherbox_version
from case.boxhelper.zboxtools import boxhelper_version

def get_project_rootdir():
    """
    获取工程的根目录
    :return:  工程根目录
    """
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 从当前目录开始向上查找
    while True:
        # 获取当前路径下的所有文件和目录
        dirs = os.listdir(current_dir)
        # 检查是否存在"venv"目录
        if 'venv' in dirs:
            return current_dir
        # 向上移动一个目录
        parent_path = os.path.dirname(current_dir)
        # 如果已到达文件系统根目录，则停止
        if parent_path == current_dir:
            return None
        current_dir = parent_path

endpoint = 'minio.ecoflow.com:9000'
access_key = 'EQS4J84JGJCDYNENIMT1'
secret_key = '8Vgk11c9bDOpZPTJMexPLrxZpzEOqro+jZyAUh+a'
bucket_name = 'rnd-app-and-device-logs'
minio_config = 'minio_config.json'

minio_motherbox_root = 'autocase/android/motherbox/'  # motherbox的根目录 (注意, 要加一个`/`结尾,可能会有重复的前缀目录, 也会被搜索出来)
minio_boxhelper_root = 'autocase/android/boxhelper/'  # boxhelper的根目录 (注意, 要加一个`/`结尾,可能会有重复的前缀目录, 也会被搜索出来)

# 定义要打包的项目路径列表

project_paths = {  #
    'motherbox.exe': os.path.join(get_project_rootdir(), 'case', 'motherbox'),  # 母盒
    'boxhelper.exe': os.path.join(get_project_rootdir(), 'case', 'boxhelper'),  # 母盒辅助器
}
# 临时文件夹(用于存入打包后的文件) - 注意, 此处修改需要同步修改setup.py中的同名变量
temp_folder = r'D:\autocase_tmp'

def __upload_minio(*args):
    minio_motherbox_x, motherbox_zip, minio_boxhelper_x, boxhelper_zip = args

    try:
        client = Minio(endpoint, access_key=access_key, secret_key=secret_key, http_client=urllib3.PoolManager(timeout=2))
        result = client.fput_object(bucket_name=bucket_name, object_name=minio_motherbox_x, file_path=motherbox_zip, num_parallel_uploads=1)
        print(f"正在上传{result.object_name}, (版本: {motherbox_version})")
        result2 = client.fput_object(bucket_name=bucket_name, object_name=minio_boxhelper_x, file_path=boxhelper_zip, num_parallel_uploads=1)
        print(f"正在上传{result2.object_name}, (版本: {boxhelper_version})")
        time.sleep(1)
        print('上传完成')
    except Exception as err:
        print(err)

def __need_version():
    """
    自动从minio获取版本号并自增+1
    :return:
    """
    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=True, http_client=urllib3.PoolManager(timeout=2))
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
        time.sleep(2)
        os.remove(name)
    except Exception as error:
        print('文件夹被进程占用, 正在强制删除: ', error)
        os.popen(f'rd /s /q {name}')  # 如果当前文件夹被占用, 则强制删除

def restart_adb():
    try:
        subprocess.run(["adb", "kill-server"], universal_newlines=True, encoding='utf-8')
        subprocess.run(["adb", "start-server"], universal_newlines=True, encoding='utf-8')
        print("ADB服务已重启")
        return True
    except Exception as e:
        print(f"x 重启ADB服务时出错: {e}")
        return False

def check_adb_install():
    try:
        cmd_output = subprocess.check_output(["adb", "version"], universal_newlines=True, encoding='utf-8')
        if "Android Debug Bridge version" in cmd_output:
            print("√ ADB已安装")
            return True
        else:
            print("x ADB未安装")
            return False
    except Exception as e:
        print(f"x 检查ADB安装时出错: {e}")
        return False

def kill_exe(_exe):
    """
    关闭指定进程
    java.exe: sonar.bat进程
    pgAdmin4.exe: 数据库进程
    """
    print(f'正在关闭{_exe}....')
    for proc in psutil.process_iter(['pid', 'name']):
        # 检查进程名
        if proc.info['name'] == _exe:
            print(f'找到进程{_exe},正在关闭...')
            # 杀掉进程
            try:
                proc.kill()
            except Exception as error:
                if 'NoSuchProcess' in str(error): print('该进程已关闭')

    print(f'{_exe}已全部关闭!')

# ---------------------------------------------- 流程 ----------------------------------------------
def pack():
    if check_adb_install():
        restart_adb()

    # 结束进程
    print('正在结束进程...')
    for project_fun, project_path in project_paths.items():
        kill_exe(project_fun)

    # 为每个项目执行打包命令
    for project_fun, project_path in project_paths.items():
        try:
            # 清空临时文件夹
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder, onerror=del_rw)
                print('临时文件夹已删除')
            # 重新创建临时文件夹
            print('正在重新创建临时文件夹')
            os.makedirs(temp_folder)
            print('即将打包:', project_fun)
            # 切换到项目目录
            print('切换到项目目录:', project_path)
            os.chdir(project_path)
            print('正在删除工程中build文件夹')
            build_path = os.path.join(project_path, 'build')
            if os.path.exists(build_path) and os.path.isdir(build_path):
                shutil.rmtree(build_path, onerror=del_rw)
                print('工程中的build文件夹已删除')
            # 再次检查build文件夹是否存在
            if os.path.exists(build_path) and os.path.isdir(build_path):
                print('工程中的build文件夹删除失败, 请手动删除后重试!')
                break
            else:
                print('开始打包...')
                # 执行打包命令(打包到临时文件夹)
                result = subprocess.run(['python', 'setup.py', 'build'], check=True)

                # 打印结果
                if result.returncode == 0:
                    print(f'{project_path} 打包成功！')
                else:
                    print(f'{project_path} 打包失败！返回码：{result.returncode}')

                # 拷贝临时文件夹的内容到项目目录下
                print('正在拷贝临时文件夹的内容到项目目录下')
                shutil.copytree(os.path.join(temp_folder, 'build'), os.path.join(project_path, 'build'))

        except Exception as e:
            print(f'在项目 {project_path} 打包时出错：{e}')

    print('所有项目打包完成')

def zip_upload():
    """
    压缩并上传
    :return:
    """
    # 方案1: 获取motherbox的minio当前版本
    # zip_version = __need_version()
    # 方案2: 获取当前母盒版本
    # 压缩motherbox
    print(f'正在压缩:motherbox -> 版本: {motherbox_version}')
    # 先创建一个临时目录
    temp_dir = tempfile.mkdtemp()
    # 拷贝build到临时目录
    shutil.copytree(os.path.join(project_paths['motherbox.exe'], 'build'), os.path.join(temp_dir, 'build'))
    # 压缩包路径(打包的父目录下)
    motherbox_zip = os.path.join(project_paths['motherbox.exe'], f'motherbox_{motherbox_version}.zip')
    motherbox_without_ext, _ = os.path.splitext(motherbox_zip)  # 去掉后缀
    shutil.make_archive(motherbox_without_ext, 'zip', temp_dir)
    # 清空并删除临时目录
    shutil.rmtree(temp_dir, onerror=del_rw)

    # 压缩boxhelper
    print(f'正在压缩: boxhelper -> 版本: {boxhelper_version}')
    # 先创建一个临时目录
    temp_dir = tempfile.mkdtemp()
    # 拷贝build到临时目录
    shutil.copytree(os.path.join(project_paths['boxhelper.exe'], 'build'), os.path.join(temp_dir, 'build'))
    # 压缩包路径(打包的父目录下)
    boxhelper_zip = os.path.join(project_paths['boxhelper.exe'], f'boxhelper.zip')
    boxhelper_without_ext, _ = os.path.splitext(boxhelper_zip)  # 去掉后缀
    shutil.make_archive(boxhelper_without_ext, 'zip', temp_dir)
    # 清空并删除临时目录
    shutil.rmtree(temp_dir, onerror=del_rw)

    # 返回需要上传到minio的参数
    minio_motherbox_x = minio_motherbox_root + f'{motherbox_version}/motherbox_{motherbox_version}.zip'
    minio_boxhelper_x = minio_boxhelper_root + 'boxhelper.zip'
    need_upload = minio_motherbox_x, motherbox_zip, minio_boxhelper_x, boxhelper_zip
    # 上传到minio
    __upload_minio(*need_upload)
    # 删除压缩包
    print(f'正在删除压缩包:{str(motherbox_zip)}, (版本: {motherbox_version})')
    time.sleep(2)
    os.remove(motherbox_zip)
    print(f'正在删除压缩包:{str(boxhelper_zip)}, (版本: {boxhelper_version})')
    time.sleep(2)
    os.remove(boxhelper_zip)

""" ----------------------------------------------- pack ----------------------------------------------- """

# 执行打包
pack()
# 执行压缩并上传
zip_upload()
pass

