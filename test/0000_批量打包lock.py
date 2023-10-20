import shutil
import stat
import subprocess
import os

# 定义要打包的项目路径列表
project_paths = {  #
    'lockscreen.exe': r'D:\project\python\autoin\demo\lockscreen',  # 扫描执行包
}

# 临时文件夹(用于存入打包后的文件) - 注意, 此处修改需要同步修改setup.py中的同名变量
temp_folder = r'D:\lock_tmp\build'

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
        time.sleep(2)
        os.remove(name)
    except Exception as error:
        print('文件夹被进程占用, 正在强制删除: ', error)
        os.popen(f'rd /s /q {name}')  # 如果当前文件夹被占用, 则强制删除

# 为每个项目执行打包命令
for project_fun, project_path in project_paths.items():
    try:
        # 清空临时文件夹
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder, onerror=del_rw)
            print('临时文件夹已删除')
        print('即将打包:', project_fun)
        # 重新创建临时文件夹
        print('正在重新创建临时文件夹')
        os.makedirs(temp_folder)
        # 切换到项目目录
        print('切换到项目目录:', project_path)
        os.chdir(project_path)
        print('正在删除build文件夹')
        build_path = os.path.join(project_path, 'build')
        if os.path.exists(build_path) and os.path.isdir(build_path):
            shutil.rmtree(build_path, onerror=del_rw)
            print('build文件夹已删除')

        # 再次检查build文件夹是否存在
        if os.path.exists(build_path) and os.path.isdir(build_path):
            print('build文件夹删除失败, 请手动删除后重试!')
        else:
            print('开始打包...')
            # 执行打包命令
            result = subprocess.run(['python', 'setup.py', 'build'], check=True)

            # 打印结果
            if result.returncode == 0:
                print(f'{project_path} 打包成功！')
            else:
                print(f'{project_path} 打包失败！返回码：{result.returncode}')

            # 拷贝临时文件夹的内容到项目目录下
            print('正在拷贝临时文件夹的内容到项目目录下')
            shutil.copytree(os.path.join(temp_folder, 'build'), os.path.join(project_path, 'build'))

    except Exception as e:
        print(f'在项目 {project_path} 打包时出错：{e}')

print('所有项目打包完成！')
