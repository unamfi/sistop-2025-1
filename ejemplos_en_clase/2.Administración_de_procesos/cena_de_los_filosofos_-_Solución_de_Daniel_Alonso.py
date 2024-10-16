#!/usr/bin/python3
import threading
import time
from random import random

porciones_servidas = 0
mutex_palillos = threading.Semaphore(1)
mutex_porciones = threading.Semaphore(1)
num_filosofos = 5
palitos = [ threading.Semaphore( 1 ) for i in range(num_filosofos) ]

class Filosofo():
    def __init__(self, num):
        self.num = num
        self.siguiente = self.__num_siguiente__()
        self.anterior = self.__num_anterior__()
        while True:
            self.piensa()
            self.come()

    def __reporta__(self, msg):
        print('%s%d: %s' % (' ' * self.num, self.num, msg))

    def __num_siguiente__(self):
        return (self.num + 1) % num_filosofos

    def __num_anterior__(self):
        return (self.num - 1) % num_filosofos

    def __levanta_palito__(self, palito):
        self.__reporta__('Levantando al palito %d' % palito)
        palitos[palito].acquire()

    def __deja_palito__(self, palito):
        self.__reporta__('Dejando al palito %d' % palito)
        palitos[palito].release()

    def come(self):
        global porciones_servidas
        la_porcion = None
        self.__reporta__('¡Pues vamos a comer!')
        with mutex_palillos:
            self.__levanta_palito__(self.anterior)
            self.__levanta_palito__(self.siguiente)
        self.__reporta__('¡Ñom ñom ñom!')
        with mutex_porciones:
            porciones_servidas = porciones_servidas + 1
            la_porcion = porciones_servidas
        time.sleep(random() / 1000)
        self.__deja_palito__(self.siguiente)
        self.__deja_palito__(self.anterior)
        self.__reporta__('* ¡Satisfecho! %d porciones servidas. *' % la_porcion)

    def piensa(self):
        self.__reporta__('Pensando...')
        time.sleep(random() / 1000)
        self.__reporta__('Como que ya hace hambre, ¿no?')


filosofos = [threading.Thread(target=Filosofo, args=[i]).start() for i in range(5)]
