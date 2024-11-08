import os
import struct
import time
from threading import Thread, Lock

class FiUnamFS:
    def __init__(self, filepath):
        self.filepath = filepath
        self.lock = Lock()
        self.cluster_size = 256
        self.directory_clusters = 4  # Clusters reservados para el directorio
        self.directory_offset = self.cluster_size  # El superbloque ocupa el primer cluster
        self.entry_size = 64
        self.validate_fs()

    def validate_fs(self):
        with open(self.filepath, 'rb') as f:
            f.seek(0)
            superblock = f.read(1024)
            name = struct.unpack('8s', superblock[0:8])[0].decode('ascii').strip('\x00')
            version = struct.unpack('5s', superblock[10:15])[0].decode('ascii').strip('\x00')
            print(f"Validando sistema de archivos... Nombre: {name}, Versión: {version}")
            if name != 'FiUnamFS' or version != '25-1':
                raise ValueError("Sistema de archivos no compatible o corrupto")


if __name__ == "__main__":
    fs = FiUnamFS(r"C:\Users\amir0\Documents\Quinto Semestre\Sistemas Operativos\sistop-2025-1\proyectos\micro-sist-de-arch-multihilos\CuevasAmir-DeLaRosaFernando\fiunamfs.img")

