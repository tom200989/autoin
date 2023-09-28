import sys
sys.path.append(r'D:\project\python\autoin\venv\Lib\site-packages')  # 这句话一定要加(路径是安装cz_freeze时的python路径)
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI' # 无窗口程序

temp_folder = r'D:\lock_tmp\build'

# 可执行文件的信息
executables = [Executable(r"D:\project\python\autoin\demo\lockscreen\lockscreen.py")]
# 构建选项
build_options = {  #
    "packages": [  #
        'autoit', 'time', 'sys', 'threading',  #
        'keyboard', 'pyautogui', 'pynput', 'os', 'pystray', 'PIL',  #
        'win32con','ctypes',  #
        'win32gui','pywintypes','win32api',  # 导入win32gui的库时, 要一并要把它内部的包pywintypes一并导入进来,否则闪退

    ],  # 全部需要导入的包

    "excludes": [],  # 需要排除的包
    "include_files": [  #
        (r'D:\project\python\autoin\demo\lockscreen\lock.png', 'lock.png')],  # 需要包含的其他文件
    'build_exe': temp_folder,  # 输出到临时文件夹 (此处修改是需要同步修改0000_批量打包lock.py中的同名变量)
}

# 创建setup
setup(  #
    name="lockscreen",  #
    version="1.0",  #
    description="use to do not lock screen",  #
    options={"build_exe": build_options},  #
    executables=executables  #
)
