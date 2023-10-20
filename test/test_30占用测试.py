def filter_info(text):
    """
    查询文件是否被占用
    """

    # 检测是否有 "No matching handles found" -- 出现该字符表示文件未被占用
    if "No matching handles found" in text:
        return False, "文件未被占用"

    # 过滤出含有exe的全部行
    lines = [line for line in text.splitlines() if ".exe" in line]
    # 提取出字符串`pid`前的字符(如:winrdlv3.exe) 以及提取出字符串`pid`和`type`之间的字符(如:9408   type: 9408)
    exes_pids = {}
    for line in lines:
        # 提取出字符串`pid`前的字符(如:winrdlv3.exe)
        exe_name = line.split('pid')[0].strip()
        # 提取出字符串`pid`和`type`之间的字符(如:9408   type: 9408)
        pid=line[line.find('pid:')+len('pid:'):line.find('type')].strip()
        # 填入字典
        exes_pids[exe_name] = pid

    return False, exes_pids

text1 = """Nthandle v5.0 - Handle viewer
Copyright (C) 1997-2022 Mark Russinovich
Sysinternals - www.sysinternals.com

No matching handles found.

None
"""

# 例子
text2 = """Nthandle v5.0 - Handle viewer
Copyright (C) 1997-2022 Mark Russinovich
Sysinternals - www.sysinternals.com

winrdlv3.exe       pid: 9408   type: File          1D30: D:\autocase\patch\p_huayan_20231020100105.zip

None
"""


print(filter_info(text1))

print(filter_info(text2))
