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

#RC4 is a stream cipher found in lecture notes 3.1
def simpRC4(ptext):
    
    key = []
    
    #Key Gen
    S = []
    for i in range(ptext):
        S.append(random.randint(0, 255))
        
    T = []
    for i in range(ptext):
        T.append(random.randint(0, 255))
        
    j = 0
    for i in range(ptext):
        j = (j + S[i] + T[i]) % ptext
        temp = S[i]
        S[i] = S[j]
        S[j] = temp
        
    #Loop through the plaintext and generate one bit of key per one bit of ptext
    j = 0
    for i in range(ptext):
        j = (j + S[i]) % ptext
        temp = S[i]
        S[i] = S[j]
        S[j] = temp
        t = (S[i] + S[j]) % ptext
        key.append(S[t])
        
    return key

#Key and ptext are list of ints (0-255)
#Returns an encrypted string
def encryptRC4(key, ptext):
    asciiText = []
    ans = []
    res = ""
    for i in range(len(ptext)):
        asciiText.append(ord(ptext[i]))
        ans.append(key[i] ^ asciiText[i])
        res = res + str(ans[i]) + "|"
    res = res[:-1]
    return res
    
#Key is a list of ints
#ctext is a string
#Returns a decrypted string
def decryptRC4(key, ctext):
    
    cipher = ctext.split("|")
    
    ans = []
    for i in range(len(cipher)):
        ans.append(key[i] ^ int(cipher[i]))
    
    #Convert the ints to chars
    word = ""
    for i in range(len(ans)):
        word = word + chr(ans[i])
    return word

#A quality of life function that generates the key and encryption for the message to send
def sendRC4(ptext):
    key = simpRC4(len(ptext))
    msg = (encryptRC4(key, ptext)).encode('utf-8')
    return msg

#A quality of life function that generates the key and decrypts the given ciphertext
def receiveRC4(ctext):
    key = simpRC4(ctext.count("|") + 1)
    msg = decryptRC4(key, ctext)
    return msg

def exp(x, e, n):
    ans = 1
    for i in range(e):
        ans = (ans * x) % n
    return ans

random.seed(1)

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
  
  #THIS SECRET KEY IS THE SEED FOR THE RC4 STREAM CIPHER
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
  
  #THIS KEY WAS ESTABLISHED THROUGH THE HANDSHAKE
  random.seed(secretKey)
  
  
  #Receive instructions on how to bank
  data = receiveRC4(sock.recv(1024).decode('utf-8'))
  print(data)
  
  
  while True:
    message = input("Enter message ('Exit' to quit): ")
  
    #Encrypt the message
    sock.sendall(sendRC4(message))
    
    #Receive the next msg
    data = sock.recv(1024).decode('utf-8')
    msg = receiveRC4(data)
    
    if(message == "Exit"):
      break
    
    if not data:
      break
    print("Received:", msg)
  sock.close()