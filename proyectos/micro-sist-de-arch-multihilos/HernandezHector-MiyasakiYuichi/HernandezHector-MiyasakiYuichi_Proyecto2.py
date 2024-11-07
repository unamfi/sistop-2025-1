import os
import struct
import threading

# Parámetros del proyecto
TAMANO_DISQUETE = 1440 * 1024  # 1440 KB
TAMANO_SECTOR = 256
TAMANO_CLUSTER = 1024  # 4 sectores de 256 bytes
TAMANO_ENTRADA = 64
SUPERBLOQUE_CLUSTER = 0
CLUSTERS_DIRECTORIO = 4
NOMBRE_SISTEMA_ARCHIVOS = 'FiUnamFS'
VERSION_SISTEMA = '25-1'
ARCHIVO_IMAGEN = 'fiunamfs.img'

# Sincronización para operaciones concurrentes
directorio_mutex = threading.Lock()

class SistemaArchivosFiUnamFS:

    def __init__(self, imagen_archivo):
        self.imagen_archivo = imagen_archivo

    def validar_sistema_archivos(self):
        with open(self.imagen_archivo, 'rb') as img:
            img.seek(0)
            superbloque = img.read(TAMANO_CLUSTER)

            nombre = superbloque[0:8].decode().strip('\x00')
            version = superbloque[10:15].decode().strip('\x00')

            if nombre != NOMBRE_SISTEMA_ARCHIVOS:
                raise ValueError("\tNombre de sistema de archivos incorrecto.")
            if version != VERSION_SISTEMA:
                raise ValueError("\tVersión del sistema de archivos no soportada.")


    def leer_directorio(self):
        directorio = []
        with open(self.imagen_archivo, 'rb') as img:
            self.validar_sistema_archivos()

            for cluster in range(CLUSTERS_DIRECTORIO):
                posicion_inicial = (SUPERBLOQUE_CLUSTER + 1 + cluster) * TAMANO_CLUSTER
                img.seek(posicion_inicial)
                cluster_datos = img.read(TAMANO_CLUSTER)

                for entrada in range(0, TAMANO_CLUSTER, TAMANO_ENTRADA):
                    entrada_actual = cluster_datos[entrada:entrada + TAMANO_ENTRADA]

                    if entrada_actual[0:1] == b'#':
                        continue  # Entrada vacía

                    archivo_info = self._procesar_entrada_directorio(entrada_actual)
                    directorio.append(archivo_info)

        return directorio

    @staticmethod
    def _procesar_entrada_directorio(entrada):
        tipo_archivo = chr(entrada[0])
        nombre_archivo = entrada[1:16].decode().strip('\x00')
        tamaño_archivo = struct.unpack('<I', entrada[16:20])[0]
        cluster_inicial = struct.unpack('<I', entrada[20:24])[0]
        fecha_creacion = entrada[24:38].decode()
        fecha_modificacion = entrada[38:52].decode()

        return {
            'Tipo': tipo_archivo,
            'Nombre': nombre_archivo,
            'Tamaño': tamaño_archivo,
            'Cluster Inicial': cluster_inicial,
            'Fecha Creación': fecha_creacion,
            'Fecha Modificación': fecha_modificacion
        }


