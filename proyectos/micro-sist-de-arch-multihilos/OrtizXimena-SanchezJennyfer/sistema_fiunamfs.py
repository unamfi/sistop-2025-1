#Ortiz Moreno Ximena
#Sánchez Gachuz Jennyfer Estefanía

import struct
import threading
import os

class SistemaFiUnamFS:
    TAMANO_CLUSTER = 256
    CLUSTERS_DIRECTORIO = 4
    TAMANO_ENTRADA_DIRECTORIO = 64
    MAXIMO_ENTRADAS = (CLUSTERS_DIRECTORIO * TAMANO_CLUSTER) // TAMANO_ENTRADA_DIRECTORIO

    def __init__(self, ruta_archivo="fiunamfs.img"):
        #Inicializa el sistema de archivos, creando el archivo base si no existe.
        self.ruta_archivo = ruta_archivo
        self.bloqueo = threading.Lock()
        self.inicializar_sistema_archivos()

    def inicializar_sistema_archivos(self):
        #Crea el archivo base y escribe el superbloque si no existe.
        if not os.path.exists(self.ruta_archivo):
            with open(self.ruta_archivo, "wb") as archivo:
                archivo.write(b'\x00' * 1440 * 1024)  # Tamaño de 1.44MB como un disquete
            with open(self.ruta_archivo, "r+b") as archivo:
                # Escribir el superbloque con información del sistema de archivos
                archivo.seek(0)
                archivo.write(b"FiUnamFS")  # Identificación del sistema de archivos
                archivo.write(b"25-1")  # Versión del sistema de archivos
                archivo.write(b"\x00" * (self.TAMANO_CLUSTER - 8))  # Relleno del superbloque

    def listar_directorio(self):
        #Lista el contenido del directorio en `FiUnamFS`.
        with open(self.ruta_archivo, "rb") as archivo:
            archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
            print("Contenido del directorio:")
            for _ in range(self.MAXIMO_ENTRADAS):
                entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                nombre = entrada[1:15].decode("ascii").strip("\x00")
                tamano = struct.unpack("<I", entrada[16:20])[0]
                # Mostrar solo entradas válidas, omitiendo espacios vacíos
                if nombre and nombre != "--------------":
                    print(f"{nombre} - {tamano} bytes")

    def copiar_a_sistema(self, nombre_archivo):
        #Copia un archivo desde `FiUnamFS` al sistema local.
        with self.bloqueo:
            with open(self.ruta_archivo, "rb") as archivo:
                archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
                for _ in range(self.MAXIMO_ENTRADAS):
                    entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                    nombre = entrada[1:15].decode("ascii").strip("\x00")
                    if nombre == nombre_archivo:
                        tamano = struct.unpack("<I", entrada[16:20])[0]
                        cluster_inicio = struct.unpack("<I", entrada[20:24])[0]
                        ruta_salida = os.path.join(".", nombre_archivo)
                        with open(ruta_salida, "wb") as archivo_salida:
                            # Leer los datos del archivo desde FiUnamFS y escribirlos en el sistema local
                            self._leer_datos_archivo(archivo, archivo_salida, cluster_inicio, tamano)
                        print(f"Archivo '{nombre_archivo}' copiado a '{ruta_salida}'")
                        return
            print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS")

    def copiar_desde_sistema(self, ruta_archivo):
        #Copia un archivo del sistema local a `FiUnamFS`.
        with self.bloqueo:
            nombre_archivo = os.path.basename(ruta_archivo)
            tamano_archivo = os.path.getsize(ruta_archivo)
            with open(ruta_archivo, "rb") as archivo_origen:
                with open(self.ruta_archivo, "r+b") as archivo:
                    archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
                    for _ in range(self.MAXIMO_ENTRADAS):
                        pos_entrada = archivo.tell()
                        entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                        nombre = entrada[1:15].decode("ascii").strip("\x00")
                        # Busca una entrada vacía en el directorio
                        if nombre == "--------------":
                            archivo.seek(pos_entrada)
                            archivo.write(b"#" + nombre_archivo.encode("ascii").ljust(15, b"\x00"))
                            archivo.write(struct.pack("<I", tamano_archivo))
                            # Encontrar el primer cluster libre para almacenar el archivo
                            cluster_inicio = self._encontrar_cluster_libre(archivo, tamano_archivo)
                            archivo.write(struct.pack("<I", cluster_inicio))
                            archivo.write(b"\x00" * (self.TAMANO_ENTRADA_DIRECTORIO - 24))  # Relleno de la entrada
                            # Escribir los datos del archivo en FiUnamFS
                            self._escribir_datos_archivo(archivo, archivo_origen, cluster_inicio, tamano_archivo)
                            print(f"Archivo '{nombre_archivo}' copiado a FiUnamFS")
                            return
            print("No hay espacio suficiente en el directorio de FiUnamFS")

    def eliminar_archivo(self, nombre_archivo):
        #Elimina un archivo en `FiUnamFS`.
        with self.bloqueo:
            with open(self.ruta_archivo, "r+b") as archivo:
                archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
                for _ in range(self.MAXIMO_ENTRADAS):
                    pos_entrada = archivo.tell()
                    entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                    nombre = entrada[1:15].decode("ascii").strip("\x00")
                    if nombre == nombre_archivo:
                        archivo.seek(pos_entrada)
                        # Marca la entrada como eliminada
                        archivo.write(b"--------------" + b"\x00" * (self.TAMANO_ENTRADA_DIRECTORIO - 15))
                        print(f"Archivo '{nombre_archivo}' eliminado de FiUnamFS")
                        return
            print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS")

    def _encontrar_cluster_libre(self, archivo, tamano_archivo):
        #Encuentra el primer cluster libre para almacenar un archivo dado el tamaño necesario.
        clusters_necesarios = (tamano_archivo + self.TAMANO_CLUSTER - 1) // self.TAMANO_CLUSTER
        archivo.seek(self.TAMANO_CLUSTER * (1 + self.CLUSTERS_DIRECTORIO))  # Saltar el superbloque y el directorio
        for numero_cluster in range(1 + self.CLUSTERS_DIRECTORIO, 1440 * 1024 // self.TAMANO_CLUSTER):
            archivo.seek(numero_cluster * self.TAMANO_CLUSTER)
            datos = archivo.read(self.TAMANO_CLUSTER)
            # Retorna el primer cluster vacío encontrado
            if datos == b'\x00' * self.TAMANO_CLUSTER:
                return numero_cluster
        raise Exception("No hay clusters libres suficientes para almacenar el archivo")

    def _leer_datos_archivo(self, archivo, archivo_salida, cluster_inicio, tamano_archivo):
        #Lee los datos desde `FiUnamFS` y los escribe en un archivo de salida.
        archivo.seek(cluster_inicio * self.TAMANO_CLUSTER)
        bytes_restantes = tamano_archivo
        while bytes_restantes > 0:
            tamano_chunk = min(self.TAMANO_CLUSTER, bytes_restantes)
            datos = archivo.read(tamano_chunk)
            archivo_salida.write(datos)
            bytes_restantes -= tamano_chunk

    def _escribir_datos_archivo(self, archivo, archivo_origen, cluster_inicio, tamano_archivo):
        #Escribe los datos de un archivo de origen en `FiUnamFS`.
        archivo.seek(cluster_inicio * self.TAMANO_CLUSTER)
        bytes_restantes = tamano_archivo
        while bytes_restantes > 0:
            chunk = archivo_origen.read(min(self.TAMANO_CLUSTER, bytes_restantes))
            archivo.write(chunk)
            bytes_restantes -= len(chunk)

    def sincronizar_estado(self):
        #Simula la sincronización de estado entre hilos.
        with self.bloqueo:
            print("Estado sincronizado entre hilos")

# Ejemplo de uso del sistema de archivos
def main():
    sistema_fs = SistemaFiUnamFS()
    sistema_fs.listar_directorio()
    sistema_fs.copiar_desde_sistema("ejemplo.txt")  # Copiar archivo desde el sistema a FiUnamFS
    sistema_fs.copiar_a_sistema("ejemplo.txt")      # Copiar archivo desde FiUnamFS al sistema
    sistema_fs.eliminar_archivo("ejemplo.txt")      # Eliminar archivo en FiUnamFS

if __name__ == "__main__":
    main()
