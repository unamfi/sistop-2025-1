#!/usr/bin/python3
from random import random
from time import sleep
import threading

class Objeto:
    def __init__(self):
        sleep(random())
        self.ident = '%0.3f' % random()
        print('→ Nuevo objeto creado: ' + self.ident)

    def procesa(self):
        sleep(random())
        print('→ El objeto %s fue utilizado.' % self.ident)

class Productor:
    def __init__(self, buf, mut, hay_objetos, lleno, yo):
        print(' P%d: Inicio.' % yo)
        while True:
            buffer_lleno.acquire()
            o = Objeto()
            mut.acquire()
            buf.append(o)
            mut.release()
            hay_objetos.release()
            print(' P%d: Coloqué a "%s" en la cinta.' % (yo, o.ident))

class Consumidor:
    def __init__(self, buf, mut, hay_objetos, lleno, yo):
        print('     C%d: Inicio' % yo)
        while True:
            hay_objetos.acquire()
            print('     C%d: ¡Hay un objeto disponible!' % yo)
            mut.acquire()
            o = buf.pop()
            mut.release()
            buffer_lleno.release()
            o.procesa()
            print('     C%d: %s Procesado. ¡Siguiente vuelta!' % (yo, o.ident))

buf = []
num_prod = 100
num_cons = 2
obj_max_en_buffer = 5
hay_objetos = threading.Semaphore(0)
buffer_lleno = threading.Semaphore(obj_max_en_buffer)
mut_buf = threading.Semaphore(1)

for i in range(num_prod):
    threading.Thread(target = Productor,
                     args = [buf, mut_buf, hay_objetos, buffer_lleno, i]
                     ).start()

for i in range(num_cons):
    threading.Thread(target = Consumidor,
                     args = [buf, mut_buf, hay_objetos, buffer_lleno, i]
                     ).start()

while True:
    with mut_buf:
        print('☺ %d objetos en el buffer' % len(buf))
    sleep(1)
