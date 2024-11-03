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

Este programa utiliza MODELO DE FUSE

"""

import os
import struct
from fuse import FUSE, Operations, FuseOSError #importamos bibliotecas necesarioas
import errno

class FiUnamFS(Operations):
    DIRECTORY_CLUSTERS = range(1, 5)
    CLUSTER_SIZE = 1024  # Cada cluster tiene 1024 bytes (4 sectores de 256 bytes)
    ENTRY_SIZE = 64  # Cada entrada en el directorio mide 64 bytes

    def __init__(self, disk_file):
        self.disk_file = disk_file
        self.files = self.read_directory()

    def read_cluster(self, cluster_number):
        with open(self.disk_file, 'rb') as f:
            f.seek(cluster_number * self.CLUSTER_SIZE)
            return f.read(self.CLUSTER_SIZE)

    def read_directory(self):
        directory_entries = []
        
        for cluster_number in self.DIRECTORY_CLUSTERS:
            cluster_data = self.read_cluster(cluster_number)
            
            for i in range(0, self.CLUSTER_SIZE, self.ENTRY_SIZE):
                entry_data = cluster_data[i:i + self.ENTRY_SIZE]
                
                if entry_data[0] == 0x23:  # Entrada vacía ('#')
                    continue
                
                file_type = chr(entry_data[0])
                file_name = entry_data[1:16].decode('ascii').strip()
                file_size = struct.unpack('<I', entry_data[16:20])[0]
                start_cluster = struct.unpack('<I', entry_data[20:24])[0]
                creation_date = entry_data[24:37].decode('ascii')
                modification_date = entry_data[38:51].decode('ascii')

                # Imprimir cada entrada de archivo leída
                print(f"Archivo encontrado: {file_name}, Tamaño: {file_size}")

                directory_entries.append({
                    'file_type': file_type,
                    'file_name': file_name,
                    'file_size': file_size,
                    'start_cluster': start_cluster,
                    'creation_date': creation_date,
                    'modification_date': modification_date
                })
        
        return directory_entries

    #Agragamos loa archvos existentes incluyendo a . y ..
    def readdir(self, path, fh):
        print("Listando archivos en readdir")
        yield '.'
        yield '..'
        for file in self.files:
            print(f"Archivo en directorio: {file['file_name']}")
            yield file['file_name']

    def getattr(self, path, fh=None):
        if path == '/':
            return dict(st_mode=(0o755 | 0o040000), st_nlink=2)

        filename = path.lstrip('/')
        file = next((f for f in self.files if f['file_name'] == filename), None)

        if file:
            return dict(
                st_mode=(0o444 | 0o100000),  # Archivo de solo lectura
                st_size=file['file_size'],
                st_ctime=int(file['creation_date']),
                st_mtime=int(file['modification_date']),
                st_atime=int(file['modification_date']),
                st_nlink=1
            )
        raise FuseOSError(errno.ENOENT)

# Inicializar y montar el sistema de archivos
if __name__ == '__main__':
    mountpoint = '/mnt'  # Cambia al punto de montaje adecuado en tu sistema
    FUSE(FiUnamFS('fiunamfs.img'), mountpoint, nothreads=True, foreground=True)
