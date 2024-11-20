#Creado por:
#María Guadalupe Martínez Pavón (318071280)

import random
from collections import deque
import matplotlib.pyplot as plt


# Generar una lista de procesos aleatorios
def generar_procesos(num_procesos, tiempo_max_llegada, tiempo_max_ejecucion):
    procesos = []
    for i in range(num_procesos):
        tiempo_llegada = random.randint(0, tiempo_max_llegada)
        tiempo_ejecucion = random.randint(1, tiempo_max_ejecucion)
        prioridad = random.randint(1, 3)  # Nivel de prioridad (1: Alta, 2: Media, 3: Baja)
        procesos.append(
            {'id': chr(65 + i), 'llegada': tiempo_llegada, 'ejecucion': tiempo_ejecucion, 'prioridad': prioridad})
    return sorted(procesos, key=lambda x: x['llegada'])


# Algoritmo de colas múltiples
def colas_multiples(procesos):
    colas = {1: deque(), 2: deque(), 3: deque()}  # Tres niveles de prioridad
    resultados = []
    tiempo_actual = 0

    for proceso in procesos:
        colas[proceso['prioridad']].append(proceso)

    while any(colas.values()):
        for prioridad in range(1, 4):  # Procesar de mayor a menor prioridad
            if colas[prioridad]:
                proceso = colas[prioridad].popleft()
                if tiempo_actual < proceso['llegada']:
                    tiempo_actual = proceso['llegada']
                inicio = tiempo_actual
                tiempo_actual += proceso['ejecucion']
                fin = tiempo_actual
                retorno = fin - proceso['llegada']
                espera = inicio - proceso['llegada']
                penalizacion = retorno / proceso['ejecucion']
                resultados.append({'id': proceso['id'], 'prioridad': prioridad, 'inicio': inicio, 'fin': fin,
                                   'espera': espera, 'retorno': retorno, 'penalizacion': penalizacion})
    return resultados


# Generar esquema visual
def generar_esquema(procesos, resultados, titulo):
    fig, ax = plt.subplots(figsize=(10, 6))
    y_ticks = []
    colors = ['skyblue', 'lightgreen', 'salmon', 'gold', 'lightcoral']
    for i, r in enumerate(resultados):
        ax.barh(r['id'], r['fin'] - r['inicio'], left=r['inicio'], color=colors[i % len(colors)], edgecolor='black')
        y_ticks.append(r['id'])
    ax.set_title(titulo)
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Procesos")
    ax.set_yticks(range(len(y_ticks)))
    ax.set_yticklabels(y_ticks)
    plt.show()


# Simulación principal
def simular(num_simulaciones=1):
    num_procesos = 5
    tiempo_max_llegada = 10
    tiempo_max_ejecucion = 10

    for i in range(num_simulaciones):
        print(f"Simulación {i + 1}:")
        procesos = generar_procesos(num_procesos, tiempo_max_llegada, tiempo_max_ejecucion)
        print("Cargas:")
        for p in procesos:
            print(f"{p['id']}: Llegada={p['llegada']}, Ejecución={p['ejecucion']}, Prioridad={p['prioridad']}")
        print()

        # Colas Múltiples
        resultados_colas = colas_multiples(procesos)
        for r in resultados_colas:
            print(f"{r['id']}: Prioridad={r['prioridad']}, Inicio={r['inicio']}, Fin={r['fin']}, "
                  f"Espera={r['espera']}, Retorno={r['retorno']}, Penalización={r['penalizacion']:.2f}")

        # Generar esquema visual
        generar_esquema(procesos, resultados_colas, "Esquema de Colas Múltiples")
        print()


# Ejecutar simulación
simular()
