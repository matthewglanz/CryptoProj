# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 15:38:16 2023
@author: Andyroo
"""

import socket
import time
import hashlib
import random
HOST = 'localhost'
PORT = 1234

def exp(x, e, n):
    ans = 1
    for i in range(e):
        ans = (ans * x) % n
    return ans

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  print(f"Connected to {HOST}:{PORT}")
  
  #BEGIN HANDSHAKE PROTOCOL
  
  #Build the certificate
  RSAp = 6073 #PRIVATE
  RSAq = 7727 #PRIVATE
  RSAn = RSAp*RSAq #PUBLIC, WILL BE SHARED = 46926071
  RSAphi = (RSAp - 1) * (RSAq - 1) #PRIVATE 46912272
  bob_id = str(random.randint(1, RSAn)) #Just a random ID to send to Server
  timestamp = str(time.time())
  RSAnToSend = str(RSAn)
  
  print(f"Sending certificate")
  sock.sendall(bob_id.encode('utf-8'))    #Part of certificate
  data = sock.recv(1024)
  sock.sendall(RSAnToSend.encode('utf-8'))#Part of certificate
  data = sock.recv(1024)
  sock.sendall(timestamp.encode('utf-8')) #Part of certificate
  data = sock.recv(1024)

  #Send the digest encrypted with bobs private key
  msg = hashlib.new('sha1')
  msg.update(b"I am Bob")
  hashVal = int(msg.hexdigest(), 16)
  
  #Encrypt the digest using bobs private key
  RSAe = 65537
  RSAd = 35345441 #BOBS PRIVATE KEY. DO NOT SHARE
  encryptedHash = exp(hashVal, RSAd, RSAn) #This becomes a digital signature
  
  #Send the digital signature, ONLY BOB CAN MAKE THIS EXACT SIGNATURE
  sock.sendall(str(encryptedHash).encode('utf-8'))
  
  #Send the public key
  sock.sendall(str(RSAe).encode('utf-8'))
  
  #Receive the shared encrypted key and decrypt it
  encryptedKey = int(sock.recv(1024).decode('utf-8'))
  secretKey = exp(encryptedKey, RSAd, RSAn)

  
  #Tell the server Bob has the secret key, send a MAC as well
  msg = random.randint(1, RSAn) #Msg for bob to send to server, this probably should be chagned to an actual string with meaning
  msgMAC = hashlib.new('sha1')
  msgMAC.update(str(msg).encode('utf-8'))
  msgMAChash = int(msgMAC.hexdigest(), 16)
  
  #Encrypt the Msg and the Hash with the secret key THIS NEEDS TO BE MADE MORE SECURE, DO NOT JUST XOR IT
  encryptedMsg = msg ^ secretKey
  encryptedMACHash = msgMAChash ^ secretKey

  #Send the msg and the MAC to the server
  sock.sendall(str(encryptedMsg).encode('utf-8'))
  sock.sendall(str(encryptedMACHash).encode('utf-8'))
  
  #DONE HANDSHAKE PROTOCOL
  
  
  
  
  
  #Receive instructions on how to bank
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