"""
Proyecto 2 - (Micro) Sistema de Archivos Multihilos
Author: Medrano Solano Enrique
Materia: Sistemas Operativos (sistop-2025-1)
lenguaje: Python 3.12.7 64 bits
Entorno: Windows 11
Fecha de entrega: 04/11/2024

Descripción de proyecto: Este programa implementa un sistema de archivos y su sadministración de procesos del mismo
el cual permitirá mediante una interfaz gráfica (GUI) listar el contenido del directorio, copiar y eliminar archivos tanto
de FiUnamFS como de manera local, así mismo se emplea el uso de multihilos (2) y sincronización para evitar concurrencia.
"""

#librerías importadas
import threading
import struct
import os
from datetime import datetime

#variables fijas
DISK_FILE = 'fiunamfs.img' #nombre de archivo ejemplo de FiUnamFS
DISK_SIZE = 1440 * 1024 # 1440 Kilobytes
CLUSTER_SIZE =  256 * 4 #Se ocupan 4 clusters de 256 bytes
disk_lock = threading.Lock() #Se sincroniza el acceso al disco

def verificar_superbloque():
    """
    Esta función verifica que el superbloque en el archivo de disco sea válido.
    Se leen los primeros 8 bytes del archivo para comprobar si la cadena contiene "FiUnamFS"
    de esta forma se verifica el archivo.

    Si no contiene se le informa al ususario:   ValueError: ¡No es un sistema de archivos del tipo FiUnamFS!
    """
    with open(DISK_FILE, 'rb') as disk:
        disk.seek(0)
        magic = disk.read(8).decode('ascii')
        if magic != "FiUnamFS":
            raise ValueError("¡No es un sistema de archivos del tipo FiUnamFS!")

def lista_directorio():
    """
    Muestra el contenido del directorio de FiUnamFS.
    Lee el directorio desde el archivo de disco y muetsra los nombre y tamaño de los archivos almacenados,
    esta información se obtiene de los clusters de datos del disco.
    """
    print("\nContenido del directorio: ")
    with open(DISK_FILE, 'rb') as disk:
        #Inicia en el directorio (cluster 1)
        disk.seek(CLUSTER_SIZE)
        for i in range(4*(CLUSTER_SIZE // 64)):
            entry = disk.read(64)
            tipo = entry[0:1].decode('ascii')
            if tipo == '#':
                continue
            nombre = entry[1:16].decode('ascii').strip()
            tamaño = struct.unpack('<I', entry[16:20])[0]
            print(f"\nArchivos: {nombre} -> Tamaño: {tamaño} bytes")

def copiar_fiunamfs_a_local(archivo_nombre):
    """
    
    """

def copiar_local_a_fiunamfs(archivo_nombre):
    """
    
    """

def eliminar_archivo(archivo_nombre):
    """
    
    """

#Funciones para la ejecución de hilos
def lista_directorio_thead():
    """
    
    """

def copiar_fiunamfs_a_local_thread():
    """
    
    """

def eliminar_archivo_thread():
    """
    
    """

#función para el menú dentro de terminal
def menu():
    """
    
    """

#Main
if __name__ == "__main__":
    try:
        verificar_superbloque()

    except ValueError as e:
        print(e)

