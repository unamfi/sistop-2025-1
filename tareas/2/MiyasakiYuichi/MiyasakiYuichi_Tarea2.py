"""
 Miyasaki Sato Yuichi Vicente           Sistop 2025-1
 Tarea #02               Fecha de entrega: 19/11/2024
"""
import random

class Proceso:
    def __init__(self, nombre, tiempo_llegada, tiempo_ejecucion):
        # Inicializa los atributos del proceso
        self.nombre = nombre
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_ejecucion = tiempo_ejecucion
        self.tiempo_restante = tiempo_ejecucion
        self.inicio = None
        self.fin = None
        self.tiempo_turnaround = 0
        self.tiempo_espera = 0
        self.proporcion_penalizacion = 0

    def reiniciar(self):
        # Reinicia los atributos relevantes para un nuevo ciclo
        self.tiempo_restante = self.tiempo_ejecucion
        self.inicio = None
        self.fin = None
        self.tiempo_turnaround = 0
        self.tiempo_espera = 0
        self.proporcion_penalizacion = 0

# Algoritmo FCFS 
def FCFS(procesos):
    tiempo_actual = 0
    resultado = []
    
    # Ordenar procesos por tiempo de llegada
    for proceso in sorted(procesos, key=lambda p: p.tiempo_llegada):
        if tiempo_actual < proceso.tiempo_llegada:
            tiempo_actual = proceso.tiempo_llegada
        proceso.inicio = tiempo_actual
        proceso.fin = tiempo_actual + proceso.tiempo_ejecucion
        proceso.tiempo_turnaround = proceso.fin - proceso.tiempo_llegada
        proceso.tiempo_espera = proceso.tiempo_turnaround - proceso.tiempo_ejecucion
        proceso.proporcion_penalizacion = proceso.tiempo_turnaround / proceso.tiempo_ejecucion
        tiempo_actual += proceso.tiempo_ejecucion
        resultado.extend([proceso.nombre] * proceso.tiempo_ejecucion)

    imprimir_resultados("FCFS", procesos, resultado)

# Algoritmo RR 
def RR(procesos, quantum):
    cola = sorted(procesos, key=lambda p: p.tiempo_llegada)
    tiempo_actual = 0
    resultado = []
    procesos_en_cola = []

    # Inicializar el tiempo restante de los procesos
    for p in cola:
        p.tiempo_restante = p.tiempo_ejecucion

    while cola or procesos_en_cola:
        while cola and cola[0].tiempo_llegada <= tiempo_actual:
            procesos_en_cola.append(cola.pop(0))

        if procesos_en_cola:
            proceso = procesos_en_cola.pop(0)
            tiempo_trabajo = min(quantum, proceso.tiempo_restante)
            proceso.tiempo_restante -= tiempo_trabajo
            resultado.extend([proceso.nombre] * tiempo_trabajo)
            tiempo_actual += tiempo_trabajo

            if proceso.tiempo_restante == 0:
                proceso.fin = tiempo_actual
                proceso.tiempo_turnaround = proceso.fin - proceso.tiempo_llegada
                proceso.tiempo_espera = proceso.tiempo_turnaround - proceso.tiempo_ejecucion
                proceso.proporcion_penalizacion = proceso.tiempo_turnaround / proceso.tiempo_ejecucion
            else:
                procesos_en_cola.append(proceso)
        else:
            if cola:
                tiempo_actual = cola[0].tiempo_llegada
            else:
                break

    imprimir_resultados(f"RR{quantum}", procesos, resultado)

# Algoritmo SPN 
def SPN(procesos):
    cola = sorted(procesos, key=lambda p: (p.tiempo_llegada, p.tiempo_ejecucion))
    tiempo_actual = 0
    resultado = []

    while cola:
        proceso = min(
            (p for p in cola if p.tiempo_llegada <= tiempo_actual),
            key=lambda p: p.tiempo_ejecucion,
            default=None,
        )
        if proceso is None:
            tiempo_actual += 1
            continue

        cola.remove(proceso)
        if tiempo_actual < proceso.tiempo_llegada:
            tiempo_actual = proceso.tiempo_llegada
        proceso.inicio = tiempo_actual
        proceso.fin = tiempo_actual + proceso.tiempo_ejecucion
        proceso.tiempo_turnaround = proceso.fin - proceso.tiempo_llegada
        proceso.tiempo_espera = proceso.tiempo_turnaround - proceso.tiempo_ejecucion
        proceso.proporcion_penalizacion = proceso.tiempo_turnaround / proceso.tiempo_ejecucion
        resultado.extend([proceso.nombre] * proceso.tiempo_ejecucion)
        tiempo_actual += proceso.tiempo_ejecucion

    imprimir_resultados("SPN", procesos, resultado)

