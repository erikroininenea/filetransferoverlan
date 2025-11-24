import socket
import os
import struct

def ensure_folder_exists():
    from pathlib import Path
    desktop = Path.home() / "Desktop"
    folder = desktop / "Delade Filer"
    folder.mkdir(exist_ok=True)
    return folder

def main():
    save_folder = ensure_folder_exists()

    HOST = "0.0.0.0"
    PORT = 5001

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)
        print("Väntar på fil på port 5001...")

        while True:
            conn, addr = server.accept()
            print(f"Ansluten: {addr}")

            with conn:
                # Ta emot filnamn längd
                name_len = struct.unpack("!I", conn.recv(4))[0]
                filename = conn.recv(name_len).decode()

                # Ta emot filstorlek
                filesize = struct.unpack("!Q", conn.recv(8))[0]

                filepath = os.path.join(save_folder, filename)

                with open(filepath, "wb") as f:
                    remaining = filesize
                    while remaining > 0:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)

                print(f"✔ Fil mottagen: {filepath}")

if __name__ == "__main__":
    main()
