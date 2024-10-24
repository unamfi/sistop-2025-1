import threading
import time
import tkinter as tk


# Usamos semáforos y mutex para manejar que usaremos en la ejecución del programa!!!

# USO DE SEMÁFOROS.
# El propósito de usar semáforos en este código va a radicar en querer controlar el número total de personas abordo de la balsa.
# Para controlar el uso de los lugares en la balsa usaremos .acquire(), donde vamos a reducir la cantidad de lugares en nuestra balsa.

# USO DE MUTEX.
# En este código mutex tendrá el propósito de controlar el proceso de los hilos que creamos en el programa.
# Tendrá la funcionalidad de controlar los hilos de serfs y hackers, esto evitará que hackers y serfs accedan y modifiquen el estado de la balsa al mismo tiempo.

semaforo_balsa = threading.Semaphore(4)  # Limitamos la cantidad de personas en la balsa
mutex = threading.Lock()  # Iniciamos el mutex

# Iniciamos los valores en 0 para que el input pueda ser iniciado desde 0.
hackers_abordo = 0
serfs_abordo = 0
personas_balsa = []


# Función para que un hacker intente subir a la balsa
def hacker(id_hacker):
    global hackers_abordo 

    while True:
        time.sleep(1)  # Simulación de tiempo de espera antes de intentar
        semaforo_balsa.acquire()  # Limitamos a 4 personas en total en la balsa, es decir, limitanmos el acceso a SOLO 4 hilos.

        with mutex: # Controlamos de que manera los hilos hacen su función, con el mismo evitamos que dos hilos o más modifiquen los valores. 
            hackers_abordo += 1 # Sumamos en 1 la cantidad de hackers para poder ir reduciendo los pasajeros.

            personas_balsa.append(f"Hacker_{id_hacker}")
            actualizar_estado_balsa(f"Hacker {id_hacker} sube a la balsa")
            mostrar_estado_sincronizacion(f"Mutex adquirido por Hacker {id_hacker} - {hackers_abordo} hackers abordo")
            animar_subida(len(personas_balsa) - 1, "Hacker", id_hacker)
            
            if hackers_abordo + serfs_abordo == 4: # Debido a que esta programado por hilos debemos de filtrar si los pasajeros ya están completos.
                                                   # Esto debido a que podrian agregarse 2 hackers y 2 serfs o 1 hacker, 1 serf, 1 hacker, 1 serf
                                                   # El orden dependerá del orden de ejecución de los hilos y del programa mismo.
                cruzar_rio() # Si ya están los 4 pasajeros, entonces llamamos a la animación

        time.sleep(3)
        semaforo_balsa.release() # Incrementamos el valor del semáforo, con ello hacemos que un hilo menos pueda entrar hasta que se cumpla la condición de 4.

# Función para que un serf intente subir a la balsa
# Al igual que la función hacker (linea 25) tendremos la misma lógica, en donde controlaremos el ingreso de los hilos y que no ingresen dos o más hilos.
def serf(id_serf):
    global serfs_abordo

    while True:
        time.sleep(1) 
        semaforo_balsa.acquire()

        with mutex:
            serfs_abordo += 1
            personas_balsa.append(f"Serf_{id_serf}")
            actualizar_estado_balsa(f"Serf {id_serf} sube a la balsa")
            mostrar_estado_sincronizacion(f"Mutex adquirido por Serf {id_serf} - {serfs_abordo} serfs abordo")
            animar_subida(len(personas_balsa) - 1, "Serf", id_serf)
            
            if hackers_abordo + serfs_abordo == 4:
                cruzar_rio()

        time.sleep(3)
        semaforo_balsa.release()

# Validar la entrada del usuario
def validar_entrada():
    try:
        num_hackers = int(hackers_entry.get())
        num_serfs = int(serfs_entry.get())
        
        # Caso válido: 2 hackers y 2 serfs, o solo hackers o solo serfs
        if (num_hackers == 2 and num_serfs == 2) or (num_hackers == 4 and num_serfs == 0) or (num_hackers == 0 and num_serfs == 4): # Caso Base
            # Limpiar y ocultar los campos de entrada
            hackers_entry.delete(0, tk.END)
            serfs_entry.delete(0, tk.END)
            hackers_entry.grid_forget()  
            serfs_entry.grid_forget()  
            boton_iniciar.grid_forget()  
            actualizar_numero_personas(num_hackers, num_serfs)  
            iniciar_simulacion(num_hackers, num_serfs) # IMPORTANTE !!! En caso de que la entrada sea válida llamaremos al hilo principal en la función iniciar_simulacion.

        # Caso no válido: 3 hackers y 1 serf o 1 hacker y 3 serfs
        elif (num_hackers == 3 and num_serfs == 1) or (num_hackers == 1 and num_serfs == 3): # Para que hackers y serfs no se peguen.
            actualizar_estado_balsa("CUIDADO!!! Se van a pelear. Combinación no válida")

        # Cualquier otro caso no válido
        else:
            actualizar_estado_balsa("Combinación no válida. Deben ser 4 personas en total.")
    
    except ValueError: # En caso de que se metan entradas extrañas
        actualizar_estado_balsa("Por favor ingrese números válidos.")

# Iniciar la simulación con los números proporcionados por el usuario
def iniciar_simulacion(num_hackers, num_serfs): 
    threading.Thread(target=simular_hackers_y_serfs, args=(num_hackers, num_serfs), daemon=True).start() # Hilo principal que llevará a cabo la llamada a la función simular_hackers_y_serfs

