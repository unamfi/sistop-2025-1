import random
from colorama import Fore, Style

# Función para generar procesos aleatorios
# Genera una lista de procesos con duración aleatoria, según los parámetros definidos.
# Parámetros:
#   lista_procesos (list): Lista donde se agregarán los procesos generados.
#   n_procesos (int): Número de procesos a generar.
#   probabilidad (int): Probabilidad de generar un proceso (1 en P).
#   tiempo_min (int): Duración mínima de los procesos generados.
#   tiempo_max (int): Duración máxima de los procesos generados.

def generar_procesos(lista_procesos, n_procesos, probabilidad, tiempo_min, tiempo_max):
    for i in range(n_procesos):
        if random.randint(1, probabilidad) == 1:  # Probabilidad de generar el proceso
            duracion = random.randint(tiempo_min, tiempo_max)  # Duración aleatoria
            lista_procesos.append((chr(65 + i), duracion))  # Agrega el proceso a la lista
    if not lista_procesos:
        print(Fore.RED + "No se generaron procesos. Intenta ajustar la probabilidad." + Style.RESET_ALL)
        exit()
        

# Función para calcular promedios y mostrar resultados
# Muestra los resultados en consola con formato colorido y calcula promedios de T, E y P.
# Parámetros:
#   tabla (list): Lista con los datos de los procesos (nombre, duración, inicio, fin, T, E, P).
#   algoritmo (str): Nombre del algoritmo utilizado.
#   esquema (str): Cadena que representa el esquema de ejecución de los procesos.

def calcular_y_mostrar(tabla, algoritmo, esquema=None):
    
    print(Fore.CYAN + f"\n{algoritmo}\n" + Style.RESET_ALL)
    print(Fore.YELLOW + "Proceso\tDuración\tInicio\tFin\tT\tE\tP" + Style.RESET_ALL)

    t_total, e_total, p_total = 0, 0, 0
    for proceso in tabla:
        print(f"{proceso[0]}\t{proceso[1]}\t\t{proceso[2]}\t{proceso[3]}\t{proceso[4]}\t{proceso[5]}\t{proceso[6]:.2f}")
        t_total += proceso[4]
        e_total += proceso[5]
        p_total += proceso[6]

    n = len(tabla)
    print(Fore.GREEN + f"Promedio:\t\t\t\t\tT={t_total / n:.2f}\tE={e_total / n:.2f}\tP={p_total / n:.2f}" + Style.RESET_ALL)
    
    if esquema:
        print(Fore.MAGENTA + f"ESQUEMA:\n{esquema}" + Style.RESET_ALL)
        

# Algoritmo FCFS (First Come First Served)
# Los procesos se ejecutan en el orden en que llegan sin interrupciones.
# Parámetros:
#   lista_procesos (list): Lista de procesos con su duración.

def fcfs(lista_procesos):
    tiempo = 0  # Variable que lleva el tiempo total de ejecución
    tabla = []  # Tabla para almacenar los resultados de cada proceso
    for proceso, duracion in lista_procesos:
        inicio = max(tiempo, 0)  # El inicio es el tiempo actual
        fin = inicio + duracion  # El fin es el inicio más la duración del proceso
        tiempo = fin  # Actualiza el tiempo total
        t = fin - inicio  # Tiempo total de ejecución
        e = inicio - 0  # Tiempo de espera
        p = t / duracion  # Tiempo de respuesta (T/D)
        tabla.append((proceso, duracion, inicio, fin, t, e, p))  # Guarda el resultado
    calcular_y_mostrar(tabla, "FCFS")
    

# Algoritmo Round Robin con quantum variable
# Los procesos se ejecutan de manera cíclica en bloques de tamaño igual a la quantum.
# Parámetros:
#   lista_procesos (list): Lista de procesos con su duración.
#   quantum (int): Tiempo máximo que puede ejecutarse cada proceso antes de pasar al siguiente.

