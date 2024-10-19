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
# Variables
import socket
import sys
import os
import json

# Configuring Server
SERVER_HOST = 'localhost'
SERVER_PORT = 3000

def initiateClientConnection():
    """
    Function to initiate the client and connect to the server.
    Handles sending and receiving messages in sequence.
    """
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((SERVER_HOST, SERVER_PORT))

        # Receive the initial message from the server
        serverMessage = clientSocket.recv(1024).decode()
        if serverMessage == "Server is full. Please try again later.":
            print(serverMessage)
            clientSocket.close()
            return
        else:
            clientName = serverMessage
            print(f"Connected to the server as {clientName}")

        while True:
            userMessage = input("Enter message ('exit' to quit): ")
            if userMessage:
                clientSocket.send(userMessage.encode())
                if userMessage.lower() == 'exit':
                    break

                # Wait for server response
                serverResponse = clientSocket.recv(4096).decode()
                if not serverResponse:
                    print("Disconnected from server.")
                    break

                # Handle server full message
                if serverResponse == "Server is full. Please try again later.":
                    print(serverResponse)
                    clientSocket.close()
                    return
                elif serverResponse.startswith('FILESIZE '):
                    # Handle file transfer initiation
                    try:
                        fileSize = int(serverResponse[9:])
                        clientSocket.send('READY'.encode())

                        # Receive the file data
                        while True:
                            saveAsFileName = input("Enter the filename to save as: ").strip()
                            if saveAsFileName:
                                # Prevent directory traversal attacks
                                saveAsFileName = os.path.basename(saveAsFileName)
                                break
                            else:
                                print("Filename cannot be empty. Please enter a valid filename.")

                        with open(saveAsFileName, 'wb') as file:
                            bytesReceived = 0
                            while bytesReceived < fileSize:
                                fileChunk = clientSocket.recv(1024)
                                if not fileChunk:
                                    break
                                file.write(fileChunk)
                                bytesReceived += len(fileChunk)
                        print(f"File '{saveAsFileName}' received successfully.")
                    except ValueError:
                        print("Invalid file size received from server.")
                elif serverResponse.startswith("ERROR"):
                    # Handle error messages from the server
                    print(f"Server response:\n{serverResponse}")
                else:
                    try:
                        # Try to parse the data as JSON
                        parsedJson = json.loads(serverResponse)
                        # Pretty-print the JSON data
                        formattedJson = json.dumps(parsedJson, indent=4)
                        print(f"Server response:\n{formattedJson}")
                    except json.JSONDecodeError:
                        # If not JSON, just print the data
                        print(f"Server response:\n{serverResponse}")

        clientSocket.close()
        print("Connection closed.")

    except ConnectionRefusedError:
        print("Could not connect to the server. Is the server running?")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        pass

if __name__ == '__main__':
    initiateClientConnection()
