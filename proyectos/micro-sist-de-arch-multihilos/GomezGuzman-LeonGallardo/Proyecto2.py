"""
Proyecto: Sistema gestor de archivos
Alumnos:
    -> Gómez Guzmán Anikey Andrea
    -> León Gallardo Ian Yael
Materia: Sistemas Operativos
Grupo: 6

Entorno de desarrollo:
- Lenguaje: Python 3.8+
- Módulos requeridos:
    - os (integrado)
    - struct (integrado)
    - threading (integrado)
    - datetime (integrado)
Este código ha sido diseñado para sistemas operativos compatibles con archivos binarios y permite manipulación de archivos concurrente.
"""

"""
    Proyecto: Sistema gestor de archivos
    Alumnos: 
        -> Gómez Guzmán Anikey Andrea  
        -> León Gallardo Ian Yael   
    Materia: Sistemas Operativos    
    Grupo: 6       
"""
import os  # Proporciona funciones para interactuar con el sistema operativo, como manejo de archivos y directorios.
import struct  # Permite trabajar con datos binarios empaquetados, útil para leer y escribir en binario.
import threading  # Proporciona herramientas para crear y controlar hilos de ejecución, permitiendo operaciones concurrentes.
import datetime  # Facilita el manejo y formato de fechas y horas en el programa.
import queue  # Implementa colas para la comunicación segura entre hilos.
import time  # Proporciona funciones para controlar pausas de tiempo en la ejecución.

# Nombre y acceso al archivo de sistema de archivos.
nombre_sistemaArchivos = "fiunamfs.img"  # Nombre de la imagen de disco que simula el sistema de archivos.
sistemaArchivos = open(nombre_sistemaArchivos, "r+b")  # Abre el archivo en modo lectura/escritura binario.

# Variables de configuración del sistema de archivos:
tamanoClusters = 0  # Tamaño de cada cluster en bytes.
numeroClusters = 0  # Número de clusters en el directorio.
numeroClustersUnidad = 0  # Número total de clusters en la unidad de almacenamiento.

# Tamaño del directorio en el sistema de archivos, actualizado durante la inicialización.
tamanoDirectorio = 0

# Variables de identificación del sistema de archivos, que serán actualizadas con datos del sistema de archivos.
id_sistemaArchivos = ""  # Identificación del sistema.
version = ""  # Versión del sistema.
etiqueta = ""  # Etiqueta o nombre del volumen.

# Lista para almacenar los archivos en el directorio, utilizada para gestionar los archivos existentes.
archivosDir = []

# Clase archivo:
# Representa un archivo en el sistema de archivos.
# Almacena el nombre del archivo, su tamaño y el cluster inicial donde comienza su almacenamiento.
class archivo:
    def __init__(self, nombre, tamano, clusterInicial):
        self.nombre = nombre  # Nombre del archivo.
        self.tamano = tamano  # Tamaño del archivo en bytes.
        self.clusterInicial = clusterInicial  # Cluster inicial donde se almacena el archivo.

# Configuración para concurrencia:
operaciones_queue = queue.Queue()  # Cola para almacenar las operaciones en el sistema, para registro en el monitor.
sync_event = threading.Event()  # Evento para sincronizar el registro de operaciones.
fs_lock = threading.Lock()  # Lock para evitar conflictos en operaciones simultáneas sobre el sistema de archivos.

# Función monitor_sistema:
# Monitorea y registra las operaciones del sistema en tiempo real, mostrando un timestamp.
def monitor_sistema():
    while True:
        try:
            # Espera por una operación en la cola de operaciones.
            operacion = operaciones_queue.get(timeout=1)
            
            # Registrar la operación con un timestamp.
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[Monitor {timestamp}] {operacion}")
            
            # Notifica al sistema que la operación fue registrada y la operación fue recibida.
            sync_event.set()
            sync_event.clear()  # Resetea el evento para la siguiente operación.
        except queue.Empty:
            continue  # Si la cola está vacía, continúa esperando.
        except Exception as e:
            print(f"Error en el monitor: {e}")

