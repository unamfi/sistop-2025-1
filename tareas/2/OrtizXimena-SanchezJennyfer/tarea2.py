import random

def generar_cargas(num_tareas, max_tiempo_llegada, max_tiempo_ejecucion):
    tareas = []
    for i in range(num_tareas):
        tiempo_llegada = random.randint(0, max_tiempo_llegada)
        tiempo_ejecucion = random.randint(1, max_tiempo_ejecucion)
        tareas.append((f"T{i}", tiempo_llegada, tiempo_ejecucion))
    tareas.sort(key=lambda x: x[1])  # Ordenar por tiempo de llegada
    return tareas

def mapear_tareas_a_letras(tareas):
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    mapeo = {tarea[0]: letras[i] for i, tarea in enumerate(tareas)}
    return mapeo

def fcfs(tareas):
    tiempo_actual = 0
    resultados = []
    for tarea in tareas:
        inicio = max(tiempo_actual, tarea[1])
        fin = inicio + tarea[2]
        tiempo_actual = fin
        resultados.append((tarea[0], inicio, fin))
    return resultados

def round_robin(tareas, quantum):
    cola = tareas[:]
    tiempo_actual = 0
    resultados = {t[0]: [] for t in tareas}
    tiempos_restantes = {t[0]: t[2] for t in tareas}
    while cola:
        tarea = cola.pop(0)
        nombre, llegada, _ = tarea
        if tiempos_restantes[nombre] > 0:
            if llegada <= tiempo_actual:
                tiempo_ejecutado = min(quantum, tiempos_restantes[nombre])
                tiempos_restantes[nombre] -= tiempo_ejecutado
                resultados[nombre].append((tiempo_actual, tiempo_actual + tiempo_ejecutado))
                tiempo_actual += tiempo_ejecutado
                if tiempos_restantes[nombre] > 0:
                    cola.append((nombre, llegada, tiempos_restantes[nombre]))
            else:
                tiempo_actual += 1
                cola.append(tarea)
    return resultados

def spn(tareas):
    tiempo_actual = 0
    cola = []
    resultados = []
    tareas_restantes = tareas[:]
    while tareas_restantes or cola:
        while tareas_restantes and tareas_restantes[0][1] <= tiempo_actual:
            cola.append(tareas_restantes.pop(0))
        if cola:
            cola.sort(key=lambda x: x[2])  # Ordenar por menor tiempo de ejecución
            tarea = cola.pop(0)
            inicio = max(tiempo_actual, tarea[1])
            fin = inicio + tarea[2]
            tiempo_actual = fin
            resultados.append((tarea[0], inicio, fin))
        else:
            tiempo_actual += 1
    return resultados

def calcular_metricas(tareas, resultados):
    tiempos_finalizacion = {t[0]: 0 for t in tareas}
    for tarea, inicio, fin in resultados:
        tiempos_finalizacion[tarea] = fin
    turnarounds = [tiempos_finalizacion[t[0]] - t[1] for t in tareas]
    esperas = [turnarounds[i] - tareas[i][2] for i in range(len(tareas))]
    T = sum(turnarounds) / len(tareas)
    E = sum(esperas) / len(tareas)
    P = sum(turnarounds[i] / tareas[i][2] for i in range(len(tareas))) / len(tareas)
    return T, E, P

def generar_visualizacion(resultados, duracion_total, mapeo):
    linea_tiempo = [' '] * (duracion_total + 1)
    if isinstance(resultados, list):  # Para FCFS y SPN
        for tarea, inicio, fin in resultados:
            for t in range(inicio, fin):
                linea_tiempo[t] = mapeo[tarea]
    elif isinstance(resultados, dict):  # Para Round Robin
        for tarea, segmentos in resultados.items():
            for inicio, fin in segmentos:
                for t in range(inicio, fin):
                    linea_tiempo[t] = mapeo[tarea]
    return ''.join(linea_tiempo)

def imprimir_resultados(simulaciones, quantum1, quantum4):
    for i, simulacion in enumerate(simulaciones):
        print(f"\n- Ronda {i + 1}:")
        tareas = simulacion["tareas"]
        mapeo = mapear_tareas_a_letras(tareas)
        descripcion_tareas = "; ".join([f"{mapeo[t[0]]}: {t[1]}, t={t[2]}" for t in tareas])
        duracion_total = max(max(t[1] + t[2] for t in tareas),  # Considerar la finalización más tardía
                             max(max(segmento[1] for segmento in rr) for rr in simulacion["rr1"].values()))
        print(f"  {descripcion_tareas} (tot: {sum(t[2] for t in tareas)})")

        fcfs_resultados = simulacion["fcfs"]
        T_fcfs, E_fcfs, P_fcfs = calcular_metricas(tareas, fcfs_resultados)
        visual_fcfs = generar_visualizacion(fcfs_resultados, duracion_total, mapeo)
        print(f"  FCFS: T={T_fcfs:.2f}, E={E_fcfs:.2f}, P={P_fcfs:.2f}")
        print(f"  {visual_fcfs}")

        rr1_resultados = simulacion["rr1"]
        rr1_lista = [(t, inicio, fin) for t, tiempos in rr1_resultados.items() for inicio, fin in tiempos]
        T_rr1, E_rr1, P_rr1 = calcular_metricas(tareas, rr1_lista)
        visual_rr1 = generar_visualizacion(rr1_resultados, duracion_total, mapeo)
        print(f"  RR1: T={T_rr1:.2f}, E={E_rr1:.2f}, P={P_rr1:.2f}")
        print(f"  {visual_rr1}")

        rr4_resultados = simulacion["rr4"]
        rr4_lista = [(t, inicio, fin) for t, tiempos in rr4_resultados.items() for inicio, fin in tiempos]
        T_rr4, E_rr4, P_rr4 = calcular_metricas(tareas, rr4_lista)
        visual_rr4 = generar_visualizacion(rr4_resultados, duracion_total, mapeo)
        print(f"  RR4: T={T_rr4:.2f}, E={E_rr4:.2f}, P={P_rr4:.2f}")
        print(f"  {visual_rr4}")

        spn_resultados = simulacion["spn"]
        T_spn, E_spn, P_spn = calcular_metricas(tareas, spn_resultados)
        visual_spn = generar_visualizacion(spn_resultados, duracion_total, mapeo)
        print(f"  SPN: T={T_spn:.2f}, E={E_spn:.2f}, P={P_spn:.2f}")
        print(f"  {visual_spn}")

def ejecutar_simulaciones(num_simulaciones, num_tareas, max_tiempo_llegada, max_tiempo_ejecucion, quantum1, quantum4):
    resultados = []
    for _ in range(num_simulaciones):
        tareas = generar_cargas(num_tareas, max_tiempo_llegada, max_tiempo_ejecucion)
        fcfs_resultado = fcfs(tareas)
        rr1_resultado = round_robin(tareas, quantum1)
        rr4_resultado = round_robin(tareas, quantum4)
        spn_resultado = spn(tareas)
        resultados.append({
            "tareas": tareas,
            "fcfs": fcfs_resultado,
            "rr1": rr1_resultado,
            "rr4": rr4_resultado,
            "spn": spn_resultado,
        })
    return resultados

num_simulaciones = 5
simulaciones = ejecutar_simulaciones(num_simulaciones, num_tareas=5, max_tiempo_llegada=10, max_tiempo_ejecucion=10, quantum1=1, quantum4=4)
imprimir_resultados(simulaciones, quantum1=1, quantum4=4)
