import traceback
from b00_checknet import *

def downpatch(func_cancel):
    try:
        # 创建patch目录
        if not os.path.exists(patch_root):
            os.makedirs(patch_root)
            tmp_print(f'创建patch目录: {patch_root}')

        # 检查网络
        is_network_pass = check_all_nets()
        if not is_network_pass:
            tmp_print('x 网络检查不通过, 请检查网络')
            return False

        # 查询minio库的所有目录 ['autocase/android/patch/p_ble_net_49011_202310131506.zip']
        minio_patchs = list_minio_objs(minio_patch_root)
        # 转换成字典 {'p_ble_net_49011_202310131506':'autocase/android/patch/p_ble_net_49011_202310131506.zip'}
        patch_dicts = {fp.split('/')[-1].split('.zip')[0]: fp for fp in minio_patchs}
        # 提取key并组成元祖列表 [('0', 'p_ble_net_49011_202310131506'), ('1', 'p_ble_net_49011_202310131506')]
        patch_list = [(str(index), key) for index, key in enumerate(list(patch_dicts.keys()))]
        # 进入面板选择
        choice_patch = ['选择要下载的脚本', '请选择:', patch_list]
        patch_seleted = choice_pancel(choice_patch[0], choice_patch[1], choice_patch[2], fun_cancel=func_cancel)
        if patch_seleted is None:
            tmp_print('patch_seleted 为None: 默认为 0')
            patch_seleted = '0'
        tmp_print(f'当前选中: {patch_seleted} -> {patch_list[int(str(patch_seleted))]}')
        # 根据选择的key, 得到minio的路径 'autocase/android/patch/p_ble_net_49011_202310131506.zip'
        need_down_path = patch_dicts[patch_list[int(str(patch_seleted))][1]]
        tmp_print('minio路径: ', need_down_path)
        # 得到本地路径 'D:\\autocase\\patch\\p_ble_net_49011_202310131506.zip'
        local_path = f'{patch_root}/{need_down_path.split("/")[-1]}'
        # 如果原来有子目录, 则删除
        local_dir = local_path.replace('.zip', '')
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)
            tmp_print(f'删除子目录: {local_dir}')
        # 如果原来有zip文件, 则删除
        if os.path.exists(local_path):
            remove_who(local_path)
            tmp_print(f'删除zip文件: {local_path}')
        # 下载zip文件 (裁剪出本地路径 'D:\\autocase\\patch\\p_ble_net_49011_202310131506.zip')
        tmp_print(f'正在下载zip文件: {need_down_path} 到 {local_path}')
        download_obj(local_path, need_down_path)
        time.sleep(2)
        # 解压zip文件
        tmp_print(f'正在解压zip文件: {local_path}')
        shutil.unpack_archive(local_path, patch_root)
        time.sleep(5)
        # 删除zip文件
        remove_who(local_path)
        tmp_print(f'删除zip文件: {local_path}')
        tmp_print(f'脚本下载完成, 请回到主菜单运行脚本')

        return True
    except Exception as e:
        traceback.print_exc()
        tmp_print(f'x 脚本下载失败, {e}')
        return False
