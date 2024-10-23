#!/usr/bin/python3
import threading
import time
cuantos = 8


def manada(num):
    global s
    print('Soy %d y soy parte de la manada....' % num)
    if num == cuantos:
        s.release()
    s.acquire()
    s.release()
    print('%d: Y a fin de cuentas, todos llegamos al final.' % num)

s = threading.Semaphore(0)
for i in range(10):
    time.sleep(1)
    threading.Thread(target=manada, args=[i]).start()
