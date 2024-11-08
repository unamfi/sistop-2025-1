"""
Proyecto 2 - (Micro) Sistema de Archivos Multihilos
Author: Medrano Solano Enrique
No. Cuenta: 32015284-1
Materia: Sistemas Operativos (sistop-2025-1)

lenguaje: Python3 3.12.7 o 3.11.10 | 64 bits
Entorno: Windows 11
IDE: Visual Studio Code
Fecha de entrega: 07/11/2024

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
    Función encargada de copiar un archivo desde el sistema FiUnamFS al sistema local

    Argumentos necesarios:
    archivo_nombre (str): Nombre del archivo a copiar del sistema FiUnamFS

    En caso de que exista en FiUnamFS, lo descrga al sistema local identicamente. En caso de no ser encontrado
    se muetsra un mensaje al usuario "Archivo '{archivo_nombre}' no encontrado en FiUnamFS."
    """

    encontrado = False
    archivo_nombre = archivo_nombre.strip() #Permite eliminar espacio en blanco adicional de la cadena
    with open(DISK_FILE, 'rb') as disk:
        disk.seek(CLUSTER_SIZE) #Se dirije al inicio del directorio
        for i in range(4 * (CLUSTER_SIZE // 64)):
            entry = disk.read(64)
            tipo = entry[0:1].decode('ascii')
            #Se lee el nombre del archivo y elimina los espacio en blanco o caracteres nulos
            nombre = entry[1:16].decode('ascii').replace('\x00', '').strip()

            # print(f"Comparando con entrada de directorio: {nombre}") #Solo es para debugg en pruebas de funcionamiento

            #Hace la verificación entre archivo buscado y nombre coincidente
            if tipo == '.' and nombre == archivo_nombre:
                tamaño = struct.unpack('<I', entry[16:20])[0]
                inicio_cluster = struct.unpack('<I', entry[20:24])[0]

                #Se copia el archivo al sistema local
                disk.seek(inicio_cluster * CLUSTER_SIZE)
                data = disk.read(tamaño)

                with open(archivo_nombre, "wb") as salida_archivo:
                    salida_archivo.write(data)
                print(f"Archivo '{archivo_nombre}' copiado al sistema local correctamente!!!")
                encontrado = True
                break
    if not encontrado:
        print(f"Archivo '{archivo_nombre}' no encontrado en FiUnamFS.")

def copiar_local_a_fiunamfs(archivo_nombre):
    """
    Función para copiar un archivo desde el sistema local a FiUnamFS.

    Argumentos necesarios:
    archivo_nombre (str): nombre del archivo para copiar a FiUnamFS.

    Casos:
    SI no hay espacio suficiente para almacenar el archivo o simplemnete no existe el archivo, se mostrata un mensaje al usuario en terminal
    En caso de existir y tener espacio se copia existosamete, de tal forma que se añade al directorio de FiUnamFS.
    """

    try:
        with open(archivo_nombre, 'rb') as entrada_archivo:
            data = entrada_archivo.read()
            tamano = len(data)

        with open(DISK_FILE, 'r+b') as disk:
            disk.seek(CLUSTER_SIZE) #Dirijirse al inicio del directorio
            #Se busca una entrada libre
            for i in range(4*(CLUSTER_SIZE // 64)): 
                entry_pos = disk.tell()
                entry = disk.read(64)
                tipo = entry[0:1].decode('ascii')
                nombre = entry[1:16].decode('ascii').strip()

                if tipo == '#' or nombre == "---------------":
                    #Se agrega el archvio en la primera entrada dlibre
                    disk.seek(entry_pos)
                    disk.write(b'.') #Asignación del tipo de archivo
                    disk.write(archivo_nombre.ljust(15)).encode('ascii') #Asignación de nombre de archivo
                    disk.write(struct.pack('<I', tamano)) #Asdignación de tamaño de archivo

                    # Encontrar un espacio para el archivo en el área de datos
                    inicio_cluster = 5  # Usamos el primer cluster después del directorio
                    disk.write(struct.pack('<I', inicio_cluster))  # Cluster inicial

                    #Asignación de fecha de creación y modificación
                    fecha_act = datetime.now().strftime('%Y%m%d%H%M%S').encode('ascii')
                    disk.write(fecha_act)
                    disk.write(fecha_act)

                    #Escribit el contenido del archivo
                    disk.seek(inicio_cluster * CLUSTER_SIZE)
                    disk.write(data)
                    print(f"Archivo {archivo_nombre} copiado correctamente a FiUnamFS!!!")
                    return
            print("No hay espacio disponible en el directorio para el archivo.")
    except FileNotFoundError:
        print(f"El archivo {archivo_nombre} no existe en el sistema local.")

def eliminar_archivo(archivo_nombre):
    """
    Función para eliminar un archivo del sistema FiUnamFS.

    Argumentos necesarios:
    archivo_nombre (str): nombre del archivo a eliminar

    Casos:
    Si el archivo existe se marca como eliminado en el directorio FiUnamFS.
    EN caso de no existir, se muestra el mensaje pertinente al usuario.
    """

    with open(DISK_FILE, 'r+b') as disk:
        disk.seek(CLUSTER_SIZE) #Se dirije al inicio del directorio
        for i in range(4 * (CLUSTER_SIZE // 64)):
            entry_pos = disk.tell()
            entry = disk.read(64)
            tipo = entry[0:1].decode('ascii')
            nombre = entry[1:16].decode('ascii').strip()

            if tipo == '.' and nombre == archivo_nombre:
                #Se marca la entrada como liberada
                disk.seek(entry_pos)
                disk.write(b'#' + b"---------------".ljust(63, b'#'))
                print(f"Archivo {archivo_nombre} eliminado correctamente de FiUnamFS!!!")
                return
        print(f"Archivo {archivo_nombre} no encontrado en FiUnamFS.")

#Funciones para la ejecución de hilos
def lista_directorio_thead():
    """
    Función para listar el directorio de FiUnamFS en un hilo independiente.
    Utilizando un lock para asegurar que el acceso al disco no se solape con otros hilos.
    """
    #Se asegura que no haya interferencias en el acceso al disco
    with disk_lock:
        lista_directorio()

def copiar_fiunamfs_a_local_thread(archivo_nombre):
    """
    Función para copiar un archivo desde FiUnamFS a sistema local en un hilo independiente.
    Utilizando un lock para asegurar que el acceso al disco no se solape con otros hilos.
    """
    with disk_lock:
        copiar_fiunamfs_a_local(archivo_nombre)

def eliminar_archivo_thread(archivo_nombre):
    """
    Función para eliminar un archivo de FiUnamFS en un hilo independiente.
    Utilizando un lock para asegurar que el acceso al disco no se solape con otros hilos.
    """
    with disk_lock:
        eliminar_archivo(archivo_nombre)

#función para el menú dentro de terminal
def menu():
    """
    Muestra el menú interactivo del sistema de archivos FiUnamFS, permitiendo
    al usuario interactuar con el sistema para listar, copiar y eliminar archivos.

    Las operaciones se pretenden realizan utilizando hilos para asegurar que el sistema
    pueda realizar múltiples tareas simultáneamente.
    """

    while True:
        print("\n--- Menú de FiUnamFS ---")
        print("1. Lista de contenido del directorio")
        print("2. Copiar archivo de FiUnamFS al sistema local")
        print("3. Copiar archivo del sistema local a FiUnamFS")
        print("4. Eliminar archivo de FiUnamFS")
        print("5. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            t1 = threading.Thread(target=lista_directorio_thead)
            t1.start()
            t1.join()
        elif opcion == '2':
            archivo_nombre = input("Ingresa el nombre del archivo a copiar de FiUnamFS: ")
            t2 = threading.Thread(target=copiar_fiunamfs_a_local_thread, args=(archivo_nombre,))
            t2.start()
            t2.join()
        elif opcion == '3':
            archivo_nombre = input("Ingrese el nombre del archivo a FiUnamFS: ")
            t3 = threading.Thread(target=copiar_local_a_fiunamfs, args=(archivo_nombre,))
            t3.start()
            t3.join()
        elif opcion == '4':
            archivo_nombre = input("Ingresa el nombre del archivo a eliminar de FiUnamFS: ")
            t4 = threading.Thread(target=eliminar_archivo_thread, args=(archivo_nombre,))
            t4.start()
            t4.join()
        elif opcion == '5':
            print("Saliendo del sistema de archivos FiUnamFS.....")
            break
        else:
            print("Opción ingresada ¡no válida!, por favor intenta de nuevo :) ")

#Main
if __name__ == "__main__":
    try:
        verificar_superbloque()
        menu()
    except ValueError as e:
        print(e)

