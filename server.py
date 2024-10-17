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
# Imports
import socket
import threading
import datetime
import os

# Configuring Server
HOST = 'localhost'
PORT = 12345
MAXCLIENTS = 3
FILEDIRECTORY = 'server_files'

# Variables
clientCounter = 0
clientCounterLock = threading.Lock()
activeClients = {}
activeClientsLock = threading.Lock()

"""
This function will handle communication
with a connected client individually
"""
def handleClient(clientSocket, clientAddress, clientName):
    try:
        startTime = dateTime.dateTime.now()
        with activeClientsLock:
            activeClients[clientName] = {
                'address': clientAddress,
                'startTime': startTime,
                'endTime': None
            }
        print(f"{clientName} connected from {clientAddress}")
        
        clientSocket.send(clientName.encode())

        while True:
            data = clientSocket.recv(1024).decode()
            if not data:
                break
            data = data.strip()
            print(f"Recieved from {clientName}: {data}")

            if data.lower() == 'exit':
                endTime = datetime.datetime.now()
                with activeClientsLock:
                    activeClients[clientName]['endTime'] = endTime
                print(f"{clientName} has disconnected")
                break
            elif data.lower() == 'status':
                with activeClientsLock:
                    cacheInfo = ''
                    for cname, info in activeClients.items():
                        start = info['startTime'].strftime("%Y-%m-%d %H:%M:%S")
                        end = info['endTime'].strftime("%Y-%m-%d %H:%M:%S") if info['end_time'] else "N/A"
                        cacheInfo += f"{cname}: Connected at {start}, Disconnected at {end}\n"
                clientSocket.send(cacheInfo.encode())
            elif data.lower() == 'list':
                if os.path.isdir(FILEDIRECTORY):
                    files = os.listdir(FILEDIRECTORY)
                    filesList = '\n'.join(files)
                    clientSocket.send(filesList.encode())
                else:
                    clientSocket.send("File directory not found.".encode())
            elif data.lower().startswith('get '):
                filename = data[4:].strip()
                filepath = os.path.join(FILEDIRECTORY, filename)
                if os.path.isfile(filepath):
                    try:
                        filesize = os.path.getsize(filepath)
                        clientSocket.send(f"FILESIZE {filesize}".encode())
                        ack = clientSocket.recv(1024).decode()
                        if ack == 'READY':
                            with open(filepath, 'rb') as f:
                                while True:
                                    bytesRead = f.read(1024)
                                    if not bytesRead:
                                        break
                                    clientSocket.sendall(bytesRead)
                            print(f"File '{filename}' sent to {clientName}")
                        else:
                            print(f"'{clientName}' was not able to acknowldege the file transfer.")
                    except Exception as e:
                        clientSocket.send(f"Error sending file: {str(e)}".encode())
                else:
                    clientSocket.send(f"ERROR: File '{filename}' not found.".encode())
            else:
                response = data + " ACK"
                clientSocket.send(response.encode())
    except Exception as e:
        print(f"An error occured with {clientName}: {str(e)}")
    finally:
        clientSocket.close()
        with activeClientsLock:
            if clientName in activeClients:
                if not activeClients[clientName]['endTime']:
                    activeClients[clientName]['endTime'] = datetime.datetime.now()
        print(f"Connection with {clientName} closed.")

"""
This function will set up the server
and take incoming client connections
"""
def startServer():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((HOST, PORT))
    serverSocket.listen()
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            clientSocket, clientAddress = serverSocket.accept()
            with activeClientsLock:
                currentClients  = len([c for c in activeClients.values() if c['end_time'] is None])
            if currentClients >= MAXCLIENTS:
                message = "Server is full. Please try again later."
                clientSocket.send(message.encode())
                clientSocket.close()
                print(f"Refused connection from {clientAddress} - Server is full.")
            else:
                with clientCounterLock:
                    global clientCounter
                    clientCounter += 1
                    clientNumber = clientCounter
                clientName = f'Client{clientNumber:02d}'
                threading.Thread(target=handleClient, args=(clientSocket, clientAddress, clientName), daemon=True).start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        serverSocket.close()
