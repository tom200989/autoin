from a01_input import *

choice_box = [f'自动化测试(V{motherbox_version})', '请选择:', [('0', '退出(exit)'), ('1', '执行脚本'), ('2', '调试工具')]]

def main():
    if not is_admin():
        tmp_print('[!] 当前软件未获得管理员权限')
        tmp_print('[+] 尝试绕过UAC认证...')
        try:
            current_dir = __file__
            cmd = '{} /k {} {}'.format(CMD, PYTHON_CMD, current_dir)
            bypass_uac(cmd)
            os.system(FOD_HELPER)
            sys.exit(0)
        except Exception as e:
            tmp_print('[!] 未能绕过UAR认证, 请右键以[管理员身份]运行该软件...')
            sys.exit(1)
    else:
        #这里添加我们需要管理员权限的代码
        tmp_print('[+] 当前是正以管理员权限运行!')
        box_seleted = choice_pancel(choice_box[0], choice_box[1], choice_box[2], fun_cancel=main)
        if box_seleted == '0':
            exit()
        elif box_seleted == '1':
            select_patch(func_cancel=main)
        elif box_seleted == '2':
            select_debug(fun_cancel=main)

        # 按任意键回到主菜单
        input('按任意键回到主菜单')
        main()

@DeprecationWarning
def main2():
    """
    方式2: 可以使用prompt_toolkit库(取代之前自己写的input_what)
    :return:
    """
    session = PromptSession()
    while True:
        text = session.prompt('>>> 输入指令([0]退出测试 / [1]执行脚本 / [2]调试工具): ')
        if text == '0':  # 退出
            exit()
            break
        elif text == '1':  # 脚本选项
            select_patch(func_cancel=main2)
        elif text == '2':  # 调试选项
            select_debug(fun_cancel=main2)

if __name__ == '__main__':
    main()
