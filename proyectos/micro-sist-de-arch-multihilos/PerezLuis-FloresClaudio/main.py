import os,struct,math
from prettytable import PrettyTable
from datetime import datetime

class FSsistop():
    # [El resto de la clase FSsistop permanece igual]
    def __init__(self,img_path):
        self.img_path=img_path
        self.superblock=self.read_superblock(img_path)
        self.cluster_size=struct.unpack('<i',self.superblock[40:44])[0]
        print("tamaño del directorio en clusters:",struct.unpack('<i',self.superblock[45:49])[0])
        self.directory_size=struct.unpack('<i',self.superblock[45:49])[0]
        self.size=struct.unpack('<i',self.superblock[50:54])[0]
        self.directory=self.read_directory(img_path)

    # [Mantener todos los métodos existentes de la clase FSsistop sin cambios]
    def read_superblock(self,path):
        with open(path, 'rb+') as f:
            data = f.read(64)
            id_fs, version = struct.unpack('<9s5s', data[:14])
            id_fs=id_fs[0:-1]
            version=version[1:]
            if id_fs.decode('ascii') != 'FiUnamFS' or version.decode('ascii') != '25-1':
                raise ValueError("El archivo no es un sistema de archivos FiUnamFS o la versión es incorrecta.")
            else:
                return data

    def read_directory(self,path):
        with open(path, 'rb+') as f:
            f.seek(self.cluster_size)
            data=[]
            for i in range(64):
                temp = f.read(64)
                data.append({
                    'state':temp[0],
                    'name':temp[1:15].decode('ascii').strip(),
                    'size':struct.unpack('<i',temp[16:20])[0],
                    'start_cluster':struct.unpack('<i',temp[20:24])[0],
                    'created':temp[24:38].decode('ascii'),
                    'modified':temp[38:52].decode('ascii')
                })
            return data
    
    def copyfromFS(self,dest_path,filename):
        entry=self.find(filename)
        if not entry:
            print(f"{filename} no se encuentra en el sistema de archivos")
        else:
            with open(self.img_path, 'rb') as f:
                f.seek(entry['start_cluster']*self.cluster_size)
                data=f.read(entry['size'])
            
            with open(dest_path,'wb')as f:
                f.seek(0)
                f.write(data)

    def copytoFS(self,src_path,filename):
        index=None
        used_clusters=[]
        for content in self.directory:
            if content['state'] == 46:
                if content['name'] == filename:
                    print(f'Ya existe un archivo \'{filename}\' en el sistema de archivos')
                    return

                used_clusters.append((content['start_cluster'],
                                    math.ceil(content['start_cluster']+content['size']/self.cluster_size)))
                
            elif not index:
                index=self.directory.index(content)

        used_clusters=sorted(used_clusters,key=lambda tup: tup[1])     

        if not index:
            print('El directorio está lleno')
            return
        else:
            size=None
            create=None
            mod=None
            try:
                stat = os.stat(src_path)
                local_time = datetime.fromtimestamp(stat.st_ctime)
                create=local_time.strftime("%Y%m%d%H%M%S")
                local_time = datetime.fromtimestamp(stat.st_mtime)
                mod=local_time.strftime("%Y%m%d%H%M%S")
                size=stat.st_size
            except FileNotFoundError:
                print('FileNotFoundError: El archivo especificado no existe')
                return
            start_cluster=self.allocate(used_clusters,size)
            if not start_cluster:
                print('No hay espacio en el sistema para este archivo')
            else:
                self.write(src_path,filename,size,start_cluster,index,create,mod)

    def allocate(self,used_clusters,size):
        req_clusters=math.ceil(size/self.cluster_size)
        start_cluster = 5
        for entry in used_clusters:
            if entry[0]-start_cluster>req_clusters:
                return start_cluster
            else:
                start_cluster=entry[1]
        if 1440-start_cluster>req_clusters:
            return start_cluster
        else:
            return None

    def write(self,src_path,filename,src_size,start_cluster,dir_idx,create,mod):
        with open(src_path,'rb') as f:
            f.seek(0)
            file_data=f.read(src_size)
        
        binary_metadata=bytearray(b'.')
        binary_metadata+=(filename.ljust(14).encode('ascii')+b'\x00'+
                      struct.pack('<i',src_size)+
                      struct.pack('<i',start_cluster)+
                      create.encode('ascii')+
                      mod.encode('ascii')+
                      bytes(12)
        )   
        with open(self.img_path,'r+b') as fs:
            fs.seek(self.cluster_size+64*dir_idx)
            fs.write(binary_metadata)
            fs.seek(self.cluster_size*start_cluster)
            fs.write(file_data)
            self.directory[dir_idx]={
                'state':46,
                'name':filename,
                'size':src_size,
                'start_cluster':start_cluster,
                'created':create,
                'modified':mod
            }

    def delete(self,filename):
        for entry in self.directory:
            if entry['name']==filename:
                index=self.directory.index(entry)
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
                with open(self.img_path,'r+b') as f:
                    f.seek(self.cluster_size+index*64)
                    f.write(binary_metadata)
                return

        print(f'El archivo \'{filename}\' no se encuentra en el sistema de archivos')

    def find(self,filename) -> dict:
        for content in self.directory:
            if(content['name']==filename):
                return content
        return None

    def list_dir(self):
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

def main():
    fs = FSsistop('fi.img')
    while True:
        opcion = mostrar_menu()
        print()  # Línea en blanco para mejor presentación
        
        match opcion:
            case "1":
                fs.list_dir()
            case "2":
                nombre = input("Nombre del archivo a copiar: ")
                destino = input("Nombre del archivo de destino: ")
                fs.copyfromFS(destino, nombre)
            case "3":
                origen = input("Ruta del archivo a agregar: ")
                nombre = input("Nombre para el archivo en FIunamFS: ")
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
