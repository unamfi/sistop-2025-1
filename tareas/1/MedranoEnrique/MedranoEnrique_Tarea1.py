""" Problema 5 (El servidor Web)
Alumno: Medrano Solano Enrique
Materia: Sistemas Operativos

Python 3.12.7
Programa hecho en Visual Studio Code / Windows 11

Este programa busca dar con una solución para una interacción entre
jefes y trabajadores utilizando métodos de sincronización
Para este caso se utilizaron queue para tener control de las tareas
y se emplearon semaforos para los estados de los trabajadores
durnate las tareas"""

#Se agregan librerias a utilizar
import threading #Hilos
import queue #Colas
import time
import random

#Numéro de trabajadores | variable modificable
k = 5

#Creación de una cola para el control de las tareas
tareas_colas = queue.Queue()

#Mediante la librería theading se agrega un semaforo y una condición para el estado de los empleados
#Dormido | despierto
semaforo = threading.Semaphore(0)
condicion = threading.Condition()


#Clase de trabajadores
class trabajadores(threading.Thread):
    """Clase para la definición de los trabajores y los distintos estados que tienen
    cuando la cola esta vacía los trabajores inicializados por el jefe (k) estan en
    estado dormido, una vez que la condición cambie y en la cola se asigne una tarea,
    uno de los empleados cambia a estado despierto y pasa a procesando tarea, una vez
    pasado tiempo, pasa al estado de tarea terminada"""

    def __init__(self, trabajador_id):
        threading.Thread.__init__(self)
        self.trabajador_id = trabajador_id
        self.daemon = True
    
    def run(self):
        while True:
            with condicion:
                print(f"Hilo {self.trabajador_id} está mimiendo 💤💤")
            semaforo.acquire() #Espera aprobación del semaforo para pasar de estado
            tarea = tareas_colas.get()
            
            if tarea is None:
                break #Si no hya tareas se termina el hilo asignado
            print(f"Hilo{self.trabajador_id} esta en proceso de la tarea:{tarea} 👨‍💻👨‍💻")
            #Se simula el tiempo que se tarda en realizar la tarea asignada
            time.sleep(random.uniform(0.1, 0.5))
            print(f"Hilo {self.trabajador_id} ha terminado la tarea:{tarea} ✔️✔️")
            tareas_colas.task_done() #Se guardan las tareas finalizadas

#Clase de jefe
class jefe:
    def __init__(self, num_trabajadores):
        self.num_trabajadores = num_trabajadores
        self.trabajadores = [trabajadores(i+1) for i in range(num_trabajadores)]

    def inicio_trabajadores(self):
        #Se inicializan los hilos de los trabajores mediante un for
        for trabajador in self.trabajadores:
            trabajador.start()
    
    def asignacion_tareas(self, tarea):
        #Asignación de tareas, se guardan en queue y se distribuyen en cualquier trabajador disponible
        print(f"Jefe asigna tarea: {tarea} ⚒️⚒️")
        with condicion:
            tareas_colas.put(tarea)
            #Se cambia de estado el trabajador una vez asignada tarea disponible
            semaforo.release()

#Inicialización de ambos papeles
jefazo = jefe(k)
jefazo.inicio_trabajadores()

#Simulación de asignación y creación de tareas de forma aleatoria como si fuera el servidor web
tarea_id = 0
try:
    while True:
        tarea_id += 1
        jefazo.asignacion_tareas(tarea_id)
        #Se establece un tiempo aleatorio entre tareas asignadas
        time.sleep(random.uniform(0.1, 0.5))
except KeyboardInterrupt:
    print(f"Finalización forzada del programa ⚠️⚠️⚠️")
finally:
    #Esperar a que se completen todas las tareas insertadas en la cola
    tareas_colas.join()
    #Finalización de hilos
    for i in range(k):
        jefazo.asignacion_tareas(None) #Se terminan las tareas para los empleados
    #Finalización de tareas
    for trabajador in jefazo.trabajadores:
        trabajador.join()
