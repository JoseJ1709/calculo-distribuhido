import socket

worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
worker_socket.connect(('localhost', 12346))
worker_socket.sendall("worker".encode())

while True:

    data = worker_socket.recv(1024).decode()
    print("received..")
    if not data:
        print("no valid data")
        break
    number = list(map(int, data.split()))
    result = sum(number)
    print("sending response..")
    worker_socket.sendall(str(result).encode())
