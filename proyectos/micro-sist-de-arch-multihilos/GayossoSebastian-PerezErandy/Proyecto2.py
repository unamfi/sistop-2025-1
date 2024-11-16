import struct
import os
import time
import datetime
import math

print("Gayosso Rosillo Sebastian Emiliano y Perez Delgado Erandy Estefanya\n")

NOMBRE_IMAGEN = "fiunamfs.img"
archivos=[]
mapaAlmacenamiento = []
imagen = open(NOMBRE_IMAGEN,"br+")

#Metodos para leer y escribir dentro de archivos, codificando o decodificando con el formato indicado (valores de 32 bits, en formato little endian)
def sacaDatos(inicio, tamanio):
    global imagen
    imagen.seek(inicio)
    return imagen.read(tamanio)
def sacaDatosAscii(inicio, tamanio):
    global imagen
    imagen.seek(inicio)
    return imagen.read(tamanio).decode("ascii")
def datoUnpack(inicio, tamanio):
    global imagen
    imagen.seek(inicio)
    dato = imagen.read(tamanio)
    return struct.unpack('<i', dato)[0]
def meteDatosAscii(inicio, dato):
    global imagen
    imagen.seek(inicio)
    dato = dato.encode("ascii")
    return imagen.write(dato)
def meteDatoPack(inicio, dato):
    global imagen
    imagen.seek(inicio)
    dato = struct.pack('<i', dato)
    return imagen.write(dato)

tamanioCluster= datoUnpack(40,4) #Da 1024
clustersDirectorio = datoUnpack(45,4) #Da 4
clustersUnidad = datoUnpack(50,4) #Da 720
tamanioDirectorio = 64
#Almacena informacion basica de un archivo
class archivo:
    global tamanioCluster
    def __init__(self, nombre, tamanio, clusterInicial, fechaCreacion, fechaModificacion):
        self.nombre = nombre.replace(" ","")
        self.tamanio = tamanio
        self.clusterInicial = clusterInicial
        self.fechaCreacion = fechaCreacion
        self.fechaModificacion = fechaModificacion
        self.numClusters = math.ceil(tamanio/tamanioCluster)

#Obtiene los datos del archivo desde el directorio, creando un objeto de tipo archivo
def sacaDatosArchivo(posicion):
    inicial = 1024 + (posicion * 64)
    if(sacaDatosAscii(inicial+1,14) != "--------------"):
        nombre = sacaDatosAscii(inicial+1, 14)
        tamanio = datoUnpack(inicial+16, 4)
        clusterInicial = datoUnpack(inicial+20,4)
        fechaCreacion = sacaDatosAscii(inicial+24, 14)
        fechaModificacion = sacaDatosAscii(inicial+38, 14)
        archivoAux = archivo(nombre, tamanio, clusterInicial, fechaCreacion, fechaModificacion)
        return archivoAux

#Inicializa la lista para del mapa de memoria
def iniciaMapa():
    global mapaAlmacenamiento
    for x in range(5):
        mapaAlmacenamiento.append(1)
    while (len(mapaAlmacenamiento) != 720):
        mapaAlmacenamiento.append(0)

#Actualiza la informacion en el mapa a partir de la lista de archivos 
def actualizaMapa():
    global mapaAlmacenamiento
    global archivos
    for x in range(720):
        mapaAlmacenamiento[x]=0
    for x in range(5):
        mapaAlmacenamiento[x]=1
    for archivoActual in archivos:
        aux = archivoActual.numClusters
        for j in range(aux):
            mapaAlmacenamiento[archivoActual.clusterInicial+j] = 1

#Inicializa la lista de archivos con los datos del directorio
def inicializaArchivos():
    global archivos
    numArchivos = int((tamanioCluster * clustersDirectorio)/tamanioDirectorio)
    for x in range(numArchivos):
        resultado = sacaDatosArchivo(x)
        if(resultado != None):
            archivos.append(resultado)
            actualizaMapa()

#Entrega el indice en el que se encuentra el archivo con el nombre indicado en la lista de archivos
#Devolveran -1 en caso de no encotrar el archivo
def buscaArchivoNombre(nombre):
    global archivos
    for x in archivos:
        if(x.nombre==nombre):
            return archivos.index(x)
    return -1

