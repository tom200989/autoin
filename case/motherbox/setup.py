import sys
sys.path.append(r'D:\project\python\autoin\venv\Lib\site-packages')  # 这句话一定要加(路径是安装cz_freeze时的python路径)
from cx_Freeze import setup, Executable

# 可执行文件的信息
executables = [Executable(r"D:\project\python\autoin\case\motherbox\a00_motherbox.py")]
# 构建选项
build_options = {  #
    "packages": [  #
        'shutil', 'psutil',  # a02_updatebox.py
        'subprocess', 'request', 're',  # b00_checknet.py
        'winapps',  # b01_checkenvs.py
        'minio',  # cminio_tools.py
        'datetime', 'inspect', 'os', 'socket', 'stat', 'sys', 'time','prompt_toolkit'  # ctmp_tools.py
    ],  # 全部需要导入的包

    "excludes": [],  # 需要排除的包
    "include_files": [#
        # (r'D:\project\python\autouim\ef_app_autotest\temp\minio_upload\tmp_tools.py', 'tmp_tools.py') #
    ]  # 需要包含的其他文件
}

# 创建setup
setup(  #
    name="motherbox",  #
    version="1.0",  #
    description="Description of Your Script",  #
    options={"build_exe": build_options},  #
    executables=executables  #
)
