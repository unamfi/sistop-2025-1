import os,struct,math
from simple_term_menu import TerminalMenu
from prettytable import PrettyTable
from datetime import datetime


class FSsistop():
    def __init__(self,img_path):

        self.img_path=img_path
        self.superblock=self.read_superblock(img_path)

        #print(self.superblock[40:44])
        #print("tamaño de cluster:",struct.unpack('<i',self.superblock[40:44])[0])
        self.cluster_size=struct.unpack('<i',self.superblock[40:44])[0]

        #print(self.superblock[45:49])
        print("tamaño del directorio en clusters:",struct.unpack('<i',self.superblock[45:49])[0])
        self.directory_size=struct.unpack('<i',self.superblock[45:49])[0]

        #print(self.superblock[50:54])
        #print("numero de clusters en la unidad:",struct.unpack('<i',self.superblock[50:54])[0])
        self.size=struct.unpack('<i',self.superblock[50:54])[0]


        self.directory=self.read_directory(img_path)

    def read_superblock(self,path):
        with open(path, 'rb+') as f:
            data = f.read(64)
            id_fs, version = struct.unpack('<9s5s', data[:14])
            #print(data)

            #print(id_fs)
            id_fs=id_fs[0:-1]
            #print(id_fs)

            #print(version)
            version=version[1:]
            #print(version)
            
            if id_fs.decode('ascii') != 'FiUnamFS' or version.decode('ascii') != '25-1':
                raise ValueError("El archivo no es un sistema de archivos FiUnamFS o la versión es incorrecta.")
            else:
                return data

    def read_directory(self,path):
        with open(path, 'rb+') as f:
            f.seek(self.cluster_size)
            #print(self.cluster_size)
            data=[]
            #prueba lectura del directorio
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
                #print(data[i])

            # data = f.read(64)
            # print("Estado: ",data[0])
            # print('nombre:',data[1:16].decode('ascii'))
            # print('tamaño en bytes:',struct.unpack('<i',data[16:20])[0])
            # print('cluster inicial:',struct.unpack('<i',data[20:24])[0])
            # print('Hora y fecha de creacion:',data[24:38].decode('ascii'))
            # print('Hora y fecha de modificacion:',data[38:52].decode('ascii'))
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
                # for i in range(content['start_cluster'], 
                #             math.ceil(content['start_cluster']+content['size']/self.cluster_size)):
                #     used_clusters.append(i)
                if content['name'] == filename:
                    print(f'Ya existe un archivo \'{filename}\' en el sistema de archivos')
                    return

                used_clusters.append((content['start_cluster'],
                                    math.ceil(content['start_cluster']+content['size']/self.cluster_size)))
                
            elif not index:
                index=self.directory.index(content)
                #print(index)

        used_clusters=sorted(used_clusters,key=lambda tup: tup[1])     
        #print(used_clusters)

        if not index:
            print('El directorio está lleno')
            return
            #self.directory[i]
            #print(self.directory[i])
        else:
            size=None
            create=None
            mod=None
            try:
                stat = os.stat(src_path)

                local_time = datetime.fromtimestamp(stat.st_ctime)
                #print(local_time.strftime("%Y%m%d%H%M%S"))
                create=local_time.strftime("%Y%m%d%H%M%S")

                local_time = datetime.fromtimestamp(stat.st_mtime)
                #print(local_time.strftime("%Y%m%d%H%M%S"))
                mod=local_time.strftime("%Y%m%d%H%M%S")

                size=stat.st_size
                # print(os.stat(src_path).st_size)
                # size=os.stat(src_path).st_size
                # print(os.stat(src_path).st_ctime)
                # create=os.stat(src_path).st_ctime
                # create=datetime.utcfromtimestamp(create).strftime('%Y%m%d%H%M%S')
                # print(create)
                # print(os.stat(src_path).st_mtime)
                # mod=os.stat(src_path).st_mtime
                
            except FileNotFoundError:
                print('FileNotFoundError: El archivo especificado no existe')
                return
            # req_clusters=math.ceil(size/self.cluster_size)
            # print('req clusters',req_clusters)
            start_cluster=self.allocate(used_clusters,size)
            #print('start cluster:',start_cluster)
            if not start_cluster:
                print('No hay espacio en el sistema para este archivo')
            else:
                self.write(src_path,filename,size,start_cluster,index,create,mod)


    def allocate(self,used_clusters,size):
        req_clusters=math.ceil(size/self.cluster_size)
        #print(req_clusters)
        start_cluster = 5

        # if (used_clusters[1][0]-start_cluster<req_clusters):
        #     return start_cluster
        for entry in used_clusters:
            if entry[0]-start_cluster>req_clusters:
                #print(entry[0]-start_cluster)
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
        #     #print(file_data )
        #print(type(filename))
        
   
        # filename,
        # struct.pack('<i',src_size),
        # struct.pack('<i',start_cluster),
        # create.encode('ascii'),
        # mod.encode('ascii'),
        binary_metadata=bytearray(b'.')
        binary_metadata+=(filename.ljust(14).encode('ascii')+b'\x00'+
                      struct.pack('<i',src_size)+
                      struct.pack('<i',start_cluster)+
                      create.encode('ascii')+
                      mod.encode('ascii')+
                      bytes(12)
        )   
        with open(self.img_path,'r+b') as fs:
            #modificacion del directorio
            fs.seek(self.cluster_size+64*dir_idx)
            fs.write(binary_metadata)

            #modificacion del espacio de datos
            fs.seek(self.cluster_size*start_cluster)
            fs.write(file_data)

            #modificacion del directorio en memoria
            self.directory[dir_idx]={
                'state':46,
                'name':filename,
                'size':src_size,
                'start_cluster':start_cluster,
                'created':create,
                'modified':mod
            }
            # for i in self.directory:
            #     print(i)


    def delete(self,filename):
        for entry in self.directory:
            size = None
            start_cluster = None
            if entry['name']==filename:
                index=self.directory.index(entry)
                size = entry['size']
                start_cluster = entry['start_cluster']
                self.directory[index]={
                    'state':35,
                    'name':'--------------',
                    'size':0,
                    'start_cluster':0,
                    'created':'00000000000000',
                    'modified':'00000000000000'
                }
                # for i in self.directory:
                #     print(i)
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
        #table.reversesort=True
        print(table.get_string(sortby="Nombre"))

def main():
    
    options = ["Listar contenido", "Copiar archivo de FIunamFS", "Agregar archivo a FIunamFS", "Eliminar archivo", "Salir"]
    terminal_menu = TerminalMenu(options)
    fs=FSsistop('fi.img')
    while(True):
        print("Opciones FIunamFS:")
        opt_idx = terminal_menu.show()
        print('->'+options[opt_idx]+'\n')
        match options[opt_idx]:
            case "Listar contenido":
                fs.list_dir()
                pass
            case "Copiar archivo de FIunamFS":
                fs.copyfromFS('mensaje.jpg','mensaje.jpg')
                pass
            case "Agregar archivo a FIunamFS":
                fs.copytoFS('test.png','test.png')
                pass
            case "Eliminar archivo":
                fs.delete('test.png')
                pass
            case "Salir":
                exit(0)
        

if __name__ == "__main__":
    main()

testfs=FSsistop('fi.img')
testfs.list_dir()
testfs.copyfromFS('lol','lol')
testfs.copytoFS('test.png','test.png')
testfs.list_dir()
testfs.delete('test.png')
testfs.list_dir()
testfs.delete('test.png')
#print(os.stat('lol.png').st_size)
