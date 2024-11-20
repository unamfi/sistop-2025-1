'''*********************************************************
        Tarea 2 - Comparacion de Planificadores
        UNAM - Facultad de Ingenieria
        - Lechuga Castillo Shareny Ixchel
        - Gonzalez Cuellar Pablo Arturo

********************************************************+'''


import random

# Clase para crear un proceso
class Proceso:
    def __init__(self, nombre, tiempo_llegada, tiempo_rafaga):
        self.nombre = nombre
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_rafaga = tiempo_rafaga
        self.tiempo_restante = tiempo_rafaga
        self.tiempo_finalizacion = 0
        self.tiempo_espera = 0
        self.tiempo_retorno = 0

# Funcion para generar procesos 
def generar_procesos(numero_procesos):
    nombres = [chr(65 + i) for i in range(numero_procesos)]  
    procesos = []
    for nombre in nombres:
        tiempo_llegada = random.randint(0, 10)  # Llegadas entre 0 y 10
        tiempo_rafaga = random.randint(1, 10)   # Ráfagas entre 1 y 10
        procesos.append(Proceso(nombre, tiempo_llegada, tiempo_rafaga))
    return procesos

# Crear copias independientes de los procesos
def copiar_procesos(procesos):
    return [Proceso(p.nombre, p.tiempo_llegada, p.tiempo_rafaga) for p in procesos]
    #cada algoritmo trabaja con sus propios procesos

# Algoritmo FCFS
def fcfs(procesos):
    procesos.sort(key=lambda p: p.tiempo_llegada)
    tiempo_actual = 0
    secuencia = ""
    for p in procesos:
        if tiempo_actual < p.tiempo_llegada:
            tiempo_actual = p.tiempo_llegada
        secuencia += p.nombre * p.tiempo_rafaga
        p.tiempo_finalizacion = tiempo_actual + p.tiempo_rafaga
        p.tiempo_retorno = p.tiempo_finalizacion - p.tiempo_llegada
        p.tiempo_espera = p.tiempo_retorno - p.tiempo_rafaga
        tiempo_actual += p.tiempo_rafaga
    return procesos, secuencia

# Algoritmo Round Robin
def round_robin(procesos, quantum):
    cola = [p for p in sorted(procesos, key=lambda p: p.tiempo_llegada)]
    tiempo_actual = 0
    completados = []
    secuencia = ""
    while cola:
        proceso = cola.pop(0)
        if proceso.tiempo_llegada > tiempo_actual:
            tiempo_actual = proceso.tiempo_llegada
        if proceso.tiempo_restante > quantum:
            proceso.tiempo_restante -= quantum
            tiempo_actual += quantum
            secuencia += proceso.nombre * quantum
            cola.append(proceso)
        else:
            tiempo_actual += proceso.tiempo_restante
            secuencia += proceso.nombre * proceso.tiempo_restante
            proceso.tiempo_restante = 0
            proceso.tiempo_finalizacion = tiempo_actual
            proceso.tiempo_retorno = proceso.tiempo_finalizacion - proceso.tiempo_llegada
            proceso.tiempo_espera = proceso.tiempo_retorno - proceso.tiempo_rafaga
            completados.append(proceso)
    return completados, secuencia

# Algoritmo SPN
def spn(procesos):
    cola_listos = []
    tiempo_actual = 0
    completados = []
    secuencia = ""
    procesos.sort(key=lambda p: p.tiempo_llegada)

    while procesos or cola_listos:
        while procesos and procesos[0].tiempo_llegada <= tiempo_actual:
            cola_listos.append(procesos.pop(0))
        if cola_listos:
            cola_listos.sort(key=lambda p: p.tiempo_rafaga)
            proceso = cola_listos.pop(0)
            tiempo_actual += proceso.tiempo_rafaga
            secuencia += proceso.nombre * proceso.tiempo_rafaga
            proceso.tiempo_finalizacion = tiempo_actual
            proceso.tiempo_retorno = proceso.tiempo_finalizacion - proceso.tiempo_llegada
            proceso.tiempo_espera = proceso.tiempo_retorno - proceso.tiempo_rafaga
            completados.append(proceso)
        else:
            tiempo_actual += 1
    return completados, secuencia

# Funcion para calcular métricas
def calcular_metricas(procesos):
    total_retorno = sum(p.tiempo_retorno for p in procesos)
    total_espera = sum(p.tiempo_espera for p in procesos)
    total_penalizacion = sum(p.tiempo_retorno / p.tiempo_rafaga for p in procesos)
    n = len(procesos)
    return total_retorno / n, total_espera / n, total_penalizacion / n



def main():
    numero_rondas = 3  
    numero_procesos = 6 #Posibilidad de ajustar el num de procesos

    for ronda in range(1, numero_rondas + 1):
        print(f"\n--- Ronda {ronda} ---")

        # Generaramos los procesos
        procesos = generar_procesos(numero_procesos)

        # Imprimir tiempo de llegada y de rafaga
        total_rafaga = 0
        for p in procesos:
            print(f"{p.nombre}: TL={p.tiempo_llegada}, TR={p.tiempo_rafaga}", end="; ")
            total_rafaga += p.tiempo_rafaga
        print(f"(total={total_rafaga})\n")

        #Resultados de Ejecuciones de lo diferentes algoritmos

        #Algoritmo FCFS
        resultados_fcfs, secuencia_fcfs = fcfs(copiar_procesos(procesos))
        t, e, p = calcular_metricas(resultados_fcfs)
        print(f"FCFS: T={t:.2f}, E={e:.2f}, P={p:.2f}")
        print(secuencia_fcfs)

        #Algoritmo RR1
        resultados_rr, secuencia_rr = round_robin(copiar_procesos(procesos), 1)
        t, e, p = calcular_metricas(resultados_rr)
        print(f"RR1: T={t:.2f}, E={e:.2f}, P={p:.2f}")
        print(secuencia_rr)

        #Algoritmo RR4
        resultados_rr2, secuencia_rr2= round_robin(copiar_procesos(procesos), 4)
        t, e, p = calcular_metricas(resultados_rr2)
        print(f"RR4: T={t:.2f}, E={e:.2f}, P={p:.2f}")
        print(secuencia_rr2)

        #Algoritmo SPN
        resultados_spn, secuencia_spn = spn(copiar_procesos(procesos))
        t, e, p = calcular_metricas(resultados_spn)
        print(f"SPN: T={t:.2f}, E={e:.2f}, P={p:.2f}")
        print(secuencia_spn)

if __name__ == "__main__":
    main()
