import socket
import os
import struct
import time
import math
from tkinter import *
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

# Fråga användaren om IP och port
CLIENT_IP = input("Skriv mottagarens IP-adress: ")
PORT = 5001  # Samma port som klienten lyssnar på

def human_readable(size_bytes):
    """Konvertera storlek i bytes till KB/MB/GB."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024))) if size_bytes > 0 else 0
    p = 1024 ** i
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def send_file(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((CLIENT_IP, PORT))

            # Skicka filnamn
            s.send(struct.pack("!I", len(filename)))
            s.send(filename.encode())

            # Skicka filstorlek
            s.send(struct.pack("!Q", filesize))

            # Skapa progress-fönster
            progress_win = Toplevel(root)
            progress_win.title(f"Skickar {filename}")
            progress_win.geometry("450x220")
            
            Label(progress_win, text=f"Skickar: {filename}", font=("Arial", 12)).pack(pady=5)

            progressbar = ttk.Progressbar(progress_win, orient=HORIZONTAL, length=400, mode='determinate')
            progressbar.pack(pady=10)

            percent_label = Label(progress_win, text="0%", font=("Arial", 10))
            percent_label.pack()

            size_label = Label(progress_win, text=f"0 / {human_readable(filesize)}", font=("Arial", 10))
            size_label.pack()

            remaining_label = Label(progress_win, text=f"Kvar: {human_readable(filesize)}", font=("Arial", 10))
            remaining_label.pack()

            time_label = Label(progress_win, text="Beräknad tid: -- s", font=("Arial", 10))
            time_label.pack(pady=5)

            # Skicka filinnehållet med progress
            sent = 0
            start_time = time.time()
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    s.send(chunk)
                    sent += len(chunk)

                    # Uppdatera progress
                    progress = int(sent / filesize * 100)
                    progressbar['value'] = progress
                    percent_label.config(text=f"{progress}%")

                    size_label.config(text=f"{human_readable(sent)} / {human_readable(filesize)}")
                    remaining_label.config(text=f"Kvar: {human_readable(filesize - sent)}")

                    elapsed = time.time() - start_time
                    if sent > 0 and elapsed > 0:
                        speed = sent / elapsed  # bytes per sec
                        remaining_time = (filesize - sent) / speed
                        time_label.config(text=f"Beräknad tid: {int(remaining_time)} s")

                    progress_win.update()

            messagebox.showinfo("Färdigt", f"Skickade: {filename}")
            progress_win.destroy()

    except Exception as e:
        print(f"❌ Kunde inte skicka filen: {e}")
        messagebox.showerror("Fel", f"Kunde inte skicka filen:\n{e}")

def drop_event(event):
    paths = root.splitlist(event.data)
    for file_path in paths:
        send_file(file_path)

# UI
root = TkinterDnD.Tk()
root.title("Fildelare - Dra in filer")

label = Label(root, text="Dra och släpp filer här", width=40, height=10,
              bg="#4c8bf5", fg="white", font=("Arial", 18))
label.pack(padx=20, pady=20)

label.drop_target_register(DND_FILES)
label.dnd_bind("<<Drop>>", drop_event)

root.mainloop()
