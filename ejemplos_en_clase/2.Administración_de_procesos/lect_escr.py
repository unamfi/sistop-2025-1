#!/usr/bin/python3
import time
import threading
import random
lectores = 0
mutex = threading.Semaphore(1)
cuarto_vacio = threading.Semaphore(1)
torniquetoide = threading.Semaphore(1)

def escritor(yo):
    while True:
        time.sleep(0.01)
        torniquetoide.acquire()
        cuarto_vacio.acquire()
        escribe(yo)
        cuarto_vacio.release()
        torniquetoide.release()

def escribe(yo):
    print('    E%d escribiendo' % yo)
    time.sleep(random.random())
    print('    E%d ya se va.' % yo)

def lector(yo):
    global lectores
    while True:
        torniquetoide.acquire()
        torniquetoide.release()
        time.sleep(0.01)
        mutex.acquire()
        lectores = lectores + 1
        if lectores == 1:
            cuarto_vacio.acquire()
            print('Lector %d: Soy el primero. Prendí la luz.' % yo)
        mutex.release()

        lee(yo)

        mutex.acquire()
        lectores = lectores - 1
        if lectores == 0:
            print('Lector %d: Soy el último. Apago la luz.' % yo)
            cuarto_vacio.release()
        print('Quedan %d lectores' % lectores)
        mutex.release()


def lee(yo):
    print('Lector %d leyendo' % yo)
    time.sleep(random.random())
    print('Lector %d se va.' % yo)


for i in range(3):
    threading.Thread(target=escritor, args=[i]).start()

for i in range(40):
    threading.Thread(target=lector, args=[i]).start()

