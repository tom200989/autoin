import re

import winapps

# 判断chrome是否有安装
target_exe = 'google chrome'
exe = [app.name for app in winapps.search_installed(target_exe)]
if exe and len(exe) > 0:
    for ex in winapps.list_installed():
        # print(ex)
        exe_name = str(ex.name).lower()

#         if exe_name in target_exe or target_exe in exe_name:
#             print(ex.name)
#             print(ex.install_location)
#             print(ex.version)
#             print(ex.uninstall_string)
#
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

# 否则先卸载再安装
if len(node_infos)>0:
    # 先卸载
    tmp_print('正在卸载 Node.js...')
    # 在node_infos中查找卸载命令(此处的索引可能会随着项目的迭代而变化)
    uninstall_cmd = node_infos[3]
    # 修改指令参数 (把/I修改为/x, 后边跟随/q以静默卸载)
    uninstall_cmd = uninstall_cmd.replace('/I', '/x').replace('/i', '/x')+ ' /q'
    tmp_print(uninstall_cmd)
    # 执行卸载命令, 先卸载
    subprocess.run(uninstall_cmd, shell=True)
    time.sleep(5)
    tmp_print('Node.js 卸载完成')
