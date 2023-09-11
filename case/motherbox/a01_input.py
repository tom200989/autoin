from b00_checknet import *
from b01_checkenvs import *

choice_patch = ['选择操作类型', '请选择:', [('0', '运行脚本'), ('1', '下载脚本')]]
choice_debug = ['选择调试功能', '请选择:', [('0', '检测网络'), ('1', '检测环境'), ('2', '安装环境'), ('3', '还原环境'), ('4', '更新母盒')]]

def select_patch(func_cancel):
    """
    选择脚本操作类型
    """
    # 脚本选择面板
    patch_seleted = choice_pancel(choice_patch[0], choice_patch[1], choice_patch[2], fun_cancel=func_cancel)
    if patch_seleted == '0':
        # todo 2023/9/7 运行脚本
        print('运行脚本')
    elif patch_seleted == '1':
        # todo 2023/9/7 下载脚本
        print('下载脚本')

def select_debug(fun_cancel):
    """
    选择调试类型
    @param fun_cancel: 当前面板下点击取消的回调函数
    """
    # 脚本选择面板
    debug_selected = choice_pancel(choice_debug[0], choice_debug[1], choice_debug[2], fun_cancel=fun_cancel)
    if debug_selected == '0':
        check_all_nets()
    elif debug_selected == '1':
        check_all_sys()
    elif debug_selected == '2':
        # todo 2023/9/7 安装环境
        print('安装环境')
    elif debug_selected == '3':
        # todo 2023/9/7 还原环境
        print('还原环境')
    elif debug_selected == '4':
        # todo 2023/9/7 更新母盒
        print('更新母盒')