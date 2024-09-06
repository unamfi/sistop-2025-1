#!/usr/bin/python3
import os
import time
import signal

def maneja(sig, frame):
    signame = signal.Signals(sig).name
    print('¡Recibí una señal %d (%s)!' % (sig, signame))
    if sig == signal.SIGCHLD:
        print('Es un hijo que terminó con su trabajo. ¡Muy bien!')
        os.wait()
        print('Ya tá!')
    elif sig == signal.SIGINT:
        print("¡Adios! Fue un gusto hacer lo que me pediste.")
        exit(0)
    elif sig == signal.SIGWINCH:
         print('Cambió el tamaño de mi pantalla.')

signal.signal(signal.SIGCHLD, maneja)
signal.signal(signal.SIGWINCH, maneja)
signal.signal(signal.SIGINT, maneja)

start_pid = os.getpid()
print('Este es el proceso %d. Iniciando el programa.' % start_pid)

new_pid = os.fork()
if new_pid == 0:
    print('Soy el proceso hijo. Mi PID es: %d' % os.getpid())
    time.sleep(2)
    print('El hijo despertó, recoge sus triques y se va.')
elif new_pid > 0:
    print('Soy el proceso padre (%d). El PID del hijo es: %d' %
          (start_pid, new_pid))
    time.sleep(20)
    print('El proceso padre despertó, y la ejecución finaliza.')

exit(0)
