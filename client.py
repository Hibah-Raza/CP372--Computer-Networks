"""
*-----------------------------------
* @file client.py
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
import json
import os
import sys

# Configuring Server
SERVER_HOST = 'localhost'
SERVER_PORT = 3000

"""
This is a thread function that 
will receive messages from the server
"""
def startingClient():
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((SERVER_HOST, SERVER_PORT))
        data = clientSocket.recv(1024).decode()
        if data == "Server is full. Please try again later.":
            print(data)
            clientSocket.close()
            return
        else:
            clientName = data
            print(f"Connected to the server as {clientName}")
        while True:
            msg = input("Enter message ('exit' to quit): ")
            if msg:
                clientSocket.send(msg.encode())
                if msg.lower() == 'exit':
                    break
                data - clientSocket.recv(4096).decode()
                if not data:
                    print("Disconnected from server.")
                    break
                if data == "Server is full. Please try again later.":
                    print(data)
                    clientSocket.close()
                    return
                elif data.startswith('FILESIZE '):
                    try:
                        fileSize = int(data[9:])
                        clientSocket.send('READY'.encode())
                        while True:
                            fileName = input("Enter the filename to save as: ").strip()
                            if fileName:
                                fileName = os.path.basename(fileName)
                                break
                            else:
                                print("Filename cannot be empty. Please enter a valid filename.")
                        with open(fileName, 'wb') as f:
                            bytesReceived = 0
                            while bytesReceived < fileSize:
                                chunk = clientSocket.recv(1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                                bytesReceived += len(chunk)
                        print(f"File '{fileName}' received successfully.")
                    except ValueError:
                         print("Invalid file size received from server.")
                elif data.startswith("ERROR"):
                    print(f"Server response:\n{data}")
                else:
                    try:
                        jsonData = json.loads(data)
                        formattedJson = json.dumps(jsonData, indent=4)
                        print(f"Server response:\n{formattedJson}")
                    except json.JSONDecodeError:
                        print(f"Server response:\n{data}")
        clientSocket.close()
        print("Connection closed.")
    except ConnectionRefusedError:
        print("Could not connect to the server. Is the server running?")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        pass

    if __name__ == '__main__':
        startingClient()