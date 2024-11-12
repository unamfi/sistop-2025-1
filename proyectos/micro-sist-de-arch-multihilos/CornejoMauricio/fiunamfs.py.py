import struct
import time
import os

class FiUnamFS:
    def __init__(self, archivo_img):
        self.archivo_img = archivo_img
        self.archivo = None
        self.tamano_cluster = 4096
        self.num_clusters_directorio = 4
        self.tamano_archivo = os.path.getsize(self.archivo_img)
        
    def abrir(self):
        self.archivo = open(self.archivo_img, 'r+b')
        
    def cerrar(self):
        if self.archivo:
            self.archivo.close()

    def listar_directorio(self):
        self.abrir()
        directorio = []
        TAMANO_ENTRADA_DIRECTORIO = 32
        inicio_directorio = 0
        num_entradas = self.num_clusters_directorio * (self.tamano_cluster // TAMANO_ENTRADA_DIRECTORIO)
        
        for i in range(num_entradas):
            self.archivo.seek(inicio_directorio + i * TAMANO_ENTRADA_DIRECTORIO)
            entrada = self.archivo.read(TAMANO_ENTRADA_DIRECTORIO)
            nombre = entrada[:23].decode('utf-8').strip('\x00')
            if nombre:
                tamano, tiempo_modificacion = struct.unpack('<IQ', entrada[24:32])
                tiempo_modificacion = time.ctime(tiempo_modificacion)
                directorio.append({'nombre': nombre, 'tamano': tamano, 'tiempo_modificacion': tiempo_modificacion})
        self.cerrar()
        return directorio

    def copiar_a_fs(self, ruta_origen, nombre_archivo):
        self.abrir()
        TAMANO_ENTRADA_DIRECTORIO = 32
        inicio_directorio = 0
        encontrado = False
        
        for i in range(self.num_clusters_directorio * (self.tamano_cluster // TAMANO_ENTRADA_DIRECTORIO)):
            self.archivo.seek(inicio_directorio + i * TAMANO_ENTRADA_DIRECTORIO)
            entrada = self.archivo.read(1)
            if entrada == b'\x00':
                encontrado = True
                self.archivo.seek(-1, 1)  # Volver un byte atrás
                break

        if not encontrado:
            print('No hay espacio en el directorio para este archivo.')
            self.cerrar()
            return

        with open(ruta_origen, 'rb') as archivo_origen:
            contenido = archivo_origen.read()
        tamano_archivo = len(contenido)
        tiempo_modificacion = int(time.time())
        nombre_archivo = nombre_archivo[:23].ljust(23, '\x00').encode('utf-8')
        entrada_directorio = struct.pack('<23sBIQ', nombre_archivo, 0x01, tamano_archivo, tiempo_modificacion)
        self.archivo.write(entrada_directorio)

        cluster_datos = inicio_directorio + self.num_clusters_directorio * self.tamano_cluster
        self.archivo.seek(cluster_datos)
        self.archivo.write(contenido)
        self.cerrar()

    def eliminar_archivo(self, nombre_archivo):
        self.abrir()
        TAMANO_ENTRADA_DIRECTORIO = 32
        inicio_directorio = 0
        encontrado = False

        for i in range(self.num_clusters_directorio * (self.tamano_cluster // TAMANO_ENTRADA_DIRECTORIO)):
            self.archivo.seek(inicio_directorio + i * TAMANO_ENTRADA_DIRECTORIO)
            entrada = self.archivo.read(TAMANO_ENTRADA_DIRECTORIO)
            nombre = entrada[:23].decode('utf-8').strip('\x00')
            if nombre == nombre_archivo:
                self.archivo.seek(inicio_directorio + i * TAMANO_ENTRADA_DIRECTORIO)
                self.archivo.write(b'\x00' * TAMANO_ENTRADA_DIRECTORIO)
                encontrado = True
                break

        if not encontrado:
            print(f'Archivo "{nombre_archivo}" no encontrado en el directorio.')

        self.cerrar()
