import threading
import queue
import time
import random

# Número de trabajadores que el jefe mantiene activos
K = 3

# Definir número total de tareas a procesar
NUM_TAREAS = int(input("Ingrese el número total de tareas a procesar: "))

# Cola de tareas que contiene las solicitudes a atender
task_queue = queue.Queue()

# Evento para despertar a los trabajadores
new_task_event = threading.Event()

# Semáforo para controlar el número de trabajadores activos
available_workers = threading.Semaphore(K)

# Variable para contar tareas completadas
tareas_completadas = 0
tareas_completadas_lock = threading.Lock()

# Función del trabajador
def worker(worker_id):
    global tareas_completadas
    while True:
        # Espera hasta que haya una nueva tarea
        new_task_event.wait()

        # Adquiere el semáforo para verificar que pueda atender la tarea
        with available_workers:
            try:
                # Intenta obtener una tarea de la cola si está disponible
                task = task_queue.get_nowait()
                print(f"Trabajador {worker_id} atendiendo solicitud: {task}")
                
                # Simula el tiempo de procesamiento de la tarea
                time.sleep(random.uniform(0.5, 1.5))  
                
                print(f"Trabajador {worker_id} completó solicitud: {task}")
                
                # Marca la tarea como completada
                task_queue.task_done()
                
                # Incrementa el contador de tareas completadas de forma segura
                with tareas_completadas_lock:
                    tareas_completadas += 1
            except queue.Empty:
                # Si no hay tarea, el trabajador vuelve a dormir
                print(f"Trabajador {worker_id} no encontró tarea y vuelve a dormir.")

# Función del jefe
def jefe():
    global tareas_completadas
    
    # Inicia los hilos trabajadores
    for i in range(K):
        threading.Thread(target=worker, args=(i,), daemon=True).start()

    task_id = 1
    while task_id <= NUM_TAREAS:
        # Simula la llegada de una solicitud de red con mayor espera entre solicitudes
        time.sleep(random.uniform(8, 12))
        print(f"Jefe: Nueva solicitud recibida, asignando tarea {task_id}")

        # Coloca la solicitud en la cola
        task_queue.put(f"Tarea-{task_id}")

        # Despierta a un trabajador para que atienda la solicitud
        new_task_event.set()

        # Incrementa el ID de la tarea
        task_id += 1

        # Reset el evento si ya no hay tareas pendientes para evitar que todos los trabajadores sigan despiertos
        if task_queue.empty():
            new_task_event.clear()

    # Espera hasta que todas las tareas sean completadas
    task_queue.join()
    while True:
        # Verifica si todas las tareas fueron completadas
        with tareas_completadas_lock:
            if tareas_completadas == NUM_TAREAS:
                print("Jefe: Todas las tareas han sido completadas. Finalizando el programa.")
                break

# Inicia el proceso jefe
jefe_thread = threading.Thread(target=jefe)
jefe_thread.start()

# Mantenemos el programa en ejecución para ver la interacción entre jefe y trabajadores
jefe_thread.join()
