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
import threading
import sys

# Configuring Server
SERVER_HOST = 'localhost'
SERVER_PORT = 3000
stopThread = threading.Event()

"""
This is a thread function that 
will receive messages from the server
"""
