#Ortiz Moreno Ximena
#Sánchez Gachuz Jennyfer Estefanía

import tkinter as tk
from tkinter import filedialog, messagebox
from sistema_fiunamfs import SistemaFiUnamFS  

class InterfazFiUnamFS:
    def __init__(self, root):
        self.sistema_fs = SistemaFiUnamFS()
        self.root = root
        self.root.title("Sistema de Archivos FiUnamFS")

        # Etiqueta de título
        tk.Label(root, text="Sistema de Archivos FiUnamFS", font=("Arial", 16)).pack(pady=10)

        # Botones para cada acción
        tk.Button(root, text="Listar Contenidos", command=self.listar).pack(pady=5)
        tk.Button(root, text="Copiar a Sistema", command=self.copiar_a_sistema).pack(pady=5)
        tk.Button(root, text="Copiar desde Sistema", command=self.copiar_desde_sistema).pack(pady=5)
        tk.Button(root, text="Eliminar Archivo", command=self.eliminar_archivo).pack(pady=5)

        # Campo de entrada de nombre de archivo
        self.nombre_archivo = tk.Entry(root, width=50)
        self.nombre_archivo.pack(pady=5)
        self.nombre_archivo.insert(0, "Nombre del archivo")

        # Área de salida
        self.salida = tk.Text(root, height=10, width=60, state="disabled")
        self.salida.pack(pady=5)

    def listar(self):
        self.salida.config(state="normal")
        self.salida.delete(1.0, tk.END)
        contenido = "Contenido del directorio:\n"
        contenido += "\n".join(self.sistema_fs.listar_directorio())  
        self.salida.insert(tk.END, contenido)
        self.salida.config(state="disabled")


    def copiar_a_sistema(self):
        archivo = self.nombre_archivo.get()
        if archivo:
            try:
                self.sistema_fs.copiar_a_sistema(archivo)
                messagebox.showinfo("Copia a Sistema", f"Archivo '{archivo}' copiado a sistema local.")
            except FileNotFoundError:
                messagebox.showerror("Error", f"Archivo '{archivo}' no encontrado en FiUnamFS.")
        else:
            messagebox.showwarning("Advertencia", "Por favor, ingrese el nombre del archivo a copiar.")

    def copiar_desde_sistema(self):
        ruta_archivo = filedialog.askopenfilename()
        if ruta_archivo:
            try:
                self.sistema_fs.copiar_desde_sistema(ruta_archivo)
                messagebox.showinfo("Copia desde Sistema", f"Archivo '{ruta_archivo}' copiado a FiUnamFS.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo copiar el archivo: {e}")

    def eliminar_archivo(self):
        archivo = self.nombre_archivo.get()
        if archivo:
            try:
                self.sistema_fs.eliminar_archivo(archivo)
                messagebox.showinfo("Eliminar Archivo", f"Archivo '{archivo}' eliminado de FiUnamFS.")
            except FileNotFoundError:
                messagebox.showerror("Error", f"Archivo '{archivo}' no encontrado en FiUnamFS.")
        else:
            messagebox.showwarning("Advertencia", "Por favor, ingrese el nombre del archivo a eliminar.")

# Configuración de la ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    interfaz = InterfazFiUnamFS(root)
    root.mainloop()
