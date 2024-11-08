import os
import struct
import threading
from datetime import datetime

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

# Sincronización de operaciones concurrentes
directorio_mutex = threading.Lock()
sem_superbloque = threading.Semaphore(1)
lock_verificacion = threading.Lock()

class SistemaArchivosFiUnamFS:

    def __init__(self, imagen_archivo="fiunamfs.img"):
        self.imagen_archivo = imagen_archivo

    def verificar_archivo(self):
        with lock_verificacion:
            # Verificar si el archivo existe en el directorio actual
            if not os.path.exists(self.imagen_archivo):
                print(f"\n\tEl archivo '{self.imagen_archivo}' no se encuentra en el directorio actual.")
                
                # Solicitar ruta si el archivo no existe en el directorio actual
                while True:
                    ruta = input("\n\tPor favor, ingrese la ruta completa del archivo 'fiunamfs.img': ")
                    if os.path.exists(ruta):
                        self.imagen_archivo = ruta
                        CLEAR()
                        print(f"\tArchivo encontrado en la ruta: {self.imagen_archivo}")
                        break
                    else:
                        CLEAR()
                        print("\n\tArchivo no encontrado en la ruta especificada. Intente nuevamente.")

    def validar_sistema_archivos(self):
        with sem_superbloque:  # Acceso controlado al superbloque
            with open(self.imagen_archivo, 'rb') as img:
                img.seek(0)
                superbloque = img.read(TAMANO_CLUSTER)

                # Leer y validar el nombre y versión del sistema de archivos
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
            'Nombre': nombre_archivo.strip(),
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
                    f" | {archivo['Fecha Modificación']}\t | "
                )
            print("\t-------------------------------------------------------------"
                    "-------------------------------------------------------------")


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
                while True:
                    respuesta = input("\n\t¿Deseas copiar el archivo a un directorio específico? (s/n): ").strip().lower()
                    
                    if respuesta == 's':
                        while True:
                            ruta_destino = input("\n\tIngresa la ruta completa del directorio de destino (escribe 'v' para regresar): ").strip()
                            
                            if ruta_destino.lower() == 'v':
                                CLEAR()
                                print("\n\tRegresando al menú principal...")
                                return  # Regresa al menú principal
                            
                            # Verificar si el directorio existe
                            if os.path.exists(ruta_destino):
                                break  # Salir del ciclo si el directorio existe
                            else:
                                CLEAR()
                                print("\n\tError: El directorio no existe. Por favor, intenta de nuevo.")
                        break  # Salir del bucle externo si 's' fue seleccionado

                    elif respuesta == 'n':
                        ruta_destino = os.getcwd()  # Usar el directorio actual si no se especifica otro
                        break  # Salir del bucle externo

                    else:
                        CLEAR()
                        print("\n\tOpción no válida. Por favor ingresa 's' o 'n'.")

                # Crear la ruta completa del archivo
                nombre_base, extension = os.path.splitext(archivo_encontrado['Nombre'])
                ruta_completa = os.path.join(ruta_destino, archivo_encontrado['Nombre'])

                # Verificar si ya existe un archivo con el mismo nombre en el destino
                contador = 1
                while os.path.exists(ruta_completa):
                    ruta_completa = os.path.join(ruta_destino, f"{nombre_base}({contador}){extension}")
                    contador += 1

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


    def copiar_de_local(self, ruta_archivo_local):
        """
        Función para copiar un archivo desde la ruta especificada a la imagen de FiUnamFS.
        Si un archivo con el mismo nombre y extensión ya existe en FiUnamFS, se añade un sufijo numérico para evitar sobreescritura.
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

                nombre_base, extension = os.path.splitext(os.path.basename(ruta_archivo_local))
                
                if (len(nombre_base.strip()) + len(extension)) > 16:
                    CLEAR()
                    print("\tNo puede ingresar nombres mayores a 15 caracteres...")
                    print("\tVolviendo al menú principal...\n")
                    return   # Regresa al menú principal


                # Generar un nombre único en FiUnamFS si el archivo ya existe
                nombre_base, extension = os.path.splitext(os.path.basename(ruta_archivo_local)[:15])
                nombre_archivo = nombre_base[:15 - len(extension)] + extension  # Limitar el nombre a 15 caracteres
                contador = 1

                # Genera sufijo numerico entre los bytes 13 y 15
                while any(archivo['Nombre'] == nombre_archivo for archivo in contenido_directorio):
                    nombre_archivo = f"{nombre_base[:13 - len(str(contador))]}({contador}){extension}"[:15]
                    contador += 1

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
                    CLEAR()
                    print("\tNo hay suficiente espacio para copiar el archivo dentro de FiUnamFS.")
                    return

                # Añadir la entrada del archivo al directorio con la fecha
                fecha_actual = datetime.now().strftime("%Y%m%d%H%M%S")  # Fecha del sistema

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
                        CLEAR()
                        print("\tNo se pudo encontrar espacio en el directorio.")
                        return

                    # Escribir el archivo en clusters disponibles
                    for i, cluster in enumerate(clusters_disponibles):
                        posicion_cluster = cluster * TAMANO_CLUSTER
                        img.seek(posicion_cluster)
                        img.write(data[i * TAMANO_CLUSTER:(i + 1) * TAMANO_CLUSTER])

                CLEAR()
                print(f"\tArchivo '{nombre_archivo}' copiado a FiUnamFS.")

            except FileNotFoundError:
                CLEAR()
                print(f"\tArchivo '{ruta_archivo_local}' no encontrado en el sistema local.")

    def eliminar_archivo(self, nombre_archivo):
        with directorio_mutex:
            archivo_encontrado = False
            
            # Buscar el archivo en el directorio
            for cluster in range(CLUSTERS_DIRECTORIO):
                posicion_inicial = (SUPERBLOQUE_CLUSTER + 1 + cluster) * TAMANO_CLUSTER
                with open(self.sistema_archivos.imagen_archivo, 'r+b') as img:
                    img.seek(posicion_inicial)
                    cluster_datos = img.read(TAMANO_CLUSTER)

                    for entrada in range(0, TAMANO_CLUSTER, TAMANO_ENTRADA):
                        entrada_actual = cluster_datos[entrada:entrada + TAMANO_ENTRADA]

                        # Verifica si el archivo coincide con el nombre buscado
                        nombre_archivo_actual = entrada_actual[1:16].decode().strip('\x00').strip()
                        if nombre_archivo_actual == nombre_archivo:
                            # Sobrescribir la entrada con un símbolo de archivo vacío '#'
                            nueva_entrada = b'#' + entrada_actual[1:]  # Mantener los otros campos
                            cluster_datos = (
                                cluster_datos[:entrada] + nueva_entrada + cluster_datos[entrada + TAMANO_ENTRADA:]
                            )
                            img.seek(posicion_inicial)
                            img.write(cluster_datos)  # Guardar cambios en el cluster
                            archivo_encontrado = True
                            CLEAR()
                            print(f"\tArchivo '{nombre_archivo}' ha sido eliminado.")
                            break
                    if archivo_encontrado:
                        break

            if not archivo_encontrado:
                CLEAR()
                print(f"\tArchivo '{nombre_archivo}' no encontrado en el directorio.")




class RutaArchivo:
    """
    Clase para gestionar la obtención de la ruta de un archivo,
    preguntando si está en el directorio actual o solicitando la ruta completa.
    """

    def __init__(self):
        # Inicializa la variable para almacenar la ruta del archivo
        self.ruta_archivo = None

    def obtener_ruta(self):
        """
        Solicita al usuario si el archivo está en el directorio actual.
        Si no, permite al usuario ingresar la ruta completa del archivo.
        Devuelve la ruta del archivo si existe o None si se decide volver al menú.
        """
        while True:
            # Solicitar si el archivo está en el directorio actual
            opcion = input("\n\t¿El archivo está en el directorio actual? (s/n): ").strip().lower()
            
            if opcion == 's':
                # Solicitar el nombre del archivo si está en el directorio actual
                nombre_archivo = input("\tIngrese el nombre del archivo (con la extensión) o escriba 'v' para volver: ").strip()
                
                if nombre_archivo.lower() == 'v':
                    CLEAR()
                    print("\t Volviendo al menú principal...\n")
                    return None  # Regresa al menú principal

                # Establecer la ruta del archivo en el directorio actual
                self.ruta_archivo = os.path.join(os.getcwd(), nombre_archivo)
            
            elif opcion == 'n':
                # Solicitar la ruta completa del archivo si no está en el directorio actual
                ruta_archivo = input("\tIngrese la ruta completa del archivo (con la extensión) o escriba 'v' para volver: ").strip()
                
                if ruta_archivo.lower() == 'v':
                    CLEAR()
                    print("\t Volviendo al menú principal...\n")
                    return None  # Regresa al menú principal
                
                # Establecer la ruta del archivo ingresada
                self.ruta_archivo = ruta_archivo
            
            else:
                print("\tOpción no válida. Inténtalo de nuevo.")
                continue

            # Verificar si el archivo existe en la ruta especificada
            if not os.path.isfile(self.ruta_archivo):
                CLEAR()
                print(f"\tEl archivo '{self.ruta_archivo}' no existe. Intenta de nuevo.\n")
            else:
                # Si el archivo existe, devuelve la ruta
                return self.ruta_archivo
            
class ManejoDeHilos:

    def __init__(self, operaciones_directorio):
        
        #Inicializa la clase para gestionar los hilos y controlar los semáforos y mutex en cada operación.
        self.operaciones = operaciones_directorio 

    def ejecutar_hilo(self, operacion, *args):

        #Ejecuta la operación en un hilo independiente con los argumentos especificados.
        hilo = threading.Thread(target=operacion, args=args)
        hilo.start()
        hilo.join()

    def listar_directorio(self):

        #Crea y maneja el hilo para la operación de listar directorio.
        self.ejecutar_hilo(self.operaciones.listar_directorio)

    def copiar_de_FiUnamFs(self, nombre_archivo):

        #Crea y maneja el hilo para copiar un archivo desde FiUnamFs a nuestro sistema local.
        self.ejecutar_hilo(self.operaciones.copiar_de_FiUnamFs, nombre_archivo)

    def copiar_a_FiUnamFs(self, ruta_archivo_local):

        # Crea y maneja el hilo para copiar un archivo desde el sistema local a FiUnamFs.
        self.ejecutar_hilo(self.operaciones.copiar_de_local, ruta_archivo_local)

    def eliminar_archivo(self, nombre_archivo):

        #Crea y maneja el hilo para eliminar un archivo en FiUnamFs.
        self.ejecutar_hilo(self.operaciones.eliminar_archivo, nombre_archivo)


# Función para ejecutar los hilos de verificacion
def verificarSistema(sistema_archivos):
    # Hilo para verificar el archivo
    hilo_verificacion = threading.Thread(target=sistema_archivos.verificar_archivo)
    
    # Hilo para listar el directorio, esperando a que el primer hilo termine
    hilo_listar_directorio = threading.Thread(target=sistema_archivos.leer_directorio)
    
    hilo_verificacion.start()
    hilo_verificacion.join()  
    
    hilo_listar_directorio.start()
    hilo_listar_directorio.join() 
        

def main():

    # Crea una instancia de SistemaArchivosFiUnamFS con el archivo de imagen especificado.
    sistema_archivos = SistemaArchivosFiUnamFS(ARCHIVO_IMAGEN)
    verificarSistema(sistema_archivos)

    operaciones = OperacionesDirectorio(sistema_archivos)

    # Crea una instancia de ManejoDeHilos, pasando la instancia de OperacionesDirectorio.
    manejo_hilos = ManejoDeHilos(operaciones)

    datos_del_equipo()
    while True:
        menuMainImp()
        opcion = input("\tSeleccione una opción: ")

        match opcion:
            case "1": # Listar directorio
                manejo_hilos.listar_directorio()

            case "2": # Copiar un archivo de FiUnamFs a nuestro sistema local
                nombre_archivo = input("\n\tIngrese el nombre del archivo de FiUnamFS (sin importar la extensión): ")
                manejo_hilos.copiar_de_FiUnamFs(nombre_archivo)

            case "3": # Copiar un archivo de nuestro sistema local a FiUnamFs
                ruta_archivo_obj = RutaArchivo()
                ruta_archivo_local = ruta_archivo_obj.obtener_ruta()
                if ruta_archivo_local:
                    manejo_hilos.copiar_a_FiUnamFs(ruta_archivo_local)

            case "4": # Borrar un archivo de FiUnamFs
                nombre_archivo = input("\n\tIngrese el nombre del archivo a eliminar en FiUnamFS (con extensión): ")
                manejo_hilos.eliminar_archivo(nombre_archivo)

            case "5": # Salir del programa
                CLEAR()
                print("\n\t... Hasta luego ...\n")
                break

            case _: # Opcion no valida
                CLEAR()
                print("\tOpción no válida. Por favor, elija una opción del menú.")

# Limpiar pantalla con ANSI
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
    print("\t-------------------------------------------------------------"
          "-------------------------------------------------------------")
    print("\t| NONBRE\t\t |    TAMAÑO\t |   CLUSTER INICIAL\t |      FECHA DE CREACIÓN\t | FECHA DE MODIFICACIÓN | ")
    print("\t|------------------------------------------------------------"
          "------------------------------------------------------------|")

def datos_del_equipo():
    print("\n\tProyecto 2: (Micro) sistema de archivo multihilos")
    print ("\tAlumnos: Hernández Saldívar Héctor Saúl 329376027 y Miyasaki Sato Yuichi Vicente 318586465")
    print ("\tDocente: Ing. Gunnar Eyal Wolf Iszaevich")
    print ("\tSistemas Operativos 2025-1    grupo: 6")




if __name__ == "__main__":
    main()