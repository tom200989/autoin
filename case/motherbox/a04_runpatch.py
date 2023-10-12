from b00_checknet import *
from b01_checkenvs import *

# todo 2023/10/10 查找本地下载的脚本目录(列表)
# todo 2023/10/10 用户选择脚本目录
# todo 2023/10/10 安装脚本目录里的apk文件到手机
# todo 2023/10/10 执行脚本目录里的exe文件

# todo 2023/10/11 点击取消的操作

def do_exe(pathc_dir):
    # 查看指定目录下是否有apk文件 且 只有一个apk文件 且 apk文件名是ecoflow_oversea.apk
    files = os.listdir(pathc_dir)  # 获取指定目录下的所有文件
    apk_files = [f for f in files if f.endswith(".apk")]  # 使用列表解析找出所有以".apk"结尾的文件
    if len(apk_files) != 1:  # 检查是否只有一个APK文件且文件名为"ecoflow_oversea.apk"
        tmp_print('x apk文件检查不通过, 请检查脚本目录下是否有且只有一个apk文件')
        return False
    if apk_files[0] != 'ecoflow_oversea.apk':
        tmp_print('x apk文件检查不通过, 当前apk文件不是[ecoflow_oversea]的压测版本')
        return False

    # 查看是否有exe文件 且 是否以`auto`开头
    exe_files = [f for f in files if f.endswith(".exe")]  # 使用列表解析找出所有以".exe"结尾的文件
    if len(exe_files) != 1:  # 检查是否只有一个APK文件且文件名为"ecoflow_oversea.apk"
        tmp_print('x exe文件检查不通过, 请检查脚本目录下是否有且只有一个exe文件')
        return False
    if not exe_files[0].startswith('auto'):
        tmp_print('x exe文件检查不通过, 当前exe文件不是[自动化专项]压测版本')
        return False

    # 安装apk文件
    # todo 2023/10/12 需调试
    adb_command = f"adb install -r -t {pathc_dir}\\{apk_files[0]}"
    tmp_print(f'安装apk文件: {adb_command}')
    result = subprocess.check_output(adb_command, shell=True, stderr=subprocess.STDOUT, encoding='utf-8')
    tmp_print(result)
    time.sleep(8)

    # 执行exe文件
    # todo 2023/10/12 需调试
    exe_command = f"{pathc_dir}\\{exe_files[0]}"
    tmp_print(f'执行exe文件: {exe_command}')
    patch_exe = subprocess.Popen([exe_command], creationflags=subprocess.CREATE_NEW_CONSOLE)
    tmp_print("当前脚本进程ID:", patch_exe.pid)

def run_patch(func_cancel):
    """
    运行脚本
    :param func_cancel:  当前面板下点击取消的回调函数
    """

    # # 检查网络
    # is_network_pass = check_all_nets()
    # # 检查环境
    # is_sys_pass = check_all_sys()
    # # 如果网络或者环境变量不通过, 则不执行
    # if not is_network_pass:
    #     tmp_print('x 网络检查不通过, 请检查网络')
    #     return False
    # if not is_sys_pass:
    #     tmp_print('x 环境检查不通过, 请检查环境')
    #     return False
    # # 检查是否有脚本目录以及该目录下是否有脚本目录
    # if not os.path.exists(patch_root):
    #     tmp_print('x 此前没有下载过任何, 请先回到菜单下载脚本')
    #     return False

    # 检查脚本根目录下是否有脚本子目录 {'p_ble_conn_delta': 'D:\\autocase\\patch\\p_ble_conn_delta',}
    patch_cdirs_dict = find_cdirs_prefix(patch_root, patch_cdir_prefix)
    if patch_cdirs_dict is None:
        tmp_print('x 脚本包没有可执行脚本, 请先回到菜单下载脚本')
        return False
    # 取出所有key, 每个key组成一个元祖 [(0, 'p_bleverify'),(1,'p_ota')] 并把元祖存放到一个列表中
    patch_cdirs_list = [(str(index), cdirname) for index, cdirname in enumerate(list(patch_cdirs_dict.keys()))]
    # 进入面板选择 '0'
    choice_patch = ['选择要执行的脚本', '请选择:', patch_cdirs_list]
    patch_seleted = choice_pancel(choice_patch[0], choice_patch[1], choice_patch[2], fun_cancel=func_cancel )
    tmp_print(f'当前选中: {patch_seleted} -> {patch_cdirs_list[int(patch_seleted)]}')
    # 得到绝对路径 'D:\\autocase\\patch\\p_ble_conn_delta'
    local_path = "None"
    for tunple in patch_cdirs_list:
        if patch_seleted in tunple[0]:
            local_path = patch_cdirs_dict[tunple[1]]
            break
    tmp_print(f'脚本地址: {local_path}')
    # 地址存在, 则执行脚本
    if os.path.exists(local_path):
        do_exe(local_path)
    else:
        tmp_print(f'x 脚本目录不存在: {local_path}')
        return False

