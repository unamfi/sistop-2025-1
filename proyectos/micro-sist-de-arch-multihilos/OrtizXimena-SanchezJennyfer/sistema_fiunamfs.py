#Ortiz Moreno Ximena 
# Sánchez Gachuz Jennyfer Estefanía

import struct  # Para manipular datos binarios de tamaño fijo
import threading  # Para la sincronización entre hilos
import os  # Para operaciones de archivo en el sistema operativo

class SistemaFiUnamFS:
    # Constantes que definen tamaños de almacenamiento y estructura del sistema de archivos
    TAMANO_CLUSTER = 256  # Tamaño en bytes de cada cluster en el sistema de archivos
    CLUSTERS_DIRECTORIO = 4  # Número de clusters reservados para el directorio
    TAMANO_ENTRADA_DIRECTORIO = 64  # Tamaño de cada entrada en el directorio
    MAXIMO_ENTRADAS = (CLUSTERS_DIRECTORIO * TAMANO_CLUSTER) // TAMANO_ENTRADA_DIRECTORIO  # Máximo de archivos en el directorio

    def __init__(self, ruta_archivo="fiunamfs.img"):
        #Inicializa el sistema de archivos, creando el archivo base si no existe.
        self.ruta_archivo = ruta_archivo  # Ruta del archivo de sistema de archivos
        self.bloqueo = threading.Lock()  # Bloqueo para evitar conflictos en acceso concurrente
        self.inicializar_sistema_archivos()  # Llama a la función para configurar el sistema de archivos

    def inicializar_sistema_archivos(self):
        """
        Verifica si el archivo del sistema de archivos existe; si no, lo crea y configura el superbloque.
        El superbloque contiene la información básica del sistema de archivos.
        """
        if not os.path.exists(self.ruta_archivo):
            # Crea un archivo vacío con el tamaño de 1.44MB, simulando un disquete
            with open(self.ruta_archivo, "wb") as archivo:
                archivo.write(b'\x00' * 1440 * 1024)  # Escribe 1.44MB de ceros
            
            # Configura el superbloque al inicio del archivo
            with open(self.ruta_archivo, "r+b") as archivo:
                archivo.seek(0)
                archivo.write(b"FiUnamFS")  # Nombre del sistema de archivos
                archivo.write(b"25-1")  # Versión del sistema de archivos
                archivo.write(b"\x00" * (self.TAMANO_CLUSTER - 8))  # Relleno del superbloque

    def listar_directorio(self):
        """
        Lee el directorio del sistema de archivos y devuelve una lista de archivos.
        Cada entrada del directorio contiene el nombre y tamaño del archivo.
        Las entradas vacías se indican con "--------------".
        """
        contenido = []  # Almacena las entradas del directorio
        with open(self.ruta_archivo, "rb") as archivo:
            archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque para acceder al directorio
            for _ in range(self.MAXIMO_ENTRADAS):
                # Leer una entrada de directorio (nombre, tamaño, cluster de inicio, etc.)
                entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                nombre = entrada[1:15].decode("ascii").strip("\x00")  # Obtener nombre
                tamano = struct.unpack("<I", entrada[16:20])[0]  # Obtener tamaño en bytes
                # Verifica si la entrada tiene un archivo o está vacía
                if nombre:
                    contenido.append(f"{nombre} - {tamano} bytes")
                else:
                    contenido.append("-------------- - 0 bytes")  # Indicador de entrada vacía
        return contenido  # Devuelve la lista de archivos en el directorio

    def copiar_a_sistema(self, nombre_archivo):
        #Copia un archivo desde el sistema de archivos FiUnamFS al sistema operativo local.
        archivo_encontrado = False  # Bandera para verificar si se encontró el archivo
        with self.bloqueo:  # Bloqueo para evitar accesos concurrentes
            with open(self.ruta_archivo, "rb") as archivo:
                archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
                for _ in range(self.MAXIMO_ENTRADAS):
                    entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                    nombre = entrada[1:15].decode("ascii").strip("\x00")

                    if nombre == nombre_archivo:
                        # Archivo encontrado, proceder con la copia
                        archivo_encontrado = True
                        tamano = struct.unpack("<I", entrada[16:20])[0]
                        cluster_inicio = struct.unpack("<I", entrada[20:24])[0]
                        ruta_salida = os.path.join(".", nombre_archivo)
                        # Abrir archivo de salida en el sistema local y copiar datos
                        with open(ruta_salida, "wb") as archivo_salida:
                            self._leer_datos_archivo(archivo, archivo_salida, cluster_inicio, tamano)
                        print(f"Archivo '{nombre_archivo}' copiado a '{ruta_salida}'")
                        return True
        if not archivo_encontrado:
            # Mensaje si el archivo no se encuentra en el sistema de archivos
            print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS")
            return False

    def copiar_desde_sistema(self, ruta_archivo):
        #Copia un archivo desde el sistema operativo local a FiUnamFS.
        nombre_archivo = os.path.basename(ruta_archivo)  # Obtener el nombre del archivo
        tamano_archivo = os.path.getsize(ruta_archivo)  # Obtener tamaño en bytes del archivo
    
        with self.bloqueo:
            with open(self.ruta_archivo, "r+b") as archivo:
                archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
                entrada_disponible = False  # Bandera para verificar espacio en el directorio
            
                for _ in range(self.MAXIMO_ENTRADAS):
                    pos_entrada = archivo.tell()  # Posición de la entrada actual
                    entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                    nombre = entrada[1:15].decode("ascii").strip("\x00")
                
                    if nombre == "--------------":
                        # Entrada disponible encontrada, proceder a escribir datos del archivo
                        entrada_disponible = True
                        archivo.seek(pos_entrada)
                        archivo.write(b"#" + nombre_archivo.encode("ascii").ljust(15, b"\x00"))
                        archivo.write(struct.pack("<I", tamano_archivo))
                    
                        try:
                            # Encontrar cluster de inicio para almacenar el archivo
                            cluster_inicio = self._encontrar_cluster_libre(archivo, tamano_archivo)
                            archivo.write(struct.pack("<I", cluster_inicio))
                            archivo.write(b"\x00" * (self.TAMANO_ENTRADA_DIRECTORIO - 24))
                            # Copiar datos desde el archivo del sistema local al sistema de archivos
                            with open(ruta_archivo, "rb") as archivo_origen:
                                self._escribir_datos_archivo(archivo, archivo_origen, cluster_inicio, tamano_archivo)
                            print(f"Archivo '{nombre_archivo}' copiado a FiUnamFS")
                            return True
                        except Exception as e:
                            print(f"Error al copiar '{nombre_archivo}' a FiUnamFS: {e}")
                            return False

                if not entrada_disponible:
                    # Mensaje si no hay espacio suficiente en el directorio
                    print("No hay espacio suficiente en el directorio de FiUnamFS")
                    return False

    def eliminar_archivo(self, nombre_archivo):
        #Elimina un archivo en FiUnamFS, marcando su entrada como vacía y liberando sus clusters ocupados.
        archivo_encontrado = False  # Bandera para verificar si se encontró el archivo
        with self.bloqueo:
            with open(self.ruta_archivo, "r+b") as archivo:
                archivo.seek(self.TAMANO_CLUSTER)  # Saltar el superbloque
                for _ in range(self.MAXIMO_ENTRADAS):
                    pos_entrada = archivo.tell()  # Posición de la entrada actual
                    entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                    nombre = entrada[1:15].decode("ascii").strip("\x00")

                    if nombre == nombre_archivo:
                        # Archivo encontrado, proceder a eliminarlo
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
        #Libera los clusters ocupados por un archivo eliminando sus datos en FiUnamFS.
        clusters_necesarios = (tamano_archivo + self.TAMANO_CLUSTER - 1) // self.TAMANO_CLUSTER
        archivo.seek(cluster_inicio * self.TAMANO_CLUSTER)
        archivo.write(b"\x00" * clusters_necesarios * self.TAMANO_CLUSTER)

    def _leer_datos_archivo(self, archivo, archivo_destino, cluster_inicio, tamano_archivo):
        #Lee los datos de un archivo desde FiUnamFS y los escribe en un archivo de salida en el sistema local.
        archivo.seek(cluster_inicio * self.TAMANO_CLUSTER)
        bytes_restantes = tamano_archivo
        while bytes_restantes > 0:
            chunk = archivo.read(min(self.TAMANO_CLUSTER, bytes_restantes))
            archivo_destino.write(chunk)
            bytes_restantes -= len(chunk)

    def _escribir_datos_archivo(self, archivo, archivo_origen, cluster_inicio, tamano_archivo):
        #Escribe los datos de un archivo local en FiUnamFS a partir del cluster de inicio especificado.
        archivo.seek(cluster_inicio * self.TAMANO_CLUSTER)
        bytes_restantes = tamano_archivo
        while bytes_restantes > 0:
            chunk = archivo_origen.read(min(self.TAMANO_CLUSTER, bytes_restantes))
            archivo.write(chunk)
            bytes_restantes -= len(chunk)

    def sincronizar_estado(self):
        #Realiza una sincronización simulada del estado entre hilos en el sistema de archivos.
        with self.bloqueo:
            print("Estado sincronizado entre hilos")
