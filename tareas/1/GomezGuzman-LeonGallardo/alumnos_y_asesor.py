import threading
import time
import random
import logging

# Configuración básica de logging para registrar las preguntas y respuestas
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

x = 2  # Número de sillas en el cubículo (limite de alumnos esperando)
y = 2  # Máximo número de preguntas que un alumno puede hacer
max_intentos = 4  # Máximo número de intentos para un alumno

numero_pregunta = 1  # Inicializamos el número de pregunta
contador_lock = threading.Lock()  # Lock para asegurar que solo un hilo modifique el contador a la vez
profesor_lock = threading.Lock()  # Lock para asegurar que el profesor responde a una pregunta a la vez
sillas_disponibles = threading.Semaphore(x)  # Semáforo para limitar el número de alumnos en el cubículo

# Función que simula al alumno haciendo preguntas
def pregunta(alumno):
    global numero_pregunta  # Indicamos que vamos a modificar la variable global
    num_preguntas = random.randint(1, y)  # Cada alumno hace entre 1 y 'y' preguntas
    intentos = 0  # Contador de intentos

    while intentos < max_intentos:
        # Intentar sentarse en el cubículo
        if sillas_disponibles.acquire(blocking=False):
            logging.debug(f'El alumno {alumno} ha tomado asiento en el cubículo.')
            print(" ")
            time.sleep(1.5)

            for _ in range(num_preguntas):
                with contador_lock:  # Aseguramos que solo un hilo pueda modificar el contador a la vez
                    numero_actual = numero_pregunta
                    numero_pregunta += 1  # Incrementamos el contador de preguntas
                
                # El alumno espera su turno para hacer la pregunta
                with profesor_lock:  # Aseguramos que solo un alumno haga preguntas al mismo tiempo
                    logging.debug(f'Alumno {alumno} ha hecho la pregunta número {numero_actual} al profesor')
                    time.sleep(3)  # Simula el tiempo mientras el alumno hace la pregunta

                    # El profesor responde a la pregunta
                    logging.debug(f'El profesor está respondiendo la pregunta {numero_actual} del alumno {alumno}')
                    time.sleep(5)  # Simula el tiempo que tarda el profesor en responder
                
                # El alumno descansa y permite que otros alumnos hagan preguntas
                if _ < num_preguntas - 1:  # Si no es la última pregunta, se libera el turno para otros
                    logging.debug(f'El alumno {alumno} espera para hacer otra pregunta.')
                    time.sleep(random.randint(1, 3))  # Simulamos que el alumno espera antes de hacer otra pregunta

            logging.debug(f'El alumno {alumno} ha terminado sus preguntas y deja la silla.')
            print(" ")
            sillas_disponibles.release()  # Liberamos la silla cuando el alumno termina
            break  # El alumno termina y sale del ciclo

        else:
            time.sleep(6)
            intentos += 1
            print(" ")
            logging.debug(f'El alumno {alumno} busca alguna silla disponible ({intentos}/{max_intentos})')
            time.sleep(random.randint(1, 3))  # Simula un tiempo de espera antes de intentar de nuevo

    if intentos == max_intentos:
        print(" ")
        logging.debug(f'El alumno {alumno} se fue después de {max_intentos} intentos fallidos de encontrar asiento.')

# Creamos una lista de alumnos con su respectivo hilo
alumnos = [
    threading.Thread(name="alumno_1", target=pregunta, args=("Pablin",)),
    threading.Thread(name="alumno_2", target=pregunta, args=("Anikey",)),
    threading.Thread(name="alumno_3", target=pregunta, args=("Ian",)),
    threading.Thread(name="alumno_4", target=pregunta, args=("Luis",)),
]

# Desordenamos el orden de los alumnos usando random.shuffle
random.shuffle(alumnos)

logging.debug(f'El Profesor inicia la hora de las asesorías, entrando al aula')
logging.debug(f'El Profesor junta las sillas en lo que llegan los alumnos y toma descanso')
print(" ")

time.sleep(3)  # Simula el tiempo que tarda el profesor en responder

# Función para iniciar los hilos de los alumnos
def iniciadorPreguntas():
    for iterador in alumnos:
        iterador.start()

# Llamamos a la función para iniciar los hilos de los alumnos
iniciadorPreguntas()

# Esperar a que todos los hilos terminen
for alumno in alumnos:
    if alumno.is_alive():  # Solo unir los hilos que fueron iniciados
        alumno.join()

logging.debug('Fin de las preguntas y respuestas')
