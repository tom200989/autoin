import shutil
import time

import psutil
from a01_nettools import *
from zboxtools import *


def main():
    print('当前辅助器版本号: V', boxhelper_version)
    # 找到母盒进程所在的build文件夹
    exe_abs_path = str(find_exe_path(motherbox_exe_p))  # a00_motherbox.exe所在的绝对路径
    amd64_dir = os.path.dirname(str(exe_abs_path))  # exe.win-amd64-3.11 目录
    build_dir = os.path.dirname(str(amd64_dir))  # build 目录
    build_in_who = os.path.dirname(str(build_dir))  # 用户目录 (build所在的目录)
    # 找到路径后再退出母盒
    tmp_print(f'正在退出当前母盒...')
    kill_exe(motherbox_exe_p)
    time.sleep(2)
    if exe_abs_path:
        # 检查网络
        is_network = check_pingnet()
        # 如果网络正常
        if is_network:
            # 查询minio的母盒包(此处无需再检查是否有新版本,只要进入到这里,就说明有新版本)
            new_version = get_motherbox_version(minio_motherbox_root)
            # 拼接minio的母盒包最新版本路径
            motherbox_newpath = f'{minio_motherbox_root}{new_version}/motherbox_{new_version}.zip'
            # 删除当前母盒
            tmp_print(f'正在删除当前母盒...')
            if os.path.exists(build_dir): shutil.rmtree(build_dir, onerror=del_rw)
            # 下载最新母盒包(下载到用户目录, 因为打包上传时直接压缩build文件夹)
            # .xxx/build/exe.win-amd64-3.11/motherbox_1002.zip
            local_zip = os.path.join(build_in_who, f'motherbox_{new_version}.zip')
            tmp_print('从 ', motherbox_newpath, ' 下载')
            tmp_print('下载到: ', local_zip)
            is_downed = download_obj(local_zip, motherbox_newpath)
            if not is_downed:
                tmp_print(f'下载最新母盒包失败, 请检查网络连接!')
                input('请确保网络连接正常, 并按任意键再尝试')
                main()
            else:
                # 解压母盒包
                tmp_print(f'正在解压母盒包...')
                shutil.unpack_archive(str(local_zip), build_in_who)
                time.sleep(2)
                # 删除压缩包
                tmp_print(f'正在删除压缩包...')
                os.remove(str(local_zip))
                # 启动新的母盒
                tmp_print(f'正在启动新母盒...')
                newbox_exe = subprocess.Popen([exe_abs_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
                tmp_print("当前母盒进程ID:", newbox_exe.pid)
                # 退出母盒辅助器
                tmp_print(f'正在退出母盒辅助器...')
                os._exit(0)
                sys.exit(0)
        else:
            tmp_print("网络异常, 请根据以上提示检查网络相关连接!")
            kill_exe(motherbox_exe_p)
            input('请确保网络连接正常, 并按任意键再尝试')
            main()
    else:
        tmp_print(f'未找到{motherbox_exe_p}所在目录!')
        kill_exe(motherbox_exe_p)
        input('请勿手动删除母盒!(按任意键重启)')
        time.sleep(1)
        main()

if __name__ == '__main__':
    main()
    pass
