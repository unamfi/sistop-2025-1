#Ortiz Moreno Ximena
#Sánchez Gachuz Jennyfer Estefanía

import threading
import time
import random

# Constantes
NUM_PISOS = 5
CAPACIDAD_ELEVADOR = 5

# Primitivas de sincronización
lock_elevador = threading.Lock()  # Mutex para acceso al elevador
cond_elevador = threading.Condition(lock_elevador)  # Condición para sincronizar movimiento y abordaje
print_lock = threading.Lock()  # Mutex para sincronizar impresiones

# Variables globales
piso_actual = 1  # Piso en el que está el elevador (iniciando en 1)
direccion = 1  # 1 para subir, -1 para bajar
pasajeros_en_elevador = []  # Lista de pasajeros dentro del elevador
solicitudes = set()  # Conjunto de pisos solicitados
# Ajustamos las listas para que los índices coincidan con los números de piso
solicitudes_pisos = [[] for _ in range(NUM_PISOS + 1)]  # Índices de 0 a NUM_PISOS (0 no se usa)
pasajeros_activos = 0  # Contador de pasajeros que aún no han llegado a su destino
elevador_activo = True  # Bandera para mantener el elevador activo

class Pasajero:
    def __init__(self, id_pasajero, piso_origen, piso_destino):
        self.id_pasajero = id_pasajero
        self.piso_origen = piso_origen
        self.piso_destino = piso_destino
        self.en_elevador = False
        self.condicion = threading.Condition()

    def __str__(self):
        return f"Pasajero {self.id_pasajero} ({self.piso_origen} -> {self.piso_destino})"

def imprimir_mensaje(mensaje):
    with print_lock:
        print(mensaje)

def elevador():
    global piso_actual, direccion, elevador_activo, pasajeros_activos
    while True:
        with lock_elevador:
            # Si no hay solicitudes y no hay pasajeros en el elevador, esperar
            if not solicitudes and not pasajeros_en_elevador:
                if pasajeros_activos == 0:
                    # No hay más pasajeros activos, terminar elevador
                    elevador_activo = False
                    imprimir_mensaje("Elevador ha finalizado su servicio.")
                    break  # Salir del bucle while
                else:
                    imprimir_mensaje(f"Elevador está en espera en el piso {piso_actual}")
                    cond_elevador.wait()
                    continue

            # Determinar próximos pisos a visitar según el algoritmo SCAN
            if direccion == 1:
                pisos_por_visitar = sorted([p for p in solicitudes if p >= piso_actual])
            else:
                pisos_por_visitar = sorted([p for p in solicitudes if p <= piso_actual], reverse=True)

            if not pisos_por_visitar:
                # Cambiar dirección si no hay más pisos en la dirección actual
                direccion *= -1
                if direccion == 1:
                    pisos_por_visitar = sorted([p for p in solicitudes if p >= piso_actual])
                else:
                    pisos_por_visitar = sorted([p for p in solicitudes if p <= piso_actual], reverse=True)

            if pisos_por_visitar:
                siguiente_piso = pisos_por_visitar[0]
                # Moverse al siguiente piso
                while piso_actual != siguiente_piso:
                    piso_actual += direccion
                    imprimir_mensaje(f"Elevador se mueve al piso {piso_actual}")
                    time.sleep(1)  # Simular tiempo de desplazamiento

                # Llegamos al piso deseado
                imprimir_mensaje(f"Elevador llega al piso {piso_actual}")

                # Remover el piso de las solicitudes
                if piso_actual in solicitudes:
                    solicitudes.remove(piso_actual)

                # Pasajeros que deben bajar en el piso actual
                pasajeros_a_bajar = [p for p in pasajeros_en_elevador if p.piso_destino == piso_actual]
                for pasajero in pasajeros_a_bajar:
                    imprimir_mensaje(f"{pasajero} sale del elevador en el piso {piso_actual}")
                    pasajeros_en_elevador.remove(pasajero)
                    pasajero.en_elevador = False
                    with pasajero.condicion:
                        pasajero.condicion.notify()
                    # Disminuir el contador de pasajeros activos
                    pasajeros_activos -= 1
                    if pasajeros_activos == 0:
                        # Notificar en caso de que el elevador esté esperando para terminar
                        cond_elevador.notify_all()

                # Pasajeros que quieren subir en el piso actual
                pasajeros_a_subir = solicitudes_pisos[piso_actual]
                i = 0
                while i < len(pasajeros_a_subir) and len(pasajeros_en_elevador) < CAPACIDAD_ELEVADOR:
                    pasajero = pasajeros_a_subir[i]
                    imprimir_mensaje(f"{pasajero} aborda el elevador en el piso {piso_actual}")
                    pasajeros_en_elevador.append(pasajero)
                    pasajero.en_elevador = True
                    # Agregar piso destino a las solicitudes si no está ya
                    if pasajero.piso_destino not in solicitudes:
                        solicitudes.add(pasajero.piso_destino)
                    with pasajero.condicion:
                        pasajero.condicion.notify()
                    pasajeros_a_subir.pop(i)
                time.sleep(1)  # Simular tiempo de apertura y cierre de puertas
            else:
                # Si no hay más solicitudes en ninguna dirección, el elevador espera
                imprimir_mensaje(f"Elevador está en espera en el piso {piso_actual}")
                cond_elevador.wait()
        # Pequeña pausa antes de la siguiente iteración
        time.sleep(0.5)

