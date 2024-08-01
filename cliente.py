import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12346))
client_socket.sendall("client".encode())
print("text 'exit' if wanna close")
while True:
    number = input("Enter a number to send to the server: ")
    if number.lower() == 'exit':
        client_socket.close()
        break

    client_socket.sendall(str(number).encode())

    result = client_socket.recv(1024).decode()
    print(f"Received result from server: {result}")
