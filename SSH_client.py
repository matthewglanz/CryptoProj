# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 15:38:16 2023

@author: Andyroo
"""

import socket

HOST = 'localhost'
PORT = 1234

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  print(f"Connected to {HOST}:{PORT}")
  data = sock.recv(1024)
  print(f"{data.decode('utf-8').strip()}")
  while True:
    message = input("Enter message ('Exit' to quit): ")
    if(message.strip() == "Exit"):
      break
    sock.sendall(message.encode('utf-8'))
    data = sock.recv(1024)
    if not data:
      break
    print(f"Received: {data.decode('utf-8').strip()}")
  sock.close()