# Función leerDatosASCII:
# Lee y decodifica datos ASCII desde una posición específica en el sistema de archivos.
# Retorna un marcador "<nombre inválido>" si no puede decodificar los datos.
def leerDatosASCII(inicio, tamano):
    global sistemaArchivos
    sistemaArchivos.seek(inicio)  # Posiciona el puntero en el inicio dado.
    datos = sistemaArchivos.read(tamano)
    try:
        return datos.decode("ascii")  # Intenta decodificar los datos como texto ASCII.
    except UnicodeDecodeError:
        return "<nombre inválido>"  # Si falla, retorna un marcador indicando nombre inválido.

# Función datoUnpack:
# Lee y convierte datos binarios a un entero utilizando el formato de empaquetado ('<i').
def datoUnpack(inicio, tamano):
    global sistemaArchivos
    sistemaArchivos.seek(inicio)
    dato = sistemaArchivos.read(tamano)
    return struct.unpack('<i', dato)[0]  # Convierte y retorna el valor desempaquetado como entero.

# Función datosPack:
# Convierte un entero en datos binarios y los escribe en el sistema de archivos.
def datosPack(inicio, dato):
    global sistemaArchivos
    sistemaArchivos.seek(inicio)  # Posiciona el puntero en la ubicación de inicio.
    dato = struct.pack('<i', dato)  # Empaqueta el entero en formato binario.
    return sistemaArchivos.write(dato)  # Escribe el dato empaquetado en el archivo.

# Función leerDatosArchivo:
# Lee la información de un archivo en una posición dada en el directorio.
# Si la entrada está marcada como eliminada o inválida, retorna None para omitirla.
def leerDatosArchivo(posicion):
    inicio = 1024 + (posicion * 64)  # Calcula la posición de inicio para esta entrada en el directorio.
    
    # Lee y verifica si el nombre es válido o marcado como eliminado.
    nombre = leerDatosASCII(inicio + 1, 14).strip('\x00')
    if nombre.startswith('#') or nombre == "<nombre inválido>":
        return None  # Omitir entradas eliminadas o con nombres inválidos.

    # Intenta leer el tamaño y el cluster inicial. Si falla, omite la entrada.
    try:
        tamano = datoUnpack(inicio + 16, 4)
        clusterInicial = datoUnpack(inicio + 20, 4)
    except:
        return None
    
    # Valida el tamaño y caracteres del nombre. Si no son válidos, omite la entrada.
    if tamano <= 0 or tamano > (tamanoClusters * numeroClustersUnidad) or not nombre.isprintable():
        return None

    return archivo(nombre, tamano, clusterInicial)  # Retorna un objeto archivo con la información leída.

# Función escribirDatosASCII:
# Escribe una cadena de caracteres ASCII en el sistema de archivos en la posición especificada.
def escribirDatosASCII(inicio, dato):
    global sistemaArchivos
    sistemaArchivos.seek(inicio)  # Posiciona el puntero en la ubicación de inicio.
    dato = dato.encode("ascii")  # Codifica la cadena como ASCII.
    return sistemaArchivos.write(dato)  # Escribe los datos ASCII codificados en el archivo.

# Función copiar_a_sistema:
# Copia un archivo desde el sistema de archivos al sistema de la computadora.
def copiar_a_sistema(nombreCopia, rutaNueva):
    def copiar_proceso():
        with fs_lock:
            # Verifica si el archivo existe en el directorio.
            indexArchivo, validacion = verificarArchivo(nombreCopia)
            if not validacion:
                operaciones_queue.put(f"Error: Archivo {nombreCopia} no existe")
                return

            # Ubicación del archivo en el sistema y la ruta destino.
            archivoC = archivosDir[indexArchivo]
            try:
                if os.path.exists(rutaNueva):
                    rutaArchivoDestino = os.path.join(rutaNueva, nombreCopia)
                    with open(rutaArchivoDestino, "wb") as destino:
                        inicio_lectura = archivoC.clusterInicial * tamanoClusters
                        sistemaArchivos.seek(inicio_lectura)
                        datos_archivo = sistemaArchivos.read(archivoC.tamano)
                        destino.write(datos_archivo)
                    operaciones_queue.put(f"Archivo {nombreCopia} copiado exitosamente a {rutaArchivoDestino}")
                    sync_event.wait()
                else:
                    operaciones_queue.put(f"Error: La ruta {rutaNueva} no existe")
            except Exception as e:
                operaciones_queue.put(f"Error durante la copia: {str(e)}")

    hilo_copia = threading.Thread(target=copiar_proceso)  # Crea y lanza el hilo para copiar el archivo.
    hilo_copia.start()

