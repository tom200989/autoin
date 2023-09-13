import os
import win32api

def get_version_info(file_path):
    try:
        info = win32api.GetFileVersionInfo(file_path, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
        return version
    except:
        return "Unknown version"

if __name__ == '__main__':
    file_path = r"D:\project\python\autoin\case\boxhelper\build\exe.win-amd64-3.11\a00_boxhelper.exe"  # 例如: C:\path\to\your_program.exe
    version = get_version_info(file_path)
    print(f"版本号: {version}")
