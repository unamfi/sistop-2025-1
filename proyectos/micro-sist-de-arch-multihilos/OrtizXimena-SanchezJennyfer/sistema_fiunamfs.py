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
        # Inicializa el sistema de archivos, creando el archivo base si no existe.
        self.ruta_archivo = ruta_archivo
        self.bloqueo = threading.Lock()
        self.inicializar_sistema_archivos()

    def inicializar_sistema_archivos(self):
        # Crea el archivo base y escribe el superbloque si no existe.
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
        """Lista el contenido del directorio en `FiUnamFS` y retorna una lista de strings."""
        contenido = []
        with open(self.ruta_archivo, "rb") as archivo:
            archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
            for _ in range(self.MAXIMO_ENTRADAS):
                entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                nombre = entrada[1:15].decode("ascii").strip("\x00")
                tamano = struct.unpack("<I", entrada[16:20])[0]
                if nombre:
                    contenido.append(f"{nombre} - {tamano} bytes")
                else:
                    contenido.append("-------------- - 0 bytes")  # Mostrar como vacío
        return contenido

    def copiar_a_sistema(self, nombre_archivo):
        archivo_encontrado = False  # Variable para verificar si el archivo se encuentra
        with self.bloqueo:
            with open(self.ruta_archivo, "rb") as archivo:
                archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
                for _ in range(self.MAXIMO_ENTRADAS):
                    entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                    nombre = entrada[1:15].decode("ascii").strip("\x00")

                    if nombre == nombre_archivo:
                        archivo_encontrado = True  # El archivo fue encontrado
                        tamano = struct.unpack("<I", entrada[16:20])[0]
                        cluster_inicio = struct.unpack("<I", entrada[20:24])[0]
                        ruta_salida = os.path.join(".", nombre_archivo)
                        with open(ruta_salida, "wb") as archivo_salida:
                            self._leer_datos_archivo(archivo, archivo_salida, cluster_inicio, tamano)
                        print(f"Archivo '{nombre_archivo}' copiado a '{ruta_salida}'")
                        return True
        if not archivo_encontrado:
            print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS")
            return False

    def copiar_desde_sistema(self, ruta_archivo):
        nombre_archivo = os.path.basename(ruta_archivo)
        tamano_archivo = os.path.getsize(ruta_archivo)
    
        with self.bloqueo:
            with open(self.ruta_archivo, "r+b") as archivo:
                archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
                entrada_disponible = False  # Bandera para encontrar una entrada vacía
            
                for _ in range(self.MAXIMO_ENTRADAS):
                    pos_entrada = archivo.tell()
                    entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                    nombre = entrada[1:15].decode("ascii").strip("\x00")
                
                    if nombre == "--------------":
                        entrada_disponible = True
                        archivo.seek(pos_entrada)
                        archivo.write(b"#" + nombre_archivo.encode("ascii").ljust(15, b"\x00"))
                        archivo.write(struct.pack("<I", tamano_archivo))
                    
                        try:
                            cluster_inicio = self._encontrar_cluster_libre(archivo, tamano_archivo)
                            archivo.write(struct.pack("<I", cluster_inicio))
                            archivo.write(b"\x00" * (self.TAMANO_ENTRADA_DIRECTORIO - 24))
                            with open(ruta_archivo, "rb") as archivo_origen:
                                self._escribir_datos_archivo(archivo, archivo_origen, cluster_inicio, tamano_archivo)
                            print(f"Archivo '{nombre_archivo}' copiado a FiUnamFS")
                            return True
                        except Exception as e:
                            print(f"Error al copiar '{nombre_archivo}' a FiUnamFS: {e}")
                            return False

                if not entrada_disponible:
                    print("No hay espacio suficiente en el directorio de FiUnamFS")
                    return False

    def eliminar_archivo(self, nombre_archivo):
        archivo_encontrado = False
        with self.bloqueo:
            with open(self.ruta_archivo, "r+b") as archivo:
                archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
                for _ in range(self.MAXIMO_ENTRADAS):
                    pos_entrada = archivo.tell()
                    entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                    nombre = entrada[1:15].decode("ascii").strip("\x00")

                    if nombre == nombre_archivo:
                        archivo_encontrado = True
                        cluster_inicio = struct.unpack("<I", entrada[20:24])[0]
                        tamano = struct.unpack("<I", entrada[16:20])[0]
                    
                        archivo.seek(pos_entrada)
                        archivo.write(b"--------------" + b"\x00" * (self.TAMANO_ENTRADA_DIRECTORIO - 15))
                        self._liberar_clusters(archivo, cluster_inicio, tamano)
                    
                        print(f"Archivo '{nombre_archivo}' eliminado de FiUnamFS y espacio liberado.")
                        return True
                print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS.")
        return archivo_encontrado

    def _liberar_clusters(self, archivo, cluster_inicio, tamano_archivo):
        clusters_necesarios = (tamano_archivo + self.TAMANO_CLUSTER - 1) // self.TAMANO_CLUSTER
        archivo.seek(cluster_inicio * self.TAMANO_CLUSTER)
        for _ in range(clusters_necesarios):
            print(f"Liberando cluster en posición {archivo.tell()}")
            archivo.write(b'\x00' * self.TAMANO_CLUSTER)
            archivo.seek(archivo.tell() + self.TAMANO_CLUSTER)

    def _encontrar_cluster_libre(self, archivo, tamano_archivo):
        clusters_necesarios = (tamano_archivo + self.TAMANO_CLUSTER - 1) // self.TAMANO_CLUSTER
        archivo.seek(self.TAMANO_CLUSTER * 5)
        cluster_inicio = -1
        clusters_continuos = 0
    
        for numero_cluster in range(5, 1440 * 1024 // self.TAMANO_CLUSTER):
            archivo.seek(numero_cluster * self.TAMANO_CLUSTER)
            datos = archivo.read(self.TAMANO_CLUSTER)
        
            if datos == b'\x00' * self.TAMANO_CLUSTER:
                if cluster_inicio == -1:
                    cluster_inicio = numero_cluster
                clusters_continuos += 1
                if clusters_continuos == clusters_necesarios:
                    return cluster_inicio
            else:
                cluster_inicio = -1
                clusters_continuos = 0
    
        raise Exception("No hay clusters libres suficientes para almacenar el archivo")

    def _leer_datos_archivo(self, archivo, archivo_salida, cluster_inicio, tamano_archivo):
        archivo.seek(cluster_inicio * self.TAMANO_CLUSTER)
        bytes_restantes = tamano_archivo
        while bytes_restantes > 0:
            tamano_chunk = min(self.TAMANO_CLUSTER, bytes_restantes)
            datos = archivo.read(tamano_chunk)
            archivo_salida.write(datos)
            bytes_restantes -= tamano_chunk

    def _escribir_datos_archivo(self, archivo, archivo_origen, cluster_inicio, tamano_archivo):
        archivo.seek(cluster_inicio * self.TAMANO_CLUSTER)
        bytes_restantes = tamano_archivo
        while bytes_restantes > 0:
            chunk = archivo_origen.read(min(self.TAMANO_CLUSTER, bytes_restantes))
            archivo.write(chunk)
            bytes_restantes -= len(chunk)

    def sincronizar_estado(self):
        with self.bloqueo:
            print("Estado sincronizado entre hilos")
