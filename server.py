import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
print("Server is listening on port 12345...")
server_socket.listen(4)
worker_sockets = []


def handle_client(client_socket, client_address):
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            numbers = list(map(int, data.split()))
            numbers1, numbers2 = numbers[0:2], numbers[2:4]

            if worker_sockets and len(numbers) > 2 :
                print("sending request..")
                response = distribute_tasks(numbers1, numbers2)
            else:
                print("calculating locally..")
                response = calculate_locally(numbers)

            client_socket.send(str(response).encode())
    except ConnectionResetError:
        print(f"Connection with client {client_address} lost.")
    finally:
        client_socket.close()
        print(f"Connection with client {client_address} closed.")

def distribute_tasks(numbers1, numbers2):
    results = []
    available_workers = min(len(worker_sockets), 2)
    for i in range(available_workers):
        worker_socket = worker_sockets.pop(0)
        if i == 0:
            send_to_worker(worker_socket, numbers1,results)
        else:
            send_to_worker(worker_socket, numbers2,results)

    if len(results) == 2:
        print("Two answers recived")
        return sum(results)
    elif len(results) == 1:
        if available_workers == 1:
            print("One answers recived")
            return results[0] + sum(numbers2)
        else:
            print("One answers recived")
            return results[0] + sum(numbers1)
    else:
        print("None wokers aviable")
        return sum(numbers1 + numbers2)

def send_to_worker(worker_socket, numbers,results):
    try:
        worker_socket.sendall(' '.join(map(str, numbers)).encode())
        result_data = worker_socket.recv(1024).decode()
        if result_data.isdigit():
            results.append(int(result_data))
            worker_sockets.append(worker_socket)
        else:
            print(f"Invalid result from worker{worker_socket} closing connection..")
            worker_socket.close()
    except ConnectionResetError:
        print("Connection with a worker lost.")
        worker_socket.close()
def calculate_locally(numbers):
    return sum(numbers)

while True:
    connection_socket, connection_address = server_socket.accept()
    initial_message = connection_socket.recv(1024).decode()
    if initial_message == "client":
        print(f"Client {connection_address} connected.")
        client_thread = threading.Thread(target=handle_client, args=(connection_socket, connection_address))
        client_thread.start()
    elif initial_message == "worker":
        print(f"Worker {connection_address} connected.")
        worker_sockets.append(connection_socket)
    else:
        print(f"Unknown connection type from {connection_address}.")
        connection_socket.close()