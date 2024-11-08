import struct
import os
from threading import Lock
from datetime import datetime

DISK_FILE = '../fiunamfs.img'
CLUSTER_SIZE = 256 * 4
DISK_SIZE = 1440 * 1024

lock = Lock()

def verificar_superbloque():
    with open(DISK_FILE, 'rb') as disk:
        disk.seek(0)
        magic = disk.read(8).decode('ascii')
        if magic != "FiUnamFS":
            raise ValueError("No es un sistema de archivos FiUnamFS.")
        version = disk.read(5).decode('ascii')
        print(f"Versión del sistema: {version}")

def inicializar_mapa_almacenamiento():
    mapa = [1] * 5 + [0] * ((DISK_SIZE // CLUSTER_SIZE) - 5)
    return mapa

def listar_directorio():
    with lock:
        print("Contenido del directorio:")
        with open(DISK_FILE, 'rb') as disk:
            disk.seek(CLUSTER_SIZE)
            for i in range(4 * (CLUSTER_SIZE // 64)):
                entry = disk.read(64)
                tipo = entry[0:1].decode('ascii')
                if tipo == '-' or tipo == '#':
                    continue
                nombre = entry[1:16].decode('ascii').strip()
                tamano = struct.unpack('<I', entry[16:20])[0]
                print(f"Archivo: {nombre}, Tamaño: {tamano} bytes")

def copiar_desde_fiunamfs(nombre_archivo):
    encontrado = False
    nombre_archivo = nombre_archivo.strip()
    
    with lock:
        with open(DISK_FILE, 'rb') as disk:
            disk.seek(CLUSTER_SIZE)
            for i in range(4 * (CLUSTER_SIZE // 64)):
                entry = disk.read(64)
                tipo = entry[0:1].decode('ascii')
                nombre = entry[1:16].decode('ascii').strip()
                
                if tipo == '.' and nombre == nombre_archivo:
                    tamano = struct.unpack('<I', entry[16:20])[0]
                    cluster_inicial = struct.unpack('<I', entry[20:24])[0]
                    disk.seek(cluster_inicial * CLUSTER_SIZE)
                    data = disk.read(tamano)
                    
                    with open(nombre_archivo, 'wb') as f_out:
                        f_out.write(data)
                    print(f"Archivo '{nombre_archivo}' copiado al sistema local.")
                    encontrado = True
                    break
        if not encontrado:
            print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS.")

def copiar_a_fiunamfs(nombre_archivo):
    try:
        with open(nombre_archivo, 'rb') as f_in:
            data = f_in.read()
            tamano = len(data)
        
        with lock:
            with open(DISK_FILE, 'r+b') as disk:
                disk.seek(CLUSTER_SIZE)
                
                for i in range(4 * (CLUSTER_SIZE // 64)):
                    entry_pos = disk.tell()
                    entry = disk.read(64)
                    tipo = entry[0:1].decode('ascii')
                    nombre = entry[1:16].decode('ascii').strip()
                    
                    if tipo == '#' or nombre == "---------------":
                        disk.seek(entry_pos)
                        disk.write(b'.')
                        disk.write(nombre_archivo.ljust(15).encode('ascii'))
                        disk.write(struct.pack('<I', tamano))
                        
                        cluster_inicial = 5
                        disk.write(struct.pack('<I', cluster_inicial))
                        
                        fecha_actual = datetime.now().strftime('%Y%m%d%H%M%S').encode('ascii')
                        disk.write(fecha_actual)
                        disk.write(fecha_actual)
                        
                        disk.seek(cluster_inicial * CLUSTER_SIZE)
                        disk.write(data)
                        print(f"Archivo '{nombre_archivo}' copiado a FiUnamFS.")
                        return
                print("No hay espacio disponible en el directorio para el archivo.")
    except FileNotFoundError:
        print(f"El archivo {nombre_archivo} no existe en el sistema local.")

def eliminar_archivo(nombre_archivo):
    with lock:
        with open(DISK_FILE, 'r+b') as disk:
            disk.seek(CLUSTER_SIZE)
            for i in range(4 * (CLUSTER_SIZE // 64)):
                entry_pos = disk.tell()
                entry = disk.read(64)
                tipo = entry[0:1].decode('ascii')
                nombre = entry[1:16].decode('ascii').strip()
                
                if tipo == '.' and nombre == nombre_archivo:
                    disk.seek(entry_pos)
                    disk.write(b'#' + b'---------------'.ljust(63, b'#'))
                    print(f"Archivo '{nombre_archivo}' eliminado de FiUnamFS.")
                    return
            print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS.")

def menu():
    while True:
        print("\n--- Menú de FiUnamFS ---")
        print("1. Listar contenido del directorio")
        print("2. Copiar archivo de FiUnamFS al sistema local")
        print("3. Copiar archivo del sistema local a FiUnamFS")
        print("4. Eliminar archivo de FiUnamFS")
        print("5. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            listar_directorio()
        elif opcion == '2':
            nombre_archivo = input("Ingresa el nombre del archivo a copiar de FiUnamFS: ")
            copiar_desde_fiunamfs(nombre_archivo)
        elif opcion == '3':
            nombre_archivo = input("Ingresa el nombre del archivo a copiar a FiUnamFS: ")
            copiar_a_fiunamfs(nombre_archivo)
        elif opcion == '4':
            nombre_archivo = input("Ingresa el nombre del archivo a eliminar de FiUnamFS: ")
            eliminar_archivo(nombre_archivo)
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    try:
        verificar_superbloque()
        mapa_almacenamiento = inicializar_mapa_almacenamiento()
        menu()
    except ValueError as e:
        print(e)
