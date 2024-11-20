import random

class Proceso:
    def __init__(self, nombre, llegada, duracion):
        
        """
        Inicializamos los atributos principales del proceso
        """
        self.nombre = nombre
        self.llegada = llegada
        self.duracion = duracion
        self.tiempo_restante = duracion
        self.fin = 0

    def __repr__(self):
        return f"{self.nombre}(L={self.llegada}, D={self.duracion})"


def generar_procesos(num_procesos=5):
    """
    Generamos una lista de procesos con tiempos aleatorios de llegada y duración.
    """
    nombres = ['A', 'B', 'C', 'D', 'E']
    llegada = 0
    procesos = []
    for i in range(num_procesos):
        duracion = random.randint(1, 5)
        procesos.append(Proceso(nombres[i], llegada, duracion))
        llegada += random.randint(0, 2)
    return procesos


def calcular_metricas(terminados):
    """
    Calculamos las métricas de rendimiento para los procesos terminados:
    """
    T = [proceso.fin - proceso.llegada for proceso in terminados]
    E = [t - proceso.duracion for t, proceso in zip(T, terminados)]
    P = [t / proceso.duracion for t, proceso in zip(T, terminados)]
    return {
        'promedio_T': sum(T) / len(T),
        'promedio_E': sum(E) / len(E),
        'promedio_P': sum(P) / len(P),
    }


def imprimir_resultados(nombre_algoritmo, metricas, orden):
    """
    Mostrams las métricas calculadas junto con el orden de ejecución.
    """
    print(f"\n{nombre_algoritmo}:")
    print(f"T = {metricas['promedio_T']:.2f}, E = {metricas['promedio_E']:.2f}, P = {metricas['promedio_P']:.2f}")
    print(f"Orden de ejecución: {''.join(orden)}")


def fcfs(procesos):
    """
    Implementación el algoritmo de planificación First-Come, First-Served (FCFS):
    """
    tiempo_actual = 0
    terminados = []
    orden = []

    for proceso in sorted(procesos, key=lambda p: p.llegada):
        if tiempo_actual < proceso.llegada:
            tiempo_actual = proceso.llegada
        tiempo_actual += proceso.duracion
        proceso.fin = tiempo_actual
        terminados.append(proceso)
        orden.append(proceso.nombre)

    metricas = calcular_metricas(terminados)
    imprimir_resultados("FCFS", metricas, orden)


def round_robin(procesos, quantum):
    """
    Implementamos el algoritmo Round Robin
    """
    tiempo_actual = 0
    cola = sorted(procesos, key=lambda p: p.llegada)
    terminados = []
    orden = []

    while cola:
        proceso = cola.pop(0)
        if tiempo_actual < proceso.llegada:
            tiempo_actual = proceso.llegada

        if proceso.tiempo_restante > quantum:
            proceso.tiempo_restante -= quantum
            tiempo_actual += quantum
            orden.append(proceso.nombre)
            cola.append(proceso)  # Reagregar el proceso
        else:
            tiempo_actual += proceso.tiempo_restante
            proceso.tiempo_restante = 0
            proceso.fin = tiempo_actual
            terminados.append(proceso)
            orden.append(proceso.nombre)

    metricas = calcular_metricas(terminados)
    imprimir_resultados(f"Round Robin (Quantum={quantum})", metricas, orden)


def spn(procesos):
    """
    Implementamos el algoritmo Shortest Process Next
    """
    tiempo_actual = 0
    procesos_restantes = sorted(procesos, key=lambda p: (p.llegada, p.duracion))
    terminados = []
    orden = []

    while procesos_restantes:
        disponibles = [p for p in procesos_restantes if p.llegada <= tiempo_actual]
        if not disponibles:
            tiempo_actual = procesos_restantes[0].llegada
            continue

        proceso = min(disponibles, key=lambda p: p.duracion)
        procesos_restantes.remove(proceso)
        if tiempo_actual < proceso.llegada:
            tiempo_actual = proceso.llegada
        tiempo_actual += proceso.duracion
        proceso.fin = tiempo_actual
        terminados.append(proceso)
        orden.append(proceso.nombre)

    metricas = calcular_metricas(terminados)
    imprimir_resultados("SPN", metricas, orden)


def ejecutar_simulacion(rondas=5):
    """
    Ejecuta las simulaciones con diferentes algoritmos y rondas.
    """
    for ronda in range(1, rondas + 1):
        print(f"\nRonda {ronda}")
        procesos = generar_procesos()
        print("Procesos generados:", procesos)

        # Ejecutar algoritmos
        fcfs(procesos)
        round_robin(procesos, quantum=1) # Ejecutar Round Robin con quantum=1 y 4
        round_robin(procesos, quantum=4)
        spn(procesos)


if __name__ == "__main__":
    ejecutar_simulacion()
