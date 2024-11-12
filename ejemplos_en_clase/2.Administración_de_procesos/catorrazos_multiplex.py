#!/usr/bin/python3
import threading
import time
import random

def catorrazos(num: int, mult: threading.Semaphore):
    while True:
        vida = 100
        print('%d - ¡VUELVO A LA VIDA! Tengo %d' % (num, vida))
        time.sleep(random.random())
        mult.acquire()
        while vida > 0:
            print('%d ¡PELEA!' % num)
            time.sleep(random.random())
            daño = random.randint(0,100)
            vida -= daño
            print('%d: Tuve daño de %d 🙁 me queda %d' % (num, daño, vida))
        print('%d: MUERTO SOY' % num)
        mult.release()

print('======= ¡CATORRAZOS! ========')

multiplex = threading.Semaphore(2)
for i in range(5):
    threading.Thread(target=catorrazos, args=[i, multiplex]).start()
