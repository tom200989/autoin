from a02_updatebox import *
from a03_installenv import *
from a04_runpatch import *
from a05_downpatch import *
from a06_pullxlog import *

choice_patch = ['选择操作类型', '请选择:', [('0', '运行脚本'), ('1', '下载脚本'), ('2', '删除脚本'), ('3', '导出手机日志'), ('4', '导出手机截图')]]
choice_debug = ['选择调试功能', '请选择:', [('0', '检测网络'), ('1', '检测环境'), ('2', '安装环境'), ('3', '还原系统变量'), ('4', '更新母盒')]]

def select_patch(func_cancel):
    """
    选择脚本操作类型
    """
    # 脚本选择面板
    patch_seleted = choice_pancel(choice_patch[0], choice_patch[1], choice_patch[2], fun_cancel=func_cancel)
    if patch_seleted is None:
        tmp_print('patch_seleted: 默认为 0')
        patch_seleted = '0'
    if str(patch_seleted) == '0':
        # 返回上一级
        print('选择运行脚本')
        run_patch(back_func(select_patch, func_cancel), 'run')  # 运行脚本

    elif str(patch_seleted) == '1':
        print('选择下载脚本')
        downpatch(back_func(select_patch, func_cancel))  # 下载脚本

    elif str(patch_seleted) == '2':
        print('选择删除脚本')
        run_patch(back_func(select_patch, func_cancel), 'del')  # 删除脚本

    elif str(patch_seleted) == '3':  # 导出手机日志
        print('选择导出手机日志')
        pull_wholog('xlog')
        pass

    elif str(patch_seleted) == '4':  # 导出手机截图
        print('选择导出手机截图')
        pull_wholog('macut')

def select_debug(fun_cancel):
    """
    选择调试类型
    @param fun_cancel: 当前面板下点击取消的回调函数
    """
    # 脚本选择面板
    debug_selected = choice_pancel(choice_debug[0], choice_debug[1], choice_debug[2], fun_cancel=fun_cancel)
    if debug_selected is None:
        tmp_print('debug_selected 为None: 默认为 0')
        debug_selected = '0'
    if str(debug_selected) == '0':  # 检查网络
        check_all_nets()
    elif str(debug_selected) == '1':  # 检查环境
        check_all_sys()
    elif str(debug_selected) == '2':  # 安装环境
        install_envs()
    elif str(debug_selected) == '3':  # 还原环境
        restore_envs()
    elif str(debug_selected) == '4':  # 更新母盒
        update_box()
