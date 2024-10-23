print("\nTarea 1: El cruce del rio")
print ("Alumno: Hernández Saldívar Héctor Saúl")
print ("Docente: Ing. Gunnar Eyal Wolf Iszaevich")
print ("Sistemas Operativos  grupo: 6 2025-1\n")

import threading
import time
import random


class Balsa:
    def __init__(self):
        self.resetear()

    def resetear(self):
        #Inicializa o reinicia los contadores y semáforos.
        self.hackers = 0
        self.serfs = 0
        self.total_abordo = 0
        self.bloqueo_abordaje = threading.Semaphore(4)  # Permite máximo 4 personas
        self.mutex = threading.Semaphore(1)  # Controla acceso a contadores
        self.viaje_completo = threading.Event()  # Marca si un viaje ha terminado
        print("\nLa balsa está lista para un nuevo viaje.\n")

    def hacker_arrive(self):
        #Simula la llegada de un hacker.
        self.bloqueo_abordaje.acquire()  # Permite máximo 4 personas esperando
        with self.mutex:
            self.hackers += 1
            print(f"Hacker ha llegado. Total hackers: {self.hackers}")
            self._intentar_abordar("Hacker")

    def serf_arrive(self):
        #Simula la llegada de un serf.
        self.bloqueo_abordaje.acquire()  # Permite máximo 4 personas esperando
        with self.mutex:
            self.serfs += 1
            print(f"Serf ha llegado. Total serfs: {self.serfs}")
            self._intentar_abordar("Serf")

    def _intentar_abordar(self, tipo):
        #Intenta abordar y verifica si la balsa está llena.
        self.total_abordo += 1
        print(f"{tipo} sube a la balsa. Total a bordo: {self.total_abordo}")

        if self.total_abordo == 4:
            if self._verificar_balance():
                print("¡Formación válida! La balsa zarpa...\n")
                self._reiniciar_viaje()
            else:
                print("Formación inválida. Viaje cancelado. Todos bajan.\n")
                self._cancelar_viaje()

    def _verificar_balance(self):
        #Verifica si la combinación actual es válida.
        return (
            (self.hackers == 4) or
            (self.serfs == 4) or
            (self.hackers == 2 and self.serfs == 2)
        )

    def _cancelar_viaje(self):
        #Cancela el viaje y libera los desarrolladores.
        print("\nLa balsa está lista para otro intento.\n")
        self._liberar_abordaje()

    def _reiniciar_viaje(self):
        #Reinicia los contadores y permite otro viaje.
        self._liberar_abordaje()
        self.resetear()

    def _liberar_abordaje(self):
        #Libera a los desarrolladores para otro intento.
        self.total_abordo = 0
        self.hackers = 0
        self.serfs = 0
        self.bloqueo_abordaje.release(4)  # Libera la espera de 4 nuevas personas

def hacker(balsa):
    #Simula la llegada de hackers.
    while not balsa.viaje_completo.is_set():
        time.sleep(random.uniform(0.1, 1.0))
        balsa.hacker_arrive()

def serf(balsa):
    #Simula la llegada de serfs.
    while not balsa.viaje_completo.is_set():
        time.sleep(random.uniform(0.1, 1.0))
        balsa.serf_arrive()

def iniciar_viajes():
    #Controla los viajes consecutivos de la balsa.
    while True:
        balsa = Balsa()

        # Crear 5 threads de hackers y 5 de serfs para cada viaje
        hackers = [threading.Thread(target=hacker, args=(balsa,)) for _ in range(5)]
        serfs = [threading.Thread(target=serf, args=(balsa,)) for _ in range(5)]

        # Iniciar los threads
        for h, s in zip(hackers, serfs):
            h.start()
            s.start()

        # Esperar a que los threads terminen
        for h, s in zip(hackers, serfs):
            h.join()
            s.join()

if __name__ == "__main__":
    iniciar_viajes()
