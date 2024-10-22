import threading
import random
import time
from queue import Queue

# Número máximo de sillas en el cubículo y preguntas por alumno
NUM_SILLAS = 5
MAX_DUDAS = 3

# Colas para manejar a los alumnos y sus preguntas en orden de llegada
cola_alumnos = Queue()
cola_dudas = Queue()

# Semáforos y locks para la sincronización
despertar_profesor = threading.Semaphore(0)  # Para despertar al profesor cuando hay alumnos
mutex_cubiculo = threading.Semaphore(NUM_SILLAS)  # Controla cuántos alumnos pueden estar en el cubículo
mutex_orden = threading.Lock()  # Controla que solo un alumno interactúe con el profesor a la vez

alumnos_atendidos = 0  # Contador de alumnos atendidos
alumnos_totales = 7  # Número total de alumnos que se van a asesorar

def alumno(id):
    global alumnos_atendidos
    while True:
        # Cada alumno tiene un número aleatorio de preguntas
        num_dudas = random.randint(1, MAX_DUDAS)
        time.sleep(random.random())  # Simula la llegada del alumno

        print(f'Toc Toc ... Soy el alumno {id}, ¿Puedo pasar, profe?')
        mutex_cubiculo.acquire()  # Intenta entrar al cubículo (si hay sillas disponibles)

        # Agregar el alumno y sus dudas a las colas correspondientes
        cola_alumnos.put(id)
        cola_dudas.put(num_dudas)

        # Despertar al profesor
        despertar_profesor.release()

        print(f'Alumno {id} entrando con {num_dudas} dudas')

        # Mientras el alumno tenga preguntas pendientes
        while num_dudas > 0:
            with mutex_orden:  # Controla que solo un alumno haga preguntas a la vez
                print(f'Alumno {id}: Mi duda es...')
                time.sleep(random.uniform(1, 3))  # Simula el tiempo para hacer la pregunta
                print(f'Profesor: Respondiendo la duda del alumno {id}')
                time.sleep(random.uniform(1, 3))  # Simula el tiempo de respuesta del profesor
                num_dudas -= 1  # Resta una duda al número total de dudas del alumno

                # Si el alumno aún tiene dudas, cede el turno a otro
                if num_dudas > 0:
                    print(f'Alumno {id}: Me queda {num_dudas} duda(s), cedo el turno a otro.')
                    mutex_orden.release()  # Libera el lock para que otro alumno haga preguntas
                    time.sleep(random.uniform(1, 3))  # Espera antes de hacer su próxima pregunta
                    mutex_orden.acquire()  # Vuelve a adquirir el lock para su siguiente pregunta

        print(f'Alumno {id} ha terminado y se va')
        mutex_cubiculo.release()  # Libera su silla cuando se va
        alumnos_atendidos += 1  # Incrementa el contador de alumnos atendidos
        break

def profesor():
    global alumnos_atendidos
    print('Profesor: zzzz ... Durmiendo hasta que llegue un alumno')

    # Mientras no se hayan atendido a todos los alumnos
    while alumnos_atendidos < alumnos_totales:
        despertar_profesor.acquire()  # El profesor espera hasta ser despertado por un alumno

        # Si hay alumnos en la cola, el profesor atiende al siguiente alumno
        if not cola_alumnos.empty():
            alumno_id = cola_alumnos.get()  # Obtiene el ID del siguiente alumno
            num_dudas = cola_dudas.get()  # Obtiene el número de dudas del alumno

            print(f'Profesor ayudando al alumno {alumno_id} con {num_dudas} dudas restantes')
            time.sleep(random.uniform(1, 3))  # Simula el tiempo de asesoría con el alumno

    print('Profesor: Terminé mi turno, todos los alumnos se fueron.')

# Inicialización de los hilos del profesor y los alumnos
profesor_thread = threading.Thread(target=profesor)
profesor_thread.start()

# Creación de hilos para cada alumno
for alumno_id in range(alumnos_totales):
    threading.Thread(target=alumno, args=[alumno_id + 1]).start()
