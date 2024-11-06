import os
import struct
import threading
import math
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog
from tkinter import messagebox, filedialog


#Variable de condición para alertar al hilo que lista los archivos.
VCListFiles = threading.Condition()

#Clase del sistema de archivos
class FiUnamFS:
    #Constructor
    def __init__(self, disk): 
        self.disk = disk 
        #Mutex para trabajar de forma paralela cada una de las distitnas funciones
        #Pues en este caso el sistema de archivos es el recurso compartido
        self.lock = threading.Lock() 
        #Variable para guardar los archivos extraidos del sistema de archivos                           
        self.archivos = None 
        
    #Funcion que recibe la version y el nombre del sistema de archivos seleccionados y lo valida   
    def  __validacion__(self,version,nombre):
        if(nombre!="FiUnamFS"):
            messagebox.showerror("Error de nombre", f"Nombre incorrecto: {nombre}. Se esperaba: {"FiUnamFS"}.")
            self.root.destroy()  
        if version != "25-1":
            messagebox.showerror("Error de Versión", f"Versión incorrecta: {version}. Se esperaba: {"25-1"}.")
            self.root.destroy()  
    
    #Funcion para Leer los datos del superbloque
    def __LeerSuperBloque__(self):
        with open(self.disk, 'rb') as f:
            #Ajustamos al cluster 0 donde estan ubicados los datos del superbloque
            f.seek(0)
            #Leemos los datos del disco
            datos = f.read(54)
            #Desempaquetar los datos
            #<: Leer en little-endian, 9s: Leer 9 bytes como string (nombre), 1x: salta  1 byte
            #5s: Lee 5 bytes como cadena (Version), 5x: Salta 5 bytes, 16s: Lee 16 bytes como cadena (Etiqueta de volumen), 4x: Salta 4 bytes
            #I: Lee 4 bytes como un entero sin signo de 32 bits (Tamaño del clusterr), 1x: salta un byte,
            #I: Lee otros 4 bytes como entero sin signo de 32 birs (Cluster totales), 1x: salta un byte,
            #I: Lee el numero de clusters totales que mide la unidad

            nombre, version, Eti_volumen, Tam_cluster, dir_clusters, total_clusters = struct.unpack('<9s1x5s5x16s4xI1xI1xI', datos[:54]) 
            # Procesar los datos (decodificar)
            nombre = nombre.decode('ascii').strip('\x00')
            version = version.decode('ascii').strip('\x00')
            self.__validacion__(version,nombre)
            Eti_volumen = Eti_volumen.decode('ascii').strip('\x00')
            # Retorna todos los datos en un diccionario
            return {
                "Nombre": nombre,
                "Versión": version,
                "Etiqueta de Volumen": Eti_volumen,
                "Tamaño de Cluster": Tam_cluster,
                "Número de Clusters de Directorio": dir_clusters,
                "Total de Clusters": total_clusters
            }
    #Funcion que enlista los archivos del sistema de archivos
    def __EnlistarDirectorio__(self):
        Archivos = []
        with open(self.disk,'rb') as f:
            # Clusters 1-4 
            for i in range(1,5): 
                #Ajustamos el puntero al inicio de cada bloque
                f.seek(i*1024)
                #Nos movemos por todas las entradas disponibles en cada cluster
                for _ in range (16):
                    entry = f.read(64)
                    #<: Leer en lttle-endian, c: guardamos el caracter
                    #15s: Lee 15 bytes como cadena para el nombre del archivo 
                    #I: Lee 4 bytes como entero que representa el tamaño del archivo
                    #I: Lee 4 bytes como entero para el cluster inicial
                    #14s: Lee 14 bytes como cadena para la hora y fecha de creacion del archivo
                    #14s: Lee 14 bytes como cadena para la hora y fecha de la ultima modificacion del archivo
                    #12x: omitir los bytes de posible expansion
                    Tipo_Archivo, nombre, tamaño, clusterInicial, creado, modificado = struct.unpack('<c15sII14s14s12x', entry)
                    #Convertir el nombre del archivo para verificar si es una entrada vacia ()"---------------"  o #)
                    if Tipo_Archivo.decode("ascii") == '#':
                        continue
                    nombre = nombre.decode("ascii").strip("\x00").strip()
                    if "---------------" in nombre :
                        continue  
                    #En caso de encontrar un archivo en el directorio, guardarlo en la lista local junto con sus datos
                    Archivos.append({
                        "Nombre": nombre,
                        "Tamaño": tamaño,
                        "Creado": creado.decode("ascii", errors='ignore').strip("\x00"),
                        "Modificado": modificado.decode("ascii", errors='ignore').strip("\x00"),
                        "Cluster Inicial": clusterInicial
                    })
        self.archivos = Archivos
        return Archivos
    
    #Funcion para copiar de FIUNAMFS a mi computadora
    def __CopiarDelDisk__(self,NombreArchivoACopiar, DireccionAGuardar):
        #Tomamos el mutex para proteger el puntero al usar el seek, si hay dos hilos concurrentes puede haber condiciones de carrera y terminar leyendo datos que no deberian ser leidos
        #Ademas al tambien escribir en este caso en la computadora, pueden existir daños en el archivo si dos o más hilos escriben al mismo tiempo
        with self.lock:
            #Buscamos el archivo a copiar
            ArchivoACopiar = next((f for f in self.archivos if f["Nombre"] == NombreArchivoACopiar), None) 
            if ArchivoACopiar:
                #Obtenemos los datos del archivo que vamos a copiar del FIUnamFS
                #En este caso donde inicia el archivo y cual es su tamaño
                Cluster_inicial = ArchivoACopiar["Cluster Inicial"] 
                Tamaño = ArchivoACopiar["Tamaño"]                   
                #Abrimos el archivo en modo lectura
                with open(self.disk, 'rb') as Archivo:
                    #Ponemos el puntero en el cluster inicial
                    Archivo.seek(Cluster_inicial*1024)
                    #Leemos el archivo 
                    DatosArchivo = Archivo.read(Tamaño) 
                #Creamos el archivo en la computadora y abrimos el archivo en modo escritura
                with open(DireccionAGuardar, 'wb') as ArchivoGuardado:
                    #Escribimos los datos en el archivo 
                    ArchivoGuardado.write(DatosArchivo)                
                messagebox.showinfo("Éxito", f"Archivo '{NombreArchivoACopiar}' copiado exitosamente a '{DireccionAGuardar}'.")
            else:
                messagebox.showerror("Error", "Archivo no encontrado en el sistema de archivos.")
                   
    def __CopiarAlDisk__(self,DireccionArchivoACopiar):
        #Tomamos el mutex pues es necesario comprobar y en su caso modificar los archivos locales pues si no los hay (si se decidio copiar antes de enlistar) hay que obtenerlos.
        with self.lock: 
            if self.archivos == None:
                self.archivos = self.__EnlistarDirectorio__()
        # Obtener el nombre del archivo que se va a copiar
        Nombre = os.path.basename(DireccionArchivoACopiar).encode("ascii").ljust(15, b'\x00')
        # Verificar si ya existe un archivo con el mismo nombre
        for archivo in self.archivos:
            if archivo["Nombre"].encode("ascii").strip(b'\x00') == Nombre.strip(b'\x00'):
                messagebox.showerror("Error", f"Ya existe un archivo con el mismo nombre en el sistema de archivos: {os.path.basename(DireccionArchivoACopiar)}")
                return
        # Abrir el archivo en modo de lectura para obtener los datos del archivo y en su caso codificarlos para introducirlos al sistema de archivos
        with open(DireccionArchivoACopiar, 'rb') as ArchivoFuente:
            #Esta ultima parte ajusta la longitud a 15 que es la definida por la especificacion
            Nombre = os.path.basename(DireccionArchivoACopiar).encode("ascii").ljust(15,b'\x00') 
            Tamaño = os.path.getsize(DireccionArchivoACopiar)
            #Introducir la fecha como esta establecida en la especificacion   
            Creado = datetime.now().strftime('%Y%m%d%H%M%S').encode('ascii') 
            Modificado = Creado
            #Protegemos el acceso al disco con un mutex pues verificaremos su espacio y posteriormente lo modificaremos
            with self.lock: 
                #Verificar si hay espacio disponible y si es asi devolver el cluster donde hay espacio contiguo libre
                ClusterInicial = self.__HayEspacio__(Tamaño)
                if not ClusterInicial:
                    messagebox.showerror("Error", f"Espacio insuficiente en el disco: '{os.path.basename(DireccionArchivoACopiar)}'")
                    return False
                #Escribir la entrada del archivo en el directorio
                with open(self.disk, 'r+b') as disk_file:
                    PosicionDirectorio = self.__PosicionDeDirectorioLibre__() 
                    #si no hay pues no podemos copiar en el disk
                    if not PosicionDirectorio: 
                        messagebox.showerror("Error", f"No hay espacios en el directorio disponibles: '{os.path.basename(DireccionArchivoACopiar)}'")
                        return False
                    #Ponemos el puntero en la entrada de directorio disponible
                    disk_file.seek(PosicionDirectorio) 
                    #Empaquetamos los datos segun las especificaciones
                    disk_file.write(b'.')  
                    disk_file.write(struct.pack('<15s', Nombre))
                    disk_file.write(struct.pack('<I', Tamaño))
                    disk_file.write(struct.pack('<I', ClusterInicial))
                    disk_file.write(struct.pack('<14s', Creado))
                    disk_file.write(struct.pack('<14s', Modificado))
                    # Espacio reservado
                    disk_file.write(b'\x00' * 12)  

                #Escribir el contenido del archivo en los clusters
                with open(self.disk, 'r+b') as disk_file:
                    cluster = ClusterInicial*1024
                    i=0
                    while True:
                        #Leer un bloque (tamaño de un cluster)
                        data = ArchivoFuente.read(1024)
                        #cuando ya no haya nada que escribir salimos del bucle  
                        if not data: 
                            break
                        #Ajustamos el puntero para movernos entre los clusters
                        disk_file.seek(cluster + i * 1024)
                        #Escribimos donde apunta el puntero 
                        disk_file.write(data) 
                        i+=1
                        #Si el cluster inicial era none, entonces no habia espacio en los cluster y salimos
                        if not cluster: 
                            messagebox.showerror("Error", f"Espacio insuficiente en los clusters'{os.path.basename(DireccionArchivoACopiar)}'")
                            return False

            #Despertamos al hilo "enlistador" para que muestre los cambios en la GUI y actualice los archivos locales
            with VCListFiles: 
                VCListFiles.notify_all()
            messagebox.showinfo("Éxito", f"Archivo  copiado exitosamente a el disco.'{os.path.basename(DireccionArchivoACopiar)}'")
            return True
    
    #Esta funcion se encarga de encontrar una entrada disponible en el directorio y devolver la posicion para poder escribir en ella
    def __PosicionDeDirectorioLibre__(self): 
        with open(self.disk,'rb') as f:
            # Clusters 1-4 pues aqui se encuentra el directorio
            for i in range(1,5): 
                f.seek(i*1024)
                #Como el cluster son 1024 bytes y cada entrada son 64 bytes, significa que tendremos 16 entradas disponibles en cada cluster (0-15)
                for entry_index in range (16): 
                    #Leemos los 64 bytes de la entrada
                    entry = f.read(64)
                    #Obtenemos el nombre y el tipo para verificar si es una entrada disponible (vacia)
                    tipo, nombre = struct.unpack('<c15s48x', entry) 
                    nombre = nombre.decode("ascii").strip("\x00").strip()
                    #Comprobar si el tipo o el nombre indica que está libre
                    if tipo == b'#' or nombre == "---------------":
                        # Retorna la posicion de la entrada libre
                        return i*1024+entry_index*64 
        #Si no hay entradas de directorio libres 
        return None  
    #Funcion que verifica si hay espacio contiguo suficiente y devuelve donde comienza ese espacio disponible
    def __HayEspacio__(self, Tamaño): 
        # Tamaño de cada cluster en bytes
        cluster_size = 1024  
        # Calcular el número de clusters necesarios y  redondear hacia arriba
        clusters_necesarios = math.ceil((Tamaño) / cluster_size)  
        # Verificar el espacio ocupado por los archivos existentes
        espacio_ocupado = sum(archivo["Tamaño"] for archivo in self.archivos)
        # Verificar si hay espacio suficiente en el disco
        EspacioDelDirectorio = 1024*5
        if espacio_ocupado + Tamaño + EspacioDelDirectorio > 1440 * 1024:
            # No hay espacio total disponible
            return False  

        # Ahora buscar si hay suficiente espacio contiguo
        with open(self.disk, 'rb') as disk_file:
            # Contador para rastrear clusters libres contiguos
            espacios_contiguos = 0
             # Revisa todos los clusters
            for cluster in range(1440): 
                data = disk_file.read(cluster_size)
                # Si todos los bytes son cero, el cluster está libre
                if all(b == 0 for b in data):  

                    espacios_contiguos += 1
                    # Se encontro suficiente espacio contiguo
                    if espacios_contiguos == clusters_necesarios:
                        # Devolver el cluster inicial (donde comienza este espacio contiguo)  
                        return cluster-clusters_necesarios+1 
                else:
                    # Reiniciar contador si se encuentra un cluster ocupado
                    espacios_contiguos = 0  
        # No se encontro suficiente espacio contiguo
        return  None  
    
    #Funcion para eliminar archivos del disco
    def __EliminarDelDisk__(self,NombreArchivoAEliminar): 
        #Obtenemos los datos del archivo que vamos a eliminar
        archivo_a_eliminar= next((f for f in self.archivos if f["Nombre"] == NombreArchivoAEliminar), None) 
        cluster_inicial = archivo_a_eliminar["Cluster Inicial"]
        tamaño = archivo_a_eliminar["Tamaño"]
        #Calculamos los clusters que mide (usamos Ceil (redondear hacia arriba) porque si hay decimales si o si ocuparemos otro cluster)
        clusters_necesarios = math.ceil(tamaño / 1024) 
       #Protegemos el disco pues es el recurso compartido que usaremos 
        with self.lock: 
            # Actualizar el directorio
            with open(self.disk, 'r+b') as disk_file:
                # Solo revisamos los primeros 4 clusters para el directorio
                for i in range(1, 5):
                    #Situamos el puntero al inicio de cada cluster del directorio  
                    disk_file.seek(i * 1024)
                     #Buscamos entre todas las entradas   
                    for entry_index in range(16):
                        entry = disk_file.read(64)
                        tipo ,nombre = struct.unpack('<1b15s48x', entry)
                        nombre = nombre.decode("ascii").strip("\x00").strip()
                        #Si encontramos el archivo entonces lo marcamos como libre
                        if nombre == NombreArchivoAEliminar: 
                            disk_file.seek(i * 1024 + entry_index * 64)
                            disk_file.write(b'#')  
                            break
                # Liberar el espacio de los clusters
                for cluster in range(cluster_inicial, cluster_inicial + clusters_necesarios):
                    disk_file.seek(cluster * 1024)
                    disk_file.write(b'\x00' * 1024)  
            # Remover de los archivos locales 
            self.archivos.remove(archivo_a_eliminar)  
        
        with VCListFiles:
            VCListFiles.notify()
        messagebox.showinfo("Éxito", f"Archivo '{NombreArchivoAEliminar}' eliminado exitosamente.")
        return True



