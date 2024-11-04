import os
import struct
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, scrolledtext
from threading import Lock

# Ruta del sistema de archivos
sistema_archivos = "fiunamfs.img"
archivo_sist = []  # Lista de datos de los archivos a imprimir
buffer_archivos = Lock()

# Clase para gestionar el sistema de archivos FiUnamFS
class FiUnamFS:
    def __init__(self, disk_file):
        self.disk_file = disk_file
        self.load_superblock()  # Verificación del archivo y carga inicial del superbloque
    
    def load_superblock(self):
        with open(self.disk_file, 'rb') as file:
            file.seek(0)
            superbloque = file.read(1024)
            nombre = superbloque[0:8].decode().strip('\x00')
            version = superbloque[10:15].decode().strip('\x00')
            if nombre != "FiUnamFS" or version != "25-1":
                messagebox.showerror("Error", "El sistema de archivos no es FiUnamFS o la versión no es compatible")
                exit(1)

    def list_directory(self):
        global archivo_sist
        archivo_sist.clear()
        with open(self.disk_file, 'rb') as file:
            file.seek(1024)  # Inicio del directorio
            for _ in range(64):
                entry = file.read(64)
                file_type = entry[0:1]
                if file_type != b'#':
                    file_name = entry[1:16].decode('ascii').strip('\x00').strip()
                    file_size = struct.unpack('<I', entry[16:20])[0]
                    creation_time = entry[24:37].decode('ascii').strip('\x00').strip()
                    modification_time = entry[38:51].decode('ascii').strip('\x00').strip()
                    archivo_sist.append(f"Nombre: {file_name}, Tamaño: {file_size}, Creación: {creation_time}, Modificación: {modification_time}")
        buffer_archivos.acquire()
        buffer_archivos.release()

# Función para listar archivos en la interfaz
def listar_archivos():
    fiunamfs.list_directory()
    text_area.config(state='normal')
    text_area.delete(1.0, tk.END)
    for archivo in archivo_sist:
        text_area.insert(tk.END, archivo + "\n")
    text_area.config(state='disabled')
        def copy_to_system(self, filename, dest_path):
        with open(self.disk_file, 'rb') as file:
            file.seek(1024)
            for _ in range(64):
                entry = file.read(64)
                file_name = entry[1:16].decode('ascii').strip('\x00').strip()
                if file_name == filename.strip():  # Aseguramos comparación sin espacios
                    file_size = struct.unpack('<I', entry[16:20])[0]
                    cluster_start = struct.unpack('<I', entry[20:24])[0]
                    file.seek(cluster_start * 1024)
                    data = file.read(file_size)
                    with open(os.path.join(dest_path, filename), 'wb') as output_file:
                        output_file.write(data)
                    messagebox.showinfo("Éxito", f"Archivo '{filename}' copiado a '{dest_path}'")
                    return
        messagebox.showerror("Error", f"Archivo '{filename}' no encontrado")

# Función para copiar un archivo de FiUnamFS al sistema
def copiar_a_sistema():
    filename = simpledialog.askstring("Copiar a sistema", "Ingrese el nombre del archivo:")
    dest_path = filedialog.askdirectory()
    fiunamfs.copy_to_system(filename, dest_path)
