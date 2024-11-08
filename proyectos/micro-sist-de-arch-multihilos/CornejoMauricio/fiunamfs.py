#Cornejo Gonzalez Mauricio PROYECTO 2
import struct
import time
import os

class FiUnamFS:
    def __init__(self, archivo_img):
        # Inicializa el sistema de archivos con el archivo de imagen
        self.archivo_img = archivo_img
        self.archivo = None  # Archivo de imagen abierto
        self.tamano_cluster = 4096  # Tamaño de cada cluster
        self.num_clusters_directorio = 4  # Número de clusters usados por el directorio
        # Obtiene el tamaño total del archivo de imagen
        self.tamano_archivo = os.path.getsize(self.archivo_img)
        
    def abrir(self):
        # Abre el archivo en modo lectura/escritura binario
        self.archivo = open(self.archivo_img, 'r+b')
        
    def cerrar(self):
        # Cierra el archivo si está abierto
        if self.archivo:
            self.archivo.close()

    def listar_directorio(self):
        # Abre el archivo y crea una lista vacía para almacenar los archivos del directorio
        self.abrir()
        directorio = []
        TAMANO_ENTRADA_DIRECTORIO = 32
        inicio_directorio = 0
        # Calcula el número total de entradas de directorio
        num_entradas = self.num_clusters_directorio * (self.tamano_cluster // TAMANO_ENTRADA_DIRECTORIO)
        
        for i in range(num_entradas):
            # Posiciona el puntero para leer cada entrada de directorio
            self.archivo.seek(inicio_directorio + i * TAMANO_ENTRADA_DIRECTORIO)
            entrada = self.archivo.read(TAMANO_ENTRADA_DIRECTORIO)
            # Obtiene el nombre del archivo y lo limpia de caracteres vacíos
            nombre = entrada[:23].decode('utf-8').strip('\x00')
            if nombre:  # Si la entrada tiene un nombre válido
                tamano, tiempo_modificacion = struct.unpack('<IQ', entrada[24:32])
                tiempo_modificacion = time.ctime(tiempo_modificacion)
                # Agrega la información del archivo a la lista
                directorio.append({'nombre': nombre, 'tamano': tamano, 'tiempo_modificacion': tiempo_modificacion})
        self.cerrar()
        return directorio

    def copiar_a_fs(self, ruta_origen, nombre_archivo):
        # Abre el archivo e intenta encontrar un espacio vacío en el directorio
        self.abrir()
        TAMANO_ENTRADA_DIRECTORIO = 32
        inicio_directorio = 0
        encontrado = False
        
        for i in range(self.num_clusters_directorio * (self.tamano_cluster // TAMANO_ENTRADA_DIRECTORIO)):
            self.archivo.seek(inicio_directorio + i * TAMANO_ENTRADA_DIRECTORIO)
            entrada = self.archivo.read(1)
            if entrada == b'\x00':
                encontrado = True
                # Retrocede un byte para posicionar correctamente el puntero
                self.archivo.seek(-1, 1)
                break

        if not encontrado:
            print('No hay espacio en el directorio para este archivo.')
            self.cerrar()
            return

        # Lee el contenido del archivo a copiar
        with open(ruta_origen, 'rb') as archivo_origen:
            contenido = archivo_origen.read()
        tamano_archivo = len(contenido)
        tiempo_modificacion = int(time.time())
        # Empaqueta la entrada de directorio con el nombre, tamaño y marca de tiempo
        nombre_archivo = nombre_archivo[:23].ljust(23, '\x00').encode('utf-8')
        entrada_directorio = struct.pack('<23sBIQ', nombre_archivo, 0x01, tamano_archivo, tiempo_modificacion)
        self.archivo.write(entrada_directorio)

        # Escribe los datos del archivo en el cluster de datos
        cluster_datos = inicio_directorio + self.num_clusters_directorio * self.tamano_cluster
        self.archivo.seek(cluster_datos)
        self.archivo.write(contenido)
        self.cerrar()

    def eliminar_archivo(self, nombre_archivo):
        # Abre el archivo y busca la entrada de directorio con el nombre del archivo
        self.abrir()
        TAMANO_ENTRADA_DIRECTORIO = 32
        inicio_directorio = 0
        
        for i in range(self.num_clusters_directorio * (self.tamano_cluster // TAMANO_ENTRADA_DIRECTORIO)):
            self.archivo.seek(inicio_directorio + i * TAMANO_ENTRADA_DIRECTORIO)
            entrada = self.archivo.read(TAMANO_ENTRADA_DIRECTORIO)
            nombre = entrada[:23].decode('utf-8').strip('\x00')
            if nombre == nombre_archivo:
                # Marca la entrada de directorio como libre
                self.archivo.seek(-TAMANO_ENTRADA_DIRECTORIO, 1)
                self.archivo.write(b'\x00' * TAMANO_ENTRADA_DIRECTORIO)
                print(f'Archivo "{nombre_archivo}" eliminado.')
                break
        else:
            print(f'Archivo "{nombre_archivo}" no encontrado.')
        self.cerrar()
