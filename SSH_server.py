import socket

HOST = 'localhost'
PORT = 1234

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
      message = input("Enter message: ")
      conn.sendall(message.encode('utf-8'))
      
    
  
  
