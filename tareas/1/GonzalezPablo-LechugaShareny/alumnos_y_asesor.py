#Gonzalez Cuellar Pablo Arturo
#Lechuga Castillo Shareny Ixchel

#Ejercicio de Sincronizacion - Alumnos y Asesor

#Librerías a utilizar
import threading
import time
import random

# Parámetros del problema
n_sillas = 3  # Número de sillas en el cubículo
n_estudiantes = 5  # Número de estudiantes que quieren entrar
tiempo_pregunta = 1  # Tiempo que tarda el profesor en responder cada pregunta
max_preguntas = 2  # Número máximo de preguntas que cada estudiante puede hacer

# Semáforo para las sillas disponibles
sillas = threading.Semaphore(n_sillas)

# Lock para la interacción con el profesor
lock_profesor = threading.Lock()

# Estado del profesor (dormido o despierto)
profesor_durmiendo = threading.Event()

def estudiante(id_estudiante):
    try:
        print(f'Estudiante {id_estudiante} llega al cubículo.')

        # Estudiante intenta ocupar una silla
        sillas.acquire()
        print(f'El estudiante {id_estudiante} se sienta y espera su turno.')

        # Una vez sentado, espera su turno para preguntar
        with lock_profesor:
            print(f'El estudiante {id_estudiante} pregunta al profesor.')
            profesor_durmiendo.set()  # Despertar al profesor si está dormido

            # Simular preguntas
            for i in range(random.randint(1, max_preguntas)):
                print(f'Estudiante {id_estudiante} hace la pregunta {i+1}.')
                time.sleep(tiempo_pregunta)  # Tiempo de respuesta del profesor

            print(f'El estudiante {id_estudiante} ha terminado de preguntar.')

        # Dejar la silla a otro estudiante
        sillas.release()
        print(f'El estudiante {id_estudiante} deja la silla y se va.')

    except Exception as e:
        print(f'Error con el estudiante {id_estudiante}: {e}')
        sillas.release()  ##Excepcion por si llega a fallar el hilo

def profesor():
    while True:
        try:
            # El profesor duerme si no hay estudiantes
            if not profesor_durmiendo.is_set():
                print('El profesor está durmiendo...')
                profesor_durmiendo.wait()  # Esperar hasta que un estudiante toque la puerta

            print('El profesor está despierto y atendiendo a los estudiantes.')
            # Después de atender a los estudiantes, vuelve a dormir si no hay más
            time.sleep(1)
            profesor_durmiendo.clear()  # Dormir si no hay más estudiantes
        
        except Exception as e:
            print(f'Error en el hilo del profesor: {e}')
            #Excepcion por si llega a fallar el hilo


# Crear e iniciar los hilos de los estudiantes
for i in range(n_estudiantes):
    threading.Thread(target=estudiante, args=(i,)).start()

# Iniciar el hilo del profesor
threading.Thread(target=profesor, daemon=True).start()