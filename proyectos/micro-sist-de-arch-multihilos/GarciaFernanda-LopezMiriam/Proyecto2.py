import os
import struct
import datetime
import shutil 
from threading import Thread, Barrier


# Variables globales a utilizar en la configuracion del sistema de archivos y el control del flujo 
TAMANO_ARCHIVO_ESPERADO = 1440 * 1024  # Tmaño esperado del archivo en bytes, se espera que sea de 1440 KB
dir_fis = "" # Directorio fisico del archivo FiUnamFS
ruta_FiUnamFS = "" # Ruta de FiUnamFS
volumen = "" # Etiqueta de volumen 
cluster_set = set() # Clusters disponibles 
clusters_dir = 0 # Clusters del directorio 
clusters_uncomp = 0 # Clusters de la unidad Completos
tam_cluster = 0 #Tamaño de los clusters en bytes 
directorio = [] # Lista de los archivos del sistema FiUnamFS
menu = 0
barrier = Barrier(3) # Se hace uso de Barrier que es una clase de threading definida en Python utilizada para la sincronización de los tres hilos usados
cluster_inicial = -1 #Iniciacion del cluster 
tam_bytes = 0 # Variable para almacenar el tamaño de los archivos que se manejarán más adelante
espacio_suficiente = False # Variable booleana para indicar si hay sufiente espacio dentro de FiUNAMFS
nom_disp = False # Variable booleana para indicar si el nombre de un archivo se encuentra disponible para ser manejado 

# Clase utilizada para represntar la información de un archivo dentro del sistema FiUnamFs
class informacion_archivo:
    def __init__(self, nombre_archivo, tam_bytes, cluster_inicial, creacion, modificacion, pos):
        #Se establecen los valores inciiales de los atributos de los archivos 
        self.nombre_archivo = nombre_archivo
        self.tam_bytes = tam_bytes
        self.cluster_inicial = cluster_inicial
        self.creacion = creacion #Fecha de creacion del archivo 
        self.modificacion = modificacion #Fecha de modificacion del archivo
        self.pos = pos # Posición del archivo en el directorio

# Funciones para imprirmir texto en diferentes colores 
def prRed(mensaje): print("\033[91m {}\033[00m" .format(mensaje))
def prPurple(mensaje): print("\033[95m {}\033[00m" .format(mensaje))  # Morado
def prPink(mensaje): print("\033[95m {}\033[00m" .format(mensaje))   # Rosa
def prBlue(mensaje): print("\033[94m {}\033[00m" .format(mensaje))   # Azul
# Función que muestra un menú con el que el usuario puede interactuar para elegir lo que desea realizar 
def mostrar_menu():
    # Obtener el ancho de la terminal para centrar el texto
    terminal_width = shutil.get_terminal_size().columns
    menu_opc = "***MENÚ DE OPCIONES***"
    menu_centrado = menu_opc.center(terminal_width)

    # Impresión del texto centrado
    prPink(menu_centrado)
    print()
    print("Ingrese la opción de la acción a realizar:")
    print("1. Listar el contenido del FiUnamFS")
    print("2. Copiar un archivo de dentro del FiUnamFS hacia tu sistema")
    print("3. Copiar un archivo de tu computadora hacia tu sistema FiUnamFS")
    print("4. Eliminar un archivo del FiUnamFS")
    print("5. Salir del sistema...")
    print()
    while True:
        entrada_usuario= input("Selecciona la opción que deseas ejecutar: ")
        if entrada_usuario.isdigit():
            opcion = int(entrada_usuario)
            if 1 <= opcion <= 5:
                return opcion
            else:
                prRedprint("Lo sentimos, esa opción no es válida. Elige entre 1 - 5")
        else:
            print("Entrada no válida. Debes ingresar un número entre 1-5")
