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