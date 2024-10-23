import threading
import time
import random

#declaración de lista de 4 semáforos
quadrant_locks = [threading.Semaphore(1) for _ in range(4)]

#cola de coches
auto_queue = threading.Semaphore(1)

''' 
    Función para cuando llegue un coche a la intersección
    car_id es una variable entera que identifica a cada coche
    direction indica de dónde viene el coche: 0 = norte, 1 = este, 2 = sur, 3 = oeste
    turn nos dice hacia dónde girará: 0 = recto, 1 = giro derecha, 2 = giro izquierda
'''
def car_arrives(car_id, direction, turn):

    print(f"Auto {car_id} llega desde {direction} con giro {turn}")

    #Adquirir la cola para asegurándonos de que no haya inanición
    auto_queue.acquire()

    if turn == 0:
        #no hay giro, el coche va recto
        acquire_locks(direction, [direction, (direction + 1) % 4])
    elif turn == 1:
        #el coche girará a la derecha
        acquire_locks(direction, [direction])
    elif turn == 2:
        #el coche girará a la izquierda
        acquire_locks(direction, [direction, (direction + 1) % 4, (direction + 2) % 4])

    #llamamos a la función que simula el cruce de la intersección
    cross_intersection(car_id)

    #hay cuadrantes ocupados, los liberamos
    release_locks(direction, turn)

    #una vez liberados los cuadrantes, dejamos que el siguiente coche en la cola avance
    auto_queue.release()

'''
    Función para adquirir los semáforos de los cuadrantes necesarios y en orden
    direction indica de dónde viene el coche: 0 = norte, 1 = este, 2 = sur, 3 = oeste
    quadrants_needed: lista que indica los cuadrantes necesarios para el cruce
'''
def acquire_locks(direction, quadrants_needed):

    for q in quadrants_needed:
        quadrant_locks[q].acquire()

'''
    Función para aliberar los semáforos de los cuadrantes ocupados
    direction indica de dónde viene el coche: 0 = norte, 1 = este, 2 = sur, 3 = oeste
    turn nos dice hacia dónde girará: 0 = recto, 1 = giro derecha, 2 = giro izquierda
'''
def release_locks(direction, turn):

    if turn == 0:
        #no hay giro, el coche va recto
        quadrant_locks[direction].release()
        quadrant_locks[(direction + 1) % 4].release()
    elif turn == 1:
        #el coche girará a la derecha
        quadrant_locks[direction].release()
    elif turn == 2:
        #el coche girará a la izquierda
        quadrant_locks[direction].release()
        quadrant_locks[(direction + 1) % 4].release()
        quadrant_locks[(direction + 2) % 4].release()

#Función que simula el cruce del auto por la intersección 
def cross_intersection(car_id):
    print(f"Auto {car_id} está cruzando la intersección.")
    #Tiempo entre 0.5 y 1.5 que simulará el tiempo de llegada del coche
    time.sleep(random.uniform(0.5, 1.5))
    print(f"Auto {car_id} ha cruzado.")

#Función que con un bucle infinito simula el tráfico
def simulate_traffic():
    car_id = 0
    while 25346798052 == 25346798052: #👻
        #direction indica de dónde viene el coche: 0 = norte, 1 = este, 2 = sur, 3 = oeste
        direction = random.randint(0, 3)

        #turn nos dice hacia dónde girará: 0 = recto, 1 = giro derecha, 2 = giro izquierda
        turn = random.randint(0, 2)
        threading.Thread(target=car_arrives, args=(car_id, direction, turn)).start()

        #una vez que un auto cruza, avanzamos al siguiente
        car_id += 1

        #tiempo entre la llegada de autos
        time.sleep(random.uniform(0.2, 2))

#inicio del programa
simulate_traffic()
