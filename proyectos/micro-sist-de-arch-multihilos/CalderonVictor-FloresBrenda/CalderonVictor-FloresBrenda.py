import struct
import os
from threading import Lock
from datetime import datetime

# Configuración de archivo y tamaño de cluster
DISK_FILE = '../fiunamfs.img'
CLUSTER_SIZE = 256 * 4   # 4 clusters de 256 bytes
DISK_SIZE = 1440 * 1024  # 1440 KB

# Bloqueo para sincronización
lock = Lock()

def verificar_superbloque():
    """Verifica los datos del superbloque para asegurar que sea el sistema FiUnamFS."""
    with open(DISK_FILE, 'rb') as disk:
        disk.seek(0)
        magic = disk.read(8).decode('ascii')
        if magic != "FiUnamFS":
            raise ValueError("No es un sistema de archivos FiUnamFS.")
        version = disk.read(5).decode('ascii')
        print(f"Versión del sistema: {version}")

def inicializar_mapa_almacenamiento():
    """Inicializa el mapa de almacenamiento para los clusters."""
    # Marcamos los primeros clusters como ocupados (superbloque y directorio)
    mapa = [1] * 5 + [0] * ((DISK_SIZE // CLUSTER_SIZE) - 5)
    return mapa

# Iniciar el superbloque
try:
    verificar_superbloque()
    print("Superbloque verificado con éxito.")
    mapa_almacenamiento = inicializar_mapa_almacenamiento()
except ValueError as e:
    print(e)
