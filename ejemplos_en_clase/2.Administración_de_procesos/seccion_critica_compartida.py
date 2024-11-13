#!/usr/bin/python3
import threading
import time
import random

candado = threading.Lock()

def una_cosa(x):
    candado.acquire()
    print("%d: Entrando a una_cosa()" % x)
    time.sleep(random.random())
    print("%d: Saliendo de una_cosa()" % x)
    candado.release()

for i in range(5):
    threading.Thread(target=una_cosa, args=[i]).start()
