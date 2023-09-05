import subprocess
import requests
import re
from minio import Minio
from minio.error import S3Error

# ---------------------------------------------- wifi强度状态 ----------------------------------------------
def check_wifi_strength():
    try:
        cmd_output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], universal_newlines=True, encoding='gbk')
        wifi_info = re.findall(r"SSID\s+:\s+(.*?)\n", cmd_output)
        if 'EF-office' in wifi_info:
            print("EF-office WiFi已连接")
        else:
            print("EF-office WiFi未连接")
    except Exception as e:
        print(f"检查WiFi时出错: {e}")

# ---------------------------------------------- 后台环境状态 ----------------------------------------------
def check_apis_health():
    urls = {  #
        "欧洲节点": "https://api-e.ecoflow.com/iot-service/health",  #
        "美国节点": "https://api-a.ecoflow.com/iot-service/health",  #
        "国内生产节点": "https://api-cn.ecoflow.com/iot-service/health",  #
        "海外UAT节点": "https://api-uat-aws.ecoflow.com/iot-service/health",  #
        "国内UAT节点": "https://api-uat2.ecoflow.com/iot-service/health"  #
    }

    for key, url in urls.items():
        try:
            response = requests.get(url)
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("status") == "UP":
                    print(f"{key} 响应为200且状态为UP")
            else:
                print(f"{key} 响应非200")
        except Exception as e:
            print(f"{key} 请求失败: {e}")

# ---------------------------------------------- 外网状态 ----------------------------------------------
def check_sites():
    urls = ["https://www.google.com"]

    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"{url} 响应为200")
            else:
                print(f"{url} 响应异常: ", response.status_code)
        except Exception as e:
            print(f"{url} 请求失败: {e}")

# ---------------------------------------------- adb连接状态 ----------------------------------------------
def restart_adb_server():
    try:
        subprocess.run(["adb", "kill-server"], universal_newlines=True, encoding='utf-8')
        subprocess.run(["adb", "start-server"], universal_newlines=True, encoding='utf-8')
        print("ADB服务已重启")
    except Exception as e:
        print(f"重启ADB服务时出错: {e}")

def check_adb_installation():
    try:
        cmd_output = subprocess.check_output(["adb", "version"], universal_newlines=True, encoding='utf-8')
        if "Android Debug Bridge version" in cmd_output:
            print("ADB已安装")
            return True
        else:
            print("ADB未安装")
            return False
    except Exception as e:
        print(f"检查ADB安装时出错: {e}")
        return False

def check_adb_connections(retry_count=1):
    if not check_adb_installation():
        print("由于ADB未安装，跳过检查ADB连接")
        return

    try:
        cmd_output = subprocess.check_output(["adb", "devices"], universal_newlines=True, encoding='utf-8')
        devices = re.findall(r"\n(.*?)\tdevice", cmd_output)
        if devices:
            print(f"已连接的设备: {', '.join(devices)}")
        else:
            print("没有设备连接")
    except Exception as e:
        if retry_count > 0:
            print("检查ADB连接时出错，正在尝试重启ADB服务")
            restart_adb_server()
            check_adb_connections(retry_count=retry_count - 1)
        else:
            print(f"重试失败，检查ADB连接时出错: {e}")

# ---------------------------------------------- minio存储桶状态 ----------------------------------------------
# 使用实际的Endpoint、Access Key和Secret Key替换以下占位符
endpoint = 'minio.ecoflow.com:9000'
access_key = 'EQS4J84JGJCDYNENIMT1'
secret_key = '8Vgk11c9bDOpZPTJMexPLrxZpzEOqro+jZyAUh+a'

def check_minio(endpoint, access_key, secret_key):
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=True
    )

    try:
        # 检查是否可以列出存储桶
        buckets = client.list_buckets()
        print("MinIO 连接成功，可用的存储桶如下:")
        for bucket in buckets:
            print(bucket.name)
        return True
    except S3Error as e:
        print(f"连接MinIO时出错: {e}")
        return False

if __name__ == "__main__":
    # wifi强度
    check_wifi_strength()
    # 连接检测
    check_apis_health()
    # 外网检测
    check_sites()
    # minio存储桶
    check_minio(endpoint, access_key, secret_key)
    # adb检测
    check_adb_connections()
