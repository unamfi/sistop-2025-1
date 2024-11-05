#!/usr/bin/python3
from mmap import mmap
from time import sleep
import os

fh = open('telefonos.dat', 'r+')
fileno = fh.fileno()

datos = mmap(fileno, 0)

print(datos[(250*170):(251*170)])

cadena = ('Mi número de proceso es %d' % os.getpid()).encode('utf-8')
datos[100:(100+len(cadena))] = cadena
