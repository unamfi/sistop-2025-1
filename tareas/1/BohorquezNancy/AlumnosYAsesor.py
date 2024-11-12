import time
import threading
from random import random, randint

# Parametros del problema
num_estudiantes = 15
num_sillas = 4
max_preguntas = 5

# Semaforos y mutex
sillas_libres = threading.Semaphore(num_sillas) 
mutex_profesor = threading.Semaphore(1) 
profesor_durmiendo = threading.Semaphore(0) 
mut_contador = threading.Semaphore(1)  
contador_estudiantes = 0 

class Estudiante():
    def _init_(self, id_estudiante):
        self.id = id_estudiante
        self.preguntas_restantes = randint(1, max_preguntas)
        self.reporta('Llegué al cubículo.')

        # Sentarse
        if not sillas_libres.acquire(timeout=1):
            self.reporta('No hay sillas disponibles. Me voy.')
            return

        self.reporta('Me senté en una silla.')
        global contador_estudiantes
        with mut_contador:
            contador_estudiantes += 1

        # Despertar al profesor
        profesor_durmiendo.release()

        # Preguntar
        while self.preguntas_restantes > 0:
            
            with mutex_profesor:
                self.reporta('Voy a hacer una pregunta.')
                time.sleep(random()) 
                self.reporta('El profesor respondió.')
                self.preguntas_restantes -= 1

            if self.preguntas_restantes > 0:
                self.reporta('Cedo mi turno para que otro pregunte.')
                time.sleep(random())

        # Levantarse al teminar de preguntar
        self.reporta('Terminé todas mis preguntas y me voy.')
        sillas_libres.release()
        with mut_contador:
            contador_estudiantes -= 1

    def reporta(self, msg):
        print(f'Estudiante {self.id}: {msg}')


class Profesor():
    def _init_(self): 
        while True:
            
            self.reporta('Estoy durmiendo.')
            profesor_durmiendo.acquire()

            if contador_estudiantes > 0:
                self.reporta('Me desperté, hay estudiantes para atender.')

           
            while contador_estudiantes > 0:
                time.sleep(random()) 

            self.reporta('Todos los estudiantes se fueron. Volveré a dormir.')

    def reporta(self, msg):
        print(f'Profesor: {msg}')


# Hilo del profesor
hilo_profesor = threading.Thread(target=Profesor)
hilo_profesor.daemon = True
hilo_profesor.start()

# Hilos de los estudiantes
for i in range(num_estudiantes):
    threading.Thread(target=Estudiante, args=[i + 1]).start()

# Para que el Hilo principal no termine rapido
while True:
    time.sleep(1)