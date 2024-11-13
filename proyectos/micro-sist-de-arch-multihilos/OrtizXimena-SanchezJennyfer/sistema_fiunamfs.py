#Ortiz Moreno Ximena 
#Sánchez Gachuz Jennyfer Estefanía

import struct
import threading
import os
import time

class SistemaFiUnamFS:
    TAMANO_CLUSTER = 256
    CLUSTERS_DIRECTORIO = 4
    TAMANO_ENTRADA_DIRECTORIO = 64
    MAXIMO_ENTRADAS = (CLUSTERS_DIRECTORIO * TAMANO_CLUSTER) // TAMANO_ENTRADA_DIRECTORIO

    def __init__(self, ruta_archivo="fiunamfs.img"):
        self.ruta_archivo = ruta_archivo
        self.bloqueo = threading.Lock()
        self.inicializar_sistema_archivos()

    def inicializar_sistema_archivos(self):
        with open(self.ruta_archivo, "rb") as archivo:
            # Leer los primeros 1024 bytes del superbloque
            archivo.seek(0)
            superbloque = archivo.read(1024)
        
            # Extraer nombre y versión con el formato adecuado
            nombre = superbloque[0:8].decode('ascii').strip('\x00')
            version = superbloque[10:15].decode('ascii').strip('\x00')

            # Validar el nombre y la versión del sistema de archivos
            if nombre != "FiUnamFS" or version != "25-1":
                raise ValueError("Error: El archivo no es compatible con FiUnamFS versión 25-1.")

    def listar_directorio(self):
        """
        Lee el directorio del sistema de archivos y devuelve una lista de archivos con formato detallado.
        Cada entrada incluye nombre, tamaño, fecha de creación y modificación.
        """
        contenido = []
        with open(self.ruta_archivo, "rb") as archivo:
            archivo.seek(1024)  # Inicio del directorio después del superbloque
            for i in range(64):  # 64 entradas en total
                entrada = archivo.read(64)
                file_type = entrada[0:1]

                # Ignorar entradas vacías
                if file_type == b'#':
                    continue

                # Extraer y limpiar cada campo
                nombre = entrada[1:16].decode("ascii", errors="ignore").strip("\x00")
                tamano = struct.unpack("<I", entrada[16:20])[0]
                fecha_creacion = entrada[24:37].decode("ascii").strip("\x00")
                fecha_modificacion = entrada[38:51].decode("ascii").strip("\x00")

                # Solo agregar si el nombre no está vacío y el tamaño es mayor que cero
                if nombre and tamano > 0:
                    contenido.append(
                        f"Nombre: {nombre}, Tamaño: {tamano}, Creación: {fecha_creacion}, Modificación: {fecha_modificacion}"
                    )

        return contenido

    def copiar_a_sistema(self, nombre_archivo, dest_path="."):
        archivo_encontrado = False
        with self.bloqueo:
            with open(self.ruta_archivo, "rb") as archivo:
                archivo.seek(1024)  # Comenzamos desde el inicio del directorio
                for i in range(64):  # Revisamos las 64 entradas posibles
                    entrada = archivo.read(64)
                    file_name = entrada[1:16].decode("ascii", errors="ignore").strip("\x00").strip()

                    # Normalizar nombres eliminando espacios y caracteres no alfanuméricos
                    nombre_archivo_normalizado = ''.join(filter(str.isalnum, nombre_archivo))
                    file_name_normalizado = ''.join(filter(str.isalnum, file_name))

                    # Depuración: Mostrar el nombre del archivo leído y el comparado
                    print(f"Entrada {i}: Buscando '{nombre_archivo_normalizado}' vs Encontrado '{file_name_normalizado}'")

                    # Comparar nombres de archivos normalizados
                    if file_name_normalizado == nombre_archivo_normalizado:
                        archivo_encontrado = True
                        file_size = struct.unpack("<I", entrada[16:20])[0]
                        cluster_start = struct.unpack("<I", entrada[20:24])[0]
                    
                        # Ir al cluster inicial y leer el contenido del archivo
                        archivo.seek(cluster_start * 1024)  # Cluster inicio en tamaño de 1024 bytes
                        data = archivo.read(file_size)
                    
                        # Guardar el archivo en el sistema local
                        ruta_salida = os.path.join(dest_path, nombre_archivo)
                        with open(ruta_salida, "wb") as archivo_salida:
                            archivo_salida.write(data)
                        print(f"Archivo '{nombre_archivo}' copiado a '{ruta_salida}'")
                        return True  # Terminamos la función si copiamos el archivo

        if not archivo_encontrado:
            print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS")
            return False

    def copiar_desde_sistema(self, ruta_archivo):
        nombre_archivo = os.path.basename(ruta_archivo)  # Obtener el nombre del archivo
        tamano_archivo = os.path.getsize(ruta_archivo)  # Obtener tamaño en bytes del archivo

        if len(nombre_archivo) > 15:
            print("Error: El nombre del archivo es demasiado largo")
            return False

        with self.bloqueo:
            with open(self.ruta_archivo, "r+b") as archivo:
                archivo.seek(1024)  # Saltar el superbloque y empezar en el directorio
                entrada_disponible = False  # Bandera para verificar espacio en el directorio

                for i in range(self.MAXIMO_ENTRADAS):
                    pos_entrada = archivo.tell()  # Posición de la entrada actual
                    entrada = archivo.read(self.TAMANO_ENTRADA_DIRECTORIO)
                    file_type = entrada[0:1]

                    # Encuentra la primera entrada libre en el directorio
                    if file_type == b'#':  # La entrada está libre si tiene el caracter '#'
                        entrada_disponible = True
                        archivo.seek(pos_entrada)
                    
                        # Escribe los datos del archivo en el directorio
                        archivo.write(b"." + nombre_archivo.encode("ascii").ljust(15, b"\x00"))
                        archivo.write(struct.pack("<I", tamano_archivo))

                        try:
                            # Usa _encontrar_cluster_libre para hallar espacio en el sistema
                            cluster_inicio = self._encontrar_cluster_libre(archivo, tamano_archivo)
                            archivo.write(struct.pack("<I", cluster_inicio))
                        
                            # Obtener la fecha actual en formato AAAAMMDDHHMMSS y escribirla en los campos de creación y modificación
                            fecha_actual = time.strftime("%Y%m%d%H%M%S").encode("ascii")
                            archivo.write(fecha_actual)  # Fecha de creación
                            archivo.write(fecha_actual)  # Fecha de modificación
                        
                            # Copiar los datos del archivo del sistema local al sistema de archivos FiUnamFS
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
            with open(self.ruta_archivo, "r+b") as archivo:  # Usar 'r+b' para leer y escribir
                archivo.seek(1024)  # Comenzamos desde el inicio del directorio
                for i in range(64):  # Revisamos las 64 entradas posibles
                    pos = archivo.tell()
                    entrada = archivo.read(64)
                    file_name = entrada[1:16].decode("ascii", errors="ignore").strip("\x00")

                    # Normalizar nombres eliminando espacios y caracteres no alfanuméricos
                    nombre_archivo_normalizado = ''.join(filter(str.isalnum, nombre_archivo))
                    file_name_normalizado = ''.join(filter(str.isalnum, file_name))

                    # Depuración: Mostrar el nombre del archivo leído y el comparado
                    print(f"Entrada {i}: Buscando '{nombre_archivo_normalizado}' vs Encontrado '{file_name_normalizado}'")

                    # Comparar nombres de archivos normalizados
                    if file_name_normalizado == nombre_archivo_normalizado:
                        archivo_encontrado = True
                    
                        # Marcar la entrada como vacía
                        archivo.seek(pos)
                        archivo.write(b'#' + b'---------------')  # Marcar tipo de archivo como vacío y nombre vacío
                        print(f"Archivo '{nombre_archivo}' eliminado de FiUnamFS")
                        return True  # Terminamos la función si el archivo es eliminado

        if not archivo_encontrado:
            print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS")
            return False


    def _liberar_clusters(self, archivo, cluster_inicio, tamano_archivo):
        #Libera los clusters ocupados por un archivo eliminando sus datos en FiUnamFS.
        clusters_necesarios = (tamano_archivo + self.TAMANO_CLUSTER - 1) // self.TAMANO_CLUSTER
        archivo.seek(cluster_inicio * self.TAMANO_CLUSTER)
        archivo.write(b"\x00" * clusters_necesarios * self.TAMANO_CLUSTER)
        
    def _encontrar_cluster_libre(self, archivo, tamano_archivo):
        clusters_necesarios = (tamano_archivo + self.TAMANO_CLUSTER - 1) // self.TAMANO_CLUSTER
        archivo.seek(5 * self.TAMANO_CLUSTER)  # Comenzar después del superbloque y el directorio (clusters 0 a 4)
    
        for cluster in range(5, (1440 * 1024) // self.TAMANO_CLUSTER):
            archivo.seek(cluster * self.TAMANO_CLUSTER)
            data = archivo.read(self.TAMANO_CLUSTER * clusters_necesarios)
        
            # Verifica si los clusters están completamente vacíos
            if data == b'\x00' * (self.TAMANO_CLUSTER * clusters_necesarios):
                return cluster
    
        raise Exception("No hay suficiente espacio libre para el archivo")

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
