import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 12346))
print("Server is listening on port 12346...")
server_socket.listen(5)

# Lista de puertos de los trabajadores
worker_ports = [10001,10002]
# Lista de trabajadores disponibles
workers_available = worker_ports.copy()

def handle_client(client_socket, client_address):
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            numbers = list(map(int, data.split()))
            half_index = len(numbers) // 2
            numbers1, numbers2 = numbers[:half_index], numbers[half_index:]

            if workers_available:
                print(f"Sending request to workers {numbers1,numbers2} ...")
                response = distribute_tasks(numbers1, numbers2)
            else:
                print("Calculating locally...")
                response = calculate_locally(numbers)

            print(f"Sending response {response} to client {client_address}...")
            client_socket.send(str(response).encode())
    except ConnectionResetError:
        print(f"Connection with client {client_address} lost.")
    except KeyboardInterrupt:
        print("\nServer is shutting down gracefully...")
        server_socket.close()
    finally:
        client_socket.close()
        print(f"Connection with client {client_address} closed.")


def distribute_tasks(numbers1, numbers2):
    results = []

    if workers_available:
        worker_port = workers_available.pop(0)
        success = send_task_to_worker(worker_port, numbers1, results)
        if success:
            print(f"Valid result from worker {worker_port} : {results[0]}.")
            workers_available.append(worker_port)
        else:
            workers_available.append(worker_port)
            print("Calculating locally...")
            calculate_locally(numbers1,results)

    if numbers2 and workers_available:
        worker_port = workers_available.pop(0)
        success = send_task_to_worker(worker_port, numbers2, results)
        if success:
            print(f"Valid result from worker {worker_port} : {results[1]}.")
            workers_available.append(worker_port)
        else:
            workers_available.append(worker_port)
            print("Calculating locally...")
            calculate_locally(numbers2,results)

    return sum(results)


def send_task_to_worker(worker_port, numbers, results):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as worker_socket:
            worker_socket.connect(('localhost', worker_port))
            worker_socket.sendall(' '.join(map(str, numbers)).encode())
            result_data = worker_socket.recv(1024).decode()

            if result_data.isdigit():
                results.append(int(result_data))
                worker_socket.close()
                return True
            else:
                print(f"Invalid result from worker on port {worker_port}, closing connection...")
    except (ConnectionRefusedError, BrokenPipeError):
        print(f"Connection to worker on port {worker_port} failed or was lost.")

    return False


def calculate_locally(numbers,results):
    print(f" {numbers} :  {sum(numbers)}")
    results.append(sum(numbers))

try:
    while True:
        connection_socket, connection_address = server_socket.accept()
        initial_message = connection_socket.recv(1024).decode()
        if initial_message == "client":
            print(f"Client {connection_address} connected.")
            client_thread = threading.Thread(target=handle_client, args=(connection_socket, connection_address))
            client_thread.start()
        else:
            print(f"Unknown connection type from {connection_address}.")
            connection_socket.close()
except KeyboardInterrupt:
    print("\nServer is shutting down gracefully...")
    server_socket.close()
finally:
    server_socket.close()
    print("Socket closed.")