# Funcion para verificar la existencia del archivo fiunamfs.img 
def directorio_FiUnamFS():
    global dir_fis
    global ruta_FiUnamFS
    dir_fis = os.path.dirname(os.path.abspath(__file__)) # Se obtiene la ruta del archivo 
    ruta_FiUnamFS = os.path.join(dir_fis, "fiunamfs.img")  # Se verifica la existencia del archivo fiunam.fs 
    #Si no existe, se ejecuta este if donde se le pide al usuario ingresar el nombre de otro archivo que corresponda 
    if not os.path.exists(ruta_FiUnamFS):
        while True:
            try:
                print("Ingrese el nombre del archivo FiUnamFS: ")
                entrada_usuario = input() 
                # Construir la ruta completa
                ruta_FiUnamFS = os.path.join(dir_fis, entrada_usuario) #Se hace la ruta del archivo que ingreso el usuario 
                
                if os.path.exists(ruta_FiUnamFS): #Para verificar si el archivo existe o no 
                    return True
                else:
                    prRedprint("UPS!!! El archivo no existe. Vuelve a intentarlo")
            except PermissionError: # Se hace uso de esta excepción en caso de que el archivo si exista pero el usario no cuente con los permisos necesarios para acceder a él
                prRedprint("UPS!!!, No tienes los permisos necesarios para acceder al archivo!")
                return False
    return True

def abrir_archivo(mode, posicion=None): # Función para abrir un archivo en la ruta global ruta_FiUnamFS, de manera opcional puede moverse a una posición especifica dentro del archivo 
    global ruta_FiUnamFS
    try:
        f = open(ruta_FiUnamFS, mode)
        if posicion is not None:
            f.seek(posicion) # para mover el puntero en la posición especifica en el archivo 
        return f  # No se hace uso de 'with'  para que el archivo no se cierre prematuramente
    except PermissionError:
        prRedprint("Lo sentimos, no tienes los permisos necesarios para acceder al archivo o directorio especificado.")
        return None

def leer_numero(posicion): # Función que lee un número de 4 bytes en formato little-endian desde una posicion especifica del archivo 
    f = abrir_archivo("rb", posicion) # Se llama abrir_archivo para que el archivo sea abierto en modo de lectura binaria 'rb' y se coloca en una posicion especifica 
    if f:
        numero = struct.unpack('<I', f.read(4))[0] # Para convertir los 4 bytes leídos desde el archivo en un número entero en formato little-endian
        f.close()  # Cerramos el archivo después de leer
        return numero
    return False

def escribir_numero(posicion, numero): #Función que escribe un numero de 4 bytes en formato little-endian en una posicion dentro del archivo 
    f = abrir_archivo("r+b", posicion)
    if f:
        f.write(struct.pack('<I', numero)) # Convierte el número en una secuencia de 4 bytes en formato little-endian, con f.write se escriben esos bytes en el archivo, a partir de la posicion especificada 
        return True
    return False

def leer_ascii8(posicion, longitud): # Función que lee una cadena de caracteres en formato ASCII 8-bit desde una posicion especifica del archivo 
    f = abrir_archivo("rb", posicion)
    if f:
        data = f.read(longitud).decode('latin-1') # Si el archivo abre correctamente se usa f.read(longitud) para leer una cantidad especifica de bytes (longitud) y decode(latin-1) convierte los bytes leirods en una cadena de caracteres 
        f.close()  # Cerramos el archivo después de leer
        return data
    return False

def escribir_ascii8(posicion, cadena): #Función que escribe una cadena de caracteres en formato ASCII 8-bit 
    f = abrir_archivo("r+b", posicion)
    if f:
        f.write(bytearray(cadena, 'latin-1')) # Si el archivo se abre correctamente, bytearray() convierte la cadena en un arreglo de bytes haciendo uso de latin-1
        return True
    return False


def leer_ascii7(posicion, longitud): # Función para leer cadenas de caracteres en formato ASCII 7-bit
    f = abrir_archivo("rb", posicion)
    if f:
        data = f.read(longitud).decode('ascii') # Si el archivo se abre correctamente, f.read() lee longitud bytes a partir de la posicion especificada, decode(Ascii) convierte estos bytes en una cadena de caracteres en ASCII 7-bit
        f.close()  # Cerramos el archivo después de leer
        return data
    return False


