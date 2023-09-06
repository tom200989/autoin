from b00_checknet import *

if __name__ == '__main__':
    # 检查连接环境(含网络, adb, 后台, 外网, minio)
    conn_envs_state = check_nets()
    if not conn_envs_state:
        input('请根据以上提示确保网络连接环境正常, 按任意键退出...')
        exit(1)

    pass
