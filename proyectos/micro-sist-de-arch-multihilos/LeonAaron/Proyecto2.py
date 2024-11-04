import os
import struct
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, scrolledtext
from threading import Thread, Lock

# Ruta del sistema de archivos
sistema_archivos = "fiunamfs.img"
archivo_sist = []  # Lista de datos de los archivos a imprimir
buffer_archivos = Lock()

# Clase para gestionar el sistema de archivos FiUnamFS
class FiUnamFS:
    def __init__(self, disk_file):
        self.disk_file = disk_file
        self.load_superblock()
    
    def load_superblock(self):
        with open(self.disk_file, 'rb') as file:
            file.seek(0)
            superbloque = file.read(1024)
            nombre = superbloque[0:8].decode().strip('\x00')
            version = superbloque[10:15].decode().strip('\x00')
            if nombre != "FiUnamFS" or version != "25-1":
                messagebox.showerror("Error", "El sistema de archivos no es FiUnamFS o la versión no es compatible")
                exit(1)
            else:
                messagebox.showinfo("Verificación", "El archivo .img es válido y compatible con FiUnamFS")
    
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

    def copy_from_system(self, source_path):
        if not os.path.exists(source_path):
            messagebox.showerror("Error", "El archivo no existe en el sistema")
            return
        file_size = os.path.getsize(source_path)
        file_name = os.path.basename(source_path)
        if len(file_name) > 15:
            messagebox.showerror("Error", "El nombre del archivo es demasiado largo")
            return
        with open(source_path, 'rb') as src_file:
            data = src_file.read()
        with open(self.disk_file, 'r+b') as file:
            file.seek(1024)
            for i in range(64):
                pos = file.tell()
                entry = file.read(64)
                file_type = entry[0:1]
                if file_type == b'#':
                    file.seek(pos)
                    file.write(b'-' + file_name.ljust(15).encode('ascii'))
                    file.write(struct.pack('<I', file_size))
                    file.write(struct.pack('<I', 5 + i))
                    file.write(datetime.now().strftime('%Y%m%d%H%M%S').encode('ascii'))
                    file.write(datetime.now().strftime('%Y%m%d%H%M%S').encode('ascii'))
                    file.seek((5 + i) * 1024)
                    file.write(data)
                    messagebox.showinfo("Éxito", f"Archivo '{file_name}' copiado a FiUnamFS")
                    return
            messagebox.showerror("Error", "No hay espacio en FiUnamFS para el archivo")

    def delete_file(self, filename):
        with open(self.disk_file, 'r+b') as file:
            file.seek(1024)
            for _ in range(64):
                pos = file.tell()
                entry = file.read(64)
                file_name = entry[1:16].decode('ascii').strip('\x00').strip()
                if file_name == filename.strip():  # Aseguramos comparación sin espacios
                    file.seek(pos)
                    file.write(b'#' + b' ' * 63)
                    messagebox.showinfo("Éxito", f"Archivo '{filename}' eliminado de FiUnamFS")
                    return
        messagebox.showerror("Error", f"Archivo '{filename}' no encontrado en FiUnamFS")

# Funciones de la interfaz gráfica
def listar_archivos():
    fiunamfs.list_directory()
    text_area.config(state='normal')
    text_area.delete(1.0, tk.END)
    for archivo in archivo_sist:
        text_area.insert(tk.END, archivo + "\n")
    text_area.config(state='disabled')

def copiar_a_sistema():
    filename = simpledialog.askstring("Copiar a sistema", "Ingrese el nombre del archivo:")
    dest_path = filedialog.askdirectory()
    fiunamfs.copy_to_system(filename, dest_path)

def copiar_a_fiunamfs():
    source_path = filedialog.askopenfilename()
    fiunamfs.copy_from_system(source_path)

def eliminar_archivo():
    filename = simpledialog.askstring("Eliminar archivo", "Ingrese el nombre del archivo a eliminar:")
    fiunamfs.delete_file(filename)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("FiUnamFS")
root.geometry("500x500")
root.configure(bg='light gray')

fiunamfs = FiUnamFS(sistema_archivos)

# Botones de la interfaz
btn_verificar = tk.Button(root, text="Verificar archivo .img", command=fiunamfs.load_superblock)
btn_verificar.pack(pady=5)

btn_listar = tk.Button(root, text="Listar Archivos", command=listar_archivos)
btn_listar.pack(pady=5)

btn_copiar_sistema = tk.Button(root, text="Copiar a Sistema (de FiUnamFS)", command=copiar_a_sistema)
btn_copiar_sistema.pack(pady=5)

btn_copiar_fiunamfs = tk.Button(root, text="Copiar a FiUnamFS (del Sistema)", command=copiar_a_fiunamfs)
btn_copiar_fiunamfs.pack(pady=5)

btn_eliminar = tk.Button(root, text="Eliminar Archivo de FiUnamFS", command=eliminar_archivo)
btn_eliminar.pack(pady=5)

# Área de texto para mostrar archivos
text_area = scrolledtext.ScrolledText(root, width=60, height=15, state='disabled')
text_area.pack(pady=10)

# Botón para cerrar el programa
btn_salir = tk.Button(root, text="Cerrar Programa", command=root.quit)
btn_salir.pack(pady=5)

root.mainloop()
