import subprocess

def run_cmd():
    # 执行CMD命令并获取输出
    result = subprocess.run(['where', 'adb'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 判断命令是否成功执行
    if result.returncode == 0:
        print("v 命令执行成功，输出如下：")
        print(result.stdout)
    else:
        print("x 命令执行失败，错误信息如下：")
        print(result.stderr)

# 执行函数
run_cmd()
