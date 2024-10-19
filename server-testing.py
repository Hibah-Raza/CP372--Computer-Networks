import socket
import threading
import datetime
import os
import json  # Import json module

# Server configuration
HOST = 'localhost'
PORT = 3000
MAX_CLIENTS = 3  # Maximum number of clients
FILE_DIR = 'server_files'  # Directory containing files for the bonus requirement

# Global variables with thread synchronization
client_counter = 0
client_counter_lock = threading.Lock()
active_clients = {}
active_clients_lock = threading.Lock()

def handle_client(client_socket, client_address, client_name):
    """
    Function to handle communication with a connected client.
    """
    try:
        # Record connection start time
        start_time = datetime.datetime.now()

        # Store client information in the cache
        with active_clients_lock:
            active_clients[client_name] = {
                'address': client_address,
                'start_time': start_time,
                'end_time': None
            }

        print(f"{client_name} connected from {client_address}")

        # Send the assigned client name to the client
        client_socket.send(client_name.encode())

        # Communication loop with the client
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break  # Client disconnected

            data = data.strip()
            print(f"Received from {client_name}: {data}")

            if data.lower() == 'exit':
                # Client requests to terminate the connection
                end_time = datetime.datetime.now()
                with active_clients_lock:
                    active_clients[client_name]['end_time'] = end_time
                print(f"{client_name} has disconnected")
                break
            elif data.lower() == 'status':
                # Client requests server cache status
                with active_clients_lock:
                    # Build the JSON structure
                    status_dict = {}
                    for cname, info in active_clients.items():
                        client_info = {
                            'address': list(info['address']),  # Convert tuple to list for JSON serialization
                            'connected_at': info['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                            'disconnected_at': info['end_time'].strftime("%Y-%m-%d %H:%M:%S") if info['end_time'] else None
                        }
                        # The desired format has each client as a key with a list of client info dicts
                        status_dict[cname] = [client_info]
                    cache_info_json = json.dumps(status_dict)
                client_socket.send(cache_info_json.encode())
            elif data.lower() == 'list':
                # Client requests file list (Bonus requirement)
                if os.path.isdir(FILE_DIR):
                    files = os.listdir(FILE_DIR)
                    file_list = '\n'.join(files)
                    client_socket.send(file_list.encode())
                else:
                    client_socket.send("File directory not found.".encode())
            elif data.lower().startswith('get '):
                # Client requests a file (Bonus requirement)
                filename = data[4:].strip()
                filepath = os.path.join(FILE_DIR, filename)
                if os.path.isfile(filepath):
                    try:
                        filesize = os.path.getsize(filepath)
                        # Send file size to client
                        client_socket.send(f"FILESIZE {filesize}".encode())
                        # Wait for client's acknowledgment
                        ack = client_socket.recv(1024).decode()
                        if ack == 'READY':
                            # Send the file in chunks
                            with open(filepath, 'rb') as f:
                                while True:
                                    bytes_read = f.read(1024)
                                    if not bytes_read:
                                        break
                                    client_socket.sendall(bytes_read)
                            print(f"File '{filename}' sent to {client_name}")
                        else:
                            print(f"{client_name} did not acknowledge file transfer.")
                    except Exception as e:
                        client_socket.send(f"Error sending file: {str(e)}".encode())
                else:
                    client_socket.send(f"ERROR: File '{filename}' not found.".encode())
            else:
                # Echo message back with 'ACK' appended
                response = data + " ACK"
                client_socket.send(response.encode())

    except Exception as e:
        print(f"An error occurred with {client_name}: {str(e)}")
    finally:
        client_socket.close()
        # Update the client's end time in the cache
        with active_clients_lock:
            if client_name in active_clients:
                if not active_clients[client_name]['end_time']:
                    active_clients[client_name]['end_time'] = datetime.datetime.now()
        print(f"Connection with {client_name} closed")

def start_server():
    """
    Function to start the server and accept incoming client connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            # Check if we can accept more clients
            with active_clients_lock:
                current_clients = len([c for c in active_clients.values() if c['end_time'] is None])
            if current_clients >= MAX_CLIENTS:
                # Inform the client that the server is full and close the connection
                message = "Server is full. Please try again later."
                client_socket.send(message.encode())
                client_socket.close()
                print(f"Refused connection from {client_address} - server is full.")
            else:
                # Assign a unique client name
                with client_counter_lock:
                    global client_counter
                    client_counter += 1
                    client_number = client_counter
                client_name = f'Client{client_number:02d}'
                # Start a new thread to handle the client
                threading.Thread(target=handle_client, args=(client_socket, client_address, client_name), daemon=True).start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server()