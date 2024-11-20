import random
from collections import deque

# Configuración global
NUM_EJECUCIONES = 5
NUM_PROCESOS = 10
MAX_TIEMPO_EJECUCION = 20
NIVELES_PRIORIDAD = 3  # Para FB

# Generar cargas aleatorias
def generar_cargas(num_procesos):
    return [{'id': i, 'tiempo': random.randint(1, MAX_TIEMPO_EJECUCION)} for i in range(num_procesos)]

# Algoritmo de Colas Múltiples con Retroalimentación (FB)
def retroalimentacion_multinivel(procesos):
    colas = [deque() for _ in range(NIVELES_PRIORIDAD)]
    for p in procesos:
        colas[0].append(p)

    quantum = 2  # Quantum inicial para FB
    tiempo_total = 0
    resultados = []

    while any(colas):
        for nivel, cola in enumerate(colas):
            if cola:
                proceso = cola.popleft()
                tiempo_ejecucion = min(proceso['tiempo'], quantum)
                proceso['tiempo'] -= tiempo_ejecucion
                tiempo_total += tiempo_ejecucion

                resultados.append((proceso['id'], nivel, tiempo_total))
                
                if proceso['tiempo'] > 0:
                    if nivel + 1 < NIVELES_PRIORIDAD:
                        colas[nivel + 1].append(proceso)  # Baja de nivel
                    else:
                        colas[nivel].append(proceso)  # Permanece en el mismo nivel

    return resultados

# Algoritmo de Ronda Egoísta (SRR)
def ronda_egoista(procesos):
    cola = deque(procesos)
    quantum = 2
    tiempo_total = 0
    resultados = []

    while cola:
        proceso = cola.popleft()
        tiempo_ejecucion = min(proceso['tiempo'], quantum)
        proceso['tiempo'] -= tiempo_ejecucion
        tiempo_total += tiempo_ejecucion

        resultados.append((proceso['id'], tiempo_total))
        if proceso['tiempo'] > 0:
            cola.append(proceso)  # Vuelve al final de la cola

    return resultados

# Simular varias ejecuciones
def simular_ejecuciones():
    for i in range(NUM_EJECUCIONES):
        print(f"\n--- Ejecución {i + 1} ---")
        procesos = generar_cargas(NUM_PROCESOS)
        print("Procesos generados:")
        for p in procesos:
            print(f"  Proceso {p['id']}: {p['tiempo']} unidades de tiempo")

        print("\nResultados con Retroalimentación Multinivel (FB):")
        resultados_fb = retroalimentacion_multinivel(procesos)
        for r in resultados_fb:
            print(f"  Proceso {r[0]} terminó en nivel {r[1]} en tiempo {r[2]}")

        print("\nResultados con Ronda Egoísta (SRR):")
        resultados_srr = ronda_egoista(procesos)
        for r in resultados_srr:
            print(f"  Proceso {r[0]} terminó en tiempo {r[1]}")

# Ejecutar simulación
if __name__ == "__main__":
    simular_ejecuciones()
