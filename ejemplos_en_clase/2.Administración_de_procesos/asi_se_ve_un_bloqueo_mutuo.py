#!/usr/bin/python3
import threading
import random
import time

candado1 = threading.Lock()
candado2 = threading.Lock()

def una_cosa():
    print('Entrando a una_cosa()')
    time.sleep(random.random())
    candado1.acquire()
    time.sleep(random.random())
    print('Una: Tengo candado 1')
    candado2.acquire()
    time.sleep(random.random())
    print("Tengo ambos candados en la mano")
    candado2.release()
    candado1.release()
    print('Saliendo de una_cosa()')

def otra_cosa():
    print('Entrando a otra_cosa()')
    time.sleep(random.random())
    candado2.acquire()
    print('Otra: Tengo candado 2')
    time.sleep(random.random())
    candado1.acquire()
    print("Tengo ambos candados en la mano")
    time.sleep(random.random())
    candado1.release()
    candado2.release()
    print('Saliendo de otra_cosa()')

threading.Thread(target=otra_cosa).start()
threading.Thread(target=una_cosa).start()