#Entrega el indice en el que se encuentra el archivo con el cluster inicial indicado en la lista de archivos
#Devolveran -1 en caso de no encotrar el archivo
def buscaArchivoClusterInicial(clusterInicial):
    global archivos
    for x in archivos:
        if(x.clusterInicial==clusterInicial):
            return archivos.index(x)
    return -1

#Método que enlista los contenidos del directorio
# Método que enlista los contenidos del directorio mostrando nombre, tamaño y fechas
def muestraDirectorio():
    global archivos
    print(f"{'Nombre':<20} {'Tamaño (bytes)':<15} {'Fecha de Creación':<20} {'Fecha de Modificación':<20}")
    print("-" * 80)  # Línea divisoria para mayor claridad
    for archivo in archivos:
        print(f"{archivo.nombre:<20} {archivo.tamanio:<15} {archivo.fechaCreacion:<20} {archivo.fechaModificacion:<20}")


#Método que copia un archivo desde el sistema de archivos a la computadora
def copiaArchivoAComputadora(nombreArchivo, ruta):
    global archivos
    global imagen
    desfragmentar()
    #busca si el nombre del archvo se encuentra en nuestro sistema de archivos.
    posicion = buscaArchivoNombre(nombreArchivo)
    if(posicion != -1):
        auxiliar = sacaDatos(archivos[posicion].clusterInicial*1024,archivos[posicion].tamanio)
        if(os.path.exists(ruta) and not os.path.exists(ruta+"/"+nombreArchivo)):
            print(f"{'Nombre':<20} {'Tamaño (bytes)':<15} {'Fecha de Creación':<20} {'Fecha de Modificación':<20}")
            print(f"El archivo '{nombreArchivo}' ha sido copiado existosamente.") 

            
            ArchivoNuevo = open(ruta+"/"+nombreArchivo, "bw")
            ArchivoNuevo.write(auxiliar)
            ArchivoNuevo.close()
        else:
            print("No se pudo copiar el archivo")
    else:
        print("No se pudo copiar el archivo")

