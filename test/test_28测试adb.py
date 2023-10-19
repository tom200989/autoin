import subprocess
import time
log_path = r"D:\soft\appium\log\appium.log"
log_file = open(log_path, mode='a', encoding="utf8")
print('开始执行appium')
# subprocess.Popen(f"appium -p 4725", shell=True, stdout=log_file, stderr=subprocess.PIPE)
process = subprocess.Popen(f"appium -p 4725", shell=True, stdout=log_file, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
if stderr:
    print("发生错误:", stderr.decode())

# time.sleep(5)  # 建议8秒
# print('appium执行完毕, 开始查询端口。。。')
# result = subprocess.getoutput(f"netstat -ano | findstr {str(4725)}")
#
# result = result.split("\n")[0]
#
# print(result)
