
path_list = [ 'i','h',  'j','g','a', 'b', 'c', 'd', 'e', 'f', ]
test_paths = ['g', 'h', 'i', 'j']

# 获取 test_paths 中所有路径在 path_list 中的索引
print(all(test_path in path_list for test_path in test_paths))

indices = [path_list.index(test_path) for test_path in test_paths]
print(all(index < len(test_paths) for index in indices))
