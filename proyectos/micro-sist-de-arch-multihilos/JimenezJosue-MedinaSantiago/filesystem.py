import struct

#Tamaño de sector = 256
CLUSTER_SIZE = 256 * 4
IMG_FILE = 'fiunamfs.img'

#Suponemos que la tabla de asignación empieza en el clúster 1
ALLOCATION_TABLE_CLUSTER = 1

#Valor que indica el final de la cadena de clústeres
END_OF_CHAIN = 0xFFFFFFFF

class FiUnamFS:
    def __init__(self): 

        #Abrimos fiunamfs.img en lectura y como binario
        self.image = open(IMG_FILE, 'r+b')
        self.allocation_table = self.read_allocation_table()

    #Lectura de clústeres
    def read_cluster(self, cluster_num):
        #Buscamos en el .img la ubicación a partir del índice y el tamaño del clúster
        self.image.seek(cluster_num * CLUSTER_SIZE)
        #Lectura
        return self.image.read(CLUSTER_SIZE)

    def write_cluster(self, cluster_num, data):
        #Buscamos en el .img la ubicación a partir del índice y el tamaño del clúster
        self.image.seek(cluster_num * CLUSTER_SIZE)
        #Escritura
        self.image.write(data)

    def read_superblock(self):
        data = self.read_cluster(0)
        fs_name = data[0:8].decode('ascii').strip()
        version = data[10:15].decode('ascii').strip()
        return {
            'fs_name': fs_name,
            'version': version
        }

    def read_allocation_table(self):
        #Leer la tabla de asignación desde el clúster de la tabla, empezando en 1
        allocation_data = self.read_cluster(ALLOCATION_TABLE_CLUSTER)
        #Número de entradas en la tabla, asumiendo 32 bits
        table_size = CLUSTER_SIZE // 4
        allocation_table = []

        for i in range(table_size):
            #Interpretamos los datos en binario con struct.unpack
            entry = struct.unpack('<I', allocation_data[i * 4:(i + 1) * 4])[0]
            allocation_table.append(entry)

        return allocation_table

    def get_next_cluster(self, current_cluster):
        #Devuelve el siguiente clúster en la cadena o None si es el final
        if current_cluster < 0 or current_cluster >= len(self.allocation_table):
            #Clúster fuera de rango
            return None

        next_cluster = self.allocation_table[current_cluster]
        if next_cluster == END_OF_CHAIN:
            #Indica el final de la cadena
            return None

        #Si no estamos en el final o fuera de rango avanzamos al siguiente clúster
        return next_cluster

    def close(self):
        self.image.close()
