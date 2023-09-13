import subprocess

def check_driver(drivers):
    command = ['cmd', '/c', 'driverquery']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        print(stderr.decode('gbk'))
        return False, None
    else:
        result = stdout.decode('gbk')
        # 开始切割
        lines = result.split('\n')
        all_modules = [line.split(' ', 1)[0] for line in lines if line]
        # 查询哪些驱动没有安装
        diff = set(drivers) - set(all_modules)
        if diff and len(diff) > 0:
            print(f'以下驱动没有安装: {diff}')
            return False, list(diff)
        else:
            print('驱动检查通过')
            return True, None

# check_driver(['CH341SER_A64','CH343SER_A64','silabser'])

