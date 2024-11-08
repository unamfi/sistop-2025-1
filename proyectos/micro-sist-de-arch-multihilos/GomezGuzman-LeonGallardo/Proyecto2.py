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