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
import json

# Configuring Server
SERVER_HOST = 'localhost'
SERVER_PORT = 3000
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
def clientComm(clientSocket, clientAddress, clientName):
    try:
        startTime = datetime.datetime.now()
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
            print(f"Received from {clientName}: {data}")

            if data.lower() == 'exit':
                endTime = datetime.datetime.now()
                with activeClientsLock:
                    activeClients[clientName]['endTime'] = endTime
                print(f"{clientName} has disconnected")
                break
            elif data.lower() == 'status':
                with activeClientsLock:
                    statusDict = {}
                    for cname, info in activeClients.items():
                        clientInfo = {
                            'address': list(info['address']), 
                            'connected_at': info['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                            'disconnected_at': info['end_time'].strftime("%Y-%m-%d %H:%M:%S") if info['end_time'] else None
                        }
                        statusDict[cname] = [clientInfo]
                    cache_info_json = json.dumps(statusDict)
                clientSocket.send(cache_info_json.encode())
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
        print(f"An error occurred with {clientName}: {str(e)}")
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
def serverConnect():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((SERVER_HOST, SERVER_PORT))
    serverSocket.listen()
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

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
                threading.Thread(target=clientComm, args=(clientSocket, clientAddress, clientName), daemon=True).start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        serverSocket.close()
if __name__ == '__main__':
    serverConnect()
