import struct
import threading

# Configuración general del sistema de archivos FiUnamFS
SECTOR_SIZE = 256
CLUSTER_SIZE = SECTOR_SIZE * 4
DISK_SIZE = 1440 * 1024
SUPERBLOCK_OFFSET = 0
DIRECTORY_OFFSET = CLUSTER_SIZE
DIRECTORY_SIZE = CLUSTER_SIZE * 4

# Función para verificar si el archivo es del tipo FiUnamFS y la versión es correcta
def verify_fiunamfs(fs):
    fs.seek(SUPERBLOCK_OFFSET)
    identifier = fs.read(8).decode('ascii')
    version = fs.read(5).decode('ascii')
    if identifier != "FiUnamFS" or version != "25-1":
        raise ValueError("Este no es un sistema de archivos FiUnamFS válido")

# Función para listar los contenidos del directorio
def list_directory(fs):
    fs.seek(DIRECTORY_OFFSET)
    entries = []
    for _ in range(64):  # Directorio de tamaño fijo con 64 entradas de 64 bytes cada una
        entry = fs.read(64)
        file_type = entry[0:1].decode('ascii')
        if file_type == '#':
            continue
        filename = entry[1:16].decode('ascii').strip('-')
        size = struct.unpack('<I', entry[16:20])[0]
        cluster_start = struct.unpack('<I', entry[20:24])[0]
        entries.append((filename, size, cluster_start))
    return entries

# Función para copiar un archivo desde el sistema de archivos hacia el sistema local
def copy_from_fiunamfs(fs, filename):
    fs.seek(DIRECTORY_OFFSET)
    for _ in range(64):
        entry = fs.read(64)
        if entry[1:16].decode('ascii').strip('-') == filename:
            size = struct.unpack('<I', entry[16:20])[0]
            cluster_start = struct.unpack('<I', entry[20:24])[0]
            fs.seek(cluster_start * CLUSTER_SIZE)
            with open(filename, 'wb') as outfile:
                outfile.write(fs.read(size))
            return
    raise FileNotFoundError(f"Archivo {filename} no encontrado en FiUnamFS")

# Función para copiar un archivo desde el sistema local hacia el sistema de archivos
def copy_to_fiunamfs(fs, filename):
    fs.seek(DIRECTORY_OFFSET)
    with open(filename, 'rb') as infile:
        data = infile.read()
        filesize = len(data)
        fs.seek(0, 2)  # Ir al final del archivo
        cluster_start = fs.tell() // CLUSTER_SIZE
        fs.write(data)
        # Escribir la entrada en el directorio
        for _ in range(64):
            entry = fs.read(64)
            if entry[0:1].decode('ascii') == '#':
                fs.seek(-64, 1)
                fs.write(b'.' + filename.ljust(15, '-').encode('ascii'))
                fs.write(struct.pack('<I', filesize))
                fs.write(struct.pack('<I', cluster_start))
                fs.write(b'20231106120000')  # Fecha de creación
                fs.write(b'20231106120000')  # Fecha de modificación
                fs.write(b'\x00' * 12)  # Espacio no utilizado
                return
        raise Exception("Directorio lleno")

# Función para eliminar un archivo del sistema de archivos
def delete_from_fiunamfs(fs, filename):
    fs.seek(DIRECTORY_OFFSET)
    for _ in range(64):
        entry_start = fs.tell()
        entry = fs.read(64)
        if entry[1:16].decode('ascii').strip('-') == filename:
            fs.seek(entry_start)
            fs.write(b'#' + b'---------------'.ljust(63, b'\x00'))
            return
    raise FileNotFoundError(f"Archivo {filename} no encontrado en FiUnamFS")

# Función de hilo para sincronizar el estado de copia hacia el sistema local
def thread_copy_from_fiunamfs(fs, filename):
    with threading.Lock():
        print(f"Iniciando copia de {filename} desde FiUnamFS")
        copy_from_fiunamfs(fs, filename)
        print(f"Archivo {filename} copiado desde FiUnamFS")

# Función de hilo para sincronizar el estado de copia hacia FiUnamFS
def thread_copy_to_fiunamfs(fs, filename):
    with threading.Lock():
        print(f"Iniciando copia de {filename} hacia FiUnamFS")
        copy_to_fiunamfs(fs, filename)
        print(f"Archivo {filename} copiado hacia FiUnamFS")

# Ejecución principal
def main():
    with open("fiunamfs.img", "r+b") as fs:
        verify_fiunamfs(fs)

        # Crear hilos de copia concurrente
        thread1 = threading.Thread(target=thread_copy_from_fiunamfs, args=(fs, "archivo1.txt"))
        thread2 = threading.Thread(target=thread_copy_to_fiunamfs, args=(fs, "archivo2.txt"))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        print("Operaciones completadas")

if __name__ == "__main__":
    main()
