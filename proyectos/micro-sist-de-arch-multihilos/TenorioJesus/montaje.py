import struct

"""""
BASICAMENTE LO QUE HACE ESTE CODIGO ES SIMULAR EL MONTAJE DE FIUNAMFS

LO PRIMMERO QUE HACE ES ABRIR EL DISCO COMO LECTURA Y VA OBTENIENDO LA INFORMACION
DEL SISTEMA DE ARCHIVOS SEGUN LO ESPECIFICADO POR EL AUTOR (USTED PROFESOR)

VERIFICA SI EL SISTEMA ES DE ESTE SEMESTRE

0–8
Para identificación, el nombre del sistema de archivos. ¡Debes validar nunca modificar un sistema de archivos que no sea el correcto! Debe ser la cadena FiUnamFS.
10–14
Versión de la implementación. Estamos implementando la versión 25-1 (ojo, es una cadena, no un número). Deben validar que el sistema de archivos a utilizar sea exactamente esta versión, para evitar la corrupción de datos.
20–35
Etiqueta del volumen
40–44
Tamaño del cluster en bytes
45–49
Número de clusters que mide el directorio

- GUNNAR WOLF, (PLANTEACION PROYECTO 2025-1)

"""""

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
        disco.seek(50)
        Numunit = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n numero de cluster de la unidad completa: {Numunit}")