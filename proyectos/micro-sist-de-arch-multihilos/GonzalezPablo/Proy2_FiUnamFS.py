'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                Gonzalez Cuellar Pablo Arturo

        Proyecto 2 - Micro Sistema de Archivos Multihilo

                    Sistemas Operativos

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import struct
import threading
import time

cadena= "-------------------------"
ruta_archivo = "C:\\Users\\pablo\\Documents\\SOGeneral\\Proyecto2\\fiunamfs.img"

# Función para abrir y verificar el sistema de archivos
def abrir_sistema_archivos(ruta_archivo):
    with open(ruta_archivo, "rb") as archivo:
        # Leer los primeros 256 bytes (superbloque)
        superbloque = archivo.read(256)
        
        # Leemos los bytes 0-8 para obtener el nombre del sistema
        nombre_sistema = superbloque[0:9].decode('ascii').strip()

        # Obtenemos el tamaño del cluster y la version del sistema
        version = superbloque[10:15].decode('ascii').strip()
        tamano_cluster = struct.unpack('<I', superbloque[40:44])[0]

        print(f"Nombre del sistema: {nombre_sistema}")
        print(f"Versión: {version}")
        print(f"Tamaño del clúster: {tamano_cluster} bytes")
        
        return tamano_cluster
    
        
# Función para listar el contenido del sistema
def listar_directorio(ruta_archivo, tamano_cluster):
    with open(ruta_archivo, "rb") as archivo:

        archivo.seek(tamano_cluster)  # Ubicamos el puntero al inicio del primer cluster
        
        print("Contenido del directorio:")
        
        for i in range(4):  # Clústeres 1 a 4 están dedicados al directorio
            for j in range(tamano_cluster // 64):  # Cada entrada mide 64 bytes
                entrada = archivo.read(64)
                
                # Nombre del archivo (bytes 1-15)
                nombre_archivo = entrada[1:16].decode('ascii').strip()
                
                # Tamaño del archivo (bytes 16-20)
                tamano_archivo = struct.unpack('<I', entrada[16:20])[0]
                
                # Clúster inicial (bytes 20-23)
                cluster_inicial = struct.unpack('<I', entrada[20:24])[0]
                
                # Fecha de creación (bytes 24-37)
                fecha_creacion = entrada[24:38].decode('ascii').strip()
                anio = fecha_creacion[0:4]
                mes = fecha_creacion[4:6]
                dia = fecha_creacion[6:8]
                hora = fecha_creacion[8:10]
                minuto = fecha_creacion[10:12]
                segundo = fecha_creacion[12:14]
                fecha_creacion_formateada = f"{anio}-{mes}-{dia} {hora}:{minuto}:{segundo}"
                
                # Fecha de última modificación (bytes 38-51)
                fecha_modificacion = entrada[38:52].decode('ascii').strip()
                anio = fecha_modificacion[0:4]
                mes = fecha_modificacion[4:6]
                dia = fecha_modificacion[6:8]
                hora = fecha_modificacion[8:10]
                minuto = fecha_modificacion[10:12]
                segundo = fecha_modificacion[12:14]
                fecha_modificacion_formateada = f"{anio}-{mes}-{dia} {hora}:{minuto}:{segundo}"
                
                # Manera sucia de mostrar lo archivos que tienen info jeje
                if tamano_archivo != 0:
                    print(f"Archivo: {nombre_archivo}")
                    print(f"  Tamaño: {tamano_archivo} bytes")
                    print(f"  Clúster inicial: {cluster_inicial}")
                    print(f"  Fecha de creación: {fecha_creacion_formateada}")
                    print(f"  Fecha de última modificación: {fecha_modificacion_formateada}")
                    print()
    return nombre_archivo

def copiar_archivo_desde_fiunamfs(ruta_archivo, tamano_cluster, nombre_archivo):
    with open(ruta_archivo, "rb") as archivo:
        archivo.seek(tamano_cluster)  # Ubica el puntero al inicio del directorio

        # Itera sobre los primeros 4 clusters para buscar el archivo
        for i in range(4):
            for j in range(tamano_cluster // 64):  # Cada entrada es de 64 bytes
                entrada = archivo.read(64)
                
                # Obtiene el nombre del archivo en el sistema FiUnamFS
                nombre_archivo_fiunamfs = entrada[1:16].decode('ascii').strip()
                
                if nombre_archivo_fiunamfs == nombre_archivo:
                    # Obtiene el tamaño y clúster inicial del archivo
                    tamano_archivo = struct.unpack('<I', entrada[16:20])[0]
                    cluster_inicial = struct.unpack('<I', entrada[20:24])[0]

                    # Calcula el inicio del archivo en FiUnamFS y ubica el puntero
                    archivo.seek(cluster_inicial * tamano_cluster)
                    contenido_archivo = archivo.read(tamano_archivo)

                    # Guarda el archivo en el sistema local
                    with open(nombre_archivo, "wb") as archivo_salida:
                        archivo_salida.write(contenido_archivo)

                    print(f"Archivo '{nombre_archivo}' copiado exitosamente al sistema local.")
                    return
                
        print(f"El archivo '{nombre_archivo}' no se encontró en FiUnamFS.")



# MAIN

if __name__=="__main__":

    try:

        print("\nBienvenido al Micro Sistema de Archivos FiUnamFS\n")
        tamano_cluster = abrir_sistema_archivos(ruta_archivo)

    except Exception as e:
        print(f"Error: {e}")

    while True:
        print(cadena)
        print("\nSeleccione una opción:")
        print("1. Listar contenidos del directorio")
        print("2. Copiar archivo desde FiUnamFS al sistema")
        print("3. Copiar archivo desde el sistema a FiUnamFS")
        print("4. Eliminar archivo de FiUnamFS")
        print("5. Salir")

        op=input("Ingrese una opcion: ")

        if op=="1":
            #listar_directorio(ruta_archivo, tamano_cluster)
            print(listar_directorio(ruta_archivo,tamano_cluster))
        #elif op == "2":
            #nombre_archivo = input("Escribe el nombre del archivo que deseas copiar desde FiUnamFS: ")
            #copiar_archivo_desde_fiunamfs(ruta_archivo, tamano_cluster, nombre_archivo)
        #elif op=="4":
            #nombre_archivo_eliminar = input("Ingrese el nombre del archivo a eliminar: ")
            #eliminar_archivo(ruta_archivo, tamano_cluster, nombre_archivo_eliminar)
        if op=="5":
            break


