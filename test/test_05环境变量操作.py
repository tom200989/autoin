import os
import winreg

def backup_path_to_file(backup_file_path=r'D:\autocase\sys_env\sys_env.txt'):
    """
    备份当前环境变量
    """
    # 创建目录
    if not os.path.exists(os.path.dirname(backup_file_path)):
        os.makedirs(os.path.dirname(backup_file_path))

    # 打开注册表，获取环境变量
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
        original_path = winreg.QueryValueEx(key, 'Path')[0]

    # 备份到文件
    with open(backup_file_path, 'w') as file:
        file.write(original_path)

def prepend_to_path(new_dirs):
    """
    在原有环境变量前添加新路径
    """
    # 打开注册表，获取环境变量
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_SET_VALUE) as key:
        original_path = winreg.QueryValueEx(key, 'Path')[0]

        # 把新路径添加到原始路径前面
        new_path = ';'.join(new_dirs) + ';' + original_path

        # 更新环境变量
        winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)

def restore_path_from_file(backup_file_path=r'D:\autocase\sys_env\sys_env.txt'):
    """
    从备份文件还原环境变量
    """
    if not os.path.exists(backup_file_path):
        print('备份文件不存在，无法还原。')
        return

    # 从备份文件中读取环境变量
    with open(backup_file_path, 'r') as file:
        original_path = file.read()

    # 打开注册表，设置环境变量
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, original_path)

    print('环境变量已还原。')