# Función copiar_de_sistema_fragmentado:
# Copia un archivo desde la computadora al sistema de archivos, pidiendo ruta y cluster inicial.
def copiar_de_sistema_fragmentado():
    rutaArchivo = input("Ingresa la ruta completa del archivo en tu computadora que deseas copiar: ")

    # Verifica la existencia del archivo
    if not os.path.isfile(rutaArchivo):
        print("El archivo no existe en la ruta especificada.")
        return

    # Obtiene nombre y tamaño del archivo
    nombreArchivo = os.path.basename(rutaArchivo)[:15].ljust(15, '\x00')
    tamanoArchivo = os.path.getsize(rutaArchivo)

    # Lee el contenido del archivo para copiar
    with open(rutaArchivo, "rb") as archivoComputadora:
        contenido = archivoComputadora.read()

    # Solicita al usuario el cluster inicial para almacenar el archivo
    cluster_inicial = int(input("Ingresa el cluster inicial en el que deseas guardar el archivo: "))

    # Formato de fecha y hora actuales para crear metadatos de archivo
    fecha_actual = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # Crea la entrada del archivo en el directorio
    entrada_directorio = (
        b'-' +  # Tipo de archivo (siempre '-')
        nombreArchivo.encode('ascii', 'ignore') +  # Nombre del archivo (15 bytes)
        struct.pack('<I', tamanoArchivo) +  # Tamaño del archivo en bytes (4 bytes)
        struct.pack('<I', cluster_inicial) +  # Cluster inicial (4 bytes)
        fecha_actual.encode('ascii')[:14] +  # Fecha de creación (14 bytes)
        fecha_actual.encode('ascii')[:14] +  # Fecha de última modificación (14 bytes)
        b'\x00' * 12  # Espacio no utilizado (12 bytes)
    )

    # Escribe la entrada en el directorio, ajustando la posición según el sistema de archivos
    posicion_directorio = 1024
    sistemaArchivos.seek(posicion_directorio)
    sistemaArchivos.write(entrada_directorio)

    # Escribe el contenido del archivo en el cluster inicial
    sistemaArchivos.seek(cluster_inicial * tamanoClusters)
    sistemaArchivos.write(contenido)

    print(f"Archivo '{nombreArchivo.strip()}' de {tamanoArchivo} bytes copiado exitosamente en el cluster {cluster_inicial}.")

# Función mostrarInfo:
# Imprime información básica del sistema de archivos, como nombre, ID, versión y configuración de clusters.
def mostrarInfo():
    print("\nNombre del sistema de archivos: ", nombre_sistemaArchivos)
    print("Identificación del sistema de archivos: ", id_sistemaArchivos)
    print("Versión de la implementación: ", version)
    print("Etiqueta del volumen: ", etiqueta)
    print("Tamaño de un cluster: ", tamanoClusters)
    print("Número de clusters que mide el directorio: ", numeroClusters)
    print("Número de clusters que mide la unidad completa: ", numeroClustersUnidad)
    print("")

