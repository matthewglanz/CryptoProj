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
import sys

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

random.seed(1)

balance = 1000
paillierP = 2003 #PRIVATE
paillierQ = 2371 #PRIVATE
paillierLambda = 2372370 #PRIVATE
paillierN = paillierP * paillierQ #PUBLIC

paillierG = paillierN #GENERATED RANDOMLY (down below)
paillierR = 43922 #GENERATED RANDOMLY, i think this also has special properties but idk

#The cryptocounter to track excessive use of ATM
counter = 1
counterG = 525 #A primitive root of paillierP
counterI = 0
counterMu = pow(int(paillierL( exp(counterG, paillierLambda, paillierN*paillierN), paillierN)), -1, paillierN)

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
    key = 87281 #This is the SEED FOR THE RC4 STREAM ENCRYPTION
    
    #Encrypt it using bobs public key (RSAe)
    publicKey =int(conn.recv(1024).decode('utf-8'))
    
    #Randomize an r
    RSAr = random.randint(1, publicKey)

    #Encrypt using RSA with random padding
    randRSA = hashlib.new('sha1')
    randRSA.update(str(RSAr).encode('utf-8'))
    randRSAhash = int(randRSA.hexdigest(), 16)
    RSAy1 = exp(RSAr, publicKey, RSAn)
    RSAy2 = key ^ randRSAhash

    #Send the secret key to Bob (encrypted with his public key as y1 and y2)
    conn.sendall(str(RSAy1).encode('utf-8'))
    conn.sendall(str(RSAy2).encode('utf-8'))


    #Receive Bobs encrypted msg and encrypted MAC
    encryptedMsg = int(conn.recv(1024).decode('utf-8'))
    msg = encryptedMsg ^ key
    
    encryptedHash = int(conn.recv(1024).decode('utf-8'))
    MAChash = encryptedHash ^ key
    
    #Make sure the hashes match
    msgMAC = hashlib.new('sha1')
    msgMAC.update(str(msg).encode('utf-8'))
    #msgMAC.update("hi".encode('utf-8'))
    msgMAChash = int(msgMAC.hexdigest(), 16)    
    if(MAChash != msgMAChash):
        print("Error in hash values")
        random.seed(key)
        conn.sendall(sendRC4("Error"))
        conn.close()
        sys.exit()
    
    #END HANDSHAKE PROTOCOL, ESTABLISHED IT IS BOB
    
    #THE SHARED KEY IS USED AS THE SEED FOR RANDOMIZATION
    random.seed(key)
    
    conn.sendall(sendRC4("Welcome to CryptoBank, How can I help you today? \n Menu Options: \n || Balance || Withdraw || Deposit ||"))
    while True:
      data = receiveRC4(conn.recv(1024).decode('utf-8'))
      
         
      if not data:
        break
      print("Received:", data)
      
      #Compute the new cryptocounter
      counter = counter * exp(counterG, 1, paillierN*paillierN) * exp (494, paillierN, paillierN*paillierN) % (paillierN*paillierN)
      counterI += 1
      
      #Check if the user is suspiciously using the ATM too much...
      decCounter = paillierDecrypt(counter, paillierLambda, counterMu, paillierN)
      if(decCounter > 1000):
          conn.sendall(sendRC4("Error"))
          print("You have used the ATM too many times. It is now disabled for security reasons")
          conn.close()
          sys.exit()


      #balance
      if(data == "Balance"):
        conn.sendall(sendRC4("Your current balance is " + str(balance)))
      
      #withdraw
      elif(data == "Withdraw"):
        #send message asking for amount
        conn.sendall(sendRC4("How much would you like to withdraw? (Whole dollars)"))
        val = conn.recv(1024).decode('utf-8')
        amount = receiveRC4(val)
        if((amount.startswith('-') is True and amount[1:].isnumeric() is False) or (amount.startswith('-') is False and amount.isnumeric() is False)):
            conn.sendall(sendRC4("Error"))
            conn.close()
            sys.exit()
        amount = int(amount)
        
        if(amount > balance):
          conn.sendall(sendRC4("Insufficient Funds"))
        elif(amount < 0):
          conn.sendall(sendRC4("Cannot withdraw negative money"))
        else:
          cipherAmount = paillierEncrypt(paillierG, amount, paillierR, paillierN)
          cipherBalance = cipherBalance * pow(cipherAmount,-1, paillierN*paillierN)
          #balance = balance - amount
          balance = paillierDecrypt(cipherBalance, paillierLambda, paillierMu, paillierN)
          conn.sendall(sendRC4("Your new balance is " + str(balance)))
      
        #deposit
      elif(data == "Deposit"):
        #send message asking for amount
        conn.sendall(sendRC4("How much would you like to deposit? (Whole dollars)"))
        #receive amount
        val = conn.recv(1024).decode('utf-8')
        amount = receiveRC4(val)

        if((amount.startswith('-') is True and amount[1:].isnumeric() is False) or (amount.startswith('-') is False and amount.isnumeric() is False)):
            conn.sendall(sendRC4("Error"))
            conn.close()
            sys.exit()
        amount = int(amount)
        if(amount < 0):
            conn.sendall(sendRC4("Cannot deposit negative funds"))
        else: 
            cipherAmount = paillierEncrypt(paillierG, amount, paillierR, paillierN)
            cipherBalance = cipherBalance * cipherAmount
            balance = paillierDecrypt(cipherBalance, paillierLambda, paillierMu, paillierN)
            conn.sendall(sendRC4("Your new balance is " + str(balance)))
      
        #exit
      elif(data == "Exit"):
        conn.sendall(sendRC4("Goodbye!"))
        break
      
      else:
          conn.sendall(sendRC4("Invalid entry"))
      
    
    conn.close()