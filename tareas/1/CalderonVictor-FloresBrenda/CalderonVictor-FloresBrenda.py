import threading
import random
import time
from queue import Queue

NUM_SILLAS = 5
MAX_DUDAS = 3

cola_alumnos = Queue()
cola_dudas = Queue()

despertar_profesor = threading.Semaphore(0)
mutex_cubiculo = threading.Semaphore(NUM_SILLAS)
mutex_orden = threading.Lock()

alumnos_atendidos = 0
alumnos_totales = 7

def alumno(id):
    global alumnos_atendidos
    while True:
        num_dudas = random.randint(1, MAX_DUDAS)
        time.sleep(random.random())
        print(f'Toc Toc ... Soy el alumno {id}, ¿Puedo pasar, profe?')
        mutex_cubiculo.acquire()
        cola_alumnos.put(id)
        cola_dudas.put(num_dudas)
        despertar_profesor.release()
        print(f'Alumno {id} entrando con {num_dudas} dudas')

        while num_dudas > 0:
            with mutex_orden:
                print(f'Alumno {id}: Mi duda es...')
                time.sleep(random.uniform(1, 3))
                print(f'Profesor: Respondiendo la duda del alumno {id}')
                time.sleep(random.uniform(1, 3))
                num_dudas -= 1
                if num_dudas > 0:
                    print(f'Alumno {id}: Me queda {num_dudas} duda(s), cedo el turno a otro.')
                    mutex_orden.release()
                    time.sleep(random.uniform(1, 3))
                    mutex_orden.acquire()

        print(f'Alumno {id} ha terminado y se va')
        mutex_cubiculo.release()
        alumnos_atendidos += 1
        break

def profesor():
    global alumnos_atendidos
    print('Profesor: zzzz ... Durmiendo hasta que llegue un alumno')
    while alumnos_atendidos < alumnos_totales:
        despertar_profesor.acquire()

        if not cola_alumnos.empty():
            alumno_id = cola_alumnos.get()
            num_dudas = cola_dudas.get()
            print(f'Profesor ayudando al alumno {alumno_id} con {num_dudas} dudas restantes')
            time.sleep(random.uniform(1, 3))

    print('Profesor: Terminé mi turno, todos los alumnos se fueron.')

profesor_thread = threading.Thread(target=profesor)
profesor_thread.start()

for alumno_id in range(alumnos_totales):
    threading.Thread(target=alumno, args=[alumno_id + 1]).start()
