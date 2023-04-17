RSAp = 6073 #PRIVATE
RSAq = 7727 #PRIVATE
RSAn = RSAp*RSAq #PUBLIC, WILL BE SHARED = 46926071

RSAr = random.randint(1, RSAn)

randRSA = hashlib.new('sha1')
randRSA.update(str(RSAr).encode('utf-8'))
randRSAhash = int(randRSA.hexdigest(), 16)

RSAy1 = exp(RSAr, RSAe, RSAn)
RSAy2 = msg ^ randRSAhash

sock.sendall(str(RSAy1).encode('utf-8'))
sock.sendall(str(RSAy2).encode('utf-8'))

''''''

RSAy1 = int(conn.recv(1024).decode('utf-8'))
RSAy2 = int(conn.recv(1024).decode('utf-8'))

decrypted_r = exp(RSAy1, d, RSAn)
randRSA = hashlib.new('sha1')
randRSA.update(str(decrypted_r).encode('utf-8'))
randRSAhash = int(randRSA.hexdigest(), 16)
decrypted_msg = RSAy2 ^ decrypted_r