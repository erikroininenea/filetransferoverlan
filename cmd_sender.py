import socket

# IP och port till klienten
HOST = input("Ange klientens IP: ")  
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"[INFO] Ansluten till {HOST}:{PORT}")
    
    while True:
        command = input("Skriv kommando (eller 'exit' för att stänga): ")
        s.sendall(command.encode())
        if command.lower() == 'exit':
            break
        data = s.recv(4096)
        print(data.decode())