# Función datos:
# Lee los datos de configuración del sistema de archivos desde el archivo de sistema y los almacena en variables globales.
def datos():
    global id_sistemaArchivos, version, etiqueta, tamanoClusters, numeroClusters, numeroClustersUnidad, tamanoDirectorio

    # Lee y almacena el ID del sistema de archivos (8 bytes desde posición 0)
    id_sistemaArchivos = leerDatosASCII(0, 8)
    print(f"ID del sistema de archivos: {id_sistemaArchivos}")  # Para depuración

    # Lee y almacena la versión del sistema de archivos (4 bytes desde posición 10)
    version = leerDatosASCII(10, 4)
    print(f"Versión del sistema de archivos: {version}")  # Para depuración

    # Lee y almacena la etiqueta del volumen (19 bytes desde posición 20)
    etiqueta = leerDatosASCII(20, 19)
    print(f"Etiqueta del volumen: {etiqueta}")  # Para depuración

    # Lee y almacena el tamaño de un cluster (4 bytes desde posición 40)
    tamanoClusters = datoUnpack(40, 4)
    print(f"Tamaño de cada cluster: {tamanoClusters} bytes")  # Para depuración

    # Lee y almacena el número de clusters del directorio (4 bytes desde posición 45)
    numeroClusters = datoUnpack(45, 4)
    print(f"Número de clusters del directorio: {numeroClusters}")  # Para depuración

    # Lee y almacena el número de clusters de la unidad completa (4 bytes desde posición 50)
    numeroClustersUnidad = datoUnpack(50, 4)
    print(f"Número de clusters de la unidad completa: {numeroClustersUnidad}")  # Para depuración

    # Establece el tamaño del directorio de manera fija en 64 bytes por entrada
    tamanoDirectorio = 64


# Función verificarArchivo:
# Busca un archivo por nombre en el directorio cargado en archivosDir.
# Devuelve la posición del archivo y True si se encuentra, de lo contrario -1 y False.
def verificarArchivo(nombreCopia):
    nombreCopia = nombreCopia.strip()  # Elimina espacios alrededor del nombre
    print(f"Buscando archivo: '{nombreCopia}'")  # Para depuración
    for i, archivo in enumerate(archivosDir):
        nombre_archivo = archivo.nombre.strip()
        print(f"Comparando con: '{nombre_archivo}'")  # Para depuración
        if nombre_archivo == nombreCopia:
            return i, True
    return -1, False  # Retorna -1 si el archivo no se encuentra


# Función cargar_directorio:
# Lee todas las entradas del directorio, ignora las eliminadas y las carga en archivosDir.
def cargar_directorio():
    global archivosDir
    archivosDir = []
    for i in range(64):  # Asume que el directorio tiene un máximo de 64 entradas
        archivo = leerDatosArchivo(i)
        # Solo agrega archivos que no son None ni están marcados como eliminados
        if archivo:
            archivosDir.append(archivo)


