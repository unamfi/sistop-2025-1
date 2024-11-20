import random
from tabulate import tabulate
from colorama import Fore, Style

# Colores asignados para cada proceso
COLORES_PROCESOS = {
    'A': Fore.RED,
    'B': Fore.GREEN,
    'C': Fore.BLUE,
    'D': Fore.YELLOW,
    'E': Fore.MAGENTA
}

# Colores asignados para cada algoritmo
COLORES_ALGORITMOS = {
    'FCFS': Fore.CYAN,
    'RR1': Fore.LIGHTGREEN_EX,
    'RR4': Fore.LIGHTMAGENTA_EX,
    'SPN': Fore.LIGHTBLUE_EX,
    'SRR': Fore.LIGHTCYAN_EX,
    'FB': Fore.LIGHTWHITE_EX
}

def colorear_tiempo(tiempo): 
    #colores para los procesos
    return ''.join(COLORES_PROCESOS.get(char, '') + char + Style.RESET_ALL for char in tiempo)

def generar_procesos(numero_procesos=5, max_llegada=15, max_duracion=10):
    procesos = []
    for i in range(numero_procesos):
        llegada = random.randint(0, max_llegada)
        duracion = random.randint(1, max_duracion)
        procesos.append((chr(65 + i), llegada, duracion))
    return procesos

def fcfs(procesos):
    tiempo = []
    reloj = 0
    total_turnaround = 0
    total_espera = 0
    total_respuesta = 0

    for proceso in procesos:
        nombre, llegada, duracion = proceso
        if reloj < llegada:
            reloj = llegada  # Avanzar al momento en que el proceso llega
        tiempo_respuesta = reloj - llegada
        tiempo.extend([nombre] * duracion)  # Añadir al timeline el proceso ejecutado
        reloj += duracion
        turnaround = reloj - llegada
        espera = turnaround - duracion

        # Acumular métricas
        total_turnaround += turnaround
        total_espera += espera
        total_respuesta += tiempo_respuesta

    numero_procesos = len(procesos)
    return tiempo, total_turnaround / numero_procesos, total_espera / numero_procesos, total_respuesta / numero_procesos

def round_robin(procesos, quantum):
    cola = procesos[:]
    reloj = 0
    tiempo = []
    total_turnaround = 0
    total_espera = 0
    total_respuesta = 0
    respuesta_registrada = {p[0]: False for p in cola}  # Marcar si un proceso ha comenzado

    while cola:
        for i, (nombre, llegada, duracion) in enumerate(cola):
            if reloj < llegada:
                reloj = llegada  # Avanzar al momento en que el proceso llega
            if not respuesta_registrada[nombre]:
                total_respuesta += reloj - llegada
                respuesta_registrada[nombre] = True

            # Ejecución del proceso por quantum
            ejecucion = min(quantum, duracion)
            tiempo.extend([nombre] * ejecucion)
            reloj += ejecucion
            duracion -= ejecucion

            if duracion == 0:
                # Calcular turnaround y espera solo cuando el proceso termina
                turnaround = reloj - llegada
                espera = turnaround - cola[i][2]
                total_turnaround += turnaround
                total_espera += espera

            cola[i] = (nombre, llegada, duracion)

        # Eliminar procesos completados de la cola
        cola = [p for p in cola if p[2] > 0]

    numero_procesos = len(procesos)
    return tiempo, total_turnaround / numero_procesos, total_espera / numero_procesos, total_respuesta / numero_procesos

def spn(procesos):
    lista_listos = []
    tiempo = []
    reloj = 0
    total_turnaround = 0
    total_espera = 0
    total_respuesta = 0
    indice_procesos = 0
    n = len(procesos)

    while indice_procesos < n or lista_listos:
        # Mover procesos listos a la lista de ejecución
        while indice_procesos < n and procesos[indice_procesos][1] <= reloj:
            lista_listos.append(procesos[indice_procesos])
            indice_procesos += 1

        if lista_listos:
            lista_listos.sort(key=lambda x: x[2])  # Seleccionar el proceso más corto
            nombre, llegada, duracion = lista_listos.pop(0)
            if reloj < llegada:
                reloj = llegada  # Avanzar al momento en que el proceso llega

            total_respuesta += reloj - llegada
            tiempo.extend([nombre] * duracion)
            reloj += duracion
            turnaround = reloj - llegada
            espera = turnaround - duracion

            # Acumular métricas
            total_turnaround += turnaround
            total_espera += espera
        else:
            reloj += 1  # Avanzar el reloj si no hay procesos listos

    numero_procesos = len(procesos)
    return tiempo, total_turnaround / numero_procesos, total_espera / numero_procesos, total_respuesta / numero_procesos


def fb(procesos, niveles_maximos=3):
    colas = [[] for _ in range(niveles_maximos)]  # Multinivel de prioridades
    tiempo = []
    reloj = 0
    total_turnaround = 0
    total_espera = 0
    total_respuesta = 0
    respuesta_registrada = {p[0]: False for p in procesos}

    procesos_restantes = procesos[:]
    quantums = [2**i for i in range(niveles_maximos)]  # Quantum por nivel

    while procesos_restantes or any(colas):
        for proceso in procesos_restantes[:]:
            if proceso[1] <= reloj:
                colas[0].append((proceso[0], proceso[1], proceso[2]))
                procesos_restantes.remove(proceso)

        for nivel in range(niveles_maximos):
            if colas[nivel]:
                nombre, llegada, duracion = colas[nivel].pop(0)

                if not respuesta_registrada[nombre]:
                    total_respuesta += reloj - llegada
                    respuesta_registrada[nombre] = True

                ejecucion = min(quantums[nivel], duracion)
                tiempo.extend([nombre] * ejecucion)
                reloj += ejecucion
                duracion -= ejecucion

                if duracion > 0:
                    if nivel + 1 < niveles_maximos:
                        colas[nivel + 1].append((nombre, llegada, duracion))
                    else:
                        colas[nivel].append((nombre, llegada, duracion))
                else:
                    turnaround = reloj - llegada
                    espera = turnaround - proceso[2]
                    total_turnaround += turnaround
                    total_espera += espera
                break
        else:
            reloj += 1  # Avanzar el reloj si no hay procesos listos

    numero_procesos = len(procesos)
    return tiempo, total_turnaround / numero_procesos, total_espera / numero_procesos, total_respuesta / numero_procesos

# Generación de rondas
rondas = 5
for ronda in range(1, rondas + 1):
    procesos = generar_procesos()
    procesos.sort(key=lambda x: x[0])  # Ordenar por nombre del proceso
    tiempo_total = sum(p[2] for p in procesos)

    headers = ["Proceso", "Llegada", "Duración"]
    print(f"\n{Fore.YELLOW}Ronda {ronda}:{Style.RESET_ALL}")
    print(tabulate(procesos, headers=headers, tablefmt="grid"))
    print(f"{Fore.CYAN}Total tiempo: {tiempo_total}{Style.RESET_ALL}")
    print("-" * 50)

    # Ejecutar y mostrar resultados de cada algoritmo
    for algoritmo, funcion in [("FCFS", fcfs), ("RR1", lambda p: round_robin(p, 1)), ("RR4", lambda p: round_robin(p, 4)), ("SPN", spn), ("FB", fb)]:
        tiempo, turnaround, espera, respuesta = funcion(procesos)
        print(f"{COLORES_ALGORITMOS[algoritmo]}{algoritmo}:{Style.RESET_ALL} T={turnaround:.2f}, E={espera:.2f}, P={respuesta:.2f}")
        print(colorear_tiempo(tiempo))
    print("=" * 50)
