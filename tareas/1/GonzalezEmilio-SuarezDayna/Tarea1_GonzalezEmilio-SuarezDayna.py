"""
Tarea 1

Gonzalez Iniestra Emilio
Suarez Guzman Dayna Yarelly
"""
import threading
import time
import random
import colorama

# Parámetros
num_renos = 9
num_elfos = 30
elfos_por_grupo = 3

# Semáforos y mutex para control
santa_sem = threading.Semaphore(0)
renos_sem = threading.Semaphore(0)
elfos_ayuda_sem = threading.Semaphore(0)
renos_listos = threading.Semaphore(0)
elfos_listos = threading.Semaphore(0)

# Barreras para sincronización
renosBarrera = threading.Barrier(num_renos)
elfosBarrera = threading.Barrier(elfos_por_grupo)

# Mutex para acceso seguro a recursos compartidos
mutex = threading.Semaphore(1)

class SantaClaus:
    def __init__(self):
        self.mi_color = colorama.Fore.RED + colorama.Back.WHITE

    def imprimir(self, mensaje):
        print(self.mi_color + "Santa: " + mensaje + "\n" + colorama.Fore.RESET + colorama.Back.RESET)

    def dormir(self):
        while True:
            self.imprimir("💤 Durmiendo...")
            santa_sem.acquire()  # Espera a que los renos o elfos lo despierten
            self.imprimir("🎅 Desperté!")
            time.sleep(1)  # Retardo para simular que Santa toma su tiempo para despertarse
            self.accion_santa()  # Realiza la acción que corresponda

    def accion_santa(self):
        # Santa debe ayudar a los elfos o repartir regalos sin secuencias
        mutex.acquire()

        # Despertar basado en cuál semáforo se libera primero
        if renos_listos.acquire(blocking=False):
            self.repartir_regalos()  # Reparte regalos cuando los 9 renos estén listos
        elif elfos_listos.acquire(blocking=False):
            self.ayudar_elfos()  # Ayuda a los 3 elfos cuando están listos

        mutex.release()

    def repartir_regalos(self):
        self.imprimir("¡Todos los renos están de vuelta, es hora de repartir regalos! 🦌🎁")
        for _ in range(num_renos):
            renos_sem.release()  # Libera a los renos para repartir regalos

        for _ in range(num_renos):
            renos_sem.acquire()

        self.imprimir("¡Repartí todos los regalos, ahora a dormir! 😴")
        time.sleep(2)  # Retardo después de repartir regalos

    def ayudar_elfos(self):
        self.imprimir("¡Tres elfos tienen problemas, voy a ayudar! 🧝‍♂️🎄")
        for _ in range(elfos_por_grupo):
            elfos_ayuda_sem.release()  # Libera a los elfos para que Santa los ayude
        time.sleep(2)  # Retardo después de ayudar a los elfos


class Reno:
    def __init__(self, id_reno):
        self.id = id_reno
        self.mi_color = colorama.Fore.GREEN + colorama.Back.WHITE

    def imprimir(self, mensaje):
        print(self.mi_color + "Reno {}: {}\n".format(self.id + 1, mensaje) + colorama.Fore.RESET + colorama.Back.RESET)

    def vacaciones(self):
        time.sleep(random.randint(5, 10))  # Simula las vacaciones de manera aleatoria
        self.imprimir("¡He vuelto de vacaciones! 🌴")

        # Todos los renos deben llegar a la barrera
        renosBarrera.wait()  # Espera a que todos los renos lleguen
        renos_listos.release()  # Despierta a Santa si todos los renos están de vuelta
        santa_sem.release()  # Despierta a Santa

        renos_sem.acquire()  # Espera a que Santa los libere para repartir regalos
        self.imprimir("¡Repartiendo regalos con Santa! 🎁")
        renos_sem.release()  # Notifica a Santa que ha terminado de repartir
        time.sleep(1)  # Retardo para que el proceso no ocurra de inmediato


class Elfo:
    def __init__(self, id_elfo):
        self.id = id_elfo
        self.mi_color = colorama.Fore.BLUE + colorama.Back.WHITE

    def imprimir(self, mensaje):
        print(self.mi_color + "Elfo {}: {}".format(self.id + 1, mensaje) + "\n" + colorama.Fore.RESET + colorama.Back.RESET)

    def trabajar(self):
        while True:
            time.sleep(random.randint(2, 6))  # Simula el trabajo de los elfos
            self.imprimir("¡Tengo un problema con los juguetes! 🧸")

            # Todos los elfos deben llegar a la barrera en grupos de 3
            elfosBarrera.wait()  # Espera a que tres elfos necesiten ayuda
            elfos_listos.release()  # Despierta a Santa cuando tres elfos tienen problemas
            santa_sem.release()  # Despierta a Santa

            elfos_ayuda_sem.acquire()  # Espera a que Santa lo ayude
            self.imprimir("¡Gracias Santa por la ayuda! 🎄")
            time.sleep(1)  # Retardo para simular que los elfos siguen trabajando después


def iniciar_renos():
    for i in range(num_renos):
        reno = Reno(i)
        threading.Thread(target=reno.vacaciones).start()

def iniciar_elfos():
    for i in range(num_elfos):
        elfo = Elfo(i)
        threading.Thread(target=elfo.trabajar).start()

def main():
    colorama.init(autoreset=True)

    # Iniciar Santa Claus
    santa = SantaClaus()
    threading.Thread(target=santa.dormir).start()

    # Iniciar renos y elfos
    iniciar_renos()
    iniciar_elfos()

    # El programa sigue corriendo indefinidamente simulando el trabajo en el Polo Norte
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
