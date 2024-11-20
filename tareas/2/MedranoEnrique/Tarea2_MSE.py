"""
Tarea 2 - Comparación de planificadores
Autor: Medrano Solano Enrique

Materia: Sistemas Operativos 2025-2
Entrega: 2024-11-19

Objetivo: Se tendrá que generar un programa que genere varias cargas aleatorias,
y compare el resultado sobre varias ejecuciones.
"""

"""El programa generá adecuadamente los procesos aleatorios, comparando el rendimiento
de los diferentes planificadores: FCFS, RR, SPN, FB (retroalimentación multinivel).
Presentando una visualización del rendimiento y condiciones de cada uno de estos
procesos de manera visual."""

#Se importan las librerías a utilizar
import random

#Se crea la función que genera los procesos aleatorios
def generar_procesos(num_proc):
    """
    
    Esta función genera los procesos de manera aleatoria, de forma que entrega
    tiempos y duración de estos, los parametros a ocupar son:

    num_proc = número de procesos que se generan

    La función retorna una tupla con los siguientes datos:
    (nombre del proceso, tiempo de llegada, tiempo de ejecución)
    """
    procesos = [] #Vacía
    tiempo_actual = 0 #Se inicializa en 0
    for i in range(num_proc):
        tiempo_llegada = tiempo_actual + random.randint(0,3) #tiempo incremental para la llegada
        tiempo_ejec = random.randint(1,7) #Duración del proceso
        procesos.append((f"P{i+1}", tiempo_llegada, tiempo_ejec))
        tiempo_actual = tiempo_llegada #Actualizar tiempo_actual
    return procesos

#Se crea la función para el algoritmo FCFS
def fcfs(procesos):
    """
    La función creada planifica y realiza los procesos establecidos por el
    algoritmo FCFS, con los parámetros:
    procesos (list): Lista de los procesos de forma -> (nombre del proceso, tiempo de llegada, tiempo de ejecución)

    De retorno esta función dara la tupla con las mpetricas de los procesos en formato de diagrama de Gantt
    """
    #Se ordena conforme a la llegada (tiempo)
    ord_procesos = sorted(procesos, key=lambda x: x[1])
    tiempo_actual = 0
    tiempos = [] #Se guardaran las metricas (T, E)
    gantt = [] # Diagrama de Gantt

    for p in ord_procesos:
        nombre, llegada, duración = p
        if tiempo_actual < llegada:
            tiempo_actual = llegada #Se espera hasta la llegada del proceso actual
        gantt.extend([nombre] * duración)
        tiempo_final = tiempo_actual + duración
        tiempos.append((nombre, tiempo_actual - llegada + duración, tiempo_actual - llegada))
        tiempo_actual = tiempo_final #Se actualiza el tiempo_actual
    return gantt, tiempos

#Se crea función para el algoritmo de RR
def rr(procesos, quantum):
    """
    La función planifica y realiza los procesos según el algoritmo de 
    ROund Robin, con los parametros:
    procesos: lista de procesos con el formato (nombre del proceso, tiempo de llegada, tiempo de ejecución)
    quantum: tiempo máximo que un proceso puede ejecutar en unz vez

    De retorno esta función dara la tupla con las mpetricas de los procesos en formato de diagrama de Gantt
    """
    cola = sorted(procesos, key=lambda x: x[1])
    tiempo_actual = 0
    gantt = []
    tiempos = []
    tiempo_rest = {p[0]: p[2] for p in cola} #Duración de cada procesoi
    procesos_comp = []

    while cola or procesos_comp:
        #Se añaden los procesos que han llegado a la cola
        while cola and cola[0][1] <= tiempo_actual:
            procesos_comp.append(cola.pop(0))
        if procesos_comp:
            proceso_actual = procesos_comp.pop(0) #Se toma el proceso 1
            nombre, llegada, duración = proceso_actual
            ejecución = min(quantum, tiempo_rest[nombre]) #Se ejecuta el proceso
            gantt.extend([nombre] * ejecución)
            tiempo_actual += ejecución
            tiempo_rest[nombre] -=ejecución
            #Si no termina vuelve a la cola
            if tiempo_rest[nombre] > 0:
                procesos_comp.append(proceso_actual)
            else: #Se calculan las metricas
                tiempos.append((nombre, tiempo_actual - llegada, tiempo_actual - llegada - duración))
        else:
            tiempo_actual += 1 #avanza si no hay procesos
    return gantt, tiempos

