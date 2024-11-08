#sistema de archivos con menu finalv4
import struct
import threading
from datetime import datetime

class SistemaFiUnamFS:
    def __init__(self, nombre_archivo):
        self.nombre_archivo = nombre_archivo
        self.bloqueo = threading.Lock()  # Maneja la sincronización
        self.tamaño_cluster = 1024  # Definido en el superbloque
        self.clusters_directorio = 4  # El directorio ocupa los clusters 1 a 4

        # Cargamos el sistema de archivos simulando un diskette de 1440 KB
        with open(self.nombre_archivo, 'rb') as archivo:
            self.datos = bytearray(archivo.read())

        # Validamos el superbloque
        if not self.validar_superbloque():
            raise ValueError("El archivo no es un sistema FiUnamFS versión 25-1.")

    def validar_superbloque(self):
        # Validamos los primeros 14 bytes del superbloque
        id_sistema = self.datos[0:8].decode('ascii')
        version = self.datos[10:14].decode('ascii')
        return id_sistema == 'FiUnamFS' and version == '25-1'

    def listar_archivos(self):
        # Lista todos los archivos en el sistema de archivos
        self.bloqueo.acquire()
        try:
            print("Listado de archivos en el sistema:")
            for i in range(1, 5):  # Los clusters 1 a 4 son del directorio
                inicio = i * self.tamaño_cluster
                for j in range(0, self.tamaño_cluster, 64):  # Cada entrada ocupa 64 bytes
                    entrada = self.datos[inicio + j:inicio + j + 64]
                    tipo_archivo = entrada[0:1].decode('ascii')
                    if tipo_archivo == '#':
                        continue  # Entrada vacía
                    nombre_archivo = entrada[1:16].decode('ascii').rstrip()
                    tamaño_archivo = struct.unpack('<I', entrada[16:20])[0]
                    fecha_creacion = entrada[24:38].decode('ascii')
                    fecha_modificacion = entrada[38:52].decode('ascii')
                    print(f"Archivo: {nombre_archivo}, Tamaño: {tamaño_archivo} bytes, "
                          f"Creado: {fecha_creacion}, Modificado: {fecha_modificacion}")
        finally:
            self.bloqueo.release()

    def crear_archivo(self, nombre, contenido):
        # Crea un archivo en el sistema con el nombre y contenido especificado
        self.bloqueo.acquire()
        try:
            tamaño_archivo = len(contenido)
            fecha_creacion = datetime.now().strftime('%Y%m%d%H%M%S')

            # Encontramos una entrada de directorio vacía
            for i in range(1, 5):  # Los clusters 1 a 4 son del directorio
                inicio = i * self.tamaño_cluster
                for j in range(0, self.tamaño_cluster, 64):
                    entrada = self.datos[inicio + j:inicio + j + 64]
                    if entrada[0:1] == b'#':
                        # Escribimos los datos del archivo en la entrada
                        self.datos[inicio + j:inicio + j + 1] = b'.'  # Tipo de archivo
                        self.datos[inicio + j + 1:inicio + j + 16] = nombre.encode('ascii').ljust(15, b'-')
                        self.datos[inicio + j + 16:inicio + j + 20] = struct.pack('<I', tamaño_archivo)
                        self.datos[inicio + j + 24:inicio + j + 38] = fecha_creacion.encode('ascii')
                        self.datos[inicio + j + 38:inicio + j + 52] = fecha_creacion.encode('ascii')

                        # Escribimos el contenido del archivo en la zona de datos
                        primer_cluster_datos = 5  # Primer cluster disponible para datos
                        posicion_datos = primer_cluster_datos * self.tamaño_cluster
                        self.datos[posicion_datos:posicion_datos + tamaño_archivo] = contenido.encode('ascii')
                        print("Archivo creado exitosamente.")
                        return
            print("No hay espacio disponible en el directorio.")
        finally:
            self.bloqueo.release()

    def eliminar_archivo(self, nombre):
        # Elimina un archivo basado en su nombre
        self.bloqueo.acquire()
        try:
            for i in range(1, 5):  # Los clusters 1 a 4 son del directorio
                inicio = i * self.tamaño_cluster
                for j in range(0, self.tamaño_cluster, 64):
                    entrada = self.datos[inicio + j:inicio + j + 64]
                    nombre_entrada = entrada[1:16].decode('ascii').strip()
                    if nombre_entrada == nombre:
                        # Marcamos la entrada como vacía
                        self.datos[inicio + j:inicio + j + 64] = b'#' + b'-' * 63
                        print(f"Archivo {nombre} eliminado.")
                        return
            print("Archivo no encontrado.")
        finally:
            self.bloqueo.release()

    def guardar_cambios(self):
        # Guarda cambios en el archivo del sistema de archivos
        with open(self.nombre_archivo, 'wb') as archivo:
            archivo.write(self.datos)

def menu():
    print("Bienvenido al sistema de archivos FiUnamFS.")
    nombre_archivo = input("Ingresa el nombre del archivo del sistema de archivos: ")

    try:
        sistema = SistemaFiUnamFS(nombre_archivo)
        print("Archivo cargado exitosamente.")
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    while True:
        print("\n--- Menú de opciones ---")
        print("1. Validar el superbloque")
        print("2. Listar archivos en el sistema")
        print("3. Crear un archivo")
        print("4. Eliminar un archivo")
        print("5. Guardar cambios")
        print("6. Salir")

        opcion = input("Elige una opción (1/2/3/4/5/6): ")
        
        if opcion == "1":
            if sistema.validar_superbloque():
                print("El superbloque es válido.")
            else:
                print("El superbloque no es válido.")
                
        elif opcion == "2":
            sistema.listar_archivos()
        
        elif opcion == "3":
            nombre = input("Nombre del archivo a crear: ")
            contenido = input("Contenido del archivo: ")
            sistema.crear_archivo(nombre, contenido)
        
        elif opcion == "4":
            nombre = input("Nombre del archivo a eliminar: ")
            sistema.eliminar_archivo(nombre)
        
        elif opcion == "5":
            sistema.guardar_cambios()
            print("Cambios guardados exitosamente.")
        
        elif opcion == "6":
            print("Saliendo del programa.")
            break
        
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == '__main__':
    menu()
