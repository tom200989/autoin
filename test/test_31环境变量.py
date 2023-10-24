import os

# 获取所有环境变量
all_env_vars = os.environ
# 将所有键转换为小写，并存储在一个字典中
lowercase_env_vars = {k.lower(): v for k, v in all_env_vars.items()}
# 获取"path"环境变量（不区分大小写）
path_value = lowercase_env_vars.get('path', None)

# 检查是否获取到值
if path_value:
    print(f"Path: {path_value}")
else:
    print("Path environment variable not found.")