class OperacionesDirectorio:
    
    def __init__(self, sistema_archivos):
        self.sistema_archivos = sistema_archivos

    def listar_directorio(self):
        with directorio_mutex:
            contenido_directorio = self.sistema_archivos.leer_directorio()

            CLEAR()
            listarDirectorioImp() # imprimir las secciones del contenido del directorio

            for archivo in contenido_directorio:
                print(
                    f"\t|{archivo['Tipo']} {archivo['Nombre']:<15}\t | {archivo['Tamaño']} bytes\t"
                    f" |\t  {archivo['Cluster Inicial']}\t\t"
                    f" |\t  {archivo['Fecha Creación']}\t"
                    f" |\t  {archivo['Fecha Modificación']} | "
                )

    def copiar_de_FiUnamFs(self, nombre_archivo):
        # Usar un lock para sincronizar el acceso a la función
        with directorio_mutex:
            contenido_directorio = self.sistema_archivos.leer_directorio()
            archivo_encontrado = None

            # Buscar el archivo en el directorio
            for archivo in contenido_directorio:
                if archivo['Nombre'].startswith(nombre_archivo):  # Coincidir solo el nombre
                    archivo_encontrado = archivo
                    break

            if archivo_encontrado:
                # Preguntar si desea copiar en un directorio específico
                respuesta = input("\n\t¿Deseas copiar el archivo a un directorio específico? (s/n): ").strip().lower()
                if respuesta == 's':
                    ruta_destino = input("\n\tIngresa la ruta completa del directorio de destino: ").strip()
                    if not os.path.exists(ruta_destino):
                        os.makedirs(ruta_destino)  # Si no existe el directorio, crear uno
                else:
                    ruta_destino = os.getcwd()

                # Crear la ruta completa del archivo
                ruta_completa = os.path.join(ruta_destino, archivo_encontrado['Nombre'])

                # Verificar tamaño de lectura
                inicio_lectura = (archivo_encontrado['Cluster Inicial']) * TAMANO_CLUSTER

                with open(self.sistema_archivos.imagen_archivo, 'rb') as img:
                    img.seek(inicio_lectura)
                    data = img.read(archivo_encontrado['Tamaño'])
                    with open(ruta_completa, 'wb') as nuevo_archivo:
                        nuevo_archivo.write(data)

                CLEAR()
                print(f"\n\tCopiando archivo de tamaño: {archivo_encontrado['Tamaño']} bytes...\n")
                print(f"\tArchivo {archivo_encontrado['Nombre']} copiado a {ruta_completa}")
            else:
                CLEAR()
                print(f"\tArchivo '{nombre_archivo}' no encontrado en FiUnamFS.")


    def copiar_archivo_dentro(self, ruta_archivo_local):
        """
        Función para copiar un archivo desde la ruta especificada a la imagen de FiUnamFS.
        """
        with directorio_mutex:
            try:
                # Leer archivo local
                with open(ruta_archivo_local, 'rb') as archivo_local:
                    data = archivo_local.read()
                    tamaño_archivo = len(data)

                # Calcular clusters necesarios para almacenar el archivo
                clusters_necesarios = (tamaño_archivo + TAMANO_CLUSTER - 1) // TAMANO_CLUSTER

                # Leer directorio para verificar espacio disponible
                contenido_directorio = self.sistema_archivos.leer_directorio()

                # Buscar clusters libres para almacenar el archivo
                clusters_disponibles = []
                for cluster in range(CLUSTERS_DIRECTORIO + 1, TAMANO_DISQUETE // TAMANO_CLUSTER):
                    ocupado = False
                    for archivo in contenido_directorio:
                        cluster_inicial = archivo['Cluster Inicial']
                        clusters_ocupados = range(cluster_inicial, cluster_inicial + (archivo['Tamaño'] + TAMANO_CLUSTER - 1) // TAMANO_CLUSTER)
                        if cluster in clusters_ocupados:
                            ocupado = True
                            break
                    if not ocupado:
                        clusters_disponibles.append(cluster)
                        if len(clusters_disponibles) == clusters_necesarios:
                            break
                
                if len(clusters_disponibles) < clusters_necesarios:
                    print("\tNo hay suficiente espacio para copiar el archivo dentro de FiUnamFS.")
                    return

                # Añadir la entrada del archivo al directorio
                nombre_archivo = os.path.basename(ruta_archivo_local)[:15]  # Limitar el nombre a 15 caracteres

                fecha_actual = "20241029"  # Ejemplo de fecha; puedes adaptarlo a la fecha actual en formato deseado

                entrada_directorio = (
                    b'.' +
                    nombre_archivo.encode().ljust(15, b'\x00') +
                    struct.pack('<I', tamaño_archivo) +
                    struct.pack('<I', clusters_disponibles[0]) +
                    fecha_actual.encode().ljust(14, b'\x00') * 2 +
                    b'\x00' * (TAMANO_ENTRADA - 64)
                )

                with open(self.sistema_archivos.imagen_archivo, 'r+b') as img:
                    # Buscar entrada libre en el directorio
                    for cluster in range(CLUSTERS_DIRECTORIO):
                        posicion_inicial = (SUPERBLOQUE_CLUSTER + 1 + cluster) * TAMANO_CLUSTER
                        img.seek(posicion_inicial)
                        cluster_datos = img.read(TAMANO_CLUSTER)

                        for entrada in range(0, TAMANO_CLUSTER, TAMANO_ENTRADA):
                            if cluster_datos[entrada:entrada + 1] == b'#':  # Espacio libre
                                img.seek(posicion_inicial + entrada)
                                img.write(entrada_directorio)
                                break
                        else:
                            continue
                        break
                    else:
                        print("\tNo se pudo encontrar espacio en el directorio.")
                        return

                    # Escribir el archivo en clusters disponibles
                    for i, cluster in enumerate(clusters_disponibles):
                        posicion_cluster = cluster * TAMANO_CLUSTER
                        img.seek(posicion_cluster)
                        img.write(data[i * TAMANO_CLUSTER:(i + 1) * TAMANO_CLUSTER])

                print(f"\tArchivo '{ruta_archivo_local}' copiado a FiUnamFS.")
            
            except FileNotFoundError:
                print(f"\tArchivo '{ruta_archivo_local}' no encontrado en el sistema local.")

    def eliminar_archivo(self, nombre_archivo):
        # Implementar la lógica para eliminar un archivo de FiUnamFS aquí
        pass  # Reemplaza esto con la implementación real

class RutaArchivo:
    """
    Clase para gestionar la obtención de la ruta de un archivo,
    preguntando si está en el directorio actual o solicitando la ruta completa.
    """

    def __init__(self):
        self.ruta_archivo = None

    def obtener_ruta(self):
        """
        Pregunta al usuario si el archivo está en el directorio actual.
        Si no está, solicita la ruta completa del archivo.
        """
        opcion = input("\n\t¿El archivo está en el directorio actual? (s/n): ").strip().lower()
        
        if opcion == 's':
            nombre_archivo = input("\tIngrese el nombre del archivo en el directorio actual (con la extensión): ").strip()
            self.ruta_archivo = os.path.join(os.getcwd(), nombre_archivo)
        elif opcion == 'n':
            self.ruta_archivo = input("\tIngrese la ruta completa del archivo (con la extensión): ").strip()
        
        if not os.path.isfile(self.ruta_archivo):
            print(f"\tEl archivo '{self.ruta_archivo}' no existe.")
            self.ruta_archivo = None  # Restablecer a None si el archivo no existe

        return self.ruta_archivo


def main():
    sistema_archivos = SistemaArchivosFiUnamFS(ARCHIVO_IMAGEN)
    operaciones = OperacionesDirectorio(sistema_archivos)

    while True:
        
        menuMainImp()
        opcion = input("\tSeleccione una opción: ")

        if opcion == "1":
            hilo_listar = threading.Thread(target=operaciones.listar_directorio)
            hilo_listar.start()
            hilo_listar.join()
        elif opcion == "2":
            nombre_archivo = input("\n\tIngrese el nombre del archivo de FiUnamFS (sin importar la extensión): ")
            hilo_copiar = threading.Thread(target=operaciones.copiar_de_FiUnamFs, args=(nombre_archivo,))
            hilo_copiar.start()
            hilo_copiar.join()
        elif opcion == "3":
            ruta_archivo_obj = RutaArchivo()
            ruta_archivo_local = ruta_archivo_obj.obtener_ruta()
            if ruta_archivo_local:
                hilo_copiar_dentro = threading.Thread(target=operaciones.copiar_archivo_dentro, args=(ruta_archivo_local,))
                hilo_copiar_dentro.start()
                hilo_copiar_dentro.join()

        elif opcion == "4":
            nombre_archivo = input("\n\tIngrese el nombre del archivo a eliminar en FiUnamFS: ")
            operaciones.eliminar_archivo(nombre_archivo)
        elif opcion == "5":
            CLEAR()
            print("\n\t... Hasta luego ...\n")
            break
        else:
            CLEAR()
            print("Opción no válida. Por favor, elija una opción del menú.")

# Limpiar pantalla con una impresion
def CLEAR():
    print("\033[2J\033[H")

# Menu de desiciones para la clase principal
def menuMainImp():
    print("\n\t--------------------------------------------------------")
    print("\t|    --- Menú del Sistema de Archivos FiUnamFS ---     |")
    print("\t|------------------------------------------------------|")
    print("\t| 1. Listar contenido del directorio                   |")
    print("\t| 2. Copiar archivo desde FiUnamFS al sistema local    |")
    print("\t| 3. Copiar archivo desde el sistema local a FiUnamFS  |")
    print("\t| 4. Eliminar archivo de FiUnamFS                      |")
    print("\t| 5. Salir                                             |")
    print("\t--------------------------------------------------------\n")

# Secciones del contenido del directorio
def listarDirectorioImp():
    print("\tContenido del directorio:\n")
    print("\t| NONBRE\t\t | TAMAÑO\t |   CLUSTER INICIAL\t | FECHA DE CREACIÓN\t\t | FECHA DE MODIFICACIÓN | ")
    print("\t-------------------------------------------------------------"
          "-------------------------------------------------------------")


if __name__ == "__main__":
    main()
