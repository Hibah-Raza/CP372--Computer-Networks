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
                    