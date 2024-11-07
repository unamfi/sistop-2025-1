#    _____ _      __             ___   ______     ___   ____ ___ 
#  / ___/(_)____/ /_____  ____ |__ \ / ____/    <  /  / __ \__ \
#  \__ \/ / ___/ __/ __ \/ __ \__/ //___ \______/ /  / /_/ /_/ /
# ___/ / (__  ) /_/ /_/ / /_/ / __/____/ /_____/ /  / ____/ __/ 
#/____/_/____/\__/\____/ .___/____/_____/     /_/  /_/   /____/ 
#                     /_/                                       
#  Proyecto elaborado por:
# - Arellanes Conde Esteban
# - Esquivel Santana Christian


import os
import struct
from threading import Thread, Lock


class FiUnamFS:
    def __init__(self, filepath):
        self.filepath = filepath
        self.lock = Lock()
        with open(self.filepath, 'r+b') as f:
            self.superblock = f.read(1024)  # Leer superbloque (primer cluster)

    def validate_fs(self):
        name = struct.unpack('8s', self.superblock[0:8])[0].decode('ascii').strip('\x00')
        version = struct.unpack('5s', self.superblock[10:15])[0].decode('ascii').strip('\x00')
    
        # Imprime los valores leídos del superbloque
        print(f"Nombre del FS: {name}")
        print(f"Versión del FS: {version}")

        if name != 'FiUnamFS' or version != '25-1':
            raise ValueError("Sistema de archivos no compatible o corrupto")
    
    def list_files(self):
        with self.lock:
            with open(self.filepath, 'r+b') as f:
                f.seek(1024)  # Posicionarse al inicio del directorio
                entries = []
                for _ in range(64):
                    entry = f.read(64)
                    filename = entry[1:16].decode('ascii', 'ignore').replace('\x00', ' ').strip()
                    if filename and filename != '###############':  # Filtrar entradas vacías
                        entries.append(filename)
        return entries


def copy_file_from_fs(fs, filename, destination):
    with fs.lock:
        with open(fs.filepath, 'r+b') as disk:
            disk.seek(0)  # Posicionarse al inicio del archivo para leer el superbloque
            superblock = disk.read(1024)  # Leer el superbloque completo
            
            cluster_size = struct.unpack('<I', superblock[40:44])[0]
            total_clusters = struct.unpack('<I', superblock[50:54])[0]

            disk.seek(1024)  # Posicionarse al inicio del directorio
            file_found = False
            for i in range(64):  # Aquí empieza el bucle donde 'i' es definido
                entry = disk.read(64)
                file_name = struct.unpack('15s', entry[1:16])[0].decode('ascii').rstrip('\x00').strip()
                
                if file_name == filename:
                    file_found = True
                    file_cluster = struct.unpack('<I', entry[33:37])[0]
                    file_size = struct.unpack('<I', entry[17:21])[0]
                    break

            if not file_found:
                print(f"File {filename} not found in the file system.")
                return f"Archivo {filename} no encontrado"

            # Si se encontró el archivo, leerlo y copiarlo
            disk.seek(cluster_size * file_cluster)
            file_data = disk.read(file_size)

            # Asegurarse de que el destino sea una ruta completa de archivo
            if os.path.isdir(destination):
                destination = os.path.join(destination, filename)

            # Escribir el archivo copiado en el destino
            with open(destination, 'wb') as out_file:
                out_file.write(file_data)

            print(f"Archivo {filename} copiado a {destination}")
            return f"Archivo {filename} copiado exitosamente"



def find_free_cluster(disk, num_clusters, cluster_size):
    free_cluster = -1
    disk.seek(cluster_size)  # Saltar el superbloque
    for i in range(1, num_clusters):
        disk.seek(cluster_size * i)
        if disk.read(cluster_size) == b'\x00' * cluster_size:
            free_cluster = i
            print(f"Found free cluster: {free_cluster}")  # Imprimir si encuentra un cluster libre
            break
    return free_cluster


