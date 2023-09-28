import winreg
# 这个添加方法有效, 能添加到系统环境变量中
def add_to_system_path(new_paths):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_READ | winreg.KEY_WRITE)
    original_path = winreg.QueryValueEx(key, 'Path')[0]

    # 检查新添加的路径是否已经在原始路径中
    paths = original_path.split(";")
    for new_path in new_paths:
        if new_path not in paths:
            paths.append(new_path)

    # 更新环境变量
    new_path_str = ";".join(paths)
    winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path_str)
    winreg.CloseKey(key)

# 示例使用
new_paths = ['D:\\autocase\\sdk', 'D:\\autocase\\jdk']
add_to_system_path(new_paths)
