# Facultad de Ingenieria UNAM
# Autores: Suarez Guzman Dayna Yarelly
#	   Gonzalez Iniestra Emilio
# Asignatura: Sistemas Operativos

import struct
import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox

# Parámetros del sistema de archivos FiUnamFS
disk_file = "fiunamfs.img"
DISK_SIZE = 1440 * 1024  # Tamaño total del "disco" en bytes
CLUSTER_SIZE = 256 * 4   # Tamaño de cada cluster en bytes
DIRECTORY_START_CLUSTER = 1  # Cluster de inicio del directorio
DIRECTORY_END_CLUSTER = 4    # Cluster final del directorio
DIRECTORY_ENTRY_SIZE = 64    # Tamaño de cada entrada del directorio
FILE_NAME_SIZE = 15          # Tamaño máximo del nombre de archivo
IDENTIFICATION = b"FiUnamFS" # Identificación del sistema de archivos
VERSION = b"25-1"            # Versión del sistema de archivos

# Evento y variable compartida para sincronización entre hilos
operation_event = threading.Event()
operation_status = {
    'message': '',
    'success': False
}

def validate_and_read_superblock():
    """
    Valida la identificación y versión en el superbloque,
    y lee la etiqueta, tamaño y clusters.
    """
    try:
        with open(disk_file, "rb") as f:
            # Leer y validar Identificación
            f.seek(0)
            ident = f.read(8).strip(b"\x00").decode("ascii")  # Eliminar rellenos nulos
            if ident != IDENTIFICATION.decode("ascii"):
                messagebox.showerror("Error", "Identificación de sistema de archivos no coincide. Operación cancelada.")
                return None

            # Leer y validar Versión
            f.seek(10)
            version = f.read(5).strip(b"\x00").decode("ascii")
            if version != VERSION.decode("ascii"):
                messagebox.showerror("Error", "Versión de sistema de archivos no coincide. Operación cancelada.")
                return None

            # Leer Etiqueta del Volumen
            f.seek(20)
            label = f.read(16).decode("ascii").strip()

            # Leer Tamaño de Cluster
            f.seek(40)
            cluster_size = struct.unpack("<I", f.read(4))[0]

            # Leer Número de Clusters en el Directorio
            f.seek(45)
            directory_clusters = struct.unpack("<I", f.read(4))[0]

            # Leer Número de Clusters de la Unidad Completa
            f.seek(50)
            total_clusters = struct.unpack("<I", f.read(4))[0]

            return {
                "label": label,
                "cluster_size": cluster_size,
                "directory_clusters": directory_clusters,
                "total_clusters": total_clusters
            }
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo fiunamfs.img no existe.")
        return None

