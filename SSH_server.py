import socket

HOST = 'localhost'
PORT = 1234

balance = 1000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.bind((HOST, PORT))
  sock.listen()
  print(f"Listening on {HOST}:{PORT}")

  conn, addr = sock.accept()
  with conn:
    print(f"Connected by {addr}")
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
      if(data.decode('utf-8').strip() == "Withdraw"):
        #send message asking for amount
        conn.sendall("How much would you like to withdraw?".encode('utf-8'))
        #receive amount
        data = conn.recv(1024)
        amount = int(data.decode('utf-8').strip())
        if(amount > balance):
          conn.sendall("Insufficient Funds".encode('utf-8'))
        else:
          balance = balance - amount
          conn.sendall(f"Your new balance is {balance}".encode('utf-8'))
      #deposit
      if(data.decode('utf-8').strip() == "Deposit"):
        #send message asking for amount
        conn.sendall("How much would you like to deposit?".encode('utf-8'))
        #receive amount
        data = conn.recv(1024)
        amount = int(data.decode('utf-8').strip())
        balance = balance + amount
        conn.sendall(f"Your new balance is {balance}".encode('utf-8'))
      #exit
      if(data.decode('utf-8').strip() == "Exit"):
        conn.sendall("Goodbye!".encode('utf-8'))
        break
    conn.close()

          
    
  
  
