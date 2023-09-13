import platform
import sys

def get_pack_dirname():
    """
    获取打包后的目录名
    :return:
    """
    platform_name = platform.system().lower()
    if 'win' in platform_name: platform_name = 'win'
    architecture = platform.machine().lower()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    directory_name = f"exe.{platform_name}-{architecture}-{python_version}"
    return directory_name

print(f"Generated directory name: {get_pack_dirname()}")
print(sys.platform)
