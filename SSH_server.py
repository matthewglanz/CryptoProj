# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 15:39:40 2023
@author: Andyroo
"""

import socket
import math
import random
import time
import hashlib

def exp(x, e, n):
    ans = 1
    for i in range(e):
        ans = (ans * x) % n
    return ans

def modInverse(a, m):
    x = 1
    g = math.gcd(a, m)
    if(g != 1): 
        print("Error: inverse doesnt exist")
    else:
        res = (x % m + m) % m
        
    return res

def paillierL(x, n):
    return ((x-1) % (n*n)) / n

def paillierEncrypt(g, m, r, n):
    temp1 = g
    if(m == 0):
        g = 1
    else:
        for i in range(m-1):
            g = (g * temp1) % (n*n)

    temp2 = r
    for i in range(n-1):
        r = (r * temp2) % (n*n)
    
    return (g*r) % (n*n)

def paillierDecrypt(c, lamb, mu, n):
    temp = c % (n*n)
    for i in range(lamb - 1):
        c = (c*temp) % (n*n)
    return (paillierL(c, n)*mu) % n

    
HOST = 'localhost'
PORT = 1234

balance = 1000
paillierP = 2003 #PRIVATE
paillierQ = 2371 #PRIVATE
paillierLambda = 2372370 #PRIVATE
paillierN = paillierP * paillierQ #PUBLIC

paillierG = paillierN #GENERATED RANDOMLY (down below)
paillierR = 43922 #GENERATED RANDOMLY, i think this also has special properties but idk

while( math.gcd(paillierG, paillierN*paillierN) != 1):
    paillierG = random.randint(1, paillierN)

#Find the inverse
paillierMu = pow(int(paillierL( exp(paillierG, paillierLambda, paillierN*paillierN), paillierN)), -1, paillierN)

#Encrypt the balance. Do all operations on cipherbalance.
cipherBalance = paillierEncrypt(paillierG, balance, paillierR, paillierN)

#Decrypt the balance.
#decryptedBalance = paillierDecrypt(cipherbalance, paillierLambda, paillierMu, paillierN)      


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.bind((HOST, PORT))
  sock.listen()
  print(f"Listening on {HOST}:{PORT}")

  conn, addr = sock.accept()
  
  #Perform SSL handshake protocol
  #bobID = conn.recv(1024).decode('utf-8') #RECEIVE BOBS ID
  #conn.sendall(f"Received bob's ID".encode('utf-8'))
  #idk what to do with his id, i guess just leave it
  """ public_key = conn.recv(1024).decode('utf-8') #RECEIVE PUBLIC KEY
  receivedTimeStamp = conn.recv(1024).decode('utf-8')
  print(f"{bobID}")
  print(f"{public_key}")
  print(f"{receivedTimeStamp}")"""
  #print(bobID)
  
  with conn:
    print(f"Connected by {addr}")
    
    #BEGIN HANDSHAKE PROTOCOL
    
    #Receive bobs ID, the RSAn value, and timestamp
    bobID = conn.recv(1024).decode('utf-8')
    conn.sendall("Received bob's ID".encode('utf-8'))
    RSAn = int(conn.recv(1024).decode('utf-8'))
    conn.sendall("Received bob's public key".encode('utf-8'))
    ts = round(float(conn.recv(1024).decode('utf-8')), 1)
    conn.sendall("Received timestamp".encode('utf-8'))
    timestamp = round(time.time(), 1)

    if(ts != timestamp):
        print("Outdated timestamp")
        #NEED TO DO SOME KIND OF ERROR HERE
        
    #Receive the digest (a signature)
    signature = conn.recv(1024).decode('utf-8')
    
    #Send the secret key to be used
    key = 87281 #This is the key to be used for encryptions
    
    #Encrypt it using bobs public key (RSAe)
    publicKey =int(conn.recv(1024).decode('utf-8'))
    encryptedKey = exp(key, publicKey, RSAn)
    #Send the secret key to Bob (encrypted with his public key)
    conn.sendall(str(encryptedKey).encode('utf-8'))

    #Receive Bobs encrypted msg and encrypted MAC
    encryptedMsg = int(conn.recv(1024).decode('utf-8'))
    msg = encryptedMsg ^ key
    
    encryptedHash = int(conn.recv(1024).decode('utf-8'))
    MAChash = encryptedHash ^ key
    
    #Make sure the hashes match
    msgMAC = hashlib.new('sha1')
    msgMAC.update(str(msg).encode('utf-8'))
    msgMAChash = int(msgMAC.hexdigest(), 16)    
    if(MAChash != msgMAChash):
        print("Error in hash values")
        #NEED AN ERROR STATEMENT HERE, should NOT be able to continue
    
    #END HANDSHAKE PROTOCOL, ESTABLISHED IT IS BOB
    
    
    conn.sendall("Welcome to CryptoBank, How can I help you today? \n Menu Options: \n || Balance || Withdraw || Deposit ||".encode('utf-8'))
    while True:
      data = conn.recv(1024)
      if not data:
        break
      print(f"Received: {data.decode('utf-8').strip()}")
      
      #balance
      if(data.decode('utf-8').strip() == "Balance"):
        conn.sendall(f"Your current balance is {balance}".encode('utf-8'))
      
      #withdraw
      elif(data.decode('utf-8').strip() == "Withdraw"):
        #send message asking for amount
        conn.sendall("How much would you like to withdraw?".encode('utf-8'))
      
        #receive amount
        data = conn.recv(1024)
        amount = int(data.decode('utf-8').strip())
        if(amount > balance or amount < 0):
          conn.sendall("Insufficient Funds".encode('utf-8'))
        else:
          cipherAmount = paillierEncrypt(paillierG, amount, paillierR, paillierN)
          cipherBalance = cipherBalance * pow(cipherAmount,-1, paillierN*paillierN)
          #balance = balance - amount
          balance = paillierDecrypt(cipherBalance, paillierLambda, paillierMu, paillierN)
          conn.sendall(f"Your new balance is {balance}".encode('utf-8'))
      
        #deposit
      elif(data.decode('utf-8').strip() == "Deposit"):
        #send message asking for amount
        conn.sendall("How much would you like to deposit?".encode('utf-8'))
        #receive amount
        data = conn.recv(1024)
        amount = int(data.decode('utf-8').strip())
        if(amount < 0):
            conn.sendall("Cannot deposit negative funds".encode('utf-8'))
        cipherAmount = paillierEncrypt(paillierG, amount, paillierR, paillierN)
        cipherBalance = cipherBalance * cipherAmount
        balance = paillierDecrypt(cipherBalance, paillierLambda, paillierMu, paillierN)
        conn.sendall(f"Your new balance is {balance}".encode('utf-8'))
      
        #exit
      elif(data.decode('utf-8').strip() == "Exit"):
        conn.sendall("Goodbye!".encode('utf-8'))
        break
      
      else:
          conn.sendall("Invalid entry".encode('utf-8'))
      
    
    conn.close()
