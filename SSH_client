import socket

HOST = 'localhost'
PORT = 1234

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  print(f"Connected to {HOST}:{PORT}")
  while True:
    message = input("Enter message: ")
    sock.sendall(message.encode('utf-8'))
    data = sock.recv(1024)
    if not data:
      break
    print(f"Received: {data.decode('utf-8').strip()}")
