import os
import winreg

env_reg = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
sys_env_txt = 'D:/autocase/sys_env/sys_env.txt'

def backup_envs():
    """
    备份当前环境变量
    """
    try:
        # 创建目录
        print('正在备份环境变量...')
        if not os.path.exists(os.path.dirname(sys_env_txt)):
            os.makedirs(os.path.dirname(sys_env_txt))
        # 打开注册表，获取环境变量
        print('正在获取环境变量...')
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_reg) as key:
            original_path = winreg.QueryValueEx(key, 'Path')[0]
        # 备份到文件
        print('正在备份环境变量到文件...')
        with open(sys_env_txt, 'w') as file:
            file.write(original_path)
        print(f'环境变量备份完成: {sys_env_txt}')
        return True
    except Exception as e:
        print(f'环境变量备份失败, {e}')
        return False

def add_need_envs():
    """
    在原有环境变量前添加新路径
    """
    try:
        print('正在添加环境变量...')
        # 需要配置的环境变量路径
        test_paths = ['D:/autocase/jdk/bin'] # 其他自己补充
        print(f'正在配置所需的环境变量...')
        # 打开注册表，获取环境变量
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_reg, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            original_path = winreg.QueryValueEx(key, 'Path')[0]
            # 把新路径添加到原始路径前面
            new_path = ';'.join(test_paths) + ';' + original_path
            # # 更新环境变量
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
        print('环境变量配置完成。')
        return True
    except Exception as e:
        print(f'环境变量配置失败, {e}')
        return False

def restore_envs():
    """
    从备份文件还原环境变量
    """
    try:
        if not os.path.exists(sys_env_txt):
            print('备份文件不存在，无法还原。')
            return
        print('正在还原环境变量...')
        # 从备份文件中读取环境变量
        with open(sys_env_txt, 'r') as file:
            original_path = file.read()
        print('正在还原环境变量到注册表...')
        # 打开注册表，设置环境变量
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_reg, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, original_path)
        print(f'环境变量已从 <{sys_env_txt}> 还原')
        print(get_cur_envs())
        return True
    except Exception as e:
        print(f'环境变量还原失败, {e}')
        return False
