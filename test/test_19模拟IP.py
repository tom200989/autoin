import requests

# 待测试的代理IP列表
PROXIES = [
    'http://10.10.145.17:49155',
    'http://10.20.125.10',
    'http://10.20.125.11',
    # ... 更多代理IP
]

# 用于测试的目标网站
TEST_URL = 'http://www.google.com'

# 存放可用代理的列表
valid_proxies = []

def check_proxy(proxy):
    """
    检查代理是否可用
    """
    proxies = {
        'http': proxy,
        'https': proxy,
    }
    try:
        response = requests.get(TEST_URL, proxies=proxies, timeout=5)
        if response.status_code == 200:
            print(f"代理可用：{proxy}")
            valid_proxies.append(proxy)
        else:
            print(f"代理不可用（状态码：{response.status_code}）：{proxy}")
    except Exception as e:
        print(f"代理不可用（异常）：{proxy}, 错误信息: {e}")

# 测试每个代理
for proxy in PROXIES:
    check_proxy(proxy)

# 打印所有可用代理
print(f"所有可用代理：{valid_proxies}")