def escribir_ascii7(posicion, cadena): # Función que  escribe  cadenas de caracteres en formato ASCII 7-bit
    f = abrir_archivo("r+b", posicion)
    if f:
        f.write(bytearray(cadena, 'ascii')) # Se convierte la cadena en unarreglo de bytes en formato ASCII 7-bit 
        return True
    return False
# Función para validar el tamaño sistema de archivos FiUnamFS en base al superbloque
def tam_FiUnamFS():
    #Declaracion de variables que se usaran para almacenar valores especificos del sistema de archivos 
    global ruta_FiUnamFS
    global volumen
    global tam_cluster
    global clusters_dir
    global clusters_uncomp
    
    # Verificar si el archivo cumple con un tamaño especifico de  1440 Kilobytes
    try:
        if os.path.getsize(ruta_FiUnamFS) != TAMANO_ARCHIVO_ESPERADO:
            print(f"El archivo no es del tamaño correcto.")
            return False
    except PermissionError:
        print("UPS!!!, No tienes los permisos necesarios para acceder al archivo!")
        return False

    # Se comprueba que el nombre del sistema de archivos sea FiUnamFS
    nombre_FiUnamFS = leer_ascii8(0, 8)  # Leer el nombre usando ASCII 8-bit
    if nombre_FiUnamFS != "FiUnamFS":
        print(f"Uyyy!!! hubo un error, el nombre del sistema de archivos debería ser 'FiUnamFS', pero se obtuvo '{nombre_FiUnamFS}'.")
        return False

    # Se comprueba que la versión del sistema de archivos FiUNAMFS sea 25-1 en este caso 
    version_FiUnamFS = leer_ascii8(10, 4)  # Leer la versión usando ASCII 8-bit
    if version_FiUnamFS != "25-1":
        print(f"Versión incorrecta, la versión del sistema de archivos debería ser '25-1'")
        return False

    # Obtener la etiqueta del volumen, tamaño de los clusters y de los demás parámetros del superbloque
    volumen = leer_ascii7(20, 19)  # Leer la etiqueta del volumen usando ASCII 7-bit
    tam_cluster = leer_numero(40)  # Leer el tamaño del cluster en bytes
    clusters_dir = leer_numero(45)  # Leer el número de clusters para el directorio
    clusters_uncomp = leer_numero(50)  # Leer el número total de clusters

   
    if not volumen or tam_cluster <= 0 or clusters_dir <= 0 or clusters_uncomp <= 0: # Se verifica que volumen no este vacio y que tam_cluster, clusters_dir, clusters_uncomp sean valores positivos, para asegurar que los valores léidos sean válidos 
        print("Algunos de los parámetros del superbloque no son válidos.")
        return False
    print()
    prRed("El Sistema de archivos FiUnamFS se ha cargado correctamente en tu ordenador :)")
    print()
    return True

# Funciones para dar formato a las fechas
def formato_fecha(fecha):
   
    return fecha.strftime("%Y%m%d%H%M%S") #  Convierte un objeto datetime a una cadena con el formato: 'YYYYMMDDHHMMSS'.

def imp_fecha(fecha):
   
    # Asegurarse de que la fecha tenga la longitud adecuada (14 caracteres)
    if len(fecha) == 14:
        return f"{fecha[:4]}-{fecha[4:6]}-{fecha[6:8]} {fecha[8:10]}:{fecha[10:12]}:{fecha[12:14]}" # Convierte una fecha en formato 'YYYYMMDDHHMMSS' a un formato más legible: 'YYYY-MM-DD HH:MM:SS'.

    else:
        return "Fecha inválida"  # En caso de que la fecha no tenga el formato esperado

