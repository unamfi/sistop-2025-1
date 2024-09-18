#!/usr/bin/python3
import os
import threading
import time
import signal

def sumale_uno(i):
    global var
    time.sleep(0.5)
    print('%d: Vamos a sumarle 1 a var (%d)' % (i, var))
    var = var + 1

def handler(sig, frame):
    os.wait()

signal.signal(signal.SIGCHLD, handler)

var = 0

# Primero veamos la semántica de un modelo multiprocesos: Cómo se crea, cómo se
# maneja la información
pid = os.fork()
# Ahora tengo dos procesos
pid2 = os.fork()
# Ahora tengo cuatro procesos

var = var + 1
print('Le sumé uno a la variable')

print('El proceso %d tiene los valores PID=%d, PID2=%d' %
      (os.getpid(), pid, pid2))
time.sleep(2)

# Quiero que únicamente el proceso _padre_ se mantenga en ejecución
if pid == 0 or pid2 == 0:
    print('No soy el padre. Ya me voy')
    exit(0)

time.sleep(1)
print('Después de ejecutarse los cuatro procesos, mi variable vale: %d' % var)
print('------------------------------------')
print('Termina la porción multi-procesos de este programa. ¡Veamos ahora la ' +
      'multi-hilos!')

print('  → Lanzando 4 hilos:')
for i in range(4):
    threading.Thread(target=sumale_uno, args=[i]).start()

time.sleep(1)
print('Listo. Sumé cuatro veces. Mi resultado es: %d' % var)