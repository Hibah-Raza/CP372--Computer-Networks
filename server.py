"""
*-----------------------------------
* @file server.py
* CP372 - Socket Assignment
*-----------------------------------
* @author Hibah Hibah, Bilal Rashid
*
* @version 2024-10-15
*
*-----------------------------------
"""
import socket
import threading
import datetime
import os
import json  # Import json module

# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 3000
MAX_CLIENTS = 3  # Maximum number of clients
FILE_DIRECTORY = 'server_files'  # Directory containing files for the bonus requirement

# Global variables with thread synchronization
clientCounter = 0
clientCounterLock = threading.Lock()
activeClients = {}
activeClientsLock = threading.Lock()

def manageClientConnection(clientSocket, clientAddress, clientName):
    """
    Function to manage communication with a connected client.
    """
    try:
        # Record connection start time
        startTime = datetime.datetime.now()

        # Store client information in the cache
        with activeClientsLock:
            activeClients[clientName] = {
                'address': clientAddress,
                'start_time': startTime,
                'end_time': None
            }

        print(f"{clientName} connected from {clientAddress}")

        # Send the assigned client name to the client
        clientSocket.send(clientName.encode())

        # Communication loop with the client
        while True:
            clientData = clientSocket.recv(1024).decode()
            if not clientData:
                break  # Client disconnected

            clientData = clientData.strip()
            print(f"Received from {clientName}: {clientData}")

            if clientData.lower() == 'exit':
                # Client requests to terminate the connection
                endTime = datetime.datetime.now()
                with activeClientsLock:
                    activeClients[clientName]['end_time'] = endTime
                print(f"{clientName} has disconnected")
                break
            elif clientData.lower() == 'status':
                # Client requests server cache status
                with activeClientsLock:
                    # Build the JSON structure
                    statusDict = {}
                    for cname, info in activeClients.items():
                        clientInfo = {
                            'address': list(info['address']),  # Convert tuple to list for JSON serialization
                            'connected_at': info['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                            'disconnected_at': info['end_time'].strftime("%Y-%m-%d %H:%M:%S") if info['end_time'] else None
                        }
                        # The desired format has each client as a key with a list of client info dicts
                        statusDict[cname] = [clientInfo]
                    cacheInfoJson = json.dumps(statusDict)
                clientSocket.send(cacheInfoJson.encode())
            elif clientData.lower() == 'list':
                # Client requests file list (Bonus requirement)
                if os.path.isdir(FILE_DIRECTORY):
                    files = os.listdir(FILE_DIRECTORY)
                    fileList = '\n'.join(files)
                    clientSocket.send(fileList.encode())
                else:
                    clientSocket.send("File directory not found.".encode())
            elif clientData.lower().startswith('get '):
                # Client requests a file (Bonus requirement)
                filename = clientData[4:].strip()
                filepath = os.path.join(FILE_DIRECTORY, filename)
                if os.path.isfile(filepath):
                    try:
                        fileSize = os.path.getsize(filepath)
                        # Send file size to client
                        clientSocket.send(f"FILESIZE {fileSize}".encode())
                        # Wait for client's acknowledgment
                        ack = clientSocket.recv(1024).decode()
                        if ack == 'READY':
                            # Send the file in chunks
                            with open(filepath, 'rb') as file:
                                while True:
                                    bytesRead = file.read(1024)
                                    if not bytesRead:
                                        break
                                    clientSocket.sendall(bytesRead)
                            print(f"File '{filename}' sent to {clientName}")
                        else:
                            print(f"{clientName} did not acknowledge file transfer.")
                    except Exception as e:
                        clientSocket.send(f"Error sending file: {str(e)}".encode())
                else:
                    clientSocket.send(f"ERROR: File '{filename}' not found.".encode())
            else:
                # Echo message back with 'ACK' appended
                response = clientData + " ACK"
                clientSocket.send(response.encode())

    except Exception as e:
        print(f"An error occurred with {clientName}: {str(e)}")
    finally:
        clientSocket.close()
        # Update the client's end time in the cache
        with activeClientsLock:
            if clientName in activeClients:
                if not activeClients[clientName]['end_time']:
                    activeClients[clientName]['end_time'] = datetime.datetime.now()
        print(f"Connection with {clientName} closed")

def launchServer():
    """
    Function to launch the server and accept incoming client connections.
    """
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((SERVER_HOST, SERVER_PORT))
    serverSocket.listen()
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    try:
        while True:
            clientSocket, clientAddress = serverSocket.accept()
            # Check if we can accept more clients
            with activeClientsLock:
                currentClients = len([c for c in activeClients.values() if c['end_time'] is None])
            if currentClients >= MAX_CLIENTS:
                # Inform the client that the server is full and close the connection
                message = "Server is full. Please try again later."
                clientSocket.send(message.encode())
                clientSocket.close()
                print(f"Refused connection from {clientAddress} - server is full.")
            else:
                # Assign a unique client name
                with clientCounterLock:
                    global clientCounter
                    clientCounter += 1
                    clientNumber = clientCounter
                clientName = f'Client{clientNumber:02d}'
                # Start a new thread to handle the client
                threading.Thread(target=manageClientConnection, args=(clientSocket, clientAddress, clientName), daemon=True).start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        serverSocket.close()

if __name__ == '__main__':
    launchServer()