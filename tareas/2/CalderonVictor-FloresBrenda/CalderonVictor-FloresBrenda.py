import random

# Función para generar procesos aleatorios
def generar_procesos(num_procesos):
    procesos = []
    tiempos_llegada = [random.randint(0, 10) for _ in range(num_procesos)]
    duraciones = [random.randint(1, 10) for _ in range(num_procesos)]
    for i in range(num_procesos):
        procesos.append({
            "nombre": chr(65 + i),
            "llegada": tiempos_llegada[i],
            "duracion": duraciones[i]
        })
    procesos.sort(key=lambda x: x["llegada"])
    return procesos

# Implementación de FCFS
def fcfs(procesos):
    tiempo_actual = 0
    resultados = []
    metricas = {"T": [], "E": [], "P": []}

    for proceso in procesos:
        if tiempo_actual < proceso["llegada"]:
            tiempo_actual = proceso["llegada"]
        tiempo_finalizacion = tiempo_actual + proceso["duracion"]
        T = tiempo_finalizacion - proceso["llegada"]
        E = T - proceso["duracion"]
        P = T / proceso["duracion"]
        metricas["T"].append(T)
        metricas["E"].append(E)
        metricas["P"].append(P)
        resultados.append(proceso["nombre"] * proceso["duracion"])
        tiempo_actual = tiempo_finalizacion

    return "".join(resultados), metricas

# Implementación de Round Robin
def round_robin(procesos, quantum):
    tiempo_actual = 0
    cola = procesos.copy()
    resultados = []
    metricas = {"T": [], "E": [], "P": []}
    for p in cola:
        p["restante"] = p["duracion"]

    while cola:
        proceso = cola.pop(0)
        tiempo_ejecucion = min(quantum, proceso["restante"])
        tiempo_actual += tiempo_ejecucion
        proceso["restante"] -= tiempo_ejecucion
        resultados.append(proceso["nombre"] * tiempo_ejecucion)

        if proceso["restante"] > 0:
            cola.append(proceso)
        else:
            T = tiempo_actual - proceso["llegada"]
            E = T - proceso["duracion"]
            P = T / proceso["duracion"]
            metricas["T"].append(T)
            metricas["E"].append(E)
            metricas["P"].append(P)

    return "".join(resultados), metricas

# Implementación de SPN
def spn(procesos):
    tiempo_actual = 0
    cola = []
    resultados = []
    metricas = {"T": [], "E": [], "P": []}
    procesos_restantes = procesos.copy()

    while procesos_restantes or cola:
        for proceso in procesos_restantes[:]:
            if proceso["llegada"] <= tiempo_actual:
                cola.append(proceso)
                procesos_restantes.remove(proceso)
        cola.sort(key=lambda x: x["duracion"])

        if cola:
            proceso = cola.pop(0)
            tiempo_actual += proceso["duracion"]
            resultados.append(proceso["nombre"] * proceso["duracion"])
            T = tiempo_actual - proceso["llegada"]
            E = T - proceso["duracion"]
            P = T / proceso["duracion"]
            metricas["T"].append(T)
            metricas["E"].append(E)
            metricas["P"].append(P)
        else:
            tiempo_actual += 1

    return "".join(resultados), metricas

# Función principal para comparar algoritmos
def comparar_algoritmos(num_cargas, num_procesos, quantum):
    for i in range(num_cargas):
        print(f"\nCARGA {i + 1}:")
        procesos = generar_procesos(num_procesos)
        print("Procesos:")
        for p in procesos:
            print(f"{p['nombre']}: llegada={p['llegada']}, duración={p['duracion']}")

        # FCFS
        secuencia_fcfs, metricas_fcfs = fcfs(procesos)
        print("\nFCFS:")
        print(f"Secuencia: {secuencia_fcfs}")
        print("T=%.2f, E=%.2f, P=%.2f" % (
            sum(metricas_fcfs["T"]) / len(metricas_fcfs["T"]),
            sum(metricas_fcfs["E"]) / len(metricas_fcfs["E"]),
            sum(metricas_fcfs["P"]) / len(metricas_fcfs["P"])
        ))

        # Round Robin
        secuencia_rr, metricas_rr = round_robin(procesos, quantum)
        print("\nRound Robin:")
        print(f"Secuencia: {secuencia_rr}")
        print("T=%.2f, E=%.2f, P=%.2f" % (
            sum(metricas_rr["T"]) / len(metricas_rr["T"]),
            sum(metricas_rr["E"]) / len(metricas_rr["E"]),
            sum(metricas_rr["P"]) / len(metricas_rr["P"])
        ))

        # SPN
        secuencia_spn, metricas_spn = spn(procesos)
        print("\nSPN:")
        print(f"Secuencia: {secuencia_spn}")
        print("T=%.2f, E=%.2f, P=%.2f" % (
            sum(metricas_spn["T"]) / len(metricas_spn["T"]),
            sum(metricas_spn["E"]) / len(metricas_spn["E"]),
            sum(metricas_spn["P"]) / len(metricas_spn["P"])
        ))

# Ejecutar la comparación con 5 cargas, 5 procesos por carga y quantum = 2
comparar_algoritmos(num_cargas=5, num_procesos=5, quantum=2)
