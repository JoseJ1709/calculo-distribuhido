import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SOCK_STREAM -> TCP
server_socket.bind(('localhost', 12346))
print("Server is listening on port 12345...")
server_socket.listen(4)
worker_sockets = []
def handle_client(client_socket, client_address):
    try :
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            number = int(data)
            if worker_sockets:
                worker_socket = worker_sockets.pop(0)
                try:
                    print("Sending task to a worker")
                    worker_socket.sendall(str(number).encode())
                    result = worker_socket.recv(1024).decode()
                    worker_sockets.append(worker_socket)
                    print("Sending response")
                    client_socket.sendall(result.encode())
                except ConnectionResetError:
                    print(f"Connection with server {worker_socket} lost.")
                    worker_socket.close()
            else:
                print("No workers to make the calc, made manually")
                calc(number,client_socket, client_address)
    except ConnectionResetError:
        print(f"Connection with client {client_address} lost.")
    finally:
        client_socket.close()  # Close the client connection
        print(f"Connection with client {client_address} closed.")

def handle_workers(worker_socket, worker_address):
    worker_sockets.append(worker_socket)

def calc(data,client_socket, client_address):
    result = data * 5
    client_socket.sendall(result.encode())

while True:

    connection_socket, connection_address = server_socket.accept()
    initial_message = connection_socket.recv(1024).decode()
    if initial_message == "client":
        print(f"Client {connection_address} connected.")
        client_thread = threading.Thread(target=handle_client,args=(connection_socket,connection_address))
        client_thread.start()

    elif initial_message == "worker":
        print(f"Worker {connection_address} connected.")
        worker_thread = threading.Thread(target=handle_workers, args=(connection_socket,connection_address))
        worker_thread.start()
    else:
        print(f"Unknown connection type from {connection_address}.")
        connection_socket.close()