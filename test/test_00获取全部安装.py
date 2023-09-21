import re

import winapps

# 判断chrome是否有安装
target_exe = 'google chrome'
exe = [app.name for app in winapps.search_installed(target_exe)]
if exe and len(exe) > 0:
    for ex in winapps.list_installed():
        exe_name = str(ex.name).lower()
        if exe_name in target_exe or target_exe in exe_name:
            print(ex.name)
            print(ex.install_location)
            print(ex.version)
            print(ex.uninstall_string)

chrome_version = '200.112'
is_match = bool(re.match(r'^(10[89]|1[1-9][0-9])\.', chrome_version))
print(is_match)