def list_directory():
    """
    Lista los archivos en el directorio de FiUnamFS.
    """
    files = []
    superblock = validate_and_read_superblock()
    if not superblock:
        return files

    try:
        with open(disk_file, "rb") as f:
            # Recorrer las entradas del directorio
            for cluster in range(DIRECTORY_START_CLUSTER, DIRECTORY_END_CLUSTER + 1):
                f.seek(cluster * CLUSTER_SIZE)
                for _ in range(CLUSTER_SIZE // DIRECTORY_ENTRY_SIZE):
                    entry_data = f.read(DIRECTORY_ENTRY_SIZE)
                    if not entry_data or entry_data[0] == 0x23:  # Entrada vacía '#'
                        continue
                    if entry_data[0] != 0x2e:  # Verificar tipo de archivo '.'
                        continue
                    # Obtener nombre del archivo
                    filename = entry_data[1:16].decode("ascii").strip("-")
                    # Obtener tamaño del archivo
                    filesize = struct.unpack("<I", entry_data[16:20])[0]
                    # Obtener fechas de creación y modificación
                    created_at = entry_data[24:38].decode("ascii")
                    modified_at = entry_data[38:52].decode("ascii")
                    files.append(f"{filename} - {filesize} bytes - Creado: {created_at} - Modificado: {modified_at}")
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo fiunamfs.img no existe.")
    return files

def copy_to_local(file_name):
    """
    Inicia un hilo para copiar un archivo de FiUnamFS al sistema local.
    """
    # Iniciar hilo de copia
    threading.Thread(target=copy_to_local_thread, args=(file_name,)).start()

def copy_to_local_thread(file_name):
    """
    Hilo que copia un archivo de FiUnamFS al sistema local.
    """
    save_path = filedialog.asksaveasfilename(title="Guardar archivo en sistema local", initialfile=file_name)
    if not save_path:
        return

    with threading.Lock():
        with open(disk_file, "rb") as f:
            found = False
            for cluster in range(DIRECTORY_START_CLUSTER, DIRECTORY_END_CLUSTER + 1):
                f.seek(cluster * CLUSTER_SIZE)
                for _ in range(CLUSTER_SIZE // DIRECTORY_ENTRY_SIZE):
                    entry_data = f.read(DIRECTORY_ENTRY_SIZE)
                    entry_name = entry_data[1:16].decode("ascii").strip("-")
                    if entry_name == file_name:
                        filesize = struct.unpack("<I", entry_data[16:20])[0]
                        start_cluster = struct.unpack("<I", entry_data[20:24])[0]
                        f.seek(start_cluster * CLUSTER_SIZE)
                        data = f.read(filesize)
                        with open(save_path, "wb") as out_file:
                            out_file.write(data)
                        operation_status['message'] = f"Archivo '{file_name}' copiado a '{save_path}'"
                        operation_status['success'] = True
                        found = True
                        break
                if found:
                    break
            else:
                operation_status['message'] = f"Archivo '{file_name}' no encontrado en FiUnamFS."
                operation_status['success'] = False

    # Notificar al hilo principal
    operation_event.set()

def copy_to_fiunamfs():
    """
    Inicia un hilo para copiar un archivo desde el sistema local a FiUnamFS.
    """
    threading.Thread(target=copy_to_fiunamfs_thread).start()

def copy_to_fiunamfs_thread():
    """
    Hilo que copia un archivo desde el sistema local a FiUnamFS.
    """
    local_path = filedialog.askopenfilename(title="Selecciona un archivo para copiar a FiUnamFS")
    if not local_path:
        return

    file_name = os.path.basename(local_path)
    file_size = os.path.getsize(local_path)

    # Tamaño total disponible para archivos en FiUnamFS (excluyendo superbloque y directorio)
    data_space_start = (DIRECTORY_END_CLUSTER + 1) * CLUSTER_SIZE
    max_data_space = DISK_SIZE - data_space_start

    # Verificar espacio disponible
    total_used_space = get_total_used_space()
    available_space = max_data_space - total_used_space

    if file_size > available_space:
        operation_status['message'] = f"No hay suficiente espacio en FiUnamFS para copiar '{file_name}'."
        operation_status['success'] = False
        operation_event.set()
        return

    with threading.Lock():
        with open(disk_file, "r+b") as f, open(local_path, "rb") as in_file:
            # Encontrar un espacio vacío en el directorio
            found_space = False
            for cluster in range(DIRECTORY_START_CLUSTER, DIRECTORY_END_CLUSTER + 1):
                f.seek(cluster * CLUSTER_SIZE)
                for _ in range(CLUSTER_SIZE // DIRECTORY_ENTRY_SIZE):
                    pos = f.tell()
                    entry_data = f.read(DIRECTORY_ENTRY_SIZE)
                    if entry_data[0] == 0x23:  # Entrada vacía '#'
                        # Escribir entrada de directorio
                        f.seek(pos)
                        f.write(b".")
                        f.write(file_name.encode("ascii").ljust(FILE_NAME_SIZE, b"-"))
                        f.write(struct.pack("<I", file_size))
                        # Calcular cluster inicial
                        start_cluster = (DISK_SIZE - available_space) // CLUSTER_SIZE
                        f.write(struct.pack("<I", start_cluster))
                        # Escribir fechas de creación y modificación
                        timestamp = time.strftime("%Y%m%d%H%M%S").encode("ascii")
                        f.write(timestamp)  # Fecha de creación
                        f.write(timestamp)  # Fecha de modificación
                        # Rellenar espacio restante de la entrada
                        f.write(b"\x00" * (DIRECTORY_ENTRY_SIZE - (f.tell() - pos)))
                        # Escribir datos del archivo
                        f.seek(start_cluster * CLUSTER_SIZE)
                        f.write(in_file.read())
                        operation_status['message'] = f"Archivo '{file_name}' copiado al sistema de archivos."
                        operation_status['success'] = True
                        found_space = True
                        break
                if found_space:
                    break
            else:
                operation_status['message'] = "No se encontró espacio libre en el directorio de FiUnamFS."
                operation_status['success'] = False

    # Notificar al hilo principal
    operation_event.set()

def delete_file(file_name):
    """
    Inicia un hilo para eliminar un archivo del FiUnamFS.
    """
    threading.Thread(target=delete_file_thread, args=(file_name,)).start()

def delete_file_thread(file_name):
    """
    Hilo que elimina un archivo del FiUnamFS.
    """
    with threading.Lock():
        with open(disk_file, "r+b") as f:
            found = False
            for cluster in range(DIRECTORY_START_CLUSTER, DIRECTORY_END_CLUSTER + 1):
                f.seek(cluster * CLUSTER_SIZE)
                for _ in range(CLUSTER_SIZE // DIRECTORY_ENTRY_SIZE):
                    pos = f.tell()
                    entry_data = f.read(DIRECTORY_ENTRY_SIZE)
                    entry_name = entry_data[1:16].decode("ascii").strip("-")
                    if entry_name == file_name:
                        # Marcar entrada como vacía
                        f.seek(pos)
                        f.write(b"#" + b"-" * (DIRECTORY_ENTRY_SIZE - 1))
                        operation_status['message'] = f"Archivo '{file_name}' eliminado del sistema de archivos."
                        operation_status['success'] = True
                        found = True
                        break
                if found:
                    break
            else:
                operation_status['message'] = f"Archivo '{file_name}' no encontrado en FiUnamFS."
                operation_status['success'] = False

    # Notificar al hilo principal
    operation_event.set()

def get_total_used_space():
    """
    Calcula el espacio total ocupado en FiUnamFS, excluyendo el superbloque y directorio.
    """
    total_used = 0
    try:
        with open(disk_file, "rb") as f:
            # Recorrer las entradas del directorio
            for cluster in range(DIRECTORY_START_CLUSTER, DIRECTORY_END_CLUSTER + 1):
                f.seek(cluster * CLUSTER_SIZE)
                for _ in range(CLUSTER_SIZE // DIRECTORY_ENTRY_SIZE):
                    entry_data = f.read(DIRECTORY_ENTRY_SIZE)
                    if entry_data and entry_data[0] == 0x2e:  # Entrada ocupada '.'
                        filesize = struct.unpack("<I", entry_data[16:20])[0]
                        total_used += filesize
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo fiunamfs.img no existe.")
    return total_used

def refresh_list():
    """
    Actualiza la lista de archivos en la interfaz gráfica.
    """
    file_list.delete(0, tk.END)
    files = list_directory()
    for file in files:
        file_list.insert(tk.END, file)

def check_operation_status():
    """
    Verifica el estado de las operaciones realizadas por los hilos y actualiza la interfaz.
    """
    if operation_event.is_set():
        if operation_status['success']:
            messagebox.showinfo("Éxito", operation_status['message'])
        else:
            messagebox.showerror("Error", operation_status['message'])
        # Limpiar el estado para futuras operaciones
        operation_event.clear()
        operation_status['message'] = ''
        operation_status['success'] = False
        # Refrescar la lista de archivos
        refresh_list()
    # Continuar verificando periódicamente
    root.after(100, check_operation_status)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Gestor de FiUnamFS")

# Lista de archivos en la interfaz
file_list = Listbox(root, width=80)
file_list.pack()

# Botones de operación
btn_list = tk.Button(root, text="Listar Archivos", command=refresh_list)
btn_list.pack(pady=5)

btn_copy_to_local = tk.Button(root, text="Copiar a Local",
                              command=lambda: copy_to_local(file_list.get(tk.ACTIVE).split(" - ")[0]))
btn_copy_to_local.pack(pady=5)

btn_copy_to_fiunamfs = tk.Button(root, text="Copiar a FiUnamFS", command=copy_to_fiunamfs)
btn_copy_to_fiunamfs.pack(pady=5)

btn_delete = tk.Button(root, text="Eliminar Archivo",
                       command=lambda: delete_file(file_list.get(tk.ACTIVE).split(" - ")[0]))
btn_delete.pack(pady=5)

# Iniciar la verificación del estado de operaciones
root.after(100, check_operation_status)

# Ejecutar la aplicación
root.mainloop()