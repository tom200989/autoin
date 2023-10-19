from collections import OrderedDict

WIFI_LISTS = {  #
    'WIFI1': ['EF-aging', 'ecoflow@2023'],  # 创智云城
    # 'WIFI2': ['Redmi_huan', '87654321'],  # IOT 测试
    # 'WIFI3': ['HUAWEI-91B1SI', '123456789'],  # 波顿9F
}

ssid = 'aaa'
pwd = 'bbb'

# 把ssid, pwd添加到WIFI_LISTS的第一个位置,但不覆盖原来的值
new = OrderedDict({'xxx': [ssid, pwd]})
new.update(WIFI_LISTS)
WIFI_LISTS = new
print(dict(WIFI_LISTS))

new = OrderedDict({'yyy': ['ccc', 'ddd']})
new.update(WIFI_LISTS)
WIFI_LISTS = new
print(dict(WIFI_LISTS))