def hilo_pasajero(pasajero):
    # Pasajero llega al piso de origen y presiona el botón
    with lock_elevador:
        solicitudes_pisos[pasajero.piso_origen].append(pasajero)
        imprimir_mensaje(f"{pasajero} está esperando en el piso {pasajero.piso_origen}")
        # Agregar piso origen a las solicitudes si no está ya
        if pasajero.piso_origen not in solicitudes:
            solicitudes.add(pasajero.piso_origen)
            imprimir_mensaje(f"{pasajero} presiona el botón en el piso {pasajero.piso_origen}")
        cond_elevador.notify()  # Notificar al elevador que hay un pasajero esperando
    with pasajero.condicion:
        while not pasajero.en_elevador:
            pasajero.condicion.wait()
    # Pasajero está en el elevador, espera hasta llegar a su destino
    with pasajero.condicion:
        while pasajero.en_elevador:
            pasajero.condicion.wait()
    imprimir_mensaje(f"{pasajero} ha llegado a su destino.")

def generar_pasajeros(num_pasajeros):
    pasajeros_hilos = []
    for i in range(1, num_pasajeros + 1):  # Iniciar índice en 1
        piso_origen = random.randint(1, NUM_PISOS)
        piso_destino = random.randint(1, NUM_PISOS)
        while piso_destino == piso_origen:
            piso_destino = random.randint(1, NUM_PISOS)
        pasajero = Pasajero(i, piso_origen, piso_destino)
        pasajero_hilo = threading.Thread(target=hilo_pasajero, args=(pasajero,))
        pasajeros_hilos.append(pasajero_hilo)
        pasajero_hilo.start()
        time.sleep(random.uniform(0.5, 2))  # Los pasajeros llegan en intervalos aleatorios
    return pasajeros_hilos

def main():
    global pasajeros_activos
    pasajeros_activos = 10  # Inicializar el contador de pasajeros activos
    pasajeros_hilos = generar_pasajeros(pasajeros_activos)  # Generar 10 pasajeros
    elevador_hilo = threading.Thread(target=elevador)
    elevador_hilo.start()
    # Esperar a que todos los pasajeros terminen
    for hilo in pasajeros_hilos:
        hilo.join()
    # Esperar a que el elevador termine
    elevador_hilo.join()
    imprimir_mensaje("Todos los pasajeros han llegado a su destino.")
    imprimir_mensaje("El elevador ha completado todas sus operaciones.")

if __name__ == "__main__":
    main()
