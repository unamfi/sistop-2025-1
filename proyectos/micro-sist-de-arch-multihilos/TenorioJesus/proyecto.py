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


def main():

    #montamos el archivo
    montaje("fiunamfs.img")

    while True:
        #simulamos la terminal de windows
        entrda = input(f"{os.getcwd()}\\FiunamFS> ")


main()

