import os
import platform
import sys

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

def get_pack_dirname():
    """
    获取打包后的目录名(exe.win-amd64-3.11)
    """
    platform_name = platform.system().lower()
    if 'win' in platform_name: platform_name = 'win'
    architecture = platform.machine().lower()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    directory_name = f"exe.{platform_name}-{architecture}-{python_version}"
    return directory_name

# 临时文件夹
temp_folder = rf'D:\autocase_tmp\build\{get_pack_dirname()}'
sys.path.append(os.path.join(get_project_rootdir(),'venv','Lib','site-packages'))  # 这句话一定要加(路径是安装cz_freeze时的python路径)
from cx_Freeze import setup, Executable
from zboxtools import boxhelper_version

# 可执行文件的信息
executables = [Executable(os.path.join(get_project_rootdir(),'case','boxhelper','a00_boxhelper.py'))]
# 构建选项
build_options = {  #
    "packages": [  #
        'shutil', 'psutil',  # a00_boxhelper.py
        'subprocess', 'requests', 're',  # a01_nettools.py
        'minio',  # a02_miniotools.py
        'datetime', 'inspect', 'os', 'socket', 'stat', 'sys', 'time'  # zboxtools.py
    ],  # 全部需要导入的包

    "excludes": [],  # 需要排除的包
    "include_files": [  #
        (r'D:\project\python\autoin\autoin\demo\handle', 'handle') # 检测进程是否被占用
    ],  # 需要包含的其他文件
    'build_exe': temp_folder,  # 输出到临时文件夹 (此处修改是需要同步修改0000_批量打包box.py中的同名变量)
}

# 创建setup
setup(  #
    name="boxhelper",  #
    version=f"{boxhelper_version}",  #
    description="Description of Your Script",  #
    options={"build_exe": build_options},  #
    executables=executables  #
)