#------------------------------ Interfaz Grafica  -------------------------------------------------
class FiUnamFSApp:
    #Constructor
    def __init__(self, root, fs):
        self.fs = fs
        self.root = root
        self.root.title("FiUnamFS")
        
        
        #Crear etiquetas para mostrar la información del superbloque
        self.superblock_info = tk.Label(root, text="", justify='left')
        self.superblock_info.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        #Crear el Treeview para mostrar archivos en formato de tabla
        self.tree = ttk.Treeview(root, columns=("Nombre", "Tamaño", "Creado", "Cluster Inicial", "Modificado"), show='headings')
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Tamaño", text="Tamaño (bytes)")
        self.tree.heading("Creado", text="Creado")
        self.tree.heading("Cluster Inicial", text="Cluster Inicial")
        self.tree.heading("Modificado", text="Modificado")

        #Ajustar el ancho de las columnas de la tabla
        self.tree.column("Nombre", width=200)
        self.tree.column("Tamaño", width=100, anchor='e')
        self.tree.column("Creado", width=150)
        self.tree.column("Cluster Inicial", width=100, anchor='e')
        self.tree.column("Modificado", width=150)

        #Añadir Scrollbar
        self.tree_scroll = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)

        #Posicionamiento del Scrollbar
        self.tree_scroll.grid(row=1, column=2, sticky='ns')
        self.tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        #Inicialmente ocultar el Treeview
        self.tree.grid_remove()

        #Botones para las operaciones
        self.list_button = tk.Button(root, text="Listar Archivos", command=self.notify_list_files)
        self.list_button.grid(row=2, column=0, padx=10, pady=5)

        self.copy_to_pc_button = tk.Button(root, text="Copiar a PC", command=self.copy_to_pc)
        self.copy_to_pc_button.grid(row=2, column=1, padx=10, pady=5)

        self.copy_to_fs_button = tk.Button(root, text="Copiar a FiUnamFS", command=self.copy_to_fs)
        self.copy_to_fs_button.grid(row=3, column=0, padx=10, pady=5)

        self.delete_button = tk.Button(root, text="Eliminar Archivo", command=self.delete_file)
        self.delete_button.grid(row=3, column=1, padx=10, pady=5)
        #Leer y mostrar el superbloque
        self.show_superblock_info()
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Iniciar el hilo enlistador de archivos
        self.list_thread = threading.Thread(target=self.list_files)
        self.list_thread.start()
        
   #Funcion que se encarga de despertar el hilo enlistador de archivo
    def notify_list_files(self):
        with VCListFiles:
            VCListFiles.notify()              
        
    #Funcion enlistadora de archivos
    def list_files(self):
        #While para que pueda ser llamada cuando se necesite
        while True: 
            #Entra a la variable de condicion y queda a la espera de ser notificada
            with VCListFiles: 
                VCListFiles.wait()
                #Cuando es despertada borramos lo mostrado en la GUI para reemplazarla con los nuevos cambios
                self.tree.delete(*self.tree.get_children())  
                #Obtenemos los archivos
                files = self.fs.__EnlistarDirectorio__()  
                #Enlistamos los archivos en la GUI
                for file in files:
                    self.tree.insert("", "end", values=(file["Nombre"], file["Tamaño"], datetime.strptime(file["Creado"],"%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S"), file["Cluster Inicial"], datetime.strptime(file["Modificado"],"%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")))
                self.tree.grid()  
                self.tree_scroll.grid(row=1, column=2, sticky='ns')
    #Esta funcion muestra los datos del super bloque en la GUI  
    def show_superblock_info(self):
        #Obtener los datos del superbloque
        superblock_data = self.fs.__LeerSuperBloque__() 
        #Mostrar datos
        superblock_text = (
            f"Nombre: {superblock_data['Nombre']}\n"
            f"Versión: {superblock_data['Versión']}\n"
            f"Etiqueta de Volumen: {superblock_data['Etiqueta de Volumen']}\n"
            f"Tamaño de Cluster: {superblock_data['Tamaño de Cluster']}\n"
            f"Número de Clusters de Directorio: {superblock_data['Número de Clusters de Directorio']}\n"
            f"Total de Clusters: {superblock_data['Total de Clusters']}"
        )
        self.superblock_info.config(text=superblock_text)

    #Funcion que se ejecuta al presionar el boton "Copiar a PC"        
    def copy_to_pc(self):
        #Obtenemos la seleccion de archivos a copiar
        selected_item = self.tree.selection() 
        if not selected_item:
            messagebox.showwarning("Atención", "Selecciona un archivo para copiar.")
            return
        #-----------------------------------------------------------------------------#
        #Funcion interna para la ejecucion multihilo que manda a llamar a la funcion que realiza toda la logica de copiado con los datos adquiridos
        def CopiarAPC(NombreArchivoACopiar,DireccionAGuardar):
            self.fs.__CopiarDelDisk__(NombreArchivoACopiar,DireccionAGuardar)
        #-----------------------------------------------------------------------------#           
        for item in selected_item:
            #Obtenemos el nombre del archivo a copiar
            NombreArchivoACopiar = self.tree.item(item)["values"][0] 
            #Obtenemos su direccion
            DireccionAGuardar = filedialog.asksaveasfilename(initialfile=NombreArchivoACopiar) 
            #Si no se logra obtener la direccion vamos al siguiente archivo
            if not DireccionAGuardar:   
                continue
            #Creamos el hilo que iniciara la funcion de copiar, de este modo cada archivo que se quiera copiar sucedera al mismo tiempo        
            hilo = threading.Thread(target=CopiarAPC, args=(NombreArchivoACopiar,DireccionAGuardar)) 
            #Iniciamos el hilo
            hilo.start() 

            
    #Funcion que se ejecuta al presionar el boton "Copiar a FiUnamFS"
    def copy_to_fs(self):
        #Creamos un arreglo de hilos para posteriormente iniciarlos al mismo tiempo
        hilos = [] 
        #Obtenemos las ubicaciones de los archivos seleccionados de la computadora
        file_paths= filedialog.askopenfilenames() 
        #-----------------------------------------------------------------------------#  
        #Funcion interna para la ejecucion multihilo 
        def CopiarAFS(file_path): 
            fs.__CopiarAlDisk__(file_path)
        #-----------------------------------------------------------------------------#
        #Si no se selecciono nada, salimos.     
        if not file_paths:
            return
        #Verificamos todos los archivos de modo que coincidan con la longitud de nombre de la especificación
        for file_path in file_paths: 
            NombreArchivo = os.path.basename(file_path)
            if len(NombreArchivo) > 15:
                messagebox.showerror("Error", f"El nombre del archivo es demasiado largo '{NombreArchivo}' (máx. 15 caracteres).")
                continue
            #Creamos el hilo
            hilo = threading.Thread(target=CopiarAFS, args=(file_path,))
            #Lo agregamos a nuestra lista de hilos 
            hilos.append(hilo) 
            #Iniciamos los hilos "al mismo tiempo"
        for hilo in hilos: 
            hilo.start()
        # Limpiamos la lista de hilos utilizados   
        hilos.clear() 
        
    #Funcion que se ejecuta al presionar el boton "Eliminar Archivo"
    def delete_file(self):
        hilos = [] 
        #Obtenemos la seleccion de archivos
        selected_item = self.tree.selection() 
        #Si no seleccionamos nada salimos
        if not selected_item: 
            messagebox.showwarning("Atención", "Selecciona un archivo para eliminar.")
            return
        #Funcion interna para la ejecucion multihilo 
        #------------------------------------------------------------------
        def EliminarArchivo(NombreArchivoAEliminar):
            self.fs.__EliminarDelDisk__(NombreArchivoAEliminar)
        #------------------------------------------------------------------
        
        #Recorremos todos los archivos
        for item in selected_item: 
            #Obtenemos el nombre del archivo a eliminar
            NombreArchivoAEliminar = self.tree.item(item)["values"][0] 
            confirmacion = messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas eliminar el archivo '{NombreArchivoAEliminar}'?")
            #Si se desea eliminar definitivamente cremos el hilo anclado a la funcion y lo metemos a la lista de hilos
            if confirmacion: 
                hilo = threading.Thread(target=EliminarArchivo, args=(NombreArchivoAEliminar,))
                hilos.append(hilo)
        for hilo in hilos: 
            hilo.start()    
        hilos.clear()
                
#------------------------------ Interfaz Grafica ----------------------------------

#------------------------------------Main------------------------------------------
#obtener el sistema de archivos
fs = FiUnamFS("../fiunamfs.img") 
#Inicar la GUI
root = tk.Tk() 
app = FiUnamFSApp(root, fs)
root.mainloop()
