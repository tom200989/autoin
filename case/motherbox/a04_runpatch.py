from b00_checknet import *
from b01_checkenvs import *

# todo 2023/10/10 查找本地下载的脚本目录(列表)
# todo 2023/10/10 用户选择脚本目录
# todo 2023/10/10 安装脚本目录里的apk文件到手机
# todo 2023/10/10 执行脚本目录里的exe文件

def run_patch():
    # 检查网络
    is_network_pass = check_all_nets()
    # 检查环境
    is_sys_pass = check_all_sys()
    # 如果网络或者环境变量不通过, 则不执行
    if not is_network_pass:
        tmp_print('x 网络检查不通过, 请检查网络')
        return False
    if not is_sys_pass:
        tmp_print('x 环境检查不通过, 请检查环境')
        return False
    # 检查是否有脚本目录以及该目录下是否有脚本目录
    if not os.path.exists(patch_root):
        tmp_print('x 此前没有下载过任何, 请先回到菜单下载脚本')
        return False
    # 检查脚本根目录下是否有脚本子目录
    patch_cdirs = find_cdirs_prefix(patch_root, patch_cdir_prefix)
    if patch_cdirs is None:
        tmp_print('x 脚本包没有可执行脚本, 请先回到菜单下载脚本')
        return False
    # todo 2023/10/10 一切通过后列举出可执行脚本
    pass
