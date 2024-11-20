import random

#Función para generar procesos aleatorios, se llama en cada ronda y recibe 5
def generar_procesos(n):
    procesos = []
    for i in range(n):
        #Tiempo de llegada aleatorio entre 0 y 10
        llegada = random.randint(0, 10)
        #Duración aleatoria entre 1 y 10
        duracion = random.randint(1, 10)

        #Añade a la lista cada proceso A, B, ...
        procesos.append((chr(65 + i), llegada, duracion))
    return sorted(procesos, key=lambda x: x[1])  #Ordenados por tiempo de llegada

#Algoritmo FCFS, First-Come, First-Served
def fcfs(procesos):
    tiempo_actual = 0
    tiempos_finalizacion = []
    #Para almacenar la secuencia de ejecución
    secuencia = []
    #Iteramos sobre cada proceso estando estos ya ordenados por su tiempo de llegada
    for proceso in procesos:
    #Para cada proceso acumulamos en 'tiempo_actual' lo que tarda cada uno 
        if tiempo_actual < proceso[1]:
            tiempo_actual = proceso[1]
        tiempo_actual += proceso[2]
        #Agregar el ID del proceso veces lo que dura, para el esquema visual
        secuencia.extend([proceso[0]] * proceso[2])
        #Añadimos el id del proceso, tiempo que pasó hasta que terminó (T) y cuánto tiempo pasó antes de ejecutarse (E)
        tiempos_finalizacion.append((proceso[0], tiempo_actual - proceso[1], tiempo_actual - proceso[1] - proceso[2]))
    return tiempos_finalizacion, ''.join(secuencia)

# Algoritmo Round Robin
def round_robin(procesos, quantum):
    tiempo_actual = 0
    cola = []
    #Diccionario que almacena la duración restante de cada proceso
    tiempos_restantes = {p[0]: p[2] for p in procesos}
    tiempos_finalizacion = {}
    espera = {}
    #Copia de los procesos originales
    procesos_por_llegar = list(procesos)
    #Para almacenar la secuencia de ejecución
    secuencia = []

    '''Bucle que se ejecutará si aún hay procesos en la cola, procesos que no han llegado o alguno tiene
    tiempo restante para ejecutarse'''
    while cola or procesos_por_llegar or any(t > 0 for t in tiempos_restantes.values()):

        #Añadir a la cola los procesos que han llegado
        while procesos_por_llegar and procesos_por_llegar[0][1] <= tiempo_actual:
            cola.append(procesos_por_llegar.pop(0))

        if cola:
            #Tomar el primer proceso de la cola
            proceso = cola.pop(0)
            id, llegada, _ = proceso

            #Ejecutar el proceso por un tiempo igual al quantum o lo que reste, avanzamos el tiempo
            tiempo_ejecucion = min(quantum, tiempos_restantes[id])
            tiempo_actual += tiempo_ejecucion
            #Reducción del tiempo restante
            tiempos_restantes[id] -= tiempo_ejecucion
            #Agregar el ID del proceso veces lo que dura, para el esquema visual
            secuencia.extend([id] * tiempo_ejecucion)

            #Si el proceso terminó, calcular tiempos
            if tiempos_restantes[id] == 0:
                tiempos_finalizacion[id] = tiempo_actual
                #Calcular tiempo de espera
                espera[id] = tiempo_actual - llegada - proceso[2]
            else:
                #Si no terminó, reinsertar en la cola
                cola.append(proceso)
        else:
            #Si no hay procesos en la cola, avanzar el tiempo
            tiempo_actual += 1

    tiempos = [(id, tiempos_finalizacion[id] - llegada, espera[id]) for id, llegada, _ in procesos]
    return tiempos, ''.join(secuencia)

# Algoritmo SPN
def spn(procesos):
    tiempo_actual = 0
    cola = []
    tiempos_finalizacion = []
    #Para almacenar la secuencia de ejecución
    secuencia = []

    #Bucle que se ejecutará mientras haya procesos por llegar o haya alguno en la cola
    while procesos or cola:
        while procesos and procesos[0][1] <= tiempo_actual:
            #Mover a la cola de procesos disponibles
            cola.append(procesos.pop(0))

        if cola:
            #Ordenar por duración
            cola.sort(key=lambda x: x[2])
            #Ya ordenados en la cola, elegimos el más corto
            proceso = cola.pop(0)
            id, llegada, duracion = proceso
            tiempo_actual = max(tiempo_actual, llegada) + duracion
            #Agregar el ID del proceso veces lo que dura, para el esquema visual
            secuencia.extend([id] * duracion)
            tiempos_finalizacion.append((id, tiempo_actual - llegada, tiempo_actual - llegada - duracion))
        else:
            #Si no hay procesos disponibles, avanzar el tiempo
            tiempo_actual += 1

    return tiempos_finalizacion, ''.join(secuencia)

#Calcular métricas de rendimiento
def calcular_metricas(tiempos):
    totales = [t[1] for t in tiempos]
    esperas = [t[2] for t in tiempos]
    return {
        #Tiempo de retorno promedio
        "T": round(sum(totales) / len(tiempos), 2),
        #Tiempo de espera promedio
        "E": round(sum(esperas) / len(tiempos), 2),
        #Proporción promedio
        "P": round(sum(t / (t - e) for t, e in zip(totales, esperas)) / len(tiempos), 2)
    }

# Simulación principal
def simular():
    rondas = 5
    for ronda in range(rondas):
        print(f"- Ronda {ronda + 1}")
        procesos = generar_procesos(5)

        #Impresión de los 5 procesos generados con su respectivo tiempo de llegada y duración
        print("  ", "; ".join([f"{p[0]}: {p[1]}, t = {p[2]}" for p in procesos]), f"(Total: {sum(p[2] for p in procesos)})")
        
        #Ejecutar algoritmos
        resultados_fcfs, secuencia_fcfs = fcfs(procesos)
        resultados_rr1, secuencia_rr1 = round_robin(procesos, 1)
        resultados_rr4, secuencia_rr4 = round_robin(procesos, 4)
        resultados_spn, secuencia_spn = spn(procesos)

        #Calcular métricas
        metricas_fcfs = calcular_metricas(resultados_fcfs)
        metricas_rr1 = calcular_metricas(resultados_rr1)
        metricas_rr4 = calcular_metricas(resultados_rr4)
        metricas_spn = calcular_metricas(resultados_spn)

        #Mostrar resultados
        print(f"  FCFS: T={metricas_fcfs['T']}, E={metricas_fcfs['E']}, P={metricas_fcfs['P']}")
        print(f"  {secuencia_fcfs}")
        print(f"  RR1: T={metricas_rr1['T']}, E={metricas_rr1['E']}, P={metricas_rr1['P']}")
        print(f"  {secuencia_rr1}")
        print(f"  RR4: T={metricas_rr4['T']}, E={metricas_rr4['E']}, P={metricas_rr4['P']}")
        print(f"  {secuencia_rr4}")
        print(f"  SPN: T={metricas_spn['T']}, E={metricas_spn['E']}, P={metricas_spn['P']}")
        print(f"  {secuencia_spn}")
        print("\n")

#Arranque de la simulación
simular()