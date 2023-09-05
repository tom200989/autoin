import os

def get_chrome_version():
    try:
        chrome_path = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "Application", "chrome.exe")
        if os.path.exists(chrome_path):
            version_info = os.popen(f'"{chrome_path}" --version').read()
            version = version_info.strip().split(" ")[2]
            print(f"Chrome Version: {version}")
            return version
        else:
            print("Chrome not found.")
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None

get_chrome_version()
