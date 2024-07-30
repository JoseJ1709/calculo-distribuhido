import socket

worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
worker_socket.connect(('localhost', 12346))
worker_socket.sendall("worker".encode())

while True:

    data = worker_socket.recv(1024).decode()
    if not data:
        break
    print("working..")
    number = int(data)
    result = number * 5
    worker_socket.sendall(str(result).encode())
