import shutil
import psutil
from a01_nettools import *
from zboxtools import *

def kill_exe(_exe):
    """
    关闭指定进程
    java.exe: sonar.bat进程
    pgAdmin4.exe: 数据库进程
    """
    tmp_print(f'正在关闭{_exe}....')
    for proc in psutil.process_iter(['pid', 'name']):
        # 检查进程名
        if proc.info['name'] == _exe:
            tmp_print(f'找到进程{_exe},正在关闭...')
            # 杀掉进程
            try:
                proc.kill()
            except Exception as error:
                if 'NoSuchProcess' in str(error): tmp_print('该进程已关闭')

    tmp_print(f'{_exe}已全部关闭!')

def main():
    print('当前辅助器版本号: V', boxhelper_version)
    # 检查网络
    is_network = check_all_nets()
    # 如果网络正常
    if is_network:
        # 查询minio的母盒包(此处无需再检查是否有新版本,只要进入到这里,就说明有新版本)
        new_version = get_motherbox_version(minio_motherbox_root)
        # 拼接minio的母盒包最新版本路径
        motherbox_newpath = f'{minio_motherbox_root}{new_version}/motherbox_{new_version}.zip'
        # 结束当前母盒进程并删除当前母盒的所在目录(build)
        motherbox_exe = 'a00_motherbox.exe'
        # 结束母盒进程
        kill_exe(motherbox_exe)
        # 删除母盒进程所在的build文件夹
        exe_abs_path = str(find_exe_path(motherbox_exe))  # a00_motherbox.exe所在的绝对路径
        # exe_abs_path = r'C:\Users\huilin.xu\Desktop\d\build\exe.win-amd64-3.11\a00_motherbox.exe'
        if exe_abs_path:
            amd64_dir = os.path.dirname(str(exe_abs_path))  # exe.win-amd64-3.11 目录
            tmp_print('box_amd64_dir: ', amd64_dir)
            build_dir = os.path.dirname(str(amd64_dir))  # build 目录
            tmp_print('box_build_dir: ', build_dir)
            build_in_who = os.path.dirname(str(build_dir))  # 用户目录 (build所在的目录)
            tmp_print('box_build_in_who: ', build_in_who)
            # 此时再退出母盒
            tmp_print(f'正在退出当前母盒...')
            kill_exe(motherbox_exe)
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
                # 删除压缩包
                tmp_print(f'正在删除压缩包...')
                os.remove(str(local_zip))
                # 启动新的母盒
                tmp_print(f'正在启动新母盒...')
                newbox_exe = subprocess.Popen([exe_abs_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
                tmp_print("当前母盒进程ID:", newbox_exe.pid)
                # 退出母盒辅助器
                tmp_print(f'正在退出母盒辅助器...')
                exit(0)
                sys.exit(0)

        else:
            tmp_print(f'未找到{motherbox_exe}所在目录!')
            input('请勿手动删除母盒!')
            main()
    else:
        tmp_print("网络异常, 请根据以上提示检查网络相关连接!")
        input('请确保网络连接正常, 并按任意键再尝试')
        main()

if __name__ == '__main__':
    # shutil.rmtree(r'C:\Users\huilin.xu\Desktop\d\build', onerror=del_rw)

    # 下载 - 解压 - 删除
    # download_obj(r'C:\Users\huilin.xu\Desktop\d\motherbox_1002.zip', 'autocase/android/motherbox/1001/motherbox_1002.zip')
    # shutil.unpack_archive(r'C:\Users\huilin.xu\Desktop\d\motherbox_1002.zip', r'C:\Users\huilin.xu\Desktop\d')
    # os.remove(r'C:\Users\huilin.xu\Desktop\d\motherbox_1002.zip')

    # 删除
    # exe_abs_path = r'C:\Users\huilin.xu\Desktop\d\build\exe.win-amd64-3.11\a00_motherbox.exe'
    # arm64_dir = os.path.dirname(str(exe_abs_path))  # exe.win-amd64-3.11
    # build_dir = os.path.dirname(str(arm64_dir))  # build
    # tmp_print(f'正在删除当前母盒...')
    # shutil.rmtree(build_dir, onerror=del_rw)
    main()
    pass