def simular_hackers_y_serfs(num_hackers, num_serfs):
    actualizar_estado_balsa(f"Simulación iniciada: {num_hackers} hackers y {num_serfs} serfs.")
    
    for i in range(num_hackers):
        threading.Thread(target=hacker, args=(i,), daemon=True).start() # Hilo para hackers.

    for i in range(num_serfs):
        threading.Thread(target=serf, args=(i,), daemon=True).start() # Hilo para serfs.



# -------------------------------------------------- APARTADO DE INTERFAZ CON TKINTER --------------------------------------------------

def actualizar_estado_balsa(mensaje):
    balsa_estado.config(state=tk.NORMAL)
    balsa_estado.insert(tk.END, f"{mensaje}\n")
    balsa_estado.config(state=tk.DISABLED)
    ventana.update()

def mostrar_estado_sincronizacion(mensaje):
    estado_sincronizacion.config(state=tk.NORMAL)
    estado_sincronizacion.insert(tk.END, f"{mensaje}\n")
    estado_sincronizacion.config(state=tk.DISABLED)
    ventana.update()

def actualizar_numero_personas(num_hackers, num_serfs):
    numero_hackers.config(text=f"Número de Hackers: {num_hackers}")
    numero_serfs.config(text=f"Número de Serfs: {num_serfs}")
    ventana.update()

def cruzar_rio():
    global hackers_abordo, serfs_abordo
    actualizar_estado_balsa("La balsa está cruzando el río...")
    mostrar_estado_sincronizacion("Semáforo liberado, cruzando el río")

    for i in range(50):
        canvas.move(balsa_dibujo, 5, 0)
        for persona in personas_balsa:
            canvas.move(f"{persona}", 5, 0)  
        ventana.update()
        time.sleep(0.05)
    time.sleep(2)

    for persona in personas_balsa:
        canvas.delete(persona)
    actualizar_estado_balsa("Personas han bajado, la balsa regresa vacía")
    ventana.update()

    time.sleep(2)
    for i in range(50):  
        canvas.move(balsa_dibujo, -5, 0)
        ventana.update()
        time.sleep(0.05)

    reiniciar_simulacion()

def reiniciar_simulacion():
    global hackers_abordo, serfs_abordo, personas_balsa
    hackers_abordo = 0
    serfs_abordo = 0
    personas_balsa.clear()
    
    canvas.delete("all")
    redibujar_balsa()

    actualizar_estado_balsa("Balsa regresó vacía. Ingrese nueva entrada.")


def redibujar_balsa():
    global balsa_dibujo
    balsa_dibujo = canvas.create_rectangle(0, 160, 350, 200, fill="brown")

def animar_subida(i, persona, id_persona):
    color = "blue" if persona == "Hacker" else "green"
    x0, y0, x1, y1 = 60 + i * 50, 300, 100 + i * 50, 340
    
    for step in range(20):
        canvas.delete(f"{persona}_{id_persona}")
        y0 -= 7 
        y1 -= 7
        canvas.create_oval(x0, y0, x1, y1, fill=color, tags=f"{persona}_{id_persona}")
        ventana.update()
        time.sleep(0.05)

# -------------------------------------------------- FORMATO DE LA INTERFAZ --------------------------------------------------

ventana = tk.Tk()
ventana.title("Simulación de Cruce en Balsa")
ventana.geometry("800x700")
ventana.configure(bg="white")

titulo = tk.Label(ventana, text="Simulación de Cruce en Balsa", font=("Arial", 18), bg="white")
titulo.pack(pady=10)

canvas = tk.Canvas(ventana, width=600, height=200, bg="lightblue")
canvas.pack(pady=10)

redibujar_balsa()

estado_frame = tk.Frame(ventana, bg="white")
estado_frame.pack()

# Sección de estado de sincronización
estado_sincronizacion_label = tk.Label(estado_frame, text="Estado del Semáforo y Mutex", font=("Arial", 12), bg="white", fg="green")
estado_sincronizacion_label.grid(row=0, column=0, padx=10, pady=5)

estado_sincronizacion = tk.Text(estado_frame, height=15, width=100, state=tk.DISABLED, bg="lightgrey")
estado_sincronizacion.grid(row=1, column=0, padx=10, pady=5)

# Sección de estado de la balsa
balsa_estado_label = tk.Label(estado_frame, text="Estado de la Balsa", font=("Arial", 12), bg="white", fg="blue")
balsa_estado_label.grid(row=2, column=0, padx=10, pady=5)

balsa_estado = tk.Text(estado_frame, height=15, width=100, state=tk.DISABLED, bg="lightgrey")
balsa_estado.grid(row=3, column=0, padx=10, pady=5)

form_frame = tk.Frame(ventana, bg="white")
form_frame.pack(pady=10)

tk.Label(form_frame, text="Número de Hackers:", bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
hackers_entry = tk.Entry(form_frame)
hackers_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Número de Serfs:", bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
serfs_entry = tk.Entry(form_frame)
serfs_entry.grid(row=1, column=1, padx=5, pady=5)

boton_iniciar = tk.Button(form_frame, text="Iniciar Simulación", bg="lightgreen", command=lambda: (validar_entrada()))
boton_iniciar.grid(row=2, columnspan=2, pady=10)

numero_hackers = tk.Label(ventana, text="", font=("Arial", 12), bg="white")
numero_hackers.pack()

numero_serfs = tk.Label(ventana, text="", font=("Arial", 12), bg="white")
numero_serfs.pack()

ventana.mainloop()
