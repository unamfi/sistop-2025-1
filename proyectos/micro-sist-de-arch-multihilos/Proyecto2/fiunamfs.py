import os
import struct
import threading
import time
from colorama import init, Fore, Style

# Inicialización de colorama para color en terminal
init(autoreset=True)

# FiUnamFS - Sistema de archivos simple implementado en Python
# Este sistema de archivos simula una estructura básica de sistema de archivos
# con operaciones como agregar, eliminar, listar y copiar archivos.
# Autores: Palí Figueroa Santiago
# Fecha de creación: 05/11/2024

# -----------------------------------------------------
# Constantes del Sistema de Archivos
# -----------------------------------------------------
DIR_ENTRY_SIZE = 64                # Tamaño de una entrada de directorio en bytes
DIRECTORY_START_CLUSTER = 1        # Cluster donde empieza el directorio
DIRECTORY_END_CLUSTER = 4          # Cluster donde termina el directorio
CLUSTER_SIZE = 1024                # Tamaño de un cluster en bytes
TOTAL_CLUSTERS = 1440              # Número total de clusters (1440 KB)

# Lock global para sincronización en concurrencia
lock = threading.Lock()

# -----------------------------------------------------
# Función para inicializar FiUnamFS
# -----------------------------------------------------
def inicializar_fiunamfs():
    """
    Inicializa el sistema de archivos FiUnamFS creando un archivo binario llamado "FiUnamFS.img".
    Configura parámetros básicos del sistema de archivos, como nombre, versión y tamaño de los clusters.
    También inicializa el directorio con entradas vacías.
    """
    with open("FiUnamFS.img", "wb") as file:
        file.write(b'\x00' * (1440 * 1024))  # Crear el archivo de 1440 KB con ceros

    with open("FiUnamFS.img", "r+b") as file:
        # Configuración del encabezado del sistema de archivos
        file.seek(0)
        file.write(b'FiUnamFS')                         # Nombre del sistema
        file.seek(10)
        file.write(b'25-1')                             # Versión del sistema
        file.seek(40)
        file.write(struct.pack('<I', CLUSTER_SIZE))     # Tamaño de clusters
        file.seek(45)
        file.write(struct.pack('<I', DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1))  # Clusters del directorio
        file.seek(50)
        file.write(struct.pack('<I', TOTAL_CLUSTERS))   # Número total de clusters

        # Inicializar directorio con entradas vacías
        file.seek(DIRECTORY_START_CLUSTER * CLUSTER_SIZE)
        for _ in range((DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1) * (CLUSTER_SIZE // DIR_ENTRY_SIZE)):
            file.write(b"#" + b"---------------" + struct.pack("<I", 0) + struct.pack("<I", 0) +
                       b"00000000000000" + b"00000000000000" + b"\x00" * 12)
    print(Fore.GREEN + "Sistema de archivos FiUnamFS inicializado correctamente.")

# -----------------------------------------------------
# Función para listar el contenido del directorio
# -----------------------------------------------------
def listar_contenido_directorio():
    """
    Muestra el contenido del directorio de FiUnamFS, listando el nombre, tipo, tamaño,
    cluster inicial, y las fechas de creación y modificación de cada archivo.
    """
    with lock, open("FiUnamFS.img", "rb") as file:
        file.seek(DIRECTORY_START_CLUSTER * CLUSTER_SIZE)
        print(Fore.CYAN + "Contenido del Directorio:")
        for _ in range((DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1) * (CLUSTER_SIZE // DIR_ENTRY_SIZE)):
            entry = file.read(DIR_ENTRY_SIZE)
            tipo_archivo = entry[0:1].decode()
            nombre = entry[1:16].decode().strip("-")
            tamaño = struct.unpack('<I', entry[16:20])[0]
            cluster_inicial = struct.unpack('<I', entry[20:24])[0]
            fecha_creacion = entry[24:38].decode()
            fecha_modificacion = entry[38:52].decode()
            if nombre == "":
                continue
            print(f"{Fore.YELLOW}Tipo: {tipo_archivo}, Nombre: {nombre}, Tamaño: {tamaño} bytes, "
                  f"Cluster inicial: {cluster_inicial}, Creación: {fecha_creacion}, Modificación: {fecha_modificacion}")

# -----------------------------------------------------
# Función para encontrar un cluster libre
# -----------------------------------------------------
def encontrar_cluster_libre():
    """
    Busca un cluster libre dentro del sistema de archivos para almacenar un nuevo archivo.
    
    :return: Número de un cluster libre o None si no hay clusters libres.
    """
    with open("FiUnamFS.img", "rb") as file:
        file.seek(DIRECTORY_END_CLUSTER * CLUSTER_SIZE)
        for cluster in range(DIRECTORY_END_CLUSTER + 1, TOTAL_CLUSTERS):
            file.seek(cluster * CLUSTER_SIZE)
            if file.read(1) == b'\x00':
                return cluster
    return None

# -----------------------------------------------------
# Función para agregar un archivo a FiUnamFS
# -----------------------------------------------------
def agregar_archivo_a_fiunamfs(ruta_archivo_local):
    """
    Agrega un archivo desde el sistema local a FiUnamFS. Utiliza una entrada libre en el directorio
    y un cluster libre en el sistema para almacenar el contenido del archivo.

    :param ruta_archivo_local: Ruta del archivo en el sistema local.
    """
    with lock:
        if not os.path.exists(ruta_archivo_local):
            print(Fore.RED + "Error: El archivo no existe.")
            return
        nombre_archivo = os.path.basename(ruta_archivo_local)
        if len(nombre_archivo) > 15:
            print(Fore.RED + "Error: El nombre del archivo es demasiado largo (máximo 15 caracteres).")
            return

        with open(ruta_archivo_local, "rb") as archivo:
            contenido_archivo = archivo.read()

        with open("FiUnamFS.img", "r+b") as fiunamfs:
            fiunamfs.seek(DIRECTORY_START_CLUSTER * CLUSTER_SIZE)
            entrada_libre = None
            for _ in range((DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1) * (CLUSTER_SIZE // DIR_ENTRY_SIZE)):
                posicion = fiunamfs.tell()
                entry = fiunamfs.read(DIR_ENTRY_SIZE)
                tipo_archivo = entry[0:1].decode()
                if tipo_archivo == '#':
                    entrada_libre = posicion
                    break
            if entrada_libre is None:
                print(Fore.RED + "Error: No hay espacio en el directorio para agregar otro archivo.")
                return

            cluster_inicial = encontrar_cluster_libre()
            if cluster_inicial is None:
                print(Fore.RED + "Error: No hay espacio libre en el sistema de archivos para almacenar el archivo.")
                return

            # Escribir el contenido del archivo en el cluster libre
            fiunamfs.seek(cluster_inicial * CLUSTER_SIZE)
            fiunamfs.write(contenido_archivo)

            # Crear una entrada en el directorio para el archivo agregado
            fiunamfs.seek(entrada_libre)
            fecha_actual = time.strftime("%Y%m%d%H%M%S")
            entrada = (
                b"." +
                nombre_archivo.ljust(15, "-").encode() +
                struct.pack("<I", len(contenido_archivo)) +
                struct.pack("<I", cluster_inicial) +
                fecha_actual.encode() +
                fecha_actual.encode() +
                b"\x00" * 12
            )
            fiunamfs.write(entrada)
        print(Fore.GREEN + f"Archivo '{nombre_archivo}' agregado correctamente a FiUnamFS.")

# -----------------------------------------------------
# Función para copiar un archivo de FiUnamFS al sistema local
# -----------------------------------------------------
def copiar_archivo_de_fiunamfs(nombre_archivo, ruta_destino):
    """
    Copia un archivo desde FiUnamFS al sistema local, guardándolo en la ubicación especificada.

    :param nombre_archivo: Nombre del archivo en FiUnamFS.
    :param ruta_destino: Ruta de destino en el sistema local (incluyendo el nombre del archivo).
    """
    if os.path.isdir(ruta_destino):
        ruta_destino = os.path.join(ruta_destino, nombre_archivo)

    with lock, open("FiUnamFS.img", "rb") as fiunamfs:
        fiunamfs.seek(DIRECTORY_START_CLUSTER * CLUSTER_SIZE)
        archivo_encontrado = False
        for _ in range((DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1) * (CLUSTER_SIZE // DIR_ENTRY_SIZE)):
            entry = fiunamfs.read(DIR_ENTRY_SIZE)
            tipo_archivo = entry[0:1].decode()
            nombre = entry[1:16].decode().strip("-")
            if nombre == nombre_archivo:
                archivo_encontrado = True
                tamaño = struct.unpack('<I', entry[16:20])[0]
                cluster_inicial = struct.unpack('<I', entry[20:24])[0]
                fiunamfs.seek(cluster_inicial * CLUSTER_SIZE)
                contenido_archivo = fiunamfs.read(tamaño)
                with open(ruta_destino, "wb") as archivo_local:
                    archivo_local.write(contenido_archivo)
                print(Fore.GREEN + f"Archivo '{nombre_archivo}' copiado exitosamente a '{ruta_destino}'.")
                break
        if not archivo_encontrado:
            print(Fore.RED + f"Error: Archivo '{nombre_archivo}' no encontrado en FiUnamFS.")

# -----------------------------------------------------
# Función para eliminar un archivo de FiUnamFS
# -----------------------------------------------------
def eliminar_archivo_de_fiunamfs(nombre_archivo):
    """
    Elimina un archivo de FiUnamFS, liberando el espacio en el directorio y en el cluster asociado.

    :param nombre_archivo: Nombre del archivo a eliminar en FiUnamFS.
    """
    with lock, open("FiUnamFS.img", "r+b") as fiunamfs:
        fiunamfs.seek(DIRECTORY_START_CLUSTER * CLUSTER_SIZE)
        archivo_encontrado = False
        for _ in range((DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1) * (CLUSTER_SIZE // DIR_ENTRY_SIZE)):
            posicion = fiunamfs.tell()
            entry = fiunamfs.read(DIR_ENTRY_SIZE)
            tipo_archivo = entry[0:1].decode()
            nombre = entry[1:16].decode().strip("-")
            if nombre == nombre_archivo:
                archivo_encontrado = True
                tamaño = struct.unpack('<I', entry[16:20])[0]
                cluster_inicial = struct.unpack('<I', entry[20:24])[0]

                # Borrar contenido en el cluster asociado
                fiunamfs.seek(cluster_inicial * CLUSTER_SIZE)
                fiunamfs.write(b'\x00' * tamaño)

                # Borrar entrada en el directorio
                fiunamfs.seek(posicion)
                fiunamfs.write(b"#" + b"---------------" + struct.pack("<I", 0) + struct.pack("<I", 0) +
                               b"00000000000000" + b"00000000000000" + b"\x00" * 12)
                print(Fore.GREEN + f"Archivo '{nombre_archivo}' eliminado correctamente de FiUnamFS.")
                break
        if not archivo_encontrado:
            print(Fore.RED + f"Error: Archivo '{nombre_archivo}' no encontrado en FiUnamFS.")

# -----------------------------------------------------
# Función principal para el menú interactivo
# -----------------------------------------------------
def main():
    """
    Función principal que muestra un menú interactivo para operar sobre FiUnamFS.
    """
    while True:
        print(Fore.BLUE + "\nFiUnamFS - Sistema de Archivos")
        print("1. Inicializar sistema de archivos")
        print("2. Listar contenido del directorio")
        print("3. Agregar archivo")
        print("4. Copiar archivo al sistema local")
        print("5. Eliminar archivo")
        print("6. Salir")

        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            inicializar_fiunamfs()
        elif opcion == "2":
            listar_contenido_directorio()
        elif opcion == "3":
            ruta_archivo_local = input("Ruta del archivo a agregar: ")
            agregar_archivo_a_fiunamfs(ruta_archivo_local)
        elif opcion == "4":
            nombre_archivo = input("Nombre del archivo a copiar: ")
            ruta_destino = input("Ruta de destino en el sistema local: ")
            copiar_archivo_de_fiunamfs(nombre_archivo, ruta_destino)
        elif opcion == "5":
            nombre_archivo = input("Nombre del archivo a eliminar: ")
            eliminar_archivo_de_fiunamfs(nombre_archivo)
        elif opcion == "6":
            print(Fore.GREEN + "Saliendo de FiUnamFS. ¡Hasta luego!")
            break
        else:
            print(Fore.RED + "Opción no válida. Por favor, intenta de nuevo.")

# Ejecución del programa principal
if __name__ == "__main__":
    main()
