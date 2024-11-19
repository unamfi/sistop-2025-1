import random
import copy
from collections import deque
class Proceso:
    def __init__(self, id, tiempo_llegada, duracion):
        self.id = id
        self.tiempo_llegada = tiempo_llegada
        self.duracion = duracion
        self.restante = duracion
        self.tiempo_comienzo = None
        self.tiempo_finalizacion = None
        self.espera = 0
        self.prioridad = 0
    def __repr__(self):
        return f"P{self.id}(llegada={self.tiempo_llegada}, duracion={self.duracion})"
    
    
    
def generar_procesos(n, tiempo_max_llegada, duracion_max):
    procesos = []
    for i in range(n):
        tiempo_llegada = random.randint(0, tiempo_max_llegada)
        duracion = random.randint(1, duracion_max)
        procesos.append(Proceso(i, tiempo_llegada, duracion))
    return sorted(procesos, key=lambda p: p.tiempo_llegada)


def simular_fcfs(procesos):
    tiempo_actual= 0
    for proceso in procesos:
        #pasamos hasta donde inicial el proceso
        if tiempo_actual<proceso.tiempo_llegada: 
            #Espera si el proceso no ha llegado
            tiempo_actual= proceso.tiempo_llegada  
        #Indicamos cuando comenzo el proceso
        proceso.tiempo_comienzo= tiempo_actual    
        #Como es FcFS terminamos el primer proceso en entrar
        proceso.tiempo_finalizacion= tiempo_actual + proceso.duracion 
         #Actualizamos el tiempo actual
        tiempo_actual = proceso.tiempo_finalizacion
        # Actualizamos cuanto estuvo esperando el proceso
        proceso.espera= proceso.tiempo_comienzo - proceso.tiempo_llegada 
    return procesos

def calcular_metricas(procesos):
    #Cuantos procesos son para promediar
    n = len(procesos) 
    #Cuanto tiempo tardo en terminar
    tiempo_retorno = sum(p.tiempo_finalizacion - p.tiempo_llegada for p in procesos)/n 
    #cuanto tiempo espero
    espera = sum(p.espera for p in procesos)/n 
    penalizacion = sum((p.tiempo_finalizacion - p.tiempo_llegada)/p.duracion for p in procesos)/ n 
    return tiempo_retorno, espera, penalizacion

def representar_visualmente(procesos):
    timeline = []
    for proceso in procesos:
        timeline.extend([f"P{proceso.id}"]* proceso.duracion)
    return "".join(timeline)

def simular_rr(procesos, quantum):
    #sortemaos segun cuando llegaron
    cola = deque() 
    tiempo_actual = 0 
    # Para calcular las metricas una vez se procesaron los procesos
    completados =[] 
    #Para guardar el timeline
    TimeLine =[] 
    #mientras haya procesos disponibles o esten en espera
    while procesos or cola:
        #encolar segun su llegada
        while procesos and procesos[0].tiempo_llegada <= tiempo_actual:
            cola.append(procesos.pop(0))
        #sacamos un proceso si ya llego uno a la cola
        if cola:
            
            proceso = cola.popleft() 
        else:
            #si no continuamos
            tiempo_actual+=1
            continue
        if tiempo_actual < proceso.tiempo_llegada:
            #set del tiempo actual
            tiempo_actual= proceso.tiempo_llegada 
            
        #ejecutar lo suficiente con el fin de evitar negativos o tiempo en un proceso que ya acabo
        tiempo_ejecutado= min(proceso.restante, quantum) 
        #Actualizamos cuanto le queda por ejecutar
        proceso.restante -=tiempo_ejecutado 
        #actualizar tiempo actual
        tiempo_actual +=tiempo_ejecutado 
        if proceso.restante == 0:
            #indicar cuando acabo
            proceso.tiempo_finalizacion = tiempo_actual 
            # cuanto espero
            proceso.espera= tiempo_actual - proceso.tiempo_llegada -proceso.duracion 
            completados.append(proceso) 
        else:
            cola.append(proceso)
        for _ in range(tiempo_ejecutado):
            TimeLine.append("P" + str(proceso.id))
    return completados,TimeLine

