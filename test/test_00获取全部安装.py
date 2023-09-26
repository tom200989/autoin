import re

import winapps

# 判断chrome是否有安装
target_exe = 'Node.js'
exe = [app.name for app in winapps.search_installed(target_exe)]
if exe and len(exe) > 0:
    for ex in winapps.list_installed():
        # print(ex)
        exe_name = str(ex.name).lower()
        target_exe = target_exe.lower()
        if exe_name in target_exe or target_exe in exe_name:
            print(ex.name)
            print(ex.install_location)
            print(ex.install_source)
            print(ex.version)
            print(ex.uninstall_string)

# chrome_version = '200.112'
# is_match = bool(re.match(r'^(10[89]|1[1-9][0-9])\.', chrome_version))
# print(is_match)

# def check_exe(target_exe):
#     """
#     获取指定exe的安装信息
#     :return: [文件名, 安装路径, 版本, 卸载命令]
#     """
#     exe = [app.name for app in winapps.search_installed(target_exe)]
#     if exe and len(exe) > 0:
#         target_exe = target_exe.lower()
#         for ex in winapps.list_installed():
#             exe_name = str(ex.name).lower()
#             if exe_name in target_exe or target_exe in exe_name:
#                 # 文件名, 安装路径, 版本, 卸载命令
#                 exe_name = ex.name
#                 exe_install_path = ex.install_location
#                 if exe_install_path == '' or exe_install_path is None:exe_install_path = str(ex.install_source)
#                 exe_version = ex.version
#                 exe_uninstall_string = ex.uninstall_string
#                 return_info = [exe_name, exe_install_path, exe_version, exe_uninstall_string]
#                 return return_info
#
#     return []
#
# print(check_exe('Node.js'))
pass
