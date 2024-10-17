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
