#Arellanes Conde Esteban
#Esquivel Santana Christian
import threading
import time
import random

# Variables compartidas
elfos_problema = 0  # Cuenta de elfos con problemas
renos_de_vuelta = 0  # Cuenta de renos que han regresado
mutex = threading.Lock()  # Mutex para proteger variables compartidas
santa_cond = threading.Condition(mutex)  # Condición para despertar a Santa
elfos_sem = threading.Semaphore(0)  # Semáforo para coordinar a los elfos

# Número total de elfos y renos (se pueden cambiar por el que se desee)
NUM_ELFOS = 10
NUM_RENOS = 9

# Variable para terminar
terminar = False

def log(message):
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{current_time}] {message}\n") 

# Función para el comportamiento de Santa Claus
def santa_claus():
    global elfos_problema, renos_de_vuelta, terminar
    while True:
        with santa_cond:
            # Esperar hasta que haya 3 elfos con problemas o los 9 renos estén de vuelta
            santa_cond.wait_for(lambda: elfos_problema >= 3 or renos_de_vuelta == NUM_RENOS)
            if renos_de_vuelta == NUM_RENOS:
                log("Santa Claus: ¡Es hora de repartir los regalos!")
                terminar = True  # Establecer la variable de "terminar"
                renos_de_vuelta = 0  # Reiniciar la cuenta de renos
                # Notificar a todos los elfos y renos para continuar su trabajo
                santa_cond.notify_all()
                # También liberar el semáforo para que los elfos que estaban esperando puedan terminar
                for _ in range(elfos_problema):  # Liberar el semáforo para los elfos con problemas
                    elfos_sem.release()
                break  # Salir del bucle de Santa
            elif elfos_problema >= 3:
                log("Santa Claus: Ayudando a 3 elfos con problemas")
                # Permitir que los tres elfos continúen
                for _ in range(3):
                    elfos_sem.release()  # Liberar el semáforo para permite que los elfos sigan trabajando 
                elfos_problema = 0 

def elfo(elfo_id):
    global elfos_problema, terminar
    while True:
        log(f"Elfo {elfo_id}: Estoy trabajando...") 
        time.sleep(random.uniform(1, 5)) 
        if terminar:
            break  # Salir si Santa ha repartido los regalos (ya son libres!)
        if random.random() < 0.3:  # 30% de probabilidad de tener un problema (se puede cambiar por el porcentaje que se desee)
            with mutex:
                elfos_problema += 1
                log(f"Elfo {elfo_id}: Tengo un problema, hay {elfos_problema} elfos con problemas")
                if elfos_problema == 3:
                    # Despertar a Santa Claus
                    santa_cond.notify_all()
            # Esperar a que Santa resuelva el problema
            elfos_sem.acquire()  # Un elfo con un problema no puede seguir trabajando :(
        else:
            log(f"Elfo {elfo_id}: Todo está bien, sigo trabajando.")

        # Revisar si se debe salir después de intentar adquirir el semáforo
        if terminar:
            break



# Función para el comportamiento de los renos
def reno():
    global renos_de_vuelta, terminar
    while True:
        time.sleep(random.uniform(5, 10))  # El reno regresa después de un tiempo aleatorio
        if terminar:
            break  # Salir si Santa ha repartido los regalos
        with mutex:
            renos_de_vuelta += 1
            log(f"Reno: He regresado, hay {renos_de_vuelta} renos de vuelta")
            if renos_de_vuelta == NUM_RENOS:
                # Despertar a Santa Claus
                santa_cond.notify_all()

# Crear hilos
santa = threading.Thread(target=santa_claus)
elfos = [threading.Thread(target=elfo, args=(i,)) for i in range(NUM_ELFOS)]
renos = [threading.Thread(target=reno) for _ in range(NUM_RENOS)]

# Iniciar hilos
santa.start()
for e in elfos:
    e.start()
for r in renos:
    r.start()

# Esperar a que Santa termine
santa.join()
# Notificar a los elfos y renos que deben terminar
for e in elfos:
    e.join()
for r in renos:
    r.join()
