import struct
import time

# Tamaño de una entrada del directorio en bytes
DIR_ENTRY_SIZE = 64
DIRECTORY_START_CLUSTER = 1
DIRECTORY_END_CLUSTER = 4
CLUSTER_SIZE = 1024  # tamaño de cluster en bytes
TOTAL_CLUSTERS = 1440  # Número total de clusters (calculado para 1440 KB)

# Paso 0: Función para inicializar el archivo FiUnamFS.img
def inicializar_fiunamfs():
    with open("FiUnamFS.img", "wb") as file:
        # Crear el archivo de 1440 KB y llenar con ceros
        file.write(b'\x00' * (1440 * 1024))  # 1440 KB llenos de ceros

    with open("FiUnamFS.img", "r+b") as file:
        # Nombre del sistema (bytes 0-8)
        file.seek(0)
        file.write(b'FiUnamFS')

        # Versión del sistema (bytes 10-14)
        file.seek(10)
        file.write(b'25-1')

        # Tamaño de cluster (bytes 40-44) - 1024 bytes en formato little endian
        file.seek(40)
        file.write(struct.pack('<I', CLUSTER_SIZE))

        # Clusters para el directorio (4 clusters en esta implementación)
        file.seek(45)
        file.write(struct.pack('<I', DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1))

        # Número total de clusters
        file.seek(50)
        file.write(struct.pack('<I', TOTAL_CLUSTERS))

        # Inicializar el directorio con entradas vacías
        file.seek(DIRECTORY_START_CLUSTER * CLUSTER_SIZE)
        for _ in range((DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1) * (CLUSTER_SIZE // DIR_ENTRY_SIZE)):
            file.write(
                b"#" +  # Tipo de archivo vacío
                b"---------------" +  # Nombre de archivo vacío
                struct.pack("<I", 0) +  # Tamaño de archivo
                struct.pack("<I", 0) +  # Cluster inicial
                b"00000000000000" +  # Fecha de creación
                b"00000000000000" +  # Fecha de modificación
                b"\x00" * 12  # Espacio reservado
            )

# Ejecutar la inicialización
inicializar_fiunamfs()
print("Sistema de archivos FiUnamFS inicializado correctamente.")

# Paso 1: Función para listar el contenido del directorio
def listar_contenido_directorio():
    with open("FiUnamFS.img", "rb") as file:
        # Leer cada entrada en los clusters de directorio
        file.seek(DIRECTORY_START_CLUSTER * CLUSTER_SIZE)
        
        print("Contenido del Directorio:")
        for i in range((DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1) * (CLUSTER_SIZE // DIR_ENTRY_SIZE)):
            entry = file.read(DIR_ENTRY_SIZE)
            
            # Extraer y decodificar datos de la entrada
            tipo_archivo = entry[0:1].decode()
            nombre = entry[1:16].decode().strip("-")  # nombre es de 15 bytes
            tamaño = struct.unpack('<I', entry[16:20])[0]
            cluster_inicial = struct.unpack('<I', entry[20:24])[0]
            fecha_creacion = entry[24:38].decode()
            fecha_modificacion = entry[38:52].decode()

            # Verificar si la entrada está vacía (sin archivo)
            if nombre == "":
                continue  # saltamos las entradas vacías

            # Imprimir detalles de la entrada
            print(f"Tipo: {tipo_archivo}, Nombre: {nombre}, Tamaño: {tamaño} bytes, " +
                  f"Cluster inicial: {cluster_inicial}, Creación: {fecha_creacion}, Modificación: {fecha_modificacion}")

# Paso 2: Función para agregar un archivo desde tu equipo hacia FiUnamFS
def agregar_archivo_a_fiunamfs(ruta_archivo_local):
    # Leer el archivo local
    try:
        with open(ruta_archivo_local, "rb") as archivo:
            contenido_archivo = archivo.read()
            tamaño_archivo = len(contenido_archivo)
    except FileNotFoundError:
        print("El archivo no se encontró en tu equipo.")
        return

    nombre_archivo = ruta_archivo_local.split('/')[-1]  # Extraer solo el nombre
    if len(nombre_archivo) > 15:
        print("El nombre del archivo es demasiado largo (máximo 15 caracteres).")
        return

    # Buscar una entrada vacía en el directorio
    with open("FiUnamFS.img", "r+b") as fiunamfs:
        fiunamfs.seek(DIRECTORY_START_CLUSTER * CLUSTER_SIZE)
        entrada_libre = None

        # Recorrer todas las entradas del directorio
        for i in range((DIRECTORY_END_CLUSTER - DIRECTORY_START_CLUSTER + 1) * (CLUSTER_SIZE // DIR_ENTRY_SIZE)):
            posicion = fiunamfs.tell()
            entry = fiunamfs.read(DIR_ENTRY_SIZE)
            tipo_archivo = entry[0:1].decode()

            # Identificar entrada vacía
            if tipo_archivo == '#':
                entrada_libre = posicion
                break

        if entrada_libre is None:
            print("No hay espacio en el directorio para agregar otro archivo.")
            return

        # Encontrar el próximo cluster libre para almacenar el archivo
        cluster_inicial = 5  # asumimos que el espacio de datos empieza en el cluster 5
        fiunamfs.seek(cluster_inicial * CLUSTER_SIZE)

        # Guardar el contenido del archivo en el área de datos
        fiunamfs.write(contenido_archivo)

        # Escribir la entrada en el directorio
        fiunamfs.seek(entrada_libre)
        fecha_actual = time.strftime("%Y%m%d%H%M%S")  # formato AAAAMMDDHHMMSS
        entrada = (
            b"." +  # Tipo de archivo
            nombre_archivo.ljust(15, "-").encode() +  # Nombre del archivo
            struct.pack("<I", tamaño_archivo) +  # Tamaño del archivo en bytes
            struct.pack("<I", cluster_inicial) +  # Cluster inicial
            fecha_actual.encode() +  # Fecha de creación
            fecha_actual.encode() +  # Fecha de última modificación
            b"\x00" * 12  # Espacio reservado
        )
        fiunamfs.write(entrada)

    print(f"Archivo '{nombre_archivo}' agregado correctamente a FiUnamFS.")

# Ejemplo de uso:
listar_contenido_directorio()
agregar_archivo_a_fiunamfs("prueba1.txt")
listar_contenido_directorio()
