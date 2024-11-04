""""
Bienvenido al proyecto 1. MICRO SISTEMA DE ARCHIVOS MULTIHILOS 

Donde se utiilizaran los cnceptos vistos en clase para implementar un programa 
que pueda realizar las siguientes acciones especificadas por el profesor:

1- Listar los contenidos del directorio
2- Copiar uno de los archivos de dentro del FiUnamFS hacia tu sistema
3- Copiar un archivo de tu computadora hacia tu FiUnamFS
4- Eliminar un archivo del FiUnamFS
5- El programa que desarrollen debe contar, por lo menos, dos hilos de ejecución, 
operando concurrentemente, y que se comuniquen su estado mediante mecanismos de 
sincronización.

Este programa tratara de emular la terminald de windows, esto para que el usuario no se
de cuenta que esta trabajando sobre un programa, y tratara de parecer invisible ante este
"""
import os
import struct
import threading
from ReconocerEntradas import Reconocer
from pathlib import Path
from datetime import datetime

#definicion para listar los archivos
def montaje(fiunamfs):
    #se abre el fiunamfs.img en modo binario
    with open(fiunamfs,'rb') as disco:
        #se verifica el niombre del sistema
        disco.seek(0)
        if disco.read(8).decode('ascii')!='FiUnamFS':
            print(f"\n Este programa esta diseñado solo para fiunamfs.img")
        else:
            print("\n Sistema: FiunamFS")
        
        #ahora vamos a validar la version!
        disco.seek(10)
        version = disco.read(4).decode('ascii')
        if version != '25-1':
            print("\n Al parecer este archivo no es del semestre 25-1")

        else: print("\n Version: 25-1")

        #especificamos etiqueta del volumen
        disco.seek(20)
        vol = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n etiqueta volumen: {vol}")

        #especificamos el tamaño del cluster :D
        disco.seek(40)
        size = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n Tamño cluster: {size}")
        
        #especificamos el numero de clusteres
        disco.seek(45)
        numclusters = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n Numero de clusteres: {size}")

        #especificamos el numero de cluster de la unidad completa
        disco.seek(50)
        Numunit = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n numero de cluster de la unidad completa: {Numunit}")

