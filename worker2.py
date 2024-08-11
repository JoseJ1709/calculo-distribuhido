import socket

worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
worker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
worker_socket.bind(('localhost', 10002))
worker_socket.listen(1)
print("Server is listening to task...")

try:
    while True:
        connection_socket, connection_address = worker_socket.accept()
        print(f"Connected to {connection_address}")
        data = connection_socket.recv(1024).decode()
        print("Received data...")
        if not data:
            print("No valid data")
            connection_socket.close()
            break
        number = list(map(int, data.split()))
        print(number)
        result = sum(number)
        print("Sending response...")
        connection_socket.sendall(str(result).encode())
        connection_socket.close()
        print("Closing connection...")
except KeyboardInterrupt:
    print("\nServer is shutting down gracefully...")
finally:
    worker_socket.close()
    print("Socket closed.")