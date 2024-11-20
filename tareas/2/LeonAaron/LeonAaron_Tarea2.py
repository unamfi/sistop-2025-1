import random
from collections import deque

class Proceso:
    def __init__(self, nombre, llegada, duracion):
        self.nombre = nombre
        self.llegada = llegada
        self.duracion = duracion
        self.tiempo_restante = duracion

def generar_procesos(n, max_llegada=10, max_duracion=7):
    procesos = []
    tiempo_llegada = 0
    for i in range(n):
        duracion = random.randint(2, max_duracion)
        procesos.append(Proceso(chr(65 + i), tiempo_llegada, duracion))
        tiempo_llegada += random.randint(1, 4)
    return procesos

def fcfs(procesos):
    tiempo = 0
    resultado = []
    tiempos_finalizacion = []
    for proceso in procesos:
        if tiempo < proceso.llegada:
            tiempo = proceso.llegada
        tiempo += proceso.duracion
        resultado.extend([proceso.nombre] * proceso.duracion)
        tiempos_finalizacion.append(tiempo)
    return resultado, tiempos_finalizacion

def rr(procesos, quantum):
    tiempo = 0
    cola = deque([p for p in procesos if p.llegada <= tiempo])
    pendientes = deque([p for p in procesos if p.llegada > tiempo])
    resultado = []
    tiempos_finalizacion = {}

    while cola or pendientes:
        if not cola and pendientes:
            tiempo = pendientes[0].llegada
            cola.append(pendientes.popleft())

        proceso = cola.popleft()
        ejecutado = min(proceso.tiempo_restante, quantum)
        proceso.tiempo_restante -= ejecutado
        resultado.extend([proceso.nombre] * ejecutado)
        tiempo += ejecutado

        if proceso.tiempo_restante == 0:
            tiempos_finalizacion[proceso.nombre] = tiempo
        else:
            cola.append(proceso)

        while pendientes and pendientes[0].llegada <= tiempo:
            cola.append(pendientes.popleft())

    return resultado, [tiempos_finalizacion[p.nombre] for p in procesos]

def spn(procesos):
    tiempo = 0
    lista_espera = sorted(procesos, key=lambda p: (p.llegada, p.duracion))
    resultado = []
    tiempos_finalizacion = []
    while lista_espera:
        candidatos = [p for p in lista_espera if p.llegada <= tiempo]
        if not candidatos:
            tiempo = lista_espera[0].llegada
            continue
        proceso = min(candidatos, key=lambda p: p.duracion)
        lista_espera.remove(proceso)
        tiempo += proceso.duracion
        resultado.extend([proceso.nombre] * proceso.duracion)
        tiempos_finalizacion.append(tiempo)
    return resultado, tiempos_finalizacion

def calcular_metricas(tiempos_finalizacion, procesos):
    n = len(procesos)
    turnaround = sum([t - p.llegada for t, p in zip(tiempos_finalizacion, procesos)]) / n
    espera = sum([t - p.llegada - p.duracion for t, p in zip(tiempos_finalizacion, procesos)]) / n
    penalizacion = sum([t / p.duracion for t, p in zip(tiempos_finalizacion, procesos)]) / n
    return turnaround, espera, penalizacion

def mostrar_esquema_visual(resultado, algoritmo):
    print(f"{algoritmo}:")
    print("".join(resultado))

def ejecutar_ronda(ronda, num_procesos=5):
    print(f"\nRonda {ronda}:")
    procesos = generar_procesos(num_procesos)
    for p in procesos:
        print(f"{p.nombre}: llegada={p.llegada}, duración={p.duracion}")
    print()

    # FCFS
    fcfs_resultado, fcfs_finalizacion = fcfs(procesos)
    fcfs_metricas = calcular_metricas(fcfs_finalizacion, procesos)
    mostrar_esquema_visual(fcfs_resultado, "FCFS")
    print(f"T={fcfs_metricas[0]:.2f}, E={fcfs_metricas[1]:.2f}, P={fcfs_metricas[2]:.2f}\n")

    # RR con quantum 1
    rr1_resultado, rr1_finalizacion = rr(procesos, 1)
    rr1_metricas = calcular_metricas(rr1_finalizacion, procesos)
    mostrar_esquema_visual(rr1_resultado, "RR1")
    print(f"T={rr1_metricas[0]:.2f}, E={rr1_metricas[1]:.2f}, P={rr1_metricas[2]:.2f}\n")

    # RR con quantum 4
    rr4_resultado, rr4_finalizacion = rr(procesos, 4)
    rr4_metricas = calcular_metricas(rr4_finalizacion, procesos)
    mostrar_esquema_visual(rr4_resultado, "RR4")
    print(f"T={rr4_metricas[0]:.2f}, E={rr4_metricas[1]:.2f}, P={rr4_metricas[2]:.2f}\n")

    # SPN
    spn_resultado, spn_finalizacion = spn(procesos)
    spn_metricas = calcular_metricas(spn_finalizacion, procesos)
    mostrar_esquema_visual(spn_resultado, "SPN")
    print(f"T={spn_metricas[0]:.2f}, E={spn_metricas[1]:.2f}, P={spn_metricas[2]:.2f}\n")

def main():
    for i in range(1, 6):
        ejecutar_ronda(i)

if __name__ == "__main__":
    main()