def mostrarArchivos(fiunamfs):

    NameFiles = []

    print("Mode                 LastWriteTime         Length Name")
    print("----                 -------------         ------ ----")

    for i in range(4 * ((4*256) // 64)):  # Cada entrada del directorio ocupa 64 bytes
        entry = fiunamfs.read(64)
        
        # Tipo de archivo
        tipo = entry[0]
        if tipo == ord('#'):  # Entrada vacía
            continue
            
        # Leer nombre del archivo
        nombre = entry[1:14].decode('ascii').strip('-').strip()
        NameFiles.append(nombre)

        # Leer tamaño del archivo
        tamano = struct.unpack('<I', entry[16:20])[0]

        fecha_modificacion = entry[38:52].decode('ascii', errors='replace')

        # Imprimir los detalles del archivo
        if tamano != 0:
            print(f"-a---l     {fecha_modificacion[0:4]}\{fecha_modificacion[4:6]}\{fecha_modificacion[6:8]}   {fecha_modificacion[8:10]}:{fecha_modificacion[10:12]}:{fecha_modificacion[12:14]}        {tamano} {nombre}")

    return NameFiles

def copiar_archivo(disco, nombre_archivo, destino):

    size = 1024
    inicio = 1024

    # Buscar el archivo en el directorio
    encontrado = False
    for i in range(4 * (size // 64)):  # 4 clusters de directorio, cada entrada tiene 64 bytes
        disco.seek(inicio + i * 64)
        entry = disco.read(64)
            
        # Tipo de archivo
        tipo = entry[0]
        if tipo != ord('.'):
            continue  # Si no es un archivo válido, pasar a la siguiente entrada
        
        # Nombre del archivo
        nombre = entry[1:14].decode('ascii')
        if nombre.strip() != nombre_archivo.strip():
            continue
        
        # Tamaño del archivo y cluster inicial
        tamano = struct.unpack('<I', entry[16:20])[0]
        clusterInicial = struct.unpack('<I', entry[20:24])[0]
        encontrado = True
        break
    
    if not encontrado:
        print("Archivo no encontrado en FiUnamFS.")
        return

    # Leer los datos del archivo
    disco.seek(clusterInicial * size)  # Ir al cluster inicial de datos
    datos = disco.read(tamano)

    Ruta_destino = Path(destino)

    # Escribir los datos en un nuevo archivo en el sistema
    with Ruta_destino.open('wb') as salida:
        salida.write(datos)
        
    print(f"\nArchivo '{nombre_archivo}' copiado a '{destino}'\n")



class FiUnamFS:
    DIRECTORY_CLUSTERS = range(1, 5)
    CLUSTER_SIZE = 1024  # Cada cluster tiene 1024 bytes (4 sectores de 256 bytes)
    ENTRY_SIZE = 64  # Cada entrada en el directorio mide 64 bytes

    def __init__(self, disk_file):
        self.disk_file = disk_file

    def read_cluster(self, cluster_number):
        with open(self.disk_file, 'rb') as f:
            f.seek(cluster_number * self.CLUSTER_SIZE)
            return f.read(self.CLUSTER_SIZE)

    def write_cluster(self, cluster_number, data):
        with open(self.disk_file, 'r+b') as f:
            f.seek(cluster_number * self.CLUSTER_SIZE)
            f.write(data)

    def find_free_entry(self):
        """Busca una entrada libre en el directorio."""
        for cluster_number in self.DIRECTORY_CLUSTERS:
            cluster_data = self.read_cluster(cluster_number)
            for i in range(0, self.CLUSTER_SIZE, self.ENTRY_SIZE):
                entry_data = cluster_data[i:i + self.ENTRY_SIZE]
                if entry_data[0] == 0x23:  # Entrada vacía ('#')
                    return cluster_number, i  # Retorna el cluster y el offset
        return None, None

    def find_free_cluster(self, file_size):
        """Encuentra un cluster libre que pueda almacenar el archivo."""
        total_clusters = (file_size + self.CLUSTER_SIZE - 1) // self.CLUSTER_SIZE
        data_start_cluster = max(self.DIRECTORY_CLUSTERS) + 1
        with open(self.disk_file, 'rb') as f:
            for cluster in range(data_start_cluster, 1440):
                f.seek(cluster * self.CLUSTER_SIZE)
                if f.read(1) == b'\x00':
                    return cluster
        return None

    def write_file_direct(self, file_name, file_content):
        if len(file_name) > 15:
            raise ValueError("El nombre del archivo es demasiado largo.")
        
        file_size = len(file_content)
        start_cluster = self.find_free_cluster(file_size)
        if start_cluster is None:
            raise RuntimeError("No hay espacio libre en el sistema de archivos.")
        
        cluster_number, entry_offset = self.find_free_entry()
        if cluster_number is None:
            raise RuntimeError("No hay entradas libres en el directorio.")

        # Escribir contenido del archivo en el cluster
        self.write_cluster(start_cluster, file_content.ljust(self.CLUSTER_SIZE, b'\x00'))

        # Crear la entrada del archivo en el directorio
        creation_date = datetime.now().strftime('%Y%m%d%H%M%S')
        modification_date = creation_date

        entry_data = bytearray(self.ENTRY_SIZE)
        entry_data[0] = 0x2e  # Tipo de archivo regular
        entry_data[1:16] = file_name.encode('ascii').ljust(15, b'\x00')
        entry_data[16:20] = struct.pack('<I', file_size)
        entry_data[20:24] = struct.pack('<I', start_cluster)
        entry_data[24:37] = creation_date.encode('ascii')
        entry_data[38:51] = modification_date.encode('ascii')

        # Escribir la entrada en el directorio
        cluster_data = self.read_cluster(cluster_number)
        cluster_data = (cluster_data[:entry_offset] + entry_data + 
                        cluster_data[entry_offset + self.ENTRY_SIZE:])
        self.write_cluster(cluster_number, cluster_data)

        print(f"Archivo '{file_name}' escrito en fiunamfs.img")
    
def eliminar_archivo(disco, nombre_archivo):
    cluster_size = 1024  # Tamaño del cluster
    inicio_directorio = 1024  # Offset donde comienza el directorio
    encontrado = False

    # Recorrer cada entrada en el directorio para encontrar el archivo
    for i in range(4 * (cluster_size // 64)):  # 4 clusters de directorio, cada entrada ocupa 64 bytes
        disco.seek(inicio_directorio + i * 64)
        entry = disco.read(64)
        
        # Leer el tipo de archivo y nombre
        tipo = entry[0]
        nombre = entry[1:14].decode('ascii').strip()
        
        # Verificar si es el archivo que queremos eliminar
        if tipo == ord('.') and nombre == nombre_archivo:
            # Marcamos la entrada como vacía, sobrescribiendo el tipo
            disco.seek(inicio_directorio + i * 64)
            disco.write(b'#')  # Indicador de entrada vacía
            encontrado = True
            print(f"Archivo '{nombre_archivo}' eliminado exitosamente.")
            break

    if not encontrado:
        print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS.")


def main():

    NameFiles = []
    #montamos el archivo
    print("Montando FiUnamFs\n")
    montaje("fiunamfs.img")

    with open("fiunamfs.img",'r+b') as disco:
        while True:

            #simulamos la terminal de widows
            entrada = input(f"{os.getcwd()}\\FiunamFS> ")
            print("\n")

            #Si la entrada fue ls entonces el usuario quiere ver los archivos
            if entrada == "ls":
                    NameFiles = mostrarArchivos(disco)

            elif entrada == "exit" or entrada =="cd ..":
                print("Desmontando FiunamFs...\n")
                break

            elif entrada.startswith("copy "):

                NameFiles = mostrarArchivos(disco)
                os.system('cls')
                
                ruta_origen, ruta_destino = Reconocer(entrada)
                
                for nombre in NameFiles:

                    if(os.getcwd()+'\\FiunamFS\\'+nombre==ruta_origen.strip()):
                        
                        copiar_archivo(disco,nombre,ruta_destino+"\\"+nombre)
                        break
                
                    if(os.getcwd()+'\\FiunamFS\\'==ruta_destino.strip()):
                        fs = FiUnamFS('fiunamfs.img')
                        fs.write_file_direct('Reconocer.py',b"contenido")
                        break
            elif entrada.startswith("delete "):
                eliminar_archivo(disco, entrada.split(" ")[1])

            else: 
                print("Por el momento la entrada anterior no es valida\n")

if __name__ == "__main__":
    main()