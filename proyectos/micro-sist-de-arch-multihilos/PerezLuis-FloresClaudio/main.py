import os,struct,math
from prettytable import PrettyTable
from datetime import datetime
import threading
import queue

class FSsistop():
    '''En esta clase se definen los metodos para la interaccion con el sistema de archivos
    fiunamfs especificado para este proyecto'''
    def __init__(self,img_path):
        self.img_path=img_path
        #lectura del superbloque (bits 0-63)
        self.superblock=self.read_superblock(img_path)
        self.cluster_size=struct.unpack('<i',self.superblock[40:44])[0]
        self.directory_size=struct.unpack('<i',self.superblock[45:49])[0]
        self.size=struct.unpack('<i',self.superblock[50:54])[0]

        #lectura del directorio, almacena una lista de diccionarios con los contenidos
        self.directory=self.read_directory(img_path)

        #Estructura de cola protegida para su ejecucion en paralelo, permite multiples productores y consumidores
        self.data_queue = queue.Queue(maxsize=10)
        self.fs_lock = threading.Lock()

    def read_superblock(self,path):
        '''Realiza la lectura del superbloque y verifica el string identificador y de versión, 
        regresa un arreglo de 64 bits con el contenido del superbloque'''
        try:
            with open(path, 'rb+') as f:
                data = f.read(64)
                id_fs, version = struct.unpack('<9s5s', data[:14])
                id_fs=id_fs[0:-1]
                version=version[1:]
                #lanza un error si no encuentra el string identificador o la versión no coincide
                if id_fs.decode('ascii') != 'FiUnamFS' or version.decode('ascii') != '25-1':
                    raise ValueError("\033[93m" + "El archivo no es un sistema de archivos FiUnamFS o la versión es incorrecta." + "\033[0m")
                else:
                    return data
        except FileNotFoundError:
            print("\033[93m" + "No se encontró el sistema de archivos" + "\033[0m")
            exit(1)

    def read_directory(self,path : str):
        '''Realiza la lectura del directorio, leyendo desde el cluster 1 hasta el 4, 
        regresa una lista de diccionarios con el contenido de cada entrada del directorio\n
        \'path\' hace referencia a la ruta del archivo .img que contiene el FS'''

        with open(path, 'rb+') as f:
            #Posiciona el cursor al inicio del cluster 1
            f.seek(self.cluster_size)
            data=[]
            for i in range(64):
                temp = f.read(64)
                #Registra cada entrada (64 bits) del directorio
                data.append({
                    'state':temp[0],
                    'name':temp[1:15].decode('ascii').strip(),
                    'size':struct.unpack('<i',temp[16:20])[0],
                    'start_cluster':struct.unpack('<i',temp[20:24])[0],
                    'created':temp[24:38].decode('ascii'),
                    'modified':temp[38:52].decode('ascii')
                })
            return data
    
    def copyfromFS(self,dest_path : str,filename : str):
        '''Define las instrucciones para copiar un archivo desde el sistema de archivos hacia la
        computadora donde se ejecuta el programa\n
        \'dest_path\': hace referencia al archivo donde se guardaran los datos en el host\n
        \'filename\' hace referencia al nombre del archivo en el FS'''

        #Busca el nombre del archivo dentro del contenido del directorio y regresa el diccionario con sus datos
        entry=self.find(filename)
        #Termina su ejecucion si no se encuentra el archivo
        if not entry:
            print("\033[93m" + f"{filename} no se encuentra en el sistema de archivos" + "\033[0m")
            return
        
        #Numero de bits leidos en cada operacion de lectura
        chunk_size = self.cluster_size
        total_size = entry['size']

        #Funcion interna para la lectura del FS
        def reader_thread():
            with open(self.img_path, 'rb') as f:
                f.seek(entry['start_cluster'] * self.cluster_size)
                bytes_read = 0
                while bytes_read < total_size:
                    #lee 1KB o los datos faltantes si es que son <1KB
                    chunk = f.read(min(chunk_size, total_size - bytes_read))
                    if not chunk:
                        break
                    #Ingresa datos a la cola compartida
                    self.data_queue.put(chunk)
                    bytes_read += len(chunk)
            self.data_queue.put(None)

        #Funcion interna para la escritura en el host
        def writer_thread():
            with open(dest_path, 'wb') as f:
                while True:
                    #Saca datos de la cola compartida
                    chunk = self.data_queue.get()
                    #Continua hasta leer un objeto None
                    if chunk is None:
                        break
                    f.write(chunk)
                    #Indica al productor que la tarea de procesamiento ha terminado
                    self.data_queue.task_done()

        #La lectura del FS y la escritura en el host se ejecutan concurrentemente
        reader = threading.Thread(target=reader_thread)
        writer = threading.Thread(target=writer_thread)
        
        reader.start()
        writer.start()
        
        reader.join()
        writer.join()

    def copytoFS(self,src_path :str,filename : str):
        '''Copia un archivo del host en el FS
        \'src_path\' hace referencia a la ruta del archivo del host\n
        \'filename\' hace referencia al nombre con el que se guardara en el FS'''

        #Indice de la entrada del directorio que contiene la informacion del archivo
        index=None
        #Lista del cluster inicial y final de cada archivo, usada para la asignacion de espacio
        used_clusters=[]
        #Verifica que el nombre no se repita, encuentra la primer entrada vacia en el directorio guarda el indice
        for content in self.directory:
            if content['state'] == 46:
                if content['name'] == filename:
                    print("\033[93m" + f'Ya existe un archivo \'{filename}\' en el sistema de archivos' + "\033[0m")
                    return

                used_clusters.append((content['start_cluster'],
                                    math.ceil(content['start_cluster']+content['size']/self.cluster_size)))
                
            elif content['state'] == 35 and index is None:
                index=self.directory.index(content)

        #Organiza de menor a mayor en funcion del cluster inicial
        used_clusters=sorted(used_clusters,key=lambda tup: tup[1])  
        #print(used_clusters)   

        #Termina si no se encontraron entradas vacias en el directorio
        if index is None:
            print("\033[93m" + 'El directorio está lleno' + "\033[0m" )
            return

        try:
            #obtiene los metadatos del archivo del host
            stat = os.stat(src_path)
            local_time = datetime.fromtimestamp(stat.st_ctime)
            create=local_time.strftime("%Y%m%d%H%M%S")
            local_time = datetime.fromtimestamp(stat.st_mtime)
            mod=local_time.strftime("%Y%m%d%H%M%S")
            size=stat.st_size
        except FileNotFoundError:
            print("\033[93m" + 'FileNotFoundError: El archivo especificado no existe' + "\033[0m" )
            return

        #Obtiene el primer cluster inicial en el cual se puede almacenar el archivo
        start_cluster = self.allocate(used_clusters,size)
        if not start_cluster:
            print("\033[93m" + 'No hay espacio en el sistema para este archivo' + "\033[0m" )
            return
        
        #tamaño de cada lectura (1KB)
        chunk_size = self.cluster_size

        #Funcion interna para la lectura del host
        def reader_thread():
            with open(src_path, 'rb') as f:
                bytes_read = 0
                while bytes_read < size:
                    #Guarda en la cola protegida
                    chunk = f.read(min(chunk_size, size - bytes_read))
                    if not chunk:
                        break
                    self.data_queue.put(chunk)
                    bytes_read += len(chunk)
            self.data_queue.put(None)

        #Funcion interna para la escritura en el FS
        def writer_thread():
                #Guarda en un bytearray los datos que se escribiran en el directorio
                binary_metadata=bytearray(b'.')
                binary_metadata+=(filename.ljust(14).encode('ascii')+b'\x00'+
                            struct.pack('<i',size)+
                            struct.pack('<i',start_cluster)+
                            create.encode('ascii')+
                            mod.encode('ascii')+
                            bytes(12))

                with open(self.img_path,'r+b') as fs:
                    #Guarda la informacion en el directorio
                    fs.seek(self.cluster_size+64*index)
                    fs.write(binary_metadata)
                    
                    #Guarda los datos del archivo
                    fs.seek(self.cluster_size*start_cluster)
                    while True:
                        #Extrae de la cola protegida
                        chunk = self.data_queue.get()
                        if chunk is None:
                            break
                        fs.write(chunk)
                        #Indica al productor que la tarea de procesamiento ha terminado
                        self.data_queue.task_done()

                #Guarda en memoria los datos del archivo
                self.directory[index]={
                    'state':46,
                    'name':filename,
                    'size':size,
                    'start_cluster':start_cluster,
                    'created':create,
                    'modified':mod
                }

        #Ejecuta la lectura y escritura de manera concurrente
        reader = threading.Thread(target=reader_thread)
        writer = threading.Thread(target=writer_thread)
        
        reader.start()
        writer.start()
        
        reader.join()
        writer.join()

    def allocate(self,used_clusters:list,size:int):
        '''Determina el primer cluster del FS en el que se puede almacenar un archivo'''
        req_clusters=math.ceil(size/self.cluster_size)

        #Inicio del espacio de datos
        start_cluster = 5
        for entry in used_clusters:
            #Verifica si hay suficiente espacio entre dos entradas para el archivo
            if entry[0]-start_cluster>req_clusters:
                return start_cluster
            else:
                start_cluster=entry[1]
        #Verifica si hay espacio al final de los archivos que se han almacenado
        if 1440-start_cluster>req_clusters:
            return start_cluster
        else:
            return None

    def delete(self,filename : str):
        '''Elimina un archivo del FS\n
        \'filename\' es el nombre del archivo a eliminar'''
        for entry in self.directory:
            if entry['name']==filename:
                index=self.directory.index(entry)
                #Borra la entrada del directorio en memoria
                self.directory[index]={
                    'state':35,
                    'name':'--------------',
                    'size':0,
                    'start_cluster':0,
                    'created':'00000000000000',
                    'modified':'00000000000000'
                }
                binary_metadata=bytearray(b'#')
                binary_metadata+=(b'--------------'+b'\x00'+
                      bytes(8)+
                      b'00000000000000'+
                      b'00000000000000'+
                      bytes(12)
                )
                #Se posiciona al inicio de la entrada del directorio y elimina la entrada, no se borran los datos del archivo
                with open(self.img_path,'r+b') as f:
                    f.seek(self.cluster_size+index*64)
                    f.write(binary_metadata)
                return

        print("\033[93m" + f'El archivo \'{filename}\' no se encuentra en el sistema de archivos' + "\033[0m" )

    def find(self,filename : str) -> dict:
        '''Determina si un archivo se encuentra en el FS t regresa el diccionario con sus datos'''
        for content in self.directory:
            if(content['name']==filename):
                return content
        return None

    def list_dir(self):
        '''Imprime una lista con todas las entradas del directorio'''
        table = PrettyTable()
        table.field_names = ["Nombre", "Tamaño", "Creado", "Modificado"]
        for content in self.directory:
            if content['state'] == 46:
                c=content['created']
                m=content['modified']
                table.add_row([content['name'],
                               content['size'],
                               f'{c[0:4]}-{c[4:6]}-{c[6:8]}  {c[8:10]}:{c[10:12]}:{c[12:14]}', 
                               f'{m[0:4]}-{m[4:6]}-{m[6:8]}  {m[8:10]}:{m[10:12]}:{m[12:14]}'])
        print(table.get_string(sortby="Nombre"))

