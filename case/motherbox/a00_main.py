from cinput_tools import *

def main():
    session = PromptSession()
    while True:
        text = session.prompt('>>> 输入指令([0]退出测试 / [1]执行脚本 / [2]调试功能): ')
        if text == '0':  # 退出
            exit()
            break
        elif text == '1':  # 脚本选项
            select_patch()
            break
        elif text == '2':  # 调试选项
            select_debug()
            break

if __name__ == '__main__':
    main()
