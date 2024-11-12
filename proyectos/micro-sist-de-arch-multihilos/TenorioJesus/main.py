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

Este programa tratara de emular la terminal de windows, esto para que el usuario no se
de cuenta que esta trabajando sobre un programa, y tratara de parecer invisible ante este

Elaborado por: Tenorio Martinez Jesus Alejandro

Sistemas Operativos, semetres 2025 - 1
"""

#importamos bibliotecas necesarias...
from montaje import montaje
from mostrararchivos import mostrarArchivos
from ReconocerEntradas import Reconocer
from copiar_a_fiunamfs import copiar_archivo_a_Fiunamfs
from copiar_a_sist import copiar_archivo_a_sistema
import os
from contenido import contenido_archivo
from eliminar_archivo import eliminar_archivo
import threading
import time

# Inicializamos un semaforo, esto para asegurar que multiples usuarios no accedan a 
# FIunamsFS a la vez
semaforo = threading.Semaphore(1)
#El semaforo tiene  el valor 1, para permiter solo una lectura o escritura a la vez

def main():

    NameFiles = [] #Arrglo para guardar los nombres dentro de FiunamFi.img

    #montamos el archivo
    print("\nMontando FiUnamFs...")
    montaje("fiunamfs.img")

    while True:
 
        #simulamos la terminal de widows
        entrada = input(f"PS: {os.getcwd()}\\FiunamFS> ")
        print("\n")

        #Si la entrada fue ls entonces el usuario quiere ver los archivos
        if entrada == "ls":
                print("\n\tEperando el recurso...\n")
                with semaforo: #adquirimos el semaforo
                    #os.system('cls')
                    with open('fiunamfs.img','r+b') as disco: #abrimos el sistema como "disco"
                        NameFiles = mostrarArchivos(disco) # Gauardamos Archivos
                    time.sleep(5)

        # Si la entrada fue exit o cd .., entonces el usuario quiere salir
        elif entrada == "exit" or entrada =="cd ..": 
            print("Desmontando FiunamFs...\n")
            break #salimos del programa (motaje simulado)

        # Si la entrada comieza con copy, el usuario quiere 
        elif entrada.startswith("copy "):

            print("\n\tEperando el recurso...\n")
            with semaforo: # Aquiurimos el semaforo para evitar condiciones de carrera
                #os.system('cls')
                with open('fiunamfs.img','rb') as disco:# Abrimos el archivo en modo lectura  
                    NameFiles = mostrarArchivos(disco)
                time.sleep(5)

            time.sleep(5)
            os.system('cls')
                
            ruta_origen, ruta_destino = Reconocer(entrada) #obtenemos las rutas que ingrso el usuario
            
            # Bucamos el nombre en los nombres de los archivos del sistema
            for nombre in NameFiles:
                
                #si la direccion de origen es de un archivo FiUnamFs enotonces quiere copiar 
                #un archivo a su sistema
                if(os.getcwd()+'\\FiunamFS\\'+nombre==ruta_origen.strip()):

                    print("\n\tEperando el recurso...\n")
                    with semaforo:#Adquirimos el semaforo
                        #os.system('cls')
                        with open('fiunamfs.img','r+b') as disco:
                            copiar_archivo_a_sistema(disco,nombre,ruta_destino+"\\"+nombre)
                        time.sleep(5)
                        #liberamos el semaforo
                    break
                
                #si bien la entrada de destino coincide con la direccion de destino entonces
                #quiere agrgar un archvo en FiUnamFs
                if(os.getcwd()+'\\FiunamFS\\'==ruta_destino.strip()):
                    contenido,fecha,nombre_archivo = contenido_archivo(ruta_origen)

                    print("\n\tEperando el recurso...\n")
                    with semaforo:
                        #os.system('cls')
                        with open('fiunamfs.img','r+b') as disco:
                            copiar_archivo_a_Fiunamfs(disco,nombre_archivo,contenido,fecha)
                        time.sleep(5)
                    break
        # Si la entrada comineza con "del", etonces el usuario quiere eliminar un arciivo
        elif entrada.startswith("del "):

            print("\n\tEperando el recurso...\n")
            #Evitando condiciones de carrera
            with semaforo:
                #os.system('cls')
                with open('fiunamfs.img','r+b') as disco:
                    eliminar_archivo(disco, entrada.split(" ")[1])
                time.sleep(5)
        # si por el contrario, ninguna entrada coincide, entonces especificamos que 
        # aun no existe esa opcion en el sistema de archivos
        else: 
            print("Por el momento la entrada anterior no es valida\n")

if __name__ == "__main__":
    main()