# Función borrar_archivo:
# Permite al usuario seleccionar y eliminar un archivo del sistema de archivos.
def borrar_archivo():
    with fs_lock:  # Bloqueo para garantizar seguridad en acceso concurrente
        global sistemaArchivos, archivosDir

        cargar_directorio()  # Cargar el directorio actualizado
        archivos_ocupados = [(idx, archivo) for idx, archivo in enumerate(archivosDir) if archivo.tamano > 0]

        # Si no hay archivos, se notifica y se sale de la función
        if not archivos_ocupados:
            operaciones_queue.put("No hay archivos ocupados en el sistema")
            return

        # Mostrar lista de archivos disponibles para eliminar
        print("Seleccione el archivo que desea eliminar:")
        for idx, archivo in archivos_ocupados:
            print(f"{idx}: {archivo.nombre.strip()} ({archivo.tamano} bytes)")

        # Obtener índice del archivo a eliminar; manejar entradas no válidas
        try:
            indexArchivo = int(input("Ingrese el número del archivo que desea eliminar: "))
            if indexArchivo not in [idx for idx, _ in archivos_ocupados]:
                operaciones_queue.put("Error: Número de archivo inválido")
                return
        except ValueError:
            operaciones_queue.put("Error: Entrada inválida")
            return

        archivo_a_eliminar = archivosDir[indexArchivo]
        confirmacion = input(f"¿Está seguro que desea eliminar '{archivo_a_eliminar.nombre.strip()}'? (s/n): ")
        
        if confirmacion.lower() == 's':
            # Marcar la entrada en el directorio como eliminada
            inicio_directorio = 1024 + indexArchivo * 64
            sistemaArchivos.seek(inicio_directorio)
            sistemaArchivos.write(b"#" * 64)  # Marcar toda la entrada con '#'
            
            # Limpiar el contenido del archivo en el área de datos
            inicio_datos = archivo_a_eliminar.clusterInicial * tamanoClusters
            sistemaArchivos.seek(inicio_datos)
            for i in range((archivo_a_eliminar.tamano + tamanoClusters - 1) // tamanoClusters):
                sistemaArchivos.write(b'\x00' * tamanoClusters)  # Sobreescribe con ceros
            
            sistemaArchivos.flush()  # Forzar escritura en disco

            cargar_directorio()  # Recargar directorio para reflejar cambios
            operaciones_queue.put(f"Archivo '{archivo_a_eliminar.nombre.strip()}' eliminado exitosamente")
            sync_event.wait()  # Esperar confirmación
        else:
            operaciones_queue.put("Operación de eliminación cancelada")

# Función principal main:
# Inicializa el sistema de archivos, arranca el monitor y muestra la terminal de comandos.
def main():
    try:
        # Inicia el hilo de monitoreo en segundo plano
        monitor_thread = threading.Thread(target=monitor_sistema, daemon=True)
        monitor_thread.start()
        
        # Registra el inicio del sistema
        operaciones_queue.put("Sistema de archivos iniciado")
        sync_event.wait()
        
        mostrar_terminal()  # Muestra la terminal interactiva
    except Exception as e:
        print(f"Error en el sistema: {e}")
    finally:
        # Cierra el sistema de archivos y registra el cierre
        operaciones_queue.put("Sistema de archivos cerrado")
        time.sleep(0.5)  # Permite registrar el último mensaje antes de cerrar
        sistemaArchivos.close()

# Función listar_contenido:
# Muestra todos los archivos válidos en el directorio, excluyendo entradas corruptas o inválidas.
def listar_contenido():
    global tamanoClusters, numeroClusters, tamanoDirectorio, archivosDir
    
    archivosDir = []
    
    print("\033[1m   Nombre\t\tTamaño   \033[0m")
    
    # Itera sobre el directorio y lista archivos válidos
    for i in range(int((tamanoClusters * numeroClusters) / tamanoDirectorio)):
        aux = leerDatosArchivo(i)
        if aux and aux.tamano > 0 and aux.nombre.isprintable():
            # Filtra entradas con tamaños no razonables
            if aux.tamano < (tamanoClusters * numeroClustersUnidad):
                print(f"   {aux.nombre}\t{aux.tamano} bytes")
                archivosDir.append(aux)
            else:
                print(f"Entrada en posición {i} es inválida y será omitida.")

# Función desfragmentarSistema:
# Reorganiza los archivos en el sistema de archivos para eliminar espacios vacíos entre ellos y optimizar el espacio.
def desfragmentarSistema():
    global archivosDir, tamanoClusters, sistemaArchivos

    # Ordenar archivos por cluster inicial para facilitar la desfragmentación
    archivosDir.sort(key=lambda x: x.clusterInicial)

    # Iterar sobre los archivos y moverlos para que queden contiguos si hay espacio vacío
    for i in range(len(archivosDir) - 1):
        # Verificar si el archivo actual y el siguiente no están contiguos
        if archivosDir[i].clusterInicial + (archivosDir[i].tamano + tamanoClusters - 1) // tamanoClusters < archivosDir[i + 1].clusterInicial:
            # Leer el archivo en una posición más lejana y moverlo a un espacio contiguo al archivo anterior
            inicio_lectura = archivosDir[i + 1].clusterInicial * tamanoClusters
            sistemaArchivos.seek(inicio_lectura)
            datos_archivo = sistemaArchivos.read(archivosDir[i + 1].tamano)

            # Escribir el archivo en la nueva posición contigua
            inicio_escritura = (archivosDir[i].clusterInicial + (archivosDir[i].tamano + tamanoClusters - 1) // tamanoClusters) * tamanoClusters
            sistemaArchivos.seek(inicio_escritura)
            sistemaArchivos.write(datos_archivo)

            # Actualizar la posición del archivo movido en la lista de archivos
            archivosDir[i + 1].clusterInicial = inicio_escritura // tamanoClusters

    # Recargar el directorio para reflejar los cambios después de la desfragmentación
    archivosDir = []
    listar_contenido()

    print("Sistema de archivos desfragmentado con éxito")

# Función comando_ayuda:
# Muestra una lista de comandos disponibles para ayudar al usuario.
def comando_ayuda():
    print("======================= Available commands | Comandos disponibles =======================")
    print("  -> ls | dir:\t\t\tList files | Lista Archivos\t\t")
    print("  -> cp:\t\t  Copy files to pc | Copia Archivos a la pc\t")
    print("  -> cpp:\t      Copy files to system | Copia Archivos al sistema\t")
    print("  -> rm:\t\t      Remove files | Elimina Archivos\t")
    print("  -> cls | clear:\t      Clean screen | Limpiar pantalla\t")
    print("  -> df:\t      Disk defragmentation | Desfragmentación disco\t")
    print("  -> info:\t\t  Disk information | Información del disco\t")
    print("")

# Función mostrar_terminal:
# Emula una terminal de comandos en la que el usuario puede ingresar comandos interactivos para gestionar archivos.
def mostrar_terminal():
    datos()  # Cargar datos iniciales del sistema de archivos
    nombre_usuario = os.getlogin()  
    nombre_computadora = os.uname().nodename if hasattr(os, "uname") else os.getenv("COMPUTERNAME")
    
    ruta_terminal = f"C:\\MicroSistema\\{nombre_usuario}>"  # Ruta inicial de la terminal
    
    while True:
        print("Ingresa 'ayuda' o 'help' para conocer los que estan disponibles")
        comando = input(f"{ruta_terminal} ").strip()
        
        if not comando:  # Ignorar comandos vacíos
            continue

        partes = comando.split()
        
        if len(partes) == 0:  # Verificar que el comando tiene contenido
            continue

        # Comandos básicos de ayuda y salida
        if partes[0].lower() in ("help", "ayuda"):
            comando_ayuda()
        
        elif partes[0].lower() in ("exit", "salir"):
            break

        # Limpiar la pantalla
        elif partes[0].lower() in ("cls", "clear"):
            limpiar_terminal()

        # Listar contenido del sistema de archivos
        elif partes[0].lower() in ("ls", "dir"):
            listar_contenido()

        # Desfragmentar el sistema de archivos
        elif partes[0].lower() in ("df"):
            desfragmentarSistema()
        
        # Mostrar información del sistema de archivos
        elif partes[0].lower() in ("info"):
            mostrarInfo()

        # Copiar archivo desde el sistema de archivos a la computadora
        elif partes[0].lower() == "cp":
            nombreCopia = input("Ingresa el nombre del archivo que deseas copiar (incluye la extensión): ")
            rutaCopiar = os.path.dirname(os.path.abspath(__file__))
            copiar_a_sistema(nombreCopia, rutaCopiar)

        # Copiar archivo desde la computadora al sistema de archivos
        elif partes[0].lower() == "cpp":
            copiar_de_sistema_fragmentado()
        
        # Eliminar un archivo del sistema de archivos
        elif partes[0].lower() == "rm":
            borrar_archivo()

        # Comando inválido
        else:
            print("Comando no valido, ingresa 'ayuda' o 'help' para conocer los comandos disponibles")

# Función limpiar_terminal:
# Limpia la pantalla de la terminal dependiendo del sistema operativo.
def limpiar_terminal():
    if os.name == 'nt':  # Comando para Windows
        os.system('cls')
    else:  # Comando para Linux y MacOS
        os.system('clear')
# Llamada a la función principal para iniciar el sistema
main()
