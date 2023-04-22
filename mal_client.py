import socket
import aes
import projecthmac
import rsa
import sha1

HOST = '127.0.0.1'
PORT = 25565


def hmacCheck(hashToCheck, message, key):
    if not projecthmac.hmacCheck(hashToCheck, message, key):
        print('Invalid hash. Connection lost.')
        quit()

def recMsg(socket, size):
    data = socket.recv(size)
    return data.decode()
    
def sendMessageEnc(msg, hmacKey, aesKey, iv, s):
    msg = msg + projecthmac.hmac(msg,hmacKey)
    msg = aes.aes_encrypt(msg, aesKey, iv)
    s.sendall(msg.encode())

f = open("replay.txt", "r")
counter = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:     
    s.connect((HOST, PORT))
    print("Welcome to the ATM! You may [c]heck balance, [d]eposit money, or [w]ithdraw money.")
    p,q,e,d =  rsa.keyGen()
    n = p*q
    print(recMsg(s, 4096))
    
    msg = str(e)+' '+str(n)
    s.sendall(msg.encode())
    
    # Receive data for keys and decrypt using RSA
    data = recMsg(s, 4096)
    keys = rsa.rsa_decrypt(data,[e,n],d)
    hmacKey = keys[:16]
    aesKey = keys[16:32]
    iv = keys[32:]
    
    hmacCheck(keys[-40:], keys[:-40], hmacKey)
    
    #username = input("Enter username: ")
    username = f.readline()
    sendMessageEnc(username, hmacKey, aesKey, iv, s)
    
    auth = recMsg(s, 4096)
    auth = aes.aes_decrypt(auth,aesKey,iv).strip()
    
    hmacCheck(auth[-40:], auth[:-40], hmacKey)
    
    print(auth[:-40])
    
    while True:
        #userIn = input("Enter command: ")
        userIn = f.readline()
        if(userIn == ""):
            print(counter, "cycles completed")
            f.seek(0,0)
            trash = f.readline()
            if(counter == 5):
                print("5 cycles completed, attack over")
                exit()
            counter+=1
            continue
            #Since theres no way to end the connection, just error out
            
        sendMessageEnc(userIn, hmacKey, aesKey, iv, s)
        response = recMsg(s, 4096)
        response = aes.aes_decrypt(response,aesKey,iv).strip()
        hmacCheck(response[-40:], response[:-40], hmacKey)
        print(response[:-40])
    
# A haiku right here
# A greeting from another
# For someone unknown