# Función para imprimir la información de los archivos en el directorio de manera más legible
def imp_info_archivos(): # Función para imprimir la información de los archivos en una tabla de manera organizada
    global directorio

    # Definir los encabezados de la tabla y sus anchos de columna (se pueden ajustar para mayor separación)
    headers = ["Nombre del archivo", "Tamaño en bytes", "Cluster inicial", "Fecha de creación", "Fecha de modificación"]
    col_widths = [25, 20, 20, 25, 25]

    # Imprimir el encabezado con el ancho especificado para la terminal usada 
    header_row = "   ".join(f"{header:<{col_widths[i]}}" for i, header in enumerate(headers))
    print(header_row)
    print("=" * (sum(col_widths) + (len(headers) - 1) * 3))  # Línea separadora, elemento estetico del programa 

    # Imprimir cada archivo en una fila formateada
    for archivo in directorio:
        # Convertir las fechas en formato legible
        fecha_creacion = imp_fecha(archivo.creacion)
        fecha_modificacion = imp_fecha(archivo.modificacion)

        # Se formatea y muestra cada fila con los anchos de columna definidos
        row = "   ".join([
            f"{archivo.nombre_archivo:<{col_widths[0]}}",
            f"{archivo.tam_bytes:<{col_widths[1]}}",
            f"{archivo.cluster_inicial:<{col_widths[2]}}",
            f"{fecha_creacion:<{col_widths[3]}}",
            f"{fecha_modificacion:<{col_widths[4]}}"
        ])
        print(row)


