import os
import struct
import threading
import math
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog
from tkinter import messagebox, filedialog
VCListFiles = threading.Condition()
class FiUnamFS:
    def __init__(self, disk):
        self.disk = disk
        self.lock = threading.Lock()
        self.archivos = None
        
        
    def  __validacion__(self,version,nombre):
        if(nombre!="FiUnamFS"):
            messagebox.showerror("Error de nombre", f"Nombre incorrecto: {nombre}. Se esperaba: {"FiUnamFS"}.")
            self.root.destroy()  
        if version != "25-1":
            messagebox.showerror("Error de Versión", f"Versión incorrecta: {version}. Se esperaba: {"25-1"}.")
            self.root.destroy()  
    
    
    def __LeerSuperBloque__(self):
        with open(self.disk, 'rb') as f:
            f.seek(0)
            datos = f.read(54)
            nombre, version, Eti_volumen, Tam_cluster, dir_clusters, total_clusters = struct.unpack('<9s1x5s5x16s4xI1xI1xI', datos[:54]) 
            #<: Leer en little-endian, 9s: Leer 9 bytes como string (nombre), 1x: salta  1 byte
            #5s: Lee 5 bytes como cadena (Version), 5x: Salta 5 bytes, 16s: Lee 16 bytes como cadena (Etiqueta de volumen), 4x: Salta 4 bytes
            #I: Lee 4 bytes como un entero sin signo de 32 bits (Tamaño del clusterr)
            #I: Lee otros 4 bytes como entero sin signo de 32 birs (Cluster totales)
            #I: Lee el numero de clusters totales que mide la unidad
            # Procesar los datos
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
    
    def __EnlistarDirectorio__(self):
        Archivos = []
        with self.lock:
            with open(self.disk,'rb') as f:
                for i in range(1,5): # Clusters 1-4 
                    f.seek(i*1024)
                    for _ in range (15):
                        entry = f.read(64)
                        Tipo_Archivo, nombre, tamaño, clusterInicial, creado, modificado = struct.unpack('<c15sII14s14s12x', entry)
                        #<: Leer en lttle-endian, c: pone un punto si el byte leido representa un archivo valido
                        #15s: Lee 15 bytes como cadena para el nombre del archivo 
                        #I: Lee 4 bytes como entero que representa el tamaño del archivo
                        #3s: Lee 3 bytes para el cluster inicial
                        #14s: Lee 14 bytes como cadena para la hora y fecha de creacion del archivo
                        #14s: Lee 14 bytes como cadena para la hora y fecha de la ultima modificacion del archivo
                        #12x: omitir los bytes de posible expansion
                        #Convertir el nombre del archivo para verificar si es "---------------"
                        if Tipo_Archivo.decode("ascii") == '#':
                            continue
                        nombre = nombre.decode("ascii").strip("\x00").strip()
                        if "---------------" in nombre :
                            continue  
                        Archivos.append({
                            "Nombre": nombre,
                            "Tamaño": tamaño,
                            "Creado": creado.decode("ascii", errors='ignore').strip("\x00"),
                            "Modificado": modificado.decode("ascii", errors='ignore').strip("\x00"),
                            "Cluster Inicial": clusterInicial
                        })
        self.archivos = Archivos
        return Archivos
    
    
    def __CopiarDelDisk__(self,NombreArchivoACopiar, DireccionAGuardar):
        with self.lock:
            ArchivoACopiar = next((f for f in self.archivos if f["Nombre"] == NombreArchivoACopiar), None)
            if ArchivoACopiar:
                Cluster_inicial = ArchivoACopiar["Cluster Inicial"]
                Tamaño = ArchivoACopiar["Tamaño"]
                
                with open(self.disk, 'rb') as Archivo:
                    Archivo.seek(Cluster_inicial*1024)
                    DatosArchivo = Archivo.read(Tamaño)
                    
                with open(DireccionAGuardar, 'wb') as ArchivoGuardado:
                    ArchivoGuardado.write(DatosArchivo)
                messagebox.showinfo("Éxito", f"Archivo '{NombreArchivoACopiar}' copiado exitosamente a '{DireccionAGuardar}'.")
            else:
                messagebox.showerror("Error", "Archivo no encontrado en el sistema de archivos.")
                   
    def __CopiarAlDisk__(self,DireccionArchivoACopiar):
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
        with open(DireccionArchivoACopiar, 'rb') as ArchivoFuente:
            Nombre = os.path.basename(DireccionArchivoACopiar).encode("ascii").ljust(15,b'\x00')
            Tamaño = os.path.getsize(DireccionArchivoACopiar)   
            Creado = datetime.now().strftime('%Y%m%d%H%M%S').encode('ascii')
            Modificado = Creado
            with self.lock:
                #Verificar si hay espacio disponible y si es asi devolver el cluster donde hay espacio contiguo libre
                ClusterInicial = self.__HayEspacio__(Tamaño)
                if not ClusterInicial:
                    messagebox.showerror("Error", f"Espacio insuficiente en el disco: '{os.path.basename(DireccionArchivoACopiar)}'")
                    return False
                #Escribir la entrada del archivo en el directorio
                with open(self.disk, 'r+b') as disk_file:
                    PosicionDirectorio = self.__PosicionDeDirectorioLibre__()
                    if not PosicionDirectorio:
                        messagebox.showerror("Error", f"No hay espacios en el directorio disponibles: '{os.path.basename(DireccionArchivoACopiar)}'")
                        return False
                    disk_file.seek(PosicionDirectorio)
                    disk_file.write(b'.')  
                    disk_file.write(struct.pack('<15s', Nombre))
                    disk_file.write(struct.pack('<I', Tamaño))
                    disk_file.write(struct.pack('<I', ClusterInicial))
                    disk_file.write(struct.pack('<14s', Creado))
                    disk_file.write(struct.pack('<14s', Modificado))
                    disk_file.write(b'\x00' * 12)  # Espacio reservado

                #Escribir el contenido del archivo en los clusters
                with open(self.disk, 'r+b') as disk_file:
                    cluster = ClusterInicial*1024
                    i=0
                    while True:
                        data = ArchivoFuente.read(1024)  #Leer un bloque (tamaño de un cluster)
                        if not data:
                            break
                        disk_file.seek(cluster + i * 1024)
                        disk_file.write(data)
                        i+=1
                        if not cluster:
                            messagebox.showerror("Error", f"Espacio insuficiente en los clusters'{os.path.basename(DireccionArchivoACopiar)}'")
                            return False

            messagebox.showinfo("Éxito", f"Archivo  copiado exitosamente a el disco.'{os.path.basename(DireccionArchivoACopiar)}'")
            with VCListFiles:
                VCListFiles.notify_all()
            return True
    
    
    def __PosicionDeDirectorioLibre__(self):
        with open(self.disk,'rb') as f:
            for i in range(1,5): # Clusters 1-4 
                f.seek(i*1024)
                for entry_index in range (15):
                    entry = f.read(64)
                    tipo, nombre = struct.unpack('<c15s48x', entry)
                    nombre = nombre.decode("ascii").strip("\x00").strip()
                    #Comprobar si el tipo o el nombre indica que está libre
                    if tipo == b'#' or nombre == "---------------":
                        return i*1024+entry_index*64  # Retorna la posicion de la entrada libre
        return None  #Si no hay entradas de directorio libres
    
    def __HayEspacio__(self, Tamaño):
        # Calcular el número de clusters necesarios
        cluster_size = 1024  # Tamaño de cada cluster en bytes
        clusters_necesarios = math.ceil((Tamaño) / cluster_size)  # Redondear hacia arriba
        # Verificar el espacio ocupado por los archivos existentes
        espacio_ocupado = sum(archivo["Tamaño"] for archivo in self.archivos)
        # Verificar si hay espacio suficiente en el disco
        if espacio_ocupado + Tamaño > 1440 * 1024:
            return False  # No hay espacio total disponible

        # Ahora buscar si hay suficiente espacio contiguo
        with open(self.disk, 'rb') as disk_file:
            # Contador para rastrear clusters libres contiguos
            espacios_contiguos = 0
            for cluster in range( 1024):  # Revisa todos los clusters
                data = disk_file.read(cluster_size)
                if all(b == 0 for b in data):  # Si todos los bytes son cero, el cluster está libre

                    espacios_contiguos += 1
                    if espacios_contiguos == clusters_necesarios:  # Se encontro suficiente espacio contiguo
                        return cluster-clusters_necesarios+1 # Devolvr el cluster inicial
                else:

                    espacios_contiguos = 0  # Reiniciar contador si se encuentra un cluster ocupado

        return  None  # No se encontro suficiente espacio contiguo
    def __EliminarDelDisk__(self,NombreArchivoAEliminar):
        archivo_a_eliminar= next((f for f in self.archivos if f["Nombre"] == NombreArchivoAEliminar), None)
        cluster_inicial = archivo_a_eliminar["Cluster Inicial"]
        tamaño = archivo_a_eliminar["Tamaño"]
        clusters_necesarios = math.ceil(tamaño / 1024)
        with self.lock:
            with open(self.disk, 'r+b') as disk_file:
                # Actualizar el directorio
                for i in range(1, 5):  # Solo revisamos los primeros 4 clusters para el directorio
                    disk_file.seek(i * 1024)
                    for entry_index in range(15):
                        entry = disk_file.read(64)
                        tipo ,nombre = struct.unpack('<1b15s48x', entry)
                        nombre = nombre.decode("ascii").strip("\x00").strip()

                        if nombre == NombreArchivoAEliminar:
                            # Marcar como libre
                            disk_file.seek(i * 1024 + entry_index * 64)
                            disk_file.write(b'#')  # Marca el tipo como libre
                            break
                # Liberar el espacio de los clusters
                for cluster in range(cluster_inicial, cluster_inicial + clusters_necesarios):
                    disk_file.seek(cluster * 1024)
                    disk_file.write(b'\x00' * 1024)  # Rellena el cluster con ceros
                    
            messagebox.showinfo("Éxito", f"Archivo '{NombreArchivoAEliminar}' eliminado exitosamente.")
            self.archivos.remove(archivo_a_eliminar)  # Remover de la lista local
        with VCListFiles:
            VCListFiles.notify()
        return True



