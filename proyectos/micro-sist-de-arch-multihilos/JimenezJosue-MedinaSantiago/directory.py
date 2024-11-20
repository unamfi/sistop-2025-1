import struct
from filesystem import FiUnamFS

DIR_ENTRY_SIZE = 64
DIR_START_CLUSTER = 1
DIR_CLUSTER_COUNT = 4
ENTRY_EMPTY = b'\x00' * DIR_ENTRY_SIZE
FILE_TYPE = b'.'

class Directory:
    def __init__(self, fs):
        self.fs = fs

    def list_files(self):
        entries = []
        for cluster_num in range(DIR_START_CLUSTER, DIR_START_CLUSTER + DIR_CLUSTER_COUNT):
            cluster_data = self.fs.read_cluster(cluster_num)
            for i in range(0, len(cluster_data), DIR_ENTRY_SIZE):
                entry = cluster_data[i:i + DIR_ENTRY_SIZE]
                #Extracción de los atributos del archivo: Tipo, nombre decodificado a ascii y su tamaño
                file_type = entry[0:1]
                filename = entry[1:16].decode('ascii').strip()
                filesize = struct.unpack('<I', entry[16:20])[0]
                
                #Ignoramos nombres vacíos
                if filename == ENTRY_EMPTY.decode('ascii'):
                    continue
                if file_type == FILE_TYPE:
                    entries.append((filename, filesize, cluster_num, i))
        return entries

    def find_empty_entry(self):
        """
        Busca una entrada vacía en el directorio, devuelve una tupla con el número de cluster
        y el offset donde se encontró la entrada vacía, devuelve None si no hay espacio
        """
        for cluster_num in range(DIR_START_CLUSTER, DIR_START_CLUSTER + DIR_CLUSTER_COUNT):
            cluster_data = self.fs.read_cluster(cluster_num)
            for i in range(0, len(cluster_data), DIR_ENTRY_SIZE):
                entry = cluster_data[i:i + DIR_ENTRY_SIZE]
                filename = entry[1:16].decode('ascii').strip()

                #Si encontramos la cadena '---------------', el cual es indicador de cadena vacía
                if filename == ENTRY_EMPTY.decode('ascii'):
                    print(f"Entrada vacía encontrada en cluster {cluster_num}, offset {i}")
                    return (cluster_num, i)
                
                #Verificar si la entrada está marcada como libre con los caracteres '#'
                file_type = entry[0:1]
                if file_type == b'#':
                    print(f"Entrada vacía marcada con # en cluster {cluster_num}, offset {i}")
                    return (cluster_num, i)

        #No hubo entrada vacía
        print("No se encontró ninguna entrada vacía.")
        return None


    def add_file(self, filename, filesize, cluster_num):
        #Buscar una entrada vacía
        empty_entry = self.find_empty_entry()
        if  not empty_entry:
            print("Error: No hay espacio en el directorio.")
            return False
        
        print(f"Agregando archivo '{filename}' al directorio...")
        
        #Ajustamos longitud
        entry_data = FILE_TYPE + filename.ljust(15).encode('ascii')
        #Tamaño del archivo
        entry_data += struct.pack('<I', filesize)
        #Cluster inicial
        entry_data += struct.pack('<I', cluster_num)
        #Fecha de creación
        entry_data += b'20241107123456'
        # Fecha de modificación
        entry_data += b'20241107123456'
        entry_data += b'\x00' * (DIR_ENTRY_SIZE - len(entry_data))
        
        #Guardar la entrada en el archivo de imagen
        cluster_num, offset = empty_entry
        cluster_data = self.fs.read_cluster(cluster_num)
        #new_data contendrá el clúster con la nueva entrada
        new_data = cluster_data[:offset] + entry_data + cluster_data[offset + DIR_ENTRY_SIZE:]
        self.fs.write_cluster(cluster_num, new_data)
        
        print(f"Archivo '{filename}' añadido correctamente en cluster {cluster_num}, offset {offset}.")
        return True

    def delete_file(self, filename):
        #Eliminamos espacios en blanco
        filename = filename.strip()
        
        #Obtener la lista de archivos
        files = self.list_files()
        print("Archivos en el directorio:", [file[0].strip() for file in files])

        #Buscar el archivo a eliminar
        for file in files:
            #Remplazamos \x00 por espacios para eliminarlos
            file_name_cleaned = file[0].replace('\x00', '').strip()

            if file_name_cleaned == filename:
                cluster_num, offset = file[2], file[3]
                
                #Marcar entrada como vacía
                cluster_data = self.fs.read_cluster(cluster_num)
                #new_data contendrá el clúster ya vacío
                new_data = cluster_data[:offset] + b'#' + ENTRY_EMPTY + cluster_data[offset + DIR_ENTRY_SIZE:]
                self.fs.write_cluster(cluster_num, new_data)
                print(f"Archivo {filename} eliminado.")
                return True

        print(f"Archivo {filename} no encontrado.")
        return False

