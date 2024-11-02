""""
Bienvenido al proyecto 1. MICRO SISTEMA DE ARCHIVOS MULTIHILOS 

Donde se utiilizaran los cnceptos vistos en clase para implementar un programa 
que pueda realizar las siguientes acciones especificadas por el profesor:

1- Listar los contenidos del directorio
2- Copiar uno de los archivos de dentro del FiUnamFS hacia tu sistema
3- Copiar un archivo de tu computadora hacia tu FiUnamFS
4- Eliminar un archivo del FiUnamFS
5- El programa que desarrollen debe contar, por lo menos, dos hilos de ejecución, 
operando concurrentemente, y que se comuniquen su estado mediante mecanismos de 
sincronización.

Este programa utiliza MODELO DE FUSE

"""

import os 
import fusepy
from fuse import FUSE, Operations

class FiUnamFS(Operations):
    def __init__(self, imagenDisco):
        self.imagenDisco = imagenDisco
    
    def ls(self):

        pass
    
    def cp(self):

        pass

    def delete(sefl):
        pass