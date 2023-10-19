# import json
# caseui_config_path = r'D:\autocase\config\caseui_config.txt'
# with open(caseui_config_path, 'r', encoding='utf-8') as f:
#     caseui_config = json.loads(f.read())  # 读取,转为json
#
#     print(type(caseui_config))  # <class 'list'>
#     print(caseui_config)
#     # 转换为字典
#     d = {}
#     for item in caseui_config:
#         d.setdefault(item['key'], item['value'])
#
# count = "10"
#
# for i in count:
#     print(type(i))
#     print(i)

with open(r'D:\autocase\config\caseui_config.txt', encoding='gbk', mode='r') as file:
    lines = file.readlines()
    print(lines)