# Algoritmo FB 
def FB(procesos, niveles_prioridad):
    colas = [[] for _ in range(niveles_prioridad)]
    tiempo_actual = 0
    resultado = []
    quantum_por_nivel = [1, 2, 4]

    # Inicializar el tiempo restante de los procesos
    cola_inicial = sorted(procesos, key=lambda p: p.tiempo_llegada)
    for proceso in cola_inicial:
        proceso.tiempo_restante = proceso.tiempo_ejecucion

    while any(colas) or cola_inicial:
        while cola_inicial and cola_inicial[0].tiempo_llegada <= tiempo_actual:
            colas[0].append(cola_inicial.pop(0))

        for nivel, cola in enumerate(colas):
            if cola:
                proceso = cola.pop(0)
                quantum = quantum_por_nivel[nivel]
                tiempo_trabajo = min(quantum, proceso.tiempo_restante)
                proceso.tiempo_restante -= tiempo_trabajo
                resultado.extend([proceso.nombre] * tiempo_trabajo)
                tiempo_actual += tiempo_trabajo

                if proceso.tiempo_restante == 0:
                    proceso.fin = tiempo_actual
                    proceso.tiempo_turnaround = proceso.fin - proceso.tiempo_llegada
                    proceso.tiempo_espera = proceso.tiempo_turnaround - proceso.tiempo_ejecucion
                    proceso.proporcion_penalizacion = proceso.tiempo_turnaround / proceso.tiempo_ejecucion
                else:
                    if nivel + 1 < niveles_prioridad:
                        colas[nivel + 1].append(proceso)
                    else:
                        cola.append(proceso)
                break
        else:
            if cola_inicial:
                tiempo_actual = cola_inicial[0].tiempo_llegada
            else:
                break

    imprimir_resultados("FB", procesos, resultado)

# Función para aplicar colores a los procesos
def colorear_proceso(nombre):
    return f"{COLORES_ANSI.get(nombre, COLORES_ANSI['RESET'])}{nombre}{COLORES_ANSI['RESET']}"

# Imprimir resultados de cada algoritmo
def imprimir_resultados(algoritmo, procesos, resultado):
    resultado_coloreado = ''.join(colorear_proceso(letra) for letra in resultado)
    print(f"\t{algoritmo}: {resultado_coloreado}")
    
    # Calcular métricas de rendimiento
    t_total = sum(p.tiempo_turnaround for p in procesos) / len(procesos)
    e_total = sum(p.tiempo_espera for p in procesos) / len(procesos)
    p_total = sum(p.proporcion_penalizacion for p in procesos) / len(procesos)
    print(f"\tT={t_total:.1f}, E={e_total:.1f}, P={p_total:.2f}\n")

# Mostrar las cargas de los procesos
def imprimir_cargas(procesos):
    total_tiempo = sum(p.tiempo_ejecucion for p in procesos)
    cargas = ' '.join(f"{colorear_proceso(p.nombre)}: {p.tiempo_llegada}, t={p.tiempo_ejecucion} |" for p in procesos)
    print(f"\t{cargas} (total:{total_tiempo})\n")

# Asignar cargas aleatorias a los procesos
def asignar_cargas_aleatorias(procesos, max_llegada=10, max_ejecucion=10):
    for proceso in procesos:
        proceso.tiempo_llegada = random.randint(0, max_llegada)
        proceso.tiempo_ejecucion = random.randint(1, max_ejecucion)
        proceso.reiniciar()

# Cargas iniciales para la primera ronda
procesos_base = [
    Proceso("A", 0, 3),
    Proceso("B", 1, 5),
    Proceso("C", 3, 2),
    Proceso("D", 9, 5),
    Proceso("E", 12, 5),
]

# Llamar a los diferentes algoritmos de planificación
def llamar_planificador():
    FCFS(list(procesos_base))
    RR(list(procesos_base), 1)
    RR(list(procesos_base), 4)
    SPN(list(procesos_base))
    FB(list(procesos_base), 3)

def main():
    for ronda in range(1, 6):  # Ejecutar 5 rondas
        print("\n\t========="
                f"====================  Ronda {ronda}  ==="
                 "============================")
        
        if ronda > 1:
            asignar_cargas_aleatorias(procesos_base)
            print("\tCargas asignadas a los procesos:")
            imprimir_cargas(procesos_base)
            llamar_planificador()

        else:
            print("\tCargas asignadas a los procesos:")
            imprimir_cargas(procesos_base)
            llamar_planificador()

# Definición de colores ANSI para mostrar los resultados de los procesos
COLORES_ANSI = {
    "A": "\033[91m",  # Rojo
    "B": "\033[92m",  # Verde
    "C": "\033[93m",  # Amarillo
    "D": "\033[94m",  # Azul
    "E": "\033[95m",  # Magenta
    "RESET": "\033[0m"  # Reset
}

if __name__ == "__main__":
    main()