def leer_dir(show=True): # Función que lee el contenido del directorio en el sistema FiUnamFs, recopila informacion de los archivos y actualiza un conjunto de clusters disponibles 
    global ruta_FiUnamFS
    global tam_cluster
    global clusters_dir
    global directorio
    global cluster_set

   
    clusters_ocupados = set(range(clusters_dir + 1, clusters_uncomp))  # Se crea un conjunto de clusters disponibles que representan las unidades de almacenamiento que pueden usarse para el almacenamiento de archivos 

    directorio = [] #Lista vacía del directorio 

    for pos in range(tam_cluster, tam_cluster * (clusters_dir + 1), 64): # Se recorre el area de almacenamiento donde estan los archivos (va de 64 en 64 bytes)
        tipo_archivo = leer_ascii8(pos, 1) #Primera posición del registro de 64 bytes 
        
        if tipo_archivo == "-": # Archivo válido
            nombre_archivo = leer_ascii7(pos + 1, 15).replace("#", "")  # Se limpia el nombre
            # Aseguramos que el nombre tenga una extensión válida de 3 caracteres
            dot_pos = nombre_archivo.find(".")
            nombre_archivo = nombre_archivo[:dot_pos] + "." + nombre_archivo[dot_pos+1:dot_pos+4]

            tam_bytes = leer_numero(pos + 16) #leer el tamaño del archivo en bytes desde la posicion especificada 
            cluster_inicial = leer_numero(pos + 20) # Se obtiene el prier cluster ocupado por el archivo 
            #Se obtienen las fehcas de creacion y modificacion de los archivos 
            creacion = leer_ascii8(pos + 24, 14)
            modificacion = leer_ascii8(pos + 38, 14)

            archivo = informacion_archivo(nombre_archivo, tam_bytes, cluster_inicial, creacion, modificacion, pos) #Se crea un objeto informacion_archivo
            directorio.append(archivo)

            for cluster in range(cluster_inicial, cluster_inicial + ((tam_bytes + tam_cluster - 1) // tam_cluster)): #Para cada archivo se calcula el rango de clusters ocupados usando tam_bytes y tam_cluster 
                clusters_ocupados.discard(cluster) # Los clusters ocupados por el archivo se eliminan del conjunto con ayuda de discard 
    
    if show:
        imp_info_archivos()


# Función para buscar un archivo en el directorio por su nombre
def buscar_archivo(nombre_archivo):
    global directorio
    for archivo in directorio:
        if archivo.nombre_archivo == nombre_archivo:
            return archivo
    return None

# Función para copiar un archivo de FiUnamFS hacia el sistema de archivos propio de cada usuario

def fiunamfs_a_sistp(nombre_archivo, ruta_local): # Recibe el nombre del archivo que se encuentra en FiUnamFS y la ruta donde el usuario quiere guardarlo en su propio sistema 
    archivo = buscar_archivo(nombre_archivo) # Para obtener la informacion dentro del FiUnamFs
    if archivo is None:
        print("El archivo que deseas manejar no existe.")
        return False
    cluster_actual = archivo.cluster_inicial #Se almacena el numero del primer cluster donde se encuentra el archivo en FiUnamFS
    tam_bytes = archivo.tam_bytes #Se almacena el tamaño del archivo en bytes 
    archivo_local = os.path.join(dir_fis, ruta_local) # Se construye la ruta local del archivo usando dir_fis(directorio actual) y ruta_local(ruta de destino)
    try:
        with open(ruta_FiUnamFS, "rb") as f: #Abre el archivo de imagen del sistema de archivos FiUnamFs en lectura binario
            f.seek(cluster_actual * tam_cluster)
            info = f.read(tam_bytes) # Lee el archivo completo en una sola operacion y se almacena el contenido en info
        with open(archivo_local, "wb") as f: # Abre o crea un archivo en la ruta archivo:local en modo binario 
            f.write(info) # Escribe su contenido en el archivo local del usuario 
        return True
    except PermissionError:
        print("UPS!!!, No tienes los permisos necesarios para acceder al archivo o directorio especificado.")
        return False


# Función para encontrar un cluster contiguo de tamaño suficiente para almacenar un archivo de tamaño tam_bytes
def encontrar_cluster(tam_bytes):
    global cluster_set
    contiguo = -1 # Para almacenar el índice del primer cluster disponible para almacenar el archivo si se encuentra un espacio contiguo 
    contiguo_actual = 0 #Para contar cuantos clusters contiguos disponibles se han econtrado 
    for cluster in cluster_set:
        contiguo_actual += 1 #Recorre cada cluster disponible 
        if contiguo_actual == (tam_bytes+tam_cluster-1) // tam_cluster: # Si contiguo_actual alcanza el valor de clusters necesario, se considera que hay espacio suficiente 
            contiguo = cluster - contiguo_actual + 1
            break
    return contiguo


def verificar_tam_bytes(ruta_local): # Función que verifica si hay suficiente espacio en FiUnamFs para almacenar un archivo externo
    global directorio
    global cluster_set
    global cluster_inicial
    global tam_bytes
    global espacio_suficiente

    tam_bytes = os.path.getsize(os.path.join(dir_fis, ruta_local)) #Se calcula el tamaño del archivo local 

    if tam_bytes > tam_cluster * len(cluster_set): #Usado para comprobar si el tamaño del archivo excede la capacidad total de FiUnamFS, espera a otros hilos con Barrier.wait () y termina la funcion
        print("Tu archivo es muy grande y no se puede almacenar en FiUnamFS.")
        espacio_suficiente = False
        barrier.wait()
        return
   
    cluster_inicial = encontrar_cluster(tam_bytes) #Para localizar clusters contiguos para el archivo
    if cluster_inicial == -1:
        print("No hay suficiente espacio en FiUnamFS.")
        espacio_suficiente = False
        barrier.wait()
        return
    espacio_suficiente = True #Si se encuentran clusters suficientes 
    barrier.wait()

def buscar_archivo(nombre_archivo): #Busca si existe un archivo con el nombre especificado en el sistema de archivos 
    global nom_disp
    archivo = next((archivo for archivo in directorio if archivo.nombre_archivo == nombre_archivo), None)
    
    if archivo:
        print("Ya existe un archivo con ese nombre.")
        nom_disp = False
    else:
        nom_disp = True
    
    barrier.wait()



def sistp_a_fiunamfs(ruta_local, nombre_archivo):# Función que permite copiar un archivo del sistema personal de cada usuario hacia FiUnamFS
    #Se crean dos hilos para verificar el tamaño der archivo y buscar archivos duplicados 
    comprobar_hilo = Thread(target=verificar_tam_bytes, args=(ruta_local,)) 
    buscar_hilo = Thread(target=buscar_archivo, args=(nombre_archivo,))
    #Se inicializan los hilos y esperan su terminacion 
    comprobar_hilo.start()
    buscar_hilo.start()
    barrier.wait()
    
    #Si no hay suficiente espacio o el nombre no etsa disponible, termina la función con false
    if not espacio_suficiente or not nom_disp:
        return False
    
    #Abre el archivo FiUnamFs en modo binario, lee el archivo local y escribe sus datps en la posicion del cluster_incial 
    try:
        with open(ruta_FiUnamFS, "r+b") as f, open(os.path.join(dir_fis, ruta_local), "rb") as f_local:
            f.seek(cluster_inicial * tam_cluster)
            f.write(f_local.read())
        
        # Descarta los clusters utilizados para el archivo desde cluster_set 
        for i in range(cluster_inicial, cluster_inicial + (tam_bytes // tam_cluster)):
            cluster_set.discard(i)
        
        creacion = formato_fecha(datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(dir_fis, ruta_local))))
        modificacion = formato_fecha(datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(dir_fis, ruta_local))))
        
        #Busca un registro libre "/" en el directorio y actualiza la entrada para el archivo
        for pos in range(tam_cluster, tam_cluster * (clusters_dir + 1), 64):
            if leer_ascii8(pos, 1) == "/":
                escribir_ascii8(pos, "-")
                escribir_ascii7(pos + 1, nombre_archivo)
                escribir_numero(pos + 16, tam_bytes)
                escribir_numero(pos + 20, cluster_inicial)
                escribir_ascii8(pos + 24, creacion)
                escribir_ascii8(pos + 38, modificacion)
                break
        
        leer_dir(False)
        return True
    except PermissionError:
        print("Lo sentimos, no cuentas con los permisos necesarios para acceder al archivo.")
        return False


def eliminar_archivo(nombre_archivo): # Función para eliminar un archivo de FiUnamFs
    archivo = buscar_archivo(nombre_archivo)
    if not archivo:
        print("Este archivo no existe.")
        return False
    
    print("El arhcivo seleccionando esta en proceso de ser borrado del sistema. Espere un minuto...")
    escribir_ascii8(archivo.pos, "/")
    escribir_ascii7(archivo.pos + 1, "###############") # Borra el nombre del archivo en el directorio y lo reemplaza por una cadena de marcadores 
    leer_dir(False) # Llama esta función para actualizar la lista del directorio

# Función principal (Interfaz del programa)
def iniciar_sistema():
    print()
    prBlue("Usted ha podido ingresar al sistema de archivos FiUnamFS, ahora se le presentarán las acciones que puede realizar a su sistema, continue...")
    print()
    prPurple("*************************************************************************************")
    directorio_FiUnamFS()
    tam_FiUnamFS()

def ejecutar_opcion(opcion):
    if opcion == 1:
        leer_dir()
    elif opcion == 2:
        nombre_archivo = input("Ingrese el nombre del archivo que desea copiar: ")
        ruta_local = input("Ingrese el nombre o la ruta donde desea guardar el archivo: ")
        fiunamfs_a_sistp(nombre_archivo, ruta_local)
    elif opcion == 3:
        ruta_local = input("Ingrese el nombre o la ruta del archivo que desea copiar: ")
        nombre_archivo = input("Ingrese el nombre del archivo en FiUnamFS: ")
        sistp_a_fiunamfs(ruta_local, nombre_archivo)
    elif opcion == 4:
        nombre_archivo = input("Ingrese el nombre del archivo que desea eliminar: ")
        eliminar_archivo(nombre_archivo)

def main():
    global menu
    iniciar_sistema()
    while menu != 5:
        menu = mostrar_menu()
        ejecutar_opcion(menu)
    print("Saliendo del programa...")

if __name__ == "__main__":
    main()

