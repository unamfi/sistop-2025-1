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