#!/usr/bin/python3
import threading
import time
cuantos = 8
contador = 0
barrera = threading.Semaphore(0)
mutex = threading.Semaphore(1)

def manada(num):
    global barrera, mutex, cuantos, contador
    print('Soy %d y soy parte de la manada....' % num)
    mutex.acquire()
    contador = contador+1
    if contador == cuantos:
        barrera.release()
    mutex.release()
    barrera.acquire()
    barrera.release()
    print('%d: Y a fin de cuentas, todos llegamos al final.' % num)

for i in range(10):
    time.sleep(1)
    threading.Thread(target=manada, args=[i]).start()
