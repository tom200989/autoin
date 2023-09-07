import subprocess
import time

def ping_ip(ip):
    """
    Ping给定的IP地址，并返回是否成功
    """
    response = subprocess.run(['ping', '-n', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return response.returncode == 0

def main():
    """
    主函数
    """
    # 初始化IP地址列表和失败次数字典
    ip_list = ['10.20.90.1', '10.20.1.98', '10.10.11.1', '10.1.1.118', '8.8.8.8']
    failure_count = {ip: 0 for ip in ip_list}

    count = 0
    # 循环Ping每个IP地址
    while True:
        count += 1
        for ip in ip_list:
            if not ping_ip(ip):
                failure_count[ip] += 1
                print(f"IP {ip} Ping失败，当前失败次数：{failure_count[ip]}, 当前已进行: {count} 次")

        # 等待一段时间再进行下一轮检查
        time.sleep(5)

if __name__ == "__main__":
    main()
