import datetime
import os
import shutil
import stat
import subprocess

def get_apk_path(package_name):
    """获取指定包名的APK路径"""
    cmd = f'adb shell pm path {package_name}'
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    apk_path = result.stdout.strip().split(":")[1]  # 输出格式通常是"package:/path/to/apk"，所以我们用":"分割并取第二部分
    return apk_path

def pull_apk(apk_path, dest_path):
    """将APK从设备拉取到电脑上"""
    cmd = f'adb pull {apk_path} {dest_path}'
    subprocess.run(cmd, shell=True)

def del_rw(action, name, exc):
    """
    切换文件夹权限(管理员)
    :param action:
    :param name:
    :param exc:
    """
    os.chmod(name, stat.S_IWRITE)
    try:
        # 先解除占用
        # unoccupied(name)
        # 再删除文件夹
        os.remove(name)
    except Exception as error:
        print('文件夹被进程占用, 正在强制删除: ', error)
        os.popen(f'rd /s /q {name}')  # 如果当前文件夹被占用, 则强制删除


pack_dirname = input('输入开始:')
# 拼接打包后的目录
date_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
new_pack_dirname = 'p_' + pack_dirname + '_' + date_time
zip_temp_dir = os.path.join('D:\\', new_pack_dirname)  # D:\p_testdemo

# 把build文件夹拷贝到压缩临时文件夹下
print('正在拷贝build文件夹到压缩临时文件夹下')
build_dir = r'C:\Users\qianli.ma\Desktop\build' # todo 2023/10/19 记得删除
shutil.copytree(build_dir, os.path.join(zip_temp_dir, new_pack_dirname, 'build'))

# 用adb导出手机里com.ecoflow包名的apk
print('正在导出手机里com.ecoflow包名的apk')
apk_adb_path = get_apk_path('com.ecoflow')  # apk在手机里的路径
apk_pull_target_path = os.path.join(zip_temp_dir, new_pack_dirname, 'ecoflow_oversea.apk')  # 要导出的apk路径(名字要固定)
pull_apk(apk_adb_path, apk_pull_target_path)  # 导出apk

# 压缩临时文件夹
print(f'正在压缩临时文件夹:{zip_temp_dir}')
shutil.make_archive(zip_temp_dir, 'zip', zip_temp_dir)
# 删除临时文件夹
print('正在删除临时文件夹')
shutil.rmtree(zip_temp_dir, onerror=del_rw)

print('所有项目打包完成')
