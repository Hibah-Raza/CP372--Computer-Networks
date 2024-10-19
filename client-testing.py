import socket
import sys
import os
import json  # Import json module

HOST = 'localhost'
PORT = 3000

def start_client():
    """
    Function to start the client and connect to the server.
    Handles sending and receiving messages sequentially.
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        # Receive the initial message from the server
        data = client_socket.recv(1024).decode()
        if data == "Server is full. Please try again later.":
            print(data)
            client_socket.close()
            return
        else:
            client_name = data
            print(f"Connected to the server as {client_name}")

        while True:
            msg = input("Enter message ('exit' to quit): ")
            if msg:
                client_socket.send(msg.encode())
                if msg.lower() == 'exit':
                    break

                # Wait for server response
                data = client_socket.recv(4096).decode()
                if not data:
                    print("Disconnected from server.")
                    break

                # Handle server full message
                if data == "Server is full. Please try again later.":
                    print(data)
                    client_socket.close()
                    return
                elif data.startswith('FILESIZE '):
                    # Handle file transfer initiation
                    try:
                        filesize = int(data[9:])
                        client_socket.send('READY'.encode())

                        # Receive the file data
                        while True:
                            filename = input("Enter the filename to save as: ").strip()
                            if filename:
                                # Prevent directory traversal attacks
                                filename = os.path.basename(filename)
                                break
                            else:
                                print("Filename cannot be empty. Please enter a valid filename.")

                        with open(filename, 'wb') as f:
                            bytes_received = 0
                            while bytes_received < filesize:
                                chunk = client_socket.recv(1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                                bytes_received += len(chunk)
                        print(f"File '{filename}' received successfully.")
                    except ValueError:
                        print("Invalid file size received from server.")
                elif data.startswith("ERROR"):
                    # Handle error messages from the server
                    print(f"Server response:\n{data}")
                else:
                    try:
                        # Try to parse the data as JSON
                        json_data = json.loads(data)
                        # Pretty-print the JSON data
                        formatted_json = json.dumps(json_data, indent=4)
                        print(f"Server response:\n{formatted_json}")
                    except json.JSONDecodeError:
                        # If not JSON, just print the data
                        print(f"Server response:\n{data}")

        client_socket.close()
        print("Connection closed.")

    except ConnectionRefusedError:
        print("Could not connect to the server. Is the server running?")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        pass

if __name__ == '__main__':
    start_client()