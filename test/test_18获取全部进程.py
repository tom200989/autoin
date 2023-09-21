import psutil

def get_running_process_names():
    process_names = []
    for process in psutil.process_iter(attrs=['name']):
        process_name = process.info['name']
        process_names.append(process_name)
    return process_names

if __name__ == "__main__":
    names = get_running_process_names()
    for name in names:
        print(name)
