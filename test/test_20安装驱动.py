import os
import re
import subprocess

def install_driver(driver_path, driver_name):
    os.chdir(driver_path)
    subprocess.run(['PnPUtil', '/add-driver', f'{driver_name}', '/install'], check=True)



def uninstall_driver(driver_name):
    """
    卸载驱动
    :param driver_name:
    """
    # 执行PnPUtil命令并获取输出结果
    cmd_output = subprocess.check_output('PnPUtil /enum-drivers', shell=True, text=True)
    print(cmd_output)
    # 把多行字符串拆成行列表
    lines = cmd_output.split("\n")
    # 初始化发布名称
    publish_name = None
    # 遍历行列表
    for i, line in enumerate(lines):
        # 如果找到了目标字符串
        if f"{driver_name}" in line:
            # 取前一行，获取发布名称
            publish_name = lines[i - 1].split(":")[1].strip()
            break

    # 输出结果
    if publish_name:
        print(f"找到匹配项，发布名称为: {publish_name}")
        # 开始卸载
        subprocess.run(f"PnPUtil /delete-driver {publish_name} /uninstall", shell=True, check=True)
        print("卸载成功")
        return True
    else:
        print("未找到匹配项")
        return False

uninstall_driver('silabser')