def mostrar_menu():
    print("\nOpciones FIunamFS:")
    print("1. Listar contenido")
    print("2. Copiar archivo de FIunamFS")
    print("3. Agregar archivo a FIunamFS")
    print("4. Eliminar archivo")
    print("5. Salir")
    return input("Seleccione una opción (1-5): ")

def test_string(s :str) -> bool:
    '''Verifica que el nombre del archivo cumpla con la especificación'''
    try:
        if len(s) > 14:
            print("\033[93m" + 'El nombre del archivo debe ser una cadena ASCII <= 14 caracteres' + "\033[0m" )
            return False
        s.encode('ascii')
        return True
    except UnicodeEncodeError:
        print("\033[93m" + 'El nombre del archivo debe ser una cadena ASCII <= 14 caracteres' + "\033[0m" )
        return False

def main():
    fs_name = input("Ingrese la ruta del sistema de archivos: ")
    fs = FSsistop(fs_name)
    while True:
        opcion = mostrar_menu()
        print()  # Línea en blanco para mejor presentación
        
        match opcion:
            case "1":
                fs.list_dir()
            case "2":
                nombre = input("Nombre del archivo a copiar: ")
                if not test_string(nombre):
                    continue
                destino = input("Nombre del archivo de destino: ")
                fs.copyfromFS(destino, nombre)
            case "3":
                print("Ingrese la ruta completa del archivo (ejemplo: /ruta/completa/archivo.txt)")
                origen = input("Ruta del archivo a agregar: ")
                nombre = input("Nombre para el archivo en FIunamFS: ")
                if not test_string(nombre):
                    continue
                fs.copytoFS(origen, nombre)
            case "4":
                nombre = input("Nombre del archivo a eliminar: ")
                fs.delete(nombre)
            case "5":
                print("¡Hasta luego!")
                exit(0)
            case _:
                print("Opción no válida. Por favor, seleccione una opción del 1 al 5.")

if __name__ == "__main__":
    main()
