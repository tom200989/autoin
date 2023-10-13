import os
import shutil

print('删除原来目录')
if os.path.exists(r'D:\autocase\patch\p_ap_match'):
    shutil.rmtree(r'D:\autocase\patch\p_ap_match')
print('开始解压...')
shutil.unpack_archive(r'D:\autocase\patch\p_ap_match.zip', r'D:\autocase\patch')
print('解压完毕!')
# print('开始删除压缩包...')
# os.remove(r'D:\autocase\patch\p_ap_match.zip')
pass
