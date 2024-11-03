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

Este programa tratara de emular la terminald de windows, esto para que el usuario no se
de cuenta que esta trabajando sobre un programa, y tratara de parecer invisible ante este
"""

import os
import struct
import threading


#definicion para listar los archivos
def montaje(fiunamfs):
    #se abre el fiunamfs.img en modo binario
    with open(fiunamfs,'rb') as disco:
        #se verifica el niombre del sistema
        disco.seek(0)
        if disco.read(8).decode('ascii')!='FiUnamFS':
            print(f"\n Este programa esta diseñado solo para fiunamfs.img")
        else:
            print("\n Sistema: FiunamFS")
        
        #ahora vamos a validar la version!
        disco.seek(10)
        version = disco.read(4).decode('ascii')
        if version != '25-1':
            print("\n Al parecer este archivo no es del semestre 25-1")

        else: print("\n Version: 25-1")

        #especificamos etiqueta del volumen
        disco.seek(20)
        vol = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n etiqueta volumen: {vol}")

        #especificamos el tamaño del cluster :D
        disco.seek(40)
        size = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n Tamño cluster: {size}")
        
        #especificamos el numero de clusteres
        disco.seek(45)
        numclusters = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n Numero de clusteres: {size}")

        #especificamos el numero de cluster de la unidad completa
        disco.seek(40)
        Numunit = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n numero de cluster de la unidad completa: {Numunit}")

def mostrarArchivos(fiunamfs):

    print("Mode                 LastWriteTime         Length Name")
    print("----                 -------------         ------ ----")

    for i in range(4 * ((4*256) // 64)):  # Cada entrada del directorio ocupa 64 bytes
        entry = fiunamfs.read(64)
        
        # Tipo de archivo
        tipo = entry[0]
        if tipo == ord('#'):  # Entrada vacía
            continue
            
        # Leer nombre del archivo
        nombre = entry[1:16].decode('ascii').strip('-')
            
            # Leer tamaño del archivo
        tamano = struct.unpack('<I', entry[16:20])[0]
            
            # Leer cluster inicial
        cluster = struct.unpack('<I', entry[20:24])[0]
            
            # Leer fechas de creación y modificación
        fecha_creacion = entry[24:37].decode('ascii')

        fecha_modificacion = entry[38:52].decode('ascii', errors='replace')

            # Imprimir los detalles del archivo
        if tamano != 0:
            print(f"-a---l     {fecha_modificacion[0:4]}\{fecha_modificacion[4:6]}\{fecha_modificacion[6:8]}   {fecha_modificacion[8:10]}:{fecha_modificacion[10:12]}:{fecha_modificacion[12:14]}        {tamano} {nombre}")

def main():

    #montamos el archivo
    montaje("fiunamfs.img")

    while True:
        #simulamos la terminal de windows
        entrada = input(f"{os.getcwd()}\\FiunamFS> ")
        print("\n")
        #Si la entrada fue ls entonces el usuario quiere ver los archivos
        if entrada == "ls":
            with open("fiunamfs.img",'rb') as disco:
                mostrarArchivos(disco)
        elif entrada == "exit" or entrada =="cd ..":
            print("Desmontando FiunamFs...\n")
            break
        else: 
            print("Por el momento la entrada anterior no es valida\n")


main()