def round_robin_n(lista_procesos, quantum):
    tareas_cola = [(proceso, duracion, i, 0) for i, (proceso, duracion) in enumerate(lista_procesos)]
    esquema = ""
    tiempo = 0
    tabla = []
    while tareas_cola:
        proceso_actual = tareas_cola.pop(0)
        proceso, duracion, idx, inicio = proceso_actual
        if inicio == 0:
            inicio = tiempo
        duracion_actual = min(duracion, quantum)
        esquema += proceso * duracion_actual
        tiempo += duracion_actual
        duracion -= duracion_actual
        if duracion > 0:
            tareas_cola.append((proceso, duracion, idx, inicio))
        else:
            fin = tiempo
            t = fin - inicio
            e = inicio - 0
            p = t / lista_procesos[idx][1]
            tabla.append((proceso, lista_procesos[idx][1], inicio, fin, t, e, p))
    calcular_y_mostrar(tabla, f"Round Robin (Q={quantum})", esquema)
    

# Algoritmo Shortest Process Next (SPN)
# Se ejecutan primero los procesos más cortos.
# Parámetros:
#   lista_procesos (list): Lista de procesos con su duración.

def shortest_process_next(lista_procesos):
    lista_procesos_ordenada = sorted(lista_procesos, key=lambda x: x[1])  # Ordena los procesos por duración
    tiempo = 0
    tabla = []
    for proceso, duracion in lista_procesos_ordenada:
        inicio = max(tiempo, 0)
        fin = inicio + duracion
        tiempo = fin
        t = fin - inicio
        e = inicio - 0
        p = t / duracion
        tabla.append((proceso, duracion, inicio, fin, t, e, p))
    calcular_y_mostrar(tabla, "Shortest Process Next")
    

# Algoritmo Selfish Round Robin
# Se ejecutan los procesos de manera Round Robin pero con quantum distinto para los procesos A y B.
# Parámetros:
#   lista_procesos (list): Lista de procesos con su duración.
#   quantum_a (int): Quantum para el proceso A.
#   quantum_b (int): Quantum para el proceso B.

def selfish_round_robin(lista_procesos, quantum_a, quantum_b):
    esquema = ""
    tiempo = 0
    tabla = []
    tareas_cola = [(proceso, duracion, i, 0) for i, (proceso, duracion) in enumerate(lista_procesos)]

    while tareas_cola:
        proceso_actual = tareas_cola.pop(0)
        proceso, duracion, idx, inicio = proceso_actual
        if inicio == 0:
            inicio = tiempo
        duracion_actual = min(duracion, quantum_a if proceso == 'A' else quantum_b)
        esquema += proceso * duracion_actual
        tiempo += duracion_actual
        duracion -= duracion_actual
        if duracion > 0:
            tareas_cola.append((proceso, duracion, idx, inicio))
        else:
            fin = tiempo
            t = fin - inicio
            e = inicio - 0
            p = t / lista_procesos[idx][1]
            tabla.append((proceso, lista_procesos[idx][1], inicio, fin, t, e, p))
    calcular_y_mostrar(tabla, f"Selfish Round Robin (A={quantum_a}, B={quantum_b})", esquema)
    

# Punto de entrada principal

if __name__ == "__main__":
    
    # Menú de entrada para el usuario
    print(Fore.BLUE + "Simulador de Planificadores de Procesos" + Style.RESET_ALL)
    procesos = []
    n_procesos = int(input("Número de procesos a generar: "))  # Número de procesos a generar
    probabilidad = int(input("Probabilidad de generación (1 en P): "))  # Probabilidad de generar un proceso
    tiempo_min = int(input("Duración mínima de un proceso: "))  # Duración mínima
    tiempo_max = int(input("Duración máxima de un proceso: "))  # Duración máxima

    # Generación de procesos aleatorios
    generar_procesos(procesos, n_procesos, probabilidad, tiempo_min, tiempo_max)

    # Ejecución de los algoritmos
    print("\n--- Algoritmo FCFS ---")
    fcfs(procesos)

    print("\n--- Round Robin (Q=1) ---")
    round_robin_n(procesos, 1)

    print("\n--- Round Robin (Q=4) ---")
    round_robin_n(procesos, 4)

    print("\n--- Shortest Process Next ---")
    shortest_process_next(procesos)

    print("\n--- Selfish Round Robin (A=2, B=1) ---")
    selfish_round_robin(procesos, 2, 1)
