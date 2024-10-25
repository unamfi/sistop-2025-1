#CornejoGonzalezMauricio

import threading
import time
import random

# Constantes
NUM_PISOS = 5
CAPACIDAD_ELEVADOR = 5

class Elevador(threading.Thread):
    def _init_(self):
        threading.Thread._init_(self)
        self.piso_actual = 0  # El elevador comienza en el piso 0
        self.pasajeros = []
        self.direccion = 1  # 1 es subiendo, -1 es bajando
        self.lock = threading.Lock()  # Para evitar colisiones de datos
        self.semaforo_pisos = [threading.Semaphore(0) for _ in range(NUM_PISOS)]  # Semáforos para los pisos

    def mover_elevador(self):
        while True:
            time.sleep(2)  # Simulamos que el elevador tarda en moverse
            with self.lock:
                # Mover el elevador al siguiente piso
                self.piso_actual += self.direccion
                print(f"El elevador está en el piso {self.piso_actual}")

                # Si llega al último piso, cambia la dirección
                if self.piso_actual == NUM_PISOS - 1:
                    self.direccion = -1
                # Si llega al primer piso, cambia la dirección
                elif self.piso_actual == 0:
                    self.direccion = 1

                # Permitir que los pasajeros suban o bajen
                self.semaforo_pisos[self.piso_actual].release()

    def subir(self, usuario):
        with self.lock:
            if len(self.pasajeros) < CAPACIDAD_ELEVADOR:
                self.pasajeros.append(usuario)
                print(f"{usuario.nombre} ha abordado el elevador en el piso {self.piso_actual}.")
                return True
            return False

    def bajar(self, usuario):
        with self.lock:
            if usuario in self.pasajeros:
                self.pasajeros.remove(usuario)
                print(f"{usuario.nombre} ha bajado del elevador en el piso {self.piso_actual}.")
                return True
            return False

    def run(self):
        self.mover_elevador()

class Usuario(threading.Thread):
    def _init_(self, nombre, piso_origen, piso_destino, elevador):
        threading.Thread._init_(self)
        self.nombre = nombre
        self.piso_origen = piso_origen
        self.piso_destino = piso_destino
        self.elevador = elevador

    def esperar_elevador(self):
        print(f"{self.nombre} está esperando el elevador en el piso {self.piso_origen}.")
        while self.elevador.piso_actual != self.piso_origen:
            self.elevador.semaforo_pisos[self.piso_origen].acquire()

        # Intentar subir al elevador
        if self.elevador.subir(self):
            print(f"{self.nombre} ha subido al elevador en el piso {self.piso_origen}.")
            self.ir_a_destino()
        else:
            print(f"{self.nombre} no pudo abordar el elevador por estar lleno.")

    def ir_a_destino(self):
        while self.elevador.piso_actual != self.piso_destino:
            self.elevador.semaforo_pisos[self.piso_destino].acquire()

        # Bajar del elevador al llegar a su destino
        if self.elevador.bajar(self):
            print(f"{self.nombre} ha llegado a su destino en el piso {self.piso_destino}.")

    def run(self):
        self.esperar_elevador()

# Simulación
def main():
    elevador = Elevador()
    elevador.start()

    # Crear usuarios con diferentes pisos de origen y destino
    usuarios = [
        Usuario(f"Usuario {i+1}", random.randint(0, NUM_PISOS-1), random.randint(0, NUM_PISOS-1), elevador)
        for i in range(10)
    ]

    # Iniciar los hilos de los usuarios
    for usuario in usuarios:
        usuario.start()

    # Esperar a que todos los hilos de usuarios terminen
    for usuario in usuarios:
        usuario.join()

    elevador.join()
if _name_ == "_main_":
    main()