'''import socket
import time
import hashlib
import random
import sys

def exp(x, e, n):
    ans = 1
    for i in range(e):
        ans = (ans * x) % n
    return ans

msg = 111
RSAp = 6073 #PRIVATE
RSAq = 7727 #PRIVATE
RSAn = RSAp*RSAq #PUBLIC, WILL BE SHARED = 46926071
RSAe = 65537
RSAd = 35345441 #BOBS PRIVATE KEY. DO NOT SHARE

'''
RSAr = random.randint(1, RSAn)

randRSA = hashlib.new('sha1')
randRSA.update(str(RSAr).encode('utf-8'))
randRSAhash = int(randRSA.hexdigest(), 16)

RSAy1 = exp(RSAr, RSAe, RSAn)
RSAy2 = msg ^ randRSAhash
'''
sock.sendall(str(RSAy1).encode('utf-8'))
sock.sendall(str(RSAy2).encode('utf-8'))
'''
''''''
'''
RSAy1 = int(conn.recv(1024).decode('utf-8'))
RSAy2 = int(conn.recv(1024).decode('utf-8'))
'''
decrypted_r = exp(RSAy1, RSAd, RSAn)
msgrandRSA = hashlib.new('sha1')
msgrandRSA.update(str(decrypted_r).encode('utf-8'))
msgrandRSAhash = int(msgrandRSA.hexdigest(), 16)

'''
if(randRSAhash != msgrandRSAhash):
    print("Error in hash values")
'''

decrypted_msg = RSAy2 ^ msgrandRSAhash