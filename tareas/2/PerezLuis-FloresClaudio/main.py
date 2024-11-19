from typing import List

class Proceso:
    def __init__(self,nombre: str,duracion: int,start_time: int)->None:
        self.nombre=nombre
        #t
        self.duration=duracion
        self.ticks=duracion
        self.start=start_time
        #Tiempo de respuesta T = tFinal - Tinicial
        self.T=0
        #Tiempo en espera E=T-t
        self.E=0
        #Proporción de penalización P=T/t
        self.P=0
        #Proporción de respuesta R=1/P
        self.R=0

def reset_procesos():
    datos=[
        ['A',3,0],
        ['B',5,1],
        ['C',2,3],
        ['D',5,9],
        ['E',5,12]
    ]
    procs=[]
    for proc in datos:
        print(proc)
        procs.append(Proceso(proc[0],proc[1],proc[2]))
    return procs

def FCFS(procesos:List[Proceso]):
    print('FCFS:')
    queue=[]
    t_total=0
    grafica=''
    #calculo del tiempo
    for proc in procesos:
        t_total+=proc.ticks

    print('\tTiempo total: ',t_total)

    for i in range(t_total):
        #Determina si hay un proceso listo
        for proc in procesos:
            if proc.start==i:
                queue.append(proc)

        #Hay un proceso en la cola
        if queue:
            queue[0].ticks-=1
            grafica+=queue[0].nombre
            if queue[0].ticks==0:
                queue[0].T = i - queue[0].start + 1
                queue[0].E = queue[0].T - queue[0].duration
                queue[0].P = queue[0].T / queue[0].duration
                queue[0].R = 1 / queue[0].P
                print(f'\t{queue[0].nombre}: T={queue[0].T}, E={queue[0].E}, P={queue[0].P:.2f}, R={queue[0].R:.2f} ')
                queue.pop(0)

    print('\t'+grafica)





    pass

procesos=reset_procesos()
print("----------------------------")
FCFS(procesos)


