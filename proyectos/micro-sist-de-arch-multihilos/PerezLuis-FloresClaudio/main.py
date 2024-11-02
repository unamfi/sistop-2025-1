import os, stat, errno, fuse, sys, struct
from fuse import Fuse


class FSsistop():
    def __init__(self,path):

        self.path=path
        self.superblock=self.read_superblock(path)

        print(self.superblock[40:44])
        print("tamaño de cluster:",struct.unpack('<i',self.superblock[40:44])[0])
        self.cluster_size=struct.unpack('<i',self.superblock[40:44])[0]

        print(self.superblock[45:49])
        print("tamaño del directorio en clusters:",struct.unpack('<i',self.superblock[45:49])[0])
        self.directory_size=struct.unpack('<i',self.superblock[45:49])[0]

        print(self.superblock[50:54])
        print("numero de clusters en la unidad:",struct.unpack('<i',self.superblock[50:54])[0])
        self.size=struct.unpack('<i',self.superblock[50:54])[0]


        self.directory=self.read_directory(path)

    def read_superblock(self,path):
        with open(path, 'rb+') as f:
            data = f.read(64)
            id_fs, version = struct.unpack('<9s5s', data[:14])
            print(data)

            print(id_fs)
            id_fs=id_fs[0:-1]
            print(id_fs)

            print(version)
            version=version[1:]
            print(version)
            
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
                data.append(f.read(64))
                print(data[i])
            # print("Estado: ",data[0])
            # print('nombre:',data[1:16].decode('ascii'))
            # print('tamaño en bytes:',struct.unpack('<i',data[16:20])[0])
            # print('cluster inicial:',struct.unpack('<i',data[20:24])[0])
            # print('Hora y fecha de creacion:',struct.unpack('<4s2s2s2s2s2s',data[24:38]))
            return data


testfs=FSsistop('fi.img')