def copy_file_to_fs(fs, source, filename):
    with fs.lock:
        with open(fs.filepath, 'r+b') as disk:
            disk.seek(0)  # Posicionarse al inicio del archivo para leer el superbloque
            superblock = disk.read(1024)  # Leer el superbloque completo
            
            cluster_size = struct.unpack('<I', superblock[40:44])[0]
            total_clusters = struct.unpack('<I', superblock[50:54])[0]

            disk.seek(1024)  # Posicionarse al inicio del directorio
            empty_entry_index = -1
            for i in range(64):
                entry = disk.read(64)
                file_name = struct.unpack('15s', entry[1:16])[0].decode('ascii').rstrip('\x00').strip()

                # Verificar si la entrada está vacía, buscando tanto '--------------' como otras marcas de vacío
                if not file_name or file_name == '###############' or file_name == '--------------':
                    empty_entry_index = i
                    break

            if empty_entry_index == -1:
                print("Debug: No space in directory")  # Mensaje de depuración adicional
                return "Sin espacio en el directorio"

            free_cluster = find_free_cluster(disk, total_clusters, cluster_size)
            if free_cluster == -1:
                print("Debug: No free cluster available")  # Mensaje de depuración adicional
                return "No hay un cluster libre disponible"

            with open(source, 'rb') as file:
                data = file.read()
                file_size = len(data)

            disk.seek(cluster_size * free_cluster)
            disk.write(data)

            disk.seek(1024 + 64 * empty_entry_index)
            filename_encoded = filename.encode('ascii')
            filename_padded = filename_encoded.ljust(15, b' ')  # Rellenar con espacios si es necesario
            entry_data = struct.pack('<c15sII52s', b'-', filename_padded, file_size, free_cluster, b'\x00' * 52)
            print(f"Writing entry data at index {empty_entry_index}: {entry_data}")  # Debugging output
            disk.seek(1024 + 64 * empty_entry_index)
            disk.write(entry_data)
            
            return "Archivo copiado exitosamente"
        

def delete_file(fs, filename):
    filename = filename.strip()
    with fs.lock:
        with open(fs.filepath, 'r+b') as disk:
            disk.seek(1024)
            for i in range(64):
                entry = disk.read(64)
                file_name = entry[1:16].decode('ascii').replace('\x00', '').strip()
                if file_name == filename:
                    disk.seek(1024 + 64 * i)
                    disk.write(b'/###############' + b'\x00' * (64 - 17))
                    return "Archivo borrado exitosamente"
            return "Archivo no encontrado"


def threaded_task(fs, task, *args):
    if task == "list":
        print("\nListando archivos...")
        print(fs.list_files())
    elif task == "copy_from_fs":
        filename, destination = args
        print(f"Copiando {filename} desde FS a {destination}...")
        print(copy_file_from_fs(fs, filename, destination))
    elif task == "copy_to_fs":
        source, filename = args
        print(f"Copiando {source} a FS desde {filename}...")
        print(copy_file_to_fs(fs, source, filename))
    elif task == "delete":
        filename = args[0]
        print(f"Borrando {filename}...")
        print(delete_file(fs, filename))


def main_menu(fs):
    while True:
        print("\nMenu:")
        print("1. Listar los contenidos del directorio")
        print("2. Copiar un archivo del FiUnamFS a tu sistema")
        print("3. Copiar un archivo de tu computadora al FiUnamFS")
        print("4. Eliminar un archivo del FiUnamFS")
        print("5. Salir")
        choice = input("Ingrese su elección: ")

        if choice == '1':
            thread = Thread(target=threaded_task, args=(fs, "list"))
            thread.start()
            thread.join()
        elif choice == '2':
            filename = input("Ingrese el nombre del archivo a copiar del FiUnamFS: ")
            destination = input("Ingrese la ruta de destino en su sistema: ")
            thread = Thread(target=threaded_task, args=(fs, "copy_from_fs", filename, destination))
            thread.start()
            thread.join()
        elif choice == '3':
            source = input("Ingrese la ruta del archivo en su sistema para copiar al FiUnamFS: ")
            filename = input("Ingrese el nombre bajo el cual guardar el archivo en el FiUnamFS: ")
            thread = Thread(target=threaded_task, args=(fs, "copy_to_fs", source, filename))
            thread.start()
            thread.join()
        elif choice == '4':
            filename = input("Ingrese el nombre del archivo a eliminar del FiUnamFS: ")
            thread = Thread(target=threaded_task, args=(fs, "delete", filename))
            thread.start()
            thread.join()
        elif choice == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Por favor intente de nuevo.")


if __name__ == "__main__":
    # Ajustar la ruta según el sistema
    fs = FiUnamFS('/home/bante/Descargas/fiunamfs.img')
    fs.validate_fs()
    main_menu(fs)
