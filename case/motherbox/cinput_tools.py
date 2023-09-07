from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import checkboxlist_dialog

choice_patch = ['选择操作类型', '请选择:', [('0', '运行脚本'), ('1', '下载脚本')]]
choice_debug = ['选择调试功能', '请选择:', [('0', '检测网络'), ('1', '环境变量'), ('2', '安装环境'), ('3', '还原环境'), ('4', '更新母盒')]]

def get_local_case():
    """
    获取本地脚本
    """
    # todo 2023/9/7 读取本地的脚本包
    pass

def __choice__(title, text, items):
    """
    选择
    """
    selects = checkboxlist_dialog(title=title, text=text, values=items).run()
    return selects[0]

def select_patch():
    """
    选择脚本操作类型
    """
    # 脚本选择面板
    patch_seleted = __choice__(choice_patch[0], choice_patch[1], choice_patch[2])
    if patch_seleted == '0':
        # todo 2023/9/7 运行脚本
        print('运行脚本')
    elif patch_seleted == '1':
        # todo 2023/9/7 下载脚本
        print('下载脚本')

def select_debug():
    """
    选择调试类型
    """
    # 脚本选择面板
    debug_selected = __choice__(choice_debug[0], choice_debug[1], choice_debug[2])
    if debug_selected == '0':
        # todo 2023/9/7 检测网络
        print('检测网络')
    elif debug_selected == '1':
        # todo 2023/9/7 环境变量
        print('环境变量')
    elif debug_selected == '2':
        # todo 2023/9/7 安装环境
        print('安装环境')
    elif debug_selected == '3':
        # todo 2023/9/7 还原环境
        print('还原环境')
    elif debug_selected == '4':
        # todo 2023/9/7 更新母盒
        print('更新母盒')