def simular_mlfq(procesos, quantum_0, quantum_1):
    # Colas por nivel de prioridad

    cola_0 = deque() 
    cola_1 = deque()
    tiempo_actual = 0
    completados = []
    timeline = []
    while procesos or cola_0 or cola_1:
        #Procesar los procesos (vaya la redundancia), segun su tiempo de llegada
        while procesos and procesos[0].tiempo_llegada <= tiempo_actual:
            cola_0.append(procesos.pop(0))
            
        if cola_0:
            #Procesar desde la cola de alta prioridad
            proceso = cola_0.popleft()
            quantum = quantum_0
        elif cola_1:
            #Procesar desde la cola de baja prioridad
            proceso = cola_1.popleft()
            quantum = quantum_1
        else:
            #No hay procesos listos, avanzar el tiempo
            tiempo_actual += 1
            continue
        

        #Actualizar el tiempo de comienzo si es la primera vez que se ejecuta
        if proceso.tiempo_comienzo is None:
            proceso.tiempo_comienzo = tiempo_actual
        #Ejecutar el proceso
        tiempo_ejecutado = min(proceso.restante, quantum)
        proceso.restante -= tiempo_ejecutado
        tiempo_actual += tiempo_ejecutado        
        for _ in range(tiempo_ejecutado):
            timeline.append("P" + str(proceso.id))
        if proceso.restante == 0:
            #Proceso completado
            proceso.tiempo_finalizacion = tiempo_actual
            proceso.espera = proceso.tiempo_finalizacion - proceso.tiempo_llegada - proceso.duracion
            completados.append(proceso)
        else:
            # over proceso a la cola correspondiente
            if proceso.prioridad == 0:
                proceso.prioridad = 1
                cola_1.append(proceso)
            else:
                cola_1.append(proceso)

    return completados, timeline



def simular_spn(procesos):
    tiempo_actual = 0
    pendientes = []
    completados = []
    #como se trabajara en el orden de duración, se trabaja un tiempo globar hasta que llegue un proceso, que con la cola ordenada sera el de menor duracion
    while procesos or pendientes: 
        while procesos and procesos[0].tiempo_llegada <= tiempo_actual:
            pendientes.append(procesos.pop(0))
        #Ordenar por duracio
        pendientes.sort(key=lambda p: p.duracion) 
        
        if pendientes:
            proceso = pendientes.pop(0)
            proceso.tiempo_comienzo = tiempo_actual
            proceso.tiempo_finalizacion = tiempo_actual + proceso.duracion
            tiempo_actual = proceso.tiempo_finalizacion
            completados.append(proceso)
            proceso.espera = tiempo_actual - proceso.tiempo_llegada -proceso.duracion
        else:
            #Avanzar el tiempo si no hay procesos disponibles
            tiempo_actual += 1  
    return completados
rondas = 5
numerodeproces = 5
tiempo_max_llegada = 5
duracionmax = 5
for i in range(rondas):
    print("-----------------------------------------------------------")
    procesos = generar_procesos(numerodeproces, tiempo_max_llegada, duracionmax)
    print("Descripcion de los procesos")
    print(procesos)
    print("")
    #FCFS

    fcfs = simular_fcfs(copy.deepcopy(procesos))
    
    T, E, P = calcular_metricas(fcfs)
    print(f"FCFS: T={T:.2f}, E={E:.2f}, P={P:.2f}")
    print(representar_visualmente(fcfs))
    print("")
    #RR
    quantum = 1
    rr,tmrr = simular_rr(copy.deepcopy(procesos), quantum)
    T, E, P = calcular_metricas(rr)
    print(f"RR: T={T:.2f}, E={E:.2f}, P={P:.2f}, Q={quantum:.2f}")
    for proceso in tmrr:
        print(proceso, end="")
    print("")
    print("")
    #SPN
    
    spn = simular_spn(copy.deepcopy(procesos))
    T, E, P = calcular_metricas(spn)
    print(f"SPN: T={T:.2f}, E={E:.2f}, P={P:.2f}")
    print(representar_visualmente(spn))

    #FB
    quantum_0 = 1
    quantum_1 = 2

    fb, timeline_fb = simular_mlfq(copy.deepcopy(procesos), quantum_0,quantum_1)
    T, E, P = calcular_metricas(fb)
    print(f"FB: T={T:.2f}, E={E:.2f}, P={P:.2f}")
    for proceso in timeline_fb:
        print(proceso, end="")
    print("")
    print("")