import rsa
import projecthmac
import socket
import aes
import sha1
import random
import paillier

def hmacCheck(hashToCheck, message, key):
    if not projecthmac.hmacCheck(hashToCheck, message, key):
        print('Invalid hash. Connection lost.')
        quit()

def generateKey(size):
    ans = ''
    for i in range(size):
        ans = ans + chr(random.randint(0,255))
    return ans

def receive(socket, size):
    data = socket.recv(size)
    return data.decode()
    
def sendMessageEnc(msg, hmacKey, aesKey, iv):
    msg = msg + projecthmac.hmac(msg,hmacKey)
    msg = aes.aes_encrypt(msg, aesKey, iv)
    conn.sendall(msg.encode())
    
HOST = '127.0.0.1'
PORT = 25565

filename = "replay.txt"
f = open(filename, "w")

transactions = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:     
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected to', addr)
        conn.sendall("You've connected to the Bank".encode())
        
        clientPubkey = list(map(int,receive(conn, 4096).split(' ')))
        
        hmacKey = generateKey(16)
        aesKey = generateKey(16)
        iv = generateKey(16)
        
        msg = str(hmacKey) + str(aesKey) + str(iv)
        msg = msg + projecthmac.hmac(msg,hmacKey)
        keys = rsa.rsa_encrypt(msg, clientPubkey)
        conn.sendall(keys.encode())
        
        username = receive(conn, 4096)
        username = aes.aes_decrypt(username,aesKey,iv).strip()
            
        f.write(username[:-40])
        f.write("\n")
        
        hmacCheck(username[-40:], username[:-40], hmacKey)
        
        print(username[:-40]+" connected.")
        msg = 'Welcome, '+username[:-40]
        sendMessageEnc(msg, hmacKey, aesKey, iv)
        
        g,p,q,lamb,u = paillier.palKeyGen(10)
        n = p*q
        
        #Have the user already start with some money
        balance = 0
        balance = paillier.palEnc(g, balance, n, u)
        
        while True:
            data = receive(conn, 4096)
            data = aes.aes_decrypt(data,aesKey,iv).strip()
            
            hmacCheck(data[-40:],data[:-40],hmacKey)
            
            msg = 'Unknown command'
            if data[0] == 'c':
                msg = 'Your balance is: $'+str(paillier.palDec(balance, lamb, n, u))
            if data[0] == 'd':
                if len(data) < 43:
                    msg = "Usage: [d amount] (For example: 'd 100')"
                else:
                    amt = int(data[2:-40])
                    amtEnc = paillier.palEnc(g, amt, n, u)
                    balance = paillier.palAdd(balance, amtEnc)
                    msg = 'Your balance is: $'+str(paillier.palDec(balance, lamb, n, u))
            if data[0] == 'w':
                if len(data) < 43:
                    msg = "Usage: [w amount] (For example: 'w 100')"
                else:
                    amt = int(data[2:-40])
                    if amt > paillier.palDec(balance, lamb, n, u):
                        msg = "I'm sorry, I can't give credit! Come back when you're a little... mmm... richer!"
                    else:
                        amtEnc = paillier.palEnc(g, -amt, n, u)
                        balance = paillier.palAdd(balance, amtEnc)
                        msg = 'Your balance is: $'+str(paillier.palDec(balance, lamb, n, u))

            f.write(data[0:-40])
            f.write("\n")
            f.flush()
            sendMessageEnc(msg, hmacKey, aesKey, iv)
            
        
        
        
f.close()
# A night spent coding
# Relaxation on my mind
# It has not yet come