def borraEnDirectorio(posicion):
    global imagen
    inicial = 1024 + (posicion * 64)
    imagen.seek(inicial)
    imagen.write(b'---------------'+b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'+b'0000000000000000000000000000'+b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

def borraEnDirectorio2(posicion):
    global imagen
    inicial = 1024 + (posicion * 64)
    imagen.seek(inicial)
    imagen.write(b'-              '+b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'+b'0000000000000000000000000000'+b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

#Método que borra un archivo de nuestro sistema de archivos
def borraArchivo(nombreArchivo, aux):
    global archivos
    for x in archivos:
        if(x.nombre==nombreArchivo):
            archivos.pop(archivos.index(x))
            actualizaMapa()
            for y in range(64):
                inicial = 1024 + (y * 64)
                nombre = sacaDatosAscii(inicial+1, 14).replace(" ","")
                print(nombre)
                if(nombre == nombreArchivo):
                    borraEnDirectorio(y)
                    print(f"El archivo '{nombreArchivo}' se ha eliminado correctamente del directorio.") 
                    return
                elif(aux==2):
                    return
    print("El archivo para borrar no existe")
    return

#Método que copia un archivo desde nuestra computadora a nuestro sistema de archivos.
def copiaArchivoAImagen(rutaOrigen):
    global archivos
    desfragmentar()
    # Verifica que el archivo exista, tenga un nombre válido y quepa en la imagen.
    if (os.path.exists(rutaOrigen) and 
        len(os.path.split(rutaOrigen)[-1].replace(" ", "")) < 15 and 
        os.stat(rutaOrigen).st_size < 732160):
        
        # Verifica si ya existe un archivo con el mismo nombre.
        if buscaArchivoNombre(os.path.split(rutaOrigen)[-1].replace(" ", "")) == -1:
            nombre = agregaEspacios(os.path.split(rutaOrigen)[-1])
            tamanio = os.stat(rutaOrigen).st_size
            clusterInicial = asignaCluster(tamanio)
            
            if clusterInicial == -1:
                print("No hay espacio disponible para almacenar el archivo.")
                return
            
            # Obtén las fechas de creación y modificación en formato AAAAMMDDHHMMSS.
            fechaCreacion = datetime.datetime.fromtimestamp(
                os.stat(rutaOrigen).st_ctime).strftime("%Y%m%d%H%M%S")
            fechaModificacion = datetime.datetime.fromtimestamp(
                os.stat(rutaOrigen).st_mtime).strftime("%Y%m%d%H%M%S")

            archivoAux = archivo(nombre, tamanio, clusterInicial, fechaCreacion, fechaModificacion)
            archivos.append(archivoAux)

            # Agrega al directorio y actualiza el mapa.
            if agregaADirectorio(archivoAux) == -1:
                return
            
            agregaArchivoAImagen(rutaOrigen, archivoAux)
            actualizaMapa()

            print(f"El archivo '{nombre.strip()}' fue copiado exitosamente.\n")
            print(f" {nombre.strip()}  Fecha de creación: {fechaCreacion}  Fecha de última modificación: {fechaModificacion}")
            
        else:
            print("Ya existe un archivo con el mismo nombre. Intente nuevamente.")


def agregaArchivoAImagen(rutaOrigen, archivoAux):
    global imagen
    Auxfile = open(rutaOrigen,"br")
    contenido = Auxfile.read()
    Auxfile.close()

    inicio=archivoAux.clusterInicial*tamanioCluster
    imagen.seek(inicio)
    imagen.write(contenido)

#Ingresa informacion de un archivo al directorio
def agregaADirectorio(archivoAux):
    for y in range(64):
        inicial = 1024 + (y * 64)
        if (sacaDatosAscii(inicial+1, 14)=="--------------"):
            borraEnDirectorio2(y)
            meteDatosAscii(inicial,"-")
            meteDatosAscii(inicial+1, archivoAux.nombre)
            meteDatoPack(inicial+16, archivoAux.tamanio)
            meteDatoPack(inicial+20, archivoAux.clusterInicial)
            meteDatosAscii(inicial+24, archivoAux.fechaCreacion)
            meteDatosAscii(inicial+38, archivoAux.fechaModificacion)
            return 1
    print("Ya no hay espacio en el directorio")
    borraArchivo(archivoAux.nombre, 2)
    return -1

#obteniene el cluster inicial en el cual puede almacenarce un archivo con el tamaño recibido como parametro dentro de la funcion dentro del mapa 
def asignaCluster(tam):
    global mapaAlmacenamiento
    try:
        clusterInicialPosible = mapaAlmacenamiento.index(0)
    except:
        print("Ya no hay espacio en el dipositivo para almacenar")
        return -1
    clustersDeArchivo = math.ceil(tam/tamanioCluster)
    if(clusterInicialPosible+clustersDeArchivo<720):
        return clusterInicialPosible
    else:
        return -1

#Agrega espacios para que la cadena sea de 14 bytes
def agregaEspacios(nombre):
    while(len(nombre) != 14):
        nombre = nombre + " "
    return nombre

# Comprime los archivos en la imagen del sistema
# busca espacios vacíos (ceros entre unos) en el mapa de almacenamiento y recorre los archivos
def desfragmentar():
    global archivos
    global imagen
    global mapaAlmacenamiento
    espacioLibre = 0
    posicionMapa = -1
    for x in mapaAlmacenamiento:
        posicionMapa += 1
        if x == 0:
            espacioLibre += 1
        elif x == 1 and espacioLibre != 0:
            # poner el archivo en su nuevo lugar de la imagen
            moverArchivoEnImagen(posicionMapa, espacioLibre)
            # actualizar su cluster inicial en archivos
            actualizarArchivos(posicionMapa, espacioLibre)
            # actualizar directorio
            actualizarDirectorio()
            espacioLibre = 0
    
    # Mensaje de confirmación
    

# Mueve el archivo en la imagen al nuevo lugar durante la desfragmentación
def moverArchivoEnImagen(posicionMapa, espacioLibre):
    global imagen
    global archivos
    imagen.seek(posicionMapa * tamanioCluster)
    tamanio = archivos[buscaArchivoClusterInicial(posicionMapa)].tamanio
    contenido = imagen.read(tamanio)
    imagen.seek(posicionMapa * tamanioCluster - espacioLibre * tamanioCluster)
    imagen.write(contenido)

# Actualiza la posición inicial del archivo en la lista de archivos
def actualizarArchivos(posicionMapa, espacioLibre):
    global archivos
    nuevoClusterInicial = posicionMapa - espacioLibre
    archivos[buscaArchivoClusterInicial(posicionMapa)].clusterInicial = nuevoClusterInicial
    actualizaMapa()

# Actualiza el directorio de archivos en la imagen
def actualizarDirectorio():
    global archivos
    for y in range(64):
        resultado = sacaDatosArchivo(y)
        if resultado:
            posicionArchivo = buscaArchivoNombre(resultado.nombre)
            if archivos[posicionArchivo] != -1:
                inicial = 1024 + (y * 64)
                imagen.seek(inicial + 20)
                almacen = struct.pack('<i', archivos[posicionArchivo].clusterInicial)
                imagen.write(almacen)

def inicio():
    # Inicializa el mapa de la imagen del sistema de archivos
    iniciaMapa()
    
    # Inicializa los archivos almacenados en el sistema de archivos FiUnamFS
    inicializaArchivos()
    
    # Muestra datos generales del sistema de archivos
    print("Datos del sistema de archivos:")
    nombreSistema = sacaDatosAscii(0, 8)  # Obtiene el nombre del sistema de archivos desde la imagen
    version = sacaDatosAscii(10, 4)       # Obtiene la versión del sistema de archivos
    etiqueta = sacaDatosAscii(20, 15)     # Obtiene la etiqueta del volumen

    # Muestra los datos del sistema de archivos al usuario
    print("\nIdentificación del sistema de archivos:", nombreSistema)
    print("Versión de la implementación:", version)
    print("Etiqueta del volumen:", etiqueta)
    print("Tamaño de un cluster:", tamanioCluster)
    print("Número de clusters que mide el directorio:", clustersDirectorio)
    print("Número de clusters que mide la unidad completa:", clustersUnidad)
    print("Tamaño del directorio:", tamanioDirectorio)
    print("\n")

    # Inicia el menú principal del sistema de archivos
    menu1 = True
    while(menu1):
        print("\nOpciones:")
        print("1. Listar archivos")
        print("2. Copiar uno de los archivos a tu computadora")
        print("3. Copiar un archivo de tu computadora hacia FiUnamFS")
        print("4. Eliminar un archivo del FiUnamFS")
        print("5. Desfragmentar el sistema de archivos")
        print("6. Cerrar el sistema de archivos\n")
        
        # Solicita al usuario elegir una opción del menú
        opcion = int(input("Ingresa una opción: "))
        
        if opcion == 1:
            # Lista los archivos del sistema de archivos
            muestraDirectorio()
            print("\n")
        
        elif opcion == 2:
            # Solicita el nombre y ruta para copiar un archivo hacia la computadora del usuario
            nombre = input("Ingresa el nombre del archivo que quieres copiar: ")
            ruta = input("Ingresa la ruta en la cual lo quieres copiar: ").replace("\\", "/")
            copiaArchivoAComputadora(nombre, ruta)
            print("\n")
        
        elif opcion == 3:
            # Solicita la ruta de un archivo en la computadora para copiarlo hacia FiUnamFS
            ruta = input("Ingresa la ruta de donde deseas copiar el archivo (incluye el archivo con su extensión):").replace("\\", "/")
            copiaArchivoAImagen(ruta)
            print("\n")
        
        elif opcion == 4:
            # Solicita el nombre del archivo para eliminarlo del sistema de archivos
            nombre = input("Ingresa el nombre del archivo que quieres eliminar (incluye la extensión): ")
            borraArchivo(nombre, 1)
            print("\n")
        
        elif opcion == 5:
            # Desfragmenta el sistema de archivos para optimizar el espacio
            desfragmentar()
            print("Sistema de archivos desfragmentado con éxito.")
            print("\n")
        
        elif opcion == 6:
            # Cierra el sistema de archivos y termina el menú
            print("Cerrando....\n")
            menu1 = False
            print("\n")
        
        else:
            # Opción no válida
            print("No ingresaste una opción válida. Por favor, inténtalo nuevamente.\n\n")
            print("\n")

# Ejecuta el inicio del sistema de archivos
inicio()

# Cierra el archivo de imagen del sistema de archivos después de finalizar el uso
imagen.close()