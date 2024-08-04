import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12346))
print("Server is listening on port 12346...")
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

            if worker_sockets and len(numbers) > 2:
                print("Sending request to workers...")
                response = distribute_tasks(numbers1, numbers2)
            else:
                print("Calculating locally...")
                response = calculate_locally(numbers)
            print(f"Sending response...")
            client_socket.send(str(response).encode())
    except ConnectionResetError:
        print(f"Connection with client {client_address} lost.")
    finally:
        client_socket.close()
        print(f"Connection with client {client_address} closed.")


def distribute_tasks(numbers1, numbers2):
    results = []

    success = False
    if len(worker_sockets) > 1:
        worker_socket = worker_sockets.pop(0)
        success = send_task_to_worker(worker_socket, numbers1, results)
        if success:
            print("Valid result..")
            worker_sockets.append(worker_socket)
    if not success:
        print("Calculating locally...")
        results.append(sum(numbers1))

    success = False
    if worker_sockets:
        worker_socket = worker_sockets.pop(0)
        success = send_task_to_worker(worker_socket, numbers2, results)
        if success:
            print("Valid result..")
            worker_sockets.append(worker_socket)
    if not success:
        print("Calculating locally...")
        results.append(sum(numbers2))

    return sum(results)


def send_task_to_worker(worker_socket, numbers, results):
    try:
        worker_socket.sendall(' '.join(map(str, numbers)).encode())
        result_data = worker_socket.recv(1024).decode()
        if result_data.isdigit():
            results.append(int(result_data))
            return True
        else:
            print(f"Invalid result from worker {worker_socket}, closing connection...")
    except (ConnectionResetError, BrokenPipeError):
        print("Connection with a worker lost.")

    if worker_socket in worker_sockets:
        worker_sockets.remove(worker_socket)

    worker_socket.close()
    return False


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