#Se crea función para el algoritmo SPN
def spn(procesos):
    """
    La función planifica los procesos a utilizar del algoritmo SPN, con los parámetros:
    procesos: lista de procesos con el formato (nombre del proceso, tiempo de llegada, tiempo de ejecución)

    De retorno esta función dara la tupla con las mpetricas de los procesos en formato de diagrama de Gantt
    """
    cola = sorted(procesos, key=lambda x: x[1]) #Ordenar por tiempos de llegada
    tiempo_actual = 0
    gantt = []
    tiempos = []

    while cola:
        disponible = [p for p in cola if p[1] <= tiempo_actual] #Procesos ya listos
        if disponible:
            proceso_actual = min(disponible, key=lambda x: x[2]) #Se elije el de menor duración
            cola.remove(proceso_actual)
            nombre, llegada, duración = proceso_actual
            gantt.extend([nombre] * duración)
            tiempo_actual += duración
            tiempos.append((nombre, tiempo_actual - llegada, tiempo_actual - llegada - duración))
        else:
            tiempo_actual += 1 #avanza si no hay procesos
    return gantt, tiempos

#Se crea la función para el algoritmo FB
def fb(procesos):
    """
    La función planifica y realiza los procesos para el algoritmo de FB utilizando 3 colas, con los parámetros:
    procesos: lista de procesos con el formato (nombre del proceso, tiempo de llegada, tiempo de ejecución)

    De retorno esta función dará la tupla con las métricas de los procesos en formato de diagrama de Gantt
    """
    cola = sorted(procesos, key=lambda x: x[1])  # Se ordena por tiempos de llegada
    tiempo_actual = 0
    gantt = []
    tiempos = []
    tiempos_rest = {p[0]: p[2] for p in procesos}  # Tiempo restante por proceso

    # Parámetros de retroalimentación
    num_colas = 3  # Número de colas
    quantum = [1, 2, 4]  # Quantum de cada nivel de cola
    colas = [[] for _ in range(num_colas)]  # Tres colas vacías

    while cola or any(colas):  # Mientras haya procesos en cola
        # Mover procesos de llegada a la primera cola
        while cola and cola[0][1] <= tiempo_actual:
            colas[0].append(cola.pop(0))

        # Buscar proceso para ejecutar
        proceso_encontrado = False
        for nivel, q in enumerate(quantum):
            if colas[nivel]:  # Si hay procesos en esta cola
                proceso_actual = colas[nivel].pop(0)
                nombre, llegada, _ = proceso_actual
                ejecución = min(q, tiempos_rest[nombre])  # Ejecutar dentro del quantum
                gantt.extend([nombre] * ejecución)
                tiempo_actual += ejecución
                tiempos_rest[nombre] -= ejecución

                if tiempos_rest[nombre] > 0:  # Si el proceso no ha terminado
                    if nivel < num_colas - 1:  # Bajar a la siguiente cola si no está en la última
                        colas[nivel + 1].append(proceso_actual)
                    else:  # Reinsertar en la misma cola si está en la última
                        colas[nivel].append(proceso_actual)
                else:
                    duracion_total = proceso_actual[2]
                    tiempos.append((nombre, tiempo_actual - llegada, tiempo_actual - llegada - duracion_total))
                proceso_encontrado = True
                break  # Salir del bucle de colas una vez que se ejecuta un proceso

        if not proceso_encontrado:  # Si no hay procesos para ejecutar, avanzar el tiempo
            tiempo_actual += 1

    return gantt, tiempos

#Se crea la función de las metricas
def calcular_metricas(tiempos):
    """
    La función se encarga de calcular las metricas de rendimiento de cada método para procesos, con parametros:
    T: retorno
    E: Espera
    P: penalización
    tiempos: lista de las metricas siguiendo este esquema -> (T, E, P) en cada proceso

    Retorna: tupla con los promedios de los tiempos de (T, E, P)
    """
    T_prom = sum([t[1] for t in tiempos]) / len(tiempos)
    E_prom = sum([t[2] for t in tiempos]) / len(tiempos)
    P_prom = sum([(t[1] / (t[1] - t[2])) for t in tiempos]) / len(tiempos)
    return T_prom, E_prom, P_prom

#Función para programa principal
def main():
    """
    Función principal que ejecuta el programa y compara los algoritmos de planificación.
    """
    rondas = 5  # Se especifica el número de rondas que hará el programa
    for ronda in range(rondas):
        print(f"\n Ronda {ronda + 1}:")
        procesos = generar_procesos(5)

        for algoritmo, funcion, parametros in [("FCFS", fcfs, None),
                                                ("RR1", rr, 1),
                                                ("RR4", rr, 4),
                                                ("SPN", spn, None),
                                                ("FB", fb, None)]:
            if parametros is None:
                gantt, tiempos = funcion(procesos)
            else:
                gantt, tiempos = funcion(procesos, parametros)

            T_prom, E_prom, P_prom = calcular_metricas(tiempos)
            gantt_str = ''.join(gantt)
            print(f"  {algoritmo}: T={T_prom:.2f}, E={E_prom:.2f}, P={P_prom:.2f}")
            print(f"  {gantt_str}")

if __name__ == "__main__":
    main()