#------------------------------ Interfaz Grafica ----------------------------------
class FiUnamFSApp:
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
        # Iniciar el hilo para listar archivos
        self.list_thread = threading.Thread(target=self.list_files)
        self.list_thread.start()
        
        
        
    def show_superblock_info(self):
        superblock_data = self.fs.__LeerSuperBloque__()
        superblock_text = (
            f"Nombre: {superblock_data['Nombre']}\n"
            f"Versión: {superblock_data['Versión']}\n"
            f"Etiqueta de Volumen: {superblock_data['Etiqueta de Volumen']}\n"
            f"Tamaño de Cluster: {superblock_data['Tamaño de Cluster']}\n"
            f"Número de Clusters de Directorio: {superblock_data['Número de Clusters de Directorio']}\n"
            f"Total de Clusters: {superblock_data['Total de Clusters']}"
        )
        self.superblock_info.config(text=superblock_text)
   
    def notify_list_files(self):
        with VCListFiles:
            VCListFiles.notify()      
    
    def list_files(self):
        while True:
            with VCListFiles:
                VCListFiles.wait()
                self.tree.delete(*self.tree.get_children())  
                files = self.fs.__EnlistarDirectorio__()  
                for file in files:
                    self.tree.insert("", "end", values=(file["Nombre"], file["Tamaño"], datetime.strptime(file["Creado"],"%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S"), file["Cluster Inicial"], datetime.strptime(file["Modificado"],"%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")))
                self.tree.grid()  
                self.tree_scroll.grid(row=1, column=2, sticky='ns')

            
    def copy_to_pc(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Selecciona un archivo para copiar.")
            return
        def CopiarAPC(NombreArchivoACopiar,DireccionAGuardar):
            self.fs.__CopiarDelDisk__(NombreArchivoACopiar,DireccionAGuardar)
        for item in selected_item:
            NombreArchivoACopiar = self.tree.item(item)["values"][0]
            DireccionAGuardar = filedialog.asksaveasfilename(initialfile=NombreArchivoACopiar)
            if not DireccionAGuardar:
                continue        
            hilo = threading.Thread(target=CopiarAPC, args=(NombreArchivoACopiar,DireccionAGuardar))
            hilo.start()

            
        
    def copy_to_fs(self):
        hilos = []
        file_paths= filedialog.askopenfilenames()
        def CopiarAFS(file_path):
            fs.__CopiarAlDisk__(file_path)
            
        if not file_paths:
            return
        for file_path in file_paths:
            NombreArchivo = os.path.basename(file_path)
            if len(NombreArchivo) > 15:
                messagebox.showerror("Error", f"El nombre del archivo es demasiado largo '{NombreArchivo}' (máx. 15 caracteres).")
                continue
            hilo = threading.Thread(target=CopiarAFS, args=(file_path,))
            hilos.append(hilo)
        for hilo in hilos:
            hilo.start()   
        hilos.clear()

    def delete_file(self):
        hilos = []
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Selecciona un archivo para eliminar.")
            return
        def EliminarArchivo(NombreArchivoAEliminar):
            self.fs.__EliminarDelDisk__(NombreArchivoAEliminar)

        for item in selected_item:
            NombreArchivoAEliminar = self.tree.item(item)["values"][0]
            confirmacion = messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas eliminar el archivo '{NombreArchivoAEliminar}'?")
            if confirmacion:
                hilo = threading.Thread(target=EliminarArchivo, args=(NombreArchivoAEliminar,))
                hilos.append(hilo)
        for hilo in hilos:
            hilo.start()    
        hilos.clear()
                
#------------------------------ Interfaz Grafica ----------------------------------

fs = FiUnamFS("../fiunamfs.img")
root = tk.Tk()
app = FiUnamFSApp(root, fs)
root.mainloop()
