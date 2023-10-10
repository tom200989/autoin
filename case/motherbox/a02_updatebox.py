from b00_checknet import *
from cminio_tools import *
from ctmp_tools import *

def check_box_version():
    """
    查询母盒最新版本
    :return: True 有新版本, False 无新版本
    """
    # 检查是否minio连接
    if not check_minio():
        tmp_print(f"x minio连接失败")
        return False
    tmp_print(f"√ minio连接成功")

    # 获取minio的box版本号
    lastest_mversion = get_motherbox_version(minio_motherbox_root)
    if lastest_mversion is None:
        tmp_print(f"x 获取minio的box版本号失败")
        return False

    # 判断版本大小
    if motherbox_version < lastest_mversion:
        tmp_print(f"当前版本: {motherbox_version}, 最新版本: {lastest_mversion}")
        return True
    else:
        tmp_print(f"当前版本: {motherbox_version}, 无最新版本")
        return False

""" ----------------------------------------------- 更新母盒 ----------------------------------------------- """

def update_box():
    # 检查网络是否畅通
    is_network = check_pingnet()
    if is_network:
        # 如果有新版本, 则更新
        need_update = check_box_version()
        if need_update:
            # 先结束母盒辅助器的进程
            tmp_print('正在结束母盒辅助器进程...')
            kill_exe(boxhelper_exe_p)
            time.sleep(2)
            # 清空母盒辅助器目录 `.xxx/build`
            tmp_print('正在清空母盒辅助器目录...')
            mbh_build = os.path.join(boxhelper_dir, 'build')
            if os.path.exists(mbh_build): shutil.rmtree(mbh_build, onerror=del_rw)
            # 下载母盒辅助器(.xxx/boxhelper/boxhelper.zip)
            tmp_print('正在下载母盒辅助器...')
            local_zip = os.path.join(boxhelper_dir, 'boxhelper.zip')
            is_downed = download_obj(local_zip, minio_boxhelper_root + "boxhelper.zip")
            if not is_downed:
                tmp_print(f"x 下载母盒辅助器失败")
                input("请检查网络连接, 然后按任意键重试...")
                update_box()
            else:
                tmp_print(f'正在解压母盒辅助器...')
                shutil.unpack_archive(str(local_zip), boxhelper_dir)
                time.sleep(2)
                # 删除压缩包
                tmp_print(f'正在删除压缩包...')
                os.remove(str(local_zip))
                # 启动母盒辅助器
                tmp_print(f'正在启动新母盒辅助器...')
                exe_abs_path = os.path.join(boxhelper_dir, 'build', get_pack_dirname(), 'a00_boxhelper.exe')
                tmp_print('启动路径: ', exe_abs_path)
                newbox_exe = subprocess.Popen([exe_abs_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
                tmp_print("当前母盒辅助器进程ID:", newbox_exe.pid)

        else:
            tmp_print("当前没有最新母盒版本, 无需更新")
        return need_update

    else:
        tmp_print("网络异常, 请根据以上提示检查网络相关连接!")
        return False
