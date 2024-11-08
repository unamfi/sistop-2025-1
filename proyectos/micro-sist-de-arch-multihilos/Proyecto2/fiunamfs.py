import struct

# Paso 1: Crear el archivo FiUnamFS.img de 1440 KB y llenar con ceros
with open("FiUnamFS.img", "wb") as file:
    file.write(b'\x00' * (1440 * 1024))  # 1440 KB llenos de ceros

# Paso 2: Configuración del superbloque en FiUnamFS.img
with open("FiUnamFS.img", "r+b") as file:
    # Nombre del sistema (bytes 0-8)
    file.seek(0)
    file.write(b'FiUnamFS')

    # Versión del sistema (bytes 10-14)
    file.seek(10)
    file.write(b'25-1')

    # Tamaño de cluster (bytes 40-44) - 1024 bytes en formato little endian
    file.seek(40)
    file.write(struct.pack('<I', 1024))

    # Clusters para el directorio (suponemos 4 clusters en esta implementación)
    file.seek(45)
    file.write(struct.pack('<I', 4))

    # Número total de clusters (calculado en base al tamaño total de 1440 KB)
    total_clusters = (1440 * 1024) // 1024  # Tamaño total / tamaño del cluster
    file.seek(50)
    file.write(struct.pack('<I', total_clusters))

# Leer y verificar los primeros datos en FiUnamFS.img
with open("FiUnamFS.img", "rb") as file:
    # Leer el nombre del sistema
    file.seek(0)
    name = file.read(8)
    print("Nombre del sistema:", name.decode())

    # Leer la versión
    file.seek(10)
    version = file.read(4)
    print("Versión del sistema:", version.decode())

    # Leer tamaño del cluster
    file.seek(40)
    cluster_size = struct.unpack('<I', file.read(4))[0]
    print("Tamaño del cluster:", cluster_size)

    # Leer total de clusters
    file.seek(50)
    total_clusters = struct.unpack('<I', file.read(4))[0]
    print("Total de clusters:", total_clusters)
