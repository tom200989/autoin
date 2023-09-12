import shutil
import stat
import subprocess
import os

# 定义要打包的项目路径列表
project_paths = {  #
    'motherbox.exe': r'D:\project\python\autoin\case\motherbox',  # 母盒
    'motherbox_helper.exe': r'D:\project\python\autoin\case\motherbox_help',  # 母盒辅助器
}

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


def pack():
    # 为每个项目执行打包命令
    for project_fun, project_path in project_paths.items():
        try:
            print('即将打包:', project_fun)
            # 切换到项目目录
            print('切换到项目目录:', project_path)
            os.chdir(project_path)
            print('正在删除build文件夹')
            build_path = os.path.join(project_path, 'build')
            if os.path.exists(build_path) and os.path.isdir(build_path):
                shutil.rmtree(build_path, onerror=del_rw)
                print('build文件夹已删除')

            print('开始打包...')
            # 执行打包命令
            result = subprocess.run(['python', 'setup.py', 'build'], check=True)

            # 打印结果
            if result.returncode == 0:
                print(f'{project_path} 打包成功！')
            else:
                print(f'{project_path} 打包失败！返回码：{result.returncode}')

        except Exception as e:
            print(f'在项目 {project_path} 打包时出错：{e}')

    print('所有项目打包完成！开始复制文件夹...')

""" ----------------------------------------------- pack ----------------------------------------------- """

# 执行打包
pack()
