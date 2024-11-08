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

def listar_directorio():
    """Lista el contenido del directorio en fiunamfs.img."""
    with lock:
        print("Contenido del directorio:")
        with open(DISK_FILE, 'rb') as disk:
            disk.seek(CLUSTER_SIZE)  # Iniciar en el primer cluster del directorio
            for i in range(4 * (CLUSTER_SIZE // 64)):  # Recorrer 4 clusters, 64 bytes por entrada
                entry = disk.read(64)
                tipo = entry[0:1].decode('ascii')
                
                # Ignorar entradas vacías
                if tipo == '-' or tipo == '#':
                    continue
                
                nombre = entry[1:16].decode('ascii').strip()
                tamano = struct.unpack('<I', entry[16:20])[0]
                
                # Formateo de la salida
                print(f"Archivo: {nombre}, Tamaño: {tamano} bytes")

def copiar_desde_fiunamfs(nombre_archivo):
    """Copia un archivo desde FiUnamFS al sistema local."""
    encontrado = False
    nombre_archivo = nombre_archivo.strip()
    
    with lock:
        with open(DISK_FILE, 'rb') as disk:
            disk.seek(CLUSTER_SIZE)  # Inicia en el directorio
            for i in range(4 * (CLUSTER_SIZE // 64)):
                entry = disk.read(64)
                tipo = entry[0:1].decode('ascii')
                nombre = entry[1:16].decode('ascii').strip()
                
                if tipo == '.' and nombre == nombre_archivo:
                    tamano = struct.unpack('<I', entry[16:20])[0]
                    cluster_inicial = struct.unpack('<I', entry[20:24])[0]
                    
                    # Ir al inicio de los datos del archivo
                    disk.seek(cluster_inicial * CLUSTER_SIZE)
                    data = disk.read(tamano)
                    
                    # Guardar en el sistema local
                    with open(nombre_archivo, 'wb') as f_out:
                        f_out.write(data)
                    print(f"Archivo '{nombre_archivo}' copiado al sistema local.")
                    encontrado = True
                    break
        if not encontrado:
            print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS.")

# Iniciar el superbloque
try:
    verificar_superbloque()
    print("Superbloque verificado con éxito.")
    mapa_almacenamiento = inicializar_mapa_almacenamiento()
except ValueError as e:
    print(e)
