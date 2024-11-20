from FIFO import fifo
from RR import rr
from spn import spn
from FB import fb
import random

class proceso:

     def __init__(self,t_requerido,t_llegada,name):

        self.t_requerido = t_requerido
        self.t_llegada = t_llegada
        self.T = 0
        self.E = 0
        self.P = 0
        self.name = name

def def_procesos():

    procesos = []

    procesos.append(proceso(random.randint(2,8),random.randint(0,8),"A"))
    procesos.append(proceso(random.randint(2,8),random.randint(0,8),"B"))
    procesos.append(proceso(random.randint(2,8),random.randint(0,8),"C"))


    for procesito in procesos:
        print(f"{procesito.name},llegada: {procesito.t_llegada},requerido: {procesito.t_requerido}\n")

    resultados,esquema = fifo(procesos)
    print("\tT\t\tE\t\tP")
    print(f"FIFO: {resultados}\n{esquema}")

    resultados,esquema = rr(procesos)
    print(f"RR: {resultados}\n{esquema}")

    resultados,esquema = spn(procesos)
    print(f"SPN: {resultados}\n{esquema}")

    resultados,esquema = fb(procesos)
    print(f"FB: {resultados}\n{esquema}")

def_procesos()