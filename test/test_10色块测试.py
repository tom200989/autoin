from InquirerPy import prompt

q0 = [
    {
        "type": "list",
        "name": "choice",
        "message": "请选择一个选项:",
        "choices": ["选项1", "选项2", "选项3", "选项4", "选项5"],
        "default": "选项1",
    }
]

r0 = prompt(q0)
# print(f"您选择了: {result['choice']}")

q1 = [
    {
        "type": "list",
        "name": "choice",
        "message": "请选择一个选项:",
        "choices": ["选项1", "选项2", "选项3", "选项4", "选项5"],
        "default": "选项1",
    }
]
r1 = prompt(q1)
