import subprocess

def get_android_version():
    try:
        result = subprocess.check_output(['adb', 'shell', 'getprop', 'ro.build.version.release'], encoding='utf-8').strip()
        return result
    except Exception as e:
        print(f"出错了：{e}")
        return None

print(get_android_version())
