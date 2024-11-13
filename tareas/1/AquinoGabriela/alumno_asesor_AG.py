import threading
import time
import random

CAPACIDAD_SALON = 3  # Capacidad 
num_sillas_ocupadas = 0  #Sillas ocupadas

# Banderas
sem_profesor = threading.Semaphore(0)  # Estado del profesor: Activo
mutex = threading.Semaphore(1)  # Num_sillas_ocupadas
sem_duda = threading.Semaphore(0)  # Dudas
sem_alumno = threading.Semaphore(0)  # Alumnos presentes

# Función del profesor
def profesor():
    while True:
        print("Profesor : Esperando alumnos...")
        sem_alumno.acquire()  # Esperando
        print("Profesor : Un alumno ha llegado, listo para resolver dudas.")
        sem_profesor.release()  # Estado del profesor: Activo
        resolver_duda()

# Función para los alumnos
def alumno(id_alumno):
    global num_sillas_ocupadas
    dudas_restantes = random.randint(1, 2)  # Genera un número aleatorio de dudas
    flag_entrado = False  # Bandera para verificar si ya está dentro del salón

    print(f"\nAlumno {id_alumno}: Llegue y tengo {dudas_restantes} duda(s).")

    while dudas_restantes > 0:
        mutex.acquire()  # Num_sillas_ocupadas

        # Verifica si hay espacio en el salón
        if num_sillas_ocupadas >= CAPACIDAD_SALON and not flag_entrado:
            print(f"Alumno {id_alumno}: Sin espacio, esperaré fuera. ")
            mutex.release()
            sem_duda.acquire()  # Espera hasta que pueda resolver la duda
        elif flag_entrado:
            print(f"Alumno {id_alumno}: Esperando mi turno en el salón ")
            mutex.release()
            sem_duda.acquire()  # Espera para resolver otra duda
        else:
            # Si hay espacio, entra
            flag_entrado = True
            num_sillas_ocupadas += 1
            print(f"\nAlumno {id_alumno}: Entra al salón. Sillas ocupadas: {num_sillas_ocupadas}")
            mutex.release()

        # Verifica que el alumno está listo para resolver dudas
        sem_alumno.release()
        # Espera al profesor para resolver la duda
        sem_profesor.acquire()

        # Resuelve la duda
        dudas_restantes -= 1
        print(f"\nAlumno {id_alumno}: Duda resuelta, Tengo aun {dudas_restantes} duda(s).")

        # Bandera activa de duda para el siguiente alumno
        sem_duda.release()

    # Al tener dudas resueltas
    mutex.acquire()
    num_sillas_ocupadas -= 1
    print(f"Alumno {id_alumno}: Sin dudas. Sillas ocupadas: {num_sillas_ocupadas}")
    mutex.release()

# Resolución de dudas
def resolver_duda():
    print("Profesor: ...Resolviendo duda... ")
    time.sleep(0.5)  # Tiempo para resolver duda

# Hilo profesor
threading.Thread(target=profesor).start()

# Hilo alumno
for i in range(5):
    threading.Thread(target=alumno, args=(i,)).start()
