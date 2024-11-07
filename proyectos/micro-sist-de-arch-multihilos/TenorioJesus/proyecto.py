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
from ReconocerEntradas import Reconocer
from pathlib import Path
from datetime import datetime
from contenido import contenido_archivo

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
        disco.seek(50)
        Numunit = struct.unpack('<I', disco.read(struct.calcsize('<I')))[0]
        print(f"\n numero de cluster de la unidad completa: {Numunit}")

def mostrarArchivos(fiunamfs):

    NameFiles = []

    print("Mode                 LastWriteTime         Length Name")
    print("----                 -------------         ------ ----")

    for i in range(4 * ((4*256) // 64)):  # Cada entrada del directorio ocupa 64 bytes
        entry = fiunamfs.read(64)
        
        # Tipo de archivo
        tipo = entry[0]
        if tipo == ord('#'):  # Entrada vacía
            continue
            
        # Leer nombre del archivo
        nombre = entry[1:14].decode('ascii').strip('-').strip()
        NameFiles.append(nombre)

        # Leer tamaño del archivo
        tamano = struct.unpack('<I', entry[16:20])[0]

        fecha_modificacion = entry[38:52].decode('ascii', errors='replace')

        # Imprimir los detalles del archivo
        if tamano != 0 and nombre.strip() != '#':
           
            print(f"-a---l     {fecha_modificacion[0:4]}\{fecha_modificacion[4:6]}\{fecha_modificacion[6:8]}   {fecha_modificacion[8:10]}:{fecha_modificacion[10:12]}:{fecha_modificacion[12:14]}        {tamano} {nombre}")

    return NameFiles

def copiar_archivo_a_sistema(disco, nombre_archivo, destino):

    size = 1024
    inicio = 1024

    # Buscar el archivo en el directorio
    encontrado = False
    for i in range(4 * (size // 64)):  # 4 clusters de directorio, cada entrada tiene 64 bytes
        disco.seek(inicio + i * 64)
        entry = disco.read(64)
            
        # Tipo de archivo
        tipo = entry[0]
        if tipo != ord('.'):
            continue  # Si no es un archivo válido, pasar a la siguiente entrada
        
        # Nombre del archivo
        nombre = entry[1:14].decode('ascii')
        if nombre.strip() != nombre_archivo.strip():
            continue
        
        # Tamaño del archivo y cluster inicial
        tamano = struct.unpack('<I', entry[16:20])[0]
        clusterInicial = struct.unpack('<I', entry[20:24])[0]
        encontrado = True
        break
    
    if not encontrado:
        print("Archivo no encontrado en FiUnamFS.")
        return

    # Leer los datos del archivo
    disco.seek(clusterInicial * size)  # Ir al cluster inicial de datos
    datos = disco.read(tamano)

    Ruta_destino = Path(destino)

    # Escribir los datos en un nuevo archivo en el sistema
    with Ruta_destino.open('wb') as salida:
        salida.write(datos)
        
    print(f"\nArchivo '{nombre_archivo}' copiado a '{destino}'\n")

    
def eliminar_archivo(disco, nombre_archivo):
    cluster_size = 1024  # Tamaño del cluster
    inicio_directorio = 1024  # Offset donde comienza el directorio
    encontrado = False

    # Recorrer cada entrada en el directorio para encontrar el archivo
    for i in range(4 * (cluster_size // 64)):  # 4 clusters de directorio, cada entrada ocupa 64 bytes
        disco.seek(inicio_directorio + i * 64)
        entry = disco.read(64)
        
        # Leer el tipo de archivo y nombre
        tipo = entry[0]
        nombre = entry[1:14].decode('ascii').strip()
        
        # Verificar si es el archivo que queremos eliminar
        if tipo == ord('.') and nombre.strip() == nombre_archivo.strip():
            # Marcamos la entrada como vacía, sobrescribiendo el tipo
            disco.seek(inicio_directorio + i * 64)
            disco.write(b'#')  # Indicador de entrada vacía
            encontrado = True
            print(f"Archivo '{nombre_archivo}' eliminado exitosamente.")
            break

    if not encontrado:
        print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS.")

def copiar_archivo_a_Fiunamfs(fiunamfs_img, nombre_archivo, contenido):
    # Tamaños y offsets
    cluster_size = 1024
    inicio_directorio = 1024  # Offset donde empieza el directorio
    max_nombre = 15  # Tamaño máximo de nombre
    encontrado = False

    # Truncar el nombre si es mayor que 15 caracteres
    if len(nombre_archivo) > max_nombre:
        nombre_archivo = nombre_archivo[:max_nombre]

    # Abre el archivo de sistema en modo binario
    with open(fiunamfs_img, 'r+b') as disco:
        # Buscar una entrada vacía en el directorio
        for i in range(4 * (cluster_size // 64)):  # Directorio tiene 4 clusters de 64 bytes por entrada
            disco.seek(inicio_directorio + i * 64)
            entry = disco.read(64)

            # Verificar si la entrada está vacía
            if entry[0] == ord('#'):
                # Posicionar en la entrada vacía encontrada
                disco.seek(inicio_directorio + i * 64)

                # 0. Tipo de archivo (1 byte)
                disco.write(b'.')  # Indicador de archivo válido

                # 1-15. Nombre del archivo (15 bytes, llenado con '')
                nombre_formateado = nombre_archivo.ljust(max_nombre)
                disco.write(nombre_formateado.encode('ascii'))

                # 16-19. Tamaño del archivo (4 bytes)
                tamano = len(contenido)
                disco.write(struct.pack('<I', tamano))

                # 20-23. Cluster inicial (4 bytes)
                # Usamos el primer cluster disponible (modificar según la gestión de clusters)
                cluster_inicial = 4  
                disco.write(struct.pack('<I', cluster_inicial))

                # 24-37. Fecha y hora de creación (14 bytes en formato AAAAMMDDHHMMSS)
                fecha_creacion = datetime.now().strftime('%Y%m%d%H%M%S')
                disco.write(fecha_creacion.encode('ascii'))

                # 38-51. Fecha y hora de última modificación (14 bytes en formato AAAAMMDDHHMMSS)
                fecha_modificacion = datetime.now().strftime('%Y%m%d%H%M%S')
                disco.write(fecha_modificacion.encode('ascii'))

                # 52-63. Espacio reservado (12 bytes)
                disco.write(b'\x00' * 12)  # Espacio reservado vacío

                encontrado = True
                break

        if not encontrado:
            print("No hay espacio en el directorio para un nuevo archivo.")
            return

        # Escribir los datos en el cluster de datos correspondiente
        disco.seek(cluster_inicial * cluster_size)
        disco.write(contenido[:tamano])

    print(f"Archivo '{nombre_archivo}' escrito exitosamente en FiUnamFS.")


def main():

    NameFiles = []
    #montamos el archivo
    print("Montando FiUnamFs\n")
    montaje("fiunamfs.img")

    
    while True:

        #simulamos la terminal de widows
        entrada = input(f"{os.getcwd()}\\FiunamFS> ")
        print("\n")

        #Si la entrada fue ls entonces el usuario quiere ver los archivos
        if entrada == "ls":
                with open('fiunamfs.img','r+b') as disco:
                    NameFiles = mostrarArchivos(disco)

        elif entrada == "exit" or entrada =="cd ..":
            print("Desmontando FiunamFs...\n")
            break

        elif entrada.startswith("copy "):

            with open ('fiunamfs.img','rb') as disco:
        
                NameFiles = mostrarArchivos(disco)
                os.system('cls')
                
            ruta_origen, ruta_destino = Reconocer(entrada)
                    
            for nombre in NameFiles:
                
                print(f"\n{os.getcwd()}\\FiunamFS\\{nombre}")
                if(os.getcwd()+'\\FiunamFS\\'+nombre==ruta_origen.strip()):
                    with open('fiunamfs.img','r+b') as disco:
                        copiar_archivo_a_sistema(disco,nombre,ruta_destino+"\\"+nombre)
                    break
                    
                if(os.getcwd()+'\\FiunamFS\\'+nombre==ruta_destino.strip()):
                    contenido,fecha,nombre_archivo = contenido_archivo(ruta_origen)
                    with open('fiunamfs.img','r+b'):
                        copiar_archivo_a_Fiunamfs(disco,nombre_archivo,contenido,fecha)
                    break
                    
        elif entrada.startswith("delete "):

            with open('fiunamfs.img','r+b') as disco:
                eliminar_archivo(disco, entrada.split(" ")[1])

        else: 
            print("Por el momento la entrada anterior no es valida\n")

if __name__ == "__main__":
    main()