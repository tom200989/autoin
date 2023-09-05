import socket

def get_computer_name():
    try:
        computer_name = socket.getfqdn()
        return computer_name
    except Exception as e:

        return None

computer_name = get_computer_name()
if computer_name:
    print(computer_name)
