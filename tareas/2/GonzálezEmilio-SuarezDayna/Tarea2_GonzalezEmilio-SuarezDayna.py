import random
import csv

# Definir la clase Proceso
class Proceso:
    def __init__(self, pid, tiempo_llegada, duracion):
        self.pid = pid
        self.tiempo_llegada = tiempo_llegada
        self.duracion = duracion
        self.tiempo_restante = duracion
        self.tiempo_inicio = None
        self.tiempo_finalizacion = None
        self.tiempo_espera = 0
        self.tiempo_retorno = 0
        self.nivel_cola = 1

    def __repr__(self):
        return f"{self.pid}: llegada={self.tiempo_llegada}, duración={self.duracion}"

# Función para generar procesos aleatorios
def generar_procesos(numero_procesos):
    procesos = []
    for i in range(numero_procesos):
        pid = chr(65 + i)
        tiempo_llegada = random.randint(0, 10)
        duracion = random.randint(1, 10)
        proceso = Proceso(pid, tiempo_llegada, duracion)
        procesos.append(proceso)
    procesos.sort(key=lambda x: x.tiempo_llegada)
    return procesos

# Planificación FCFS
def fcfs(procesos):
    tiempo = 0
    esquema = ""
    cola_procesos = sorted(procesos, key=lambda x: x.tiempo_llegada)
    for proceso in cola_procesos:
        if tiempo < proceso.tiempo_llegada:
            esquema += "_" * (proceso.tiempo_llegada - tiempo)
            tiempo = proceso.tiempo_llegada
        if proceso.tiempo_inicio is None:
            proceso.tiempo_inicio = tiempo
        esquema += proceso.pid * proceso.duracion
        tiempo += proceso.duracion
        proceso.tiempo_finalizacion = tiempo
        proceso.tiempo_espera = proceso.tiempo_inicio - proceso.tiempo_llegada
        proceso.tiempo_retorno = proceso.tiempo_finalizacion - proceso.tiempo_llegada
    return esquema

# Planificación Round Robin
def round_robin(procesos, quantum):
    tiempo = 0
    esquema = ""
    cola_listos = []
    procesos_llegados = []
    while True:
        # Añadir nuevos procesos que hayan llegado
        for proceso in procesos:
            if proceso.tiempo_llegada <= tiempo and proceso not in procesos_llegados:
                cola_listos.append(proceso)
                procesos_llegados.append(proceso)
        if not cola_listos and not any(p.tiempo_restante > 0 for p in procesos):
            break
        if not cola_listos:
            esquema += "_"
            tiempo += 1
            continue
        proceso_actual = cola_listos.pop(0)
        if proceso_actual.tiempo_inicio is None:
            proceso_actual.tiempo_inicio = tiempo
        tiempo_ejecucion = min(quantum, proceso_actual.tiempo_restante)
        esquema += proceso_actual.pid * tiempo_ejecucion
        tiempo += tiempo_ejecucion
        proceso_actual.tiempo_restante -= tiempo_ejecucion
        if proceso_actual.tiempo_restante > 0:
            # El proceso vuelve al final de la cola
            cola_listos.append(proceso_actual)
        else:
            proceso_actual.tiempo_finalizacion = tiempo
            proceso_actual.tiempo_retorno = proceso_actual.tiempo_finalizacion - proceso_actual.tiempo_llegada
            proceso_actual.tiempo_espera = proceso_actual.tiempo_retorno - proceso_actual.duracion
    return esquema

# Planificación SPN (No expropiativa)
def spn(procesos):
    tiempo = 0
    esquema = ""
    cola_listos = []
    procesos_llegados = []
    procesos_completados = []
    procesos_ordenados = sorted(procesos, key=lambda x: x.tiempo_llegada)

    while len(procesos_completados) < len(procesos):
        # Añadir nuevos procesos que hayan llegado
        for proceso in procesos_ordenados:
            if proceso.tiempo_llegada <= tiempo and proceso not in procesos_llegados:
                cola_listos.append(proceso)
                procesos_llegados.append(proceso)
        if not cola_listos:
            esquema += "_"
            tiempo += 1
            continue
        # Seleccionar proceso con el menor tiempo de ejecución
        proceso_actual = min(cola_listos, key=lambda x: x.duracion)
        cola_listos.remove(proceso_actual)
        if proceso_actual.tiempo_inicio is None:
            proceso_actual.tiempo_inicio = tiempo
        esquema += proceso_actual.pid * proceso_actual.duracion
        tiempo += proceso_actual.duracion
        proceso_actual.tiempo_finalizacion = tiempo
        proceso_actual.tiempo_retorno = proceso_actual.tiempo_finalizacion - proceso_actual.tiempo_llegada
        proceso_actual.tiempo_espera = proceso_actual.tiempo_inicio - proceso_actual.tiempo_llegada
        procesos_completados.append(proceso_actual)
    return esquema

# Planificación Retroalimentación Multinivel (FB)
def feedback(procesos):
    tiempo = 0
    esquema = ""
    procesos_llegados = []
    niveles = {1: [], 2: [], 3: []}  # Colas para cada nivel
    quantum_niveles = {1: 1, 2: 2, 3: 4}  # Quantum para cada nivel

    while True:
        # Añadir nuevos procesos que hayan llegado
        for proceso in procesos:
            if proceso.tiempo_llegada <= tiempo and proceso not in procesos_llegados:
                proceso.nivel_cola = 1
                niveles[1].append(proceso)
                procesos_llegados.append(proceso)
        # Verificar si todas las colas están vacías
        if not any(niveles[nivel] for nivel in niveles) and not any(p.tiempo_restante > 0 for p in procesos):
            break
        # Seleccionar el nivel de mayor prioridad que tenga procesos
        for nivel in sorted(niveles.keys()):
            if niveles[nivel]:
                proceso_actual = niveles[nivel].pop(0)
                break
        else:
            esquema += "_"
            tiempo += 1
            continue
        # Establecer tiempo de inicio si es la primera vez
        if proceso_actual.tiempo_inicio is None:
            proceso_actual.tiempo_inicio = tiempo
        quantum_actual = quantum_niveles[proceso_actual.nivel_cola]
        tiempo_ejecucion = min(quantum_actual, proceso_actual.tiempo_restante)
        esquema += proceso_actual.pid * tiempo_ejecucion
        tiempo += tiempo_ejecucion
        proceso_actual.tiempo_restante -= tiempo_ejecucion
        if proceso_actual.tiempo_restante > 0:
            # Degradar al siguiente nivel si no es el último nivel
            if proceso_actual.nivel_cola < 3:
                proceso_actual.nivel_cola += 1
            niveles[proceso_actual.nivel_cola].append(proceso_actual)
        else:
            proceso_actual.tiempo_finalizacion = tiempo
            proceso_actual.tiempo_retorno = proceso_actual.tiempo_finalizacion - proceso_actual.tiempo_llegada
            proceso_actual.tiempo_espera = proceso_actual.tiempo_retorno - proceso_actual.duracion
    return esquema

# Planificación Ronda Egoísta (SRR)
def srr(procesos, quantum):
    tiempo = 0
    esquema = ""
    procesos_llegados = []
    cola_listos = []

    while True:
        # Añadir nuevos procesos que hayan llegado
        for proceso in procesos:
            if proceso.tiempo_llegada <= tiempo and proceso not in procesos_llegados:
                procesos_llegados.append(proceso)
                cola_listos.append(proceso)
        if not cola_listos and not any(p.tiempo_restante > 0 for p in procesos):
            break
        if not cola_listos:
            esquema += "_"
            tiempo += 1
            continue
        # Ordenar la cola listos por tiempo restante (procesos más cortos primero)
        cola_listos.sort(key=lambda x: x.tiempo_restante)
        proceso_actual = cola_listos.pop(0)
        if proceso_actual.tiempo_inicio is None:
            proceso_actual.tiempo_inicio = tiempo
        tiempo_ejecucion = min(quantum, proceso_actual.tiempo_restante)
        esquema += proceso_actual.pid * tiempo_ejecucion
        tiempo += tiempo_ejecucion
        proceso_actual.tiempo_restante -= tiempo_ejecucion
        if proceso_actual.tiempo_restante > 0:
            # Volver a insertar en la cola listos
            cola_listos.append(proceso_actual)
        else:
            proceso_actual.tiempo_finalizacion = tiempo
            proceso_actual.tiempo_retorno = proceso_actual.tiempo_finalizacion - proceso_actual.tiempo_llegada
            proceso_actual.tiempo_espera = proceso_actual.tiempo_retorno - proceso_actual.duracion
    return esquema



# Función para imprimir la tabla de procesos
def print_process_table(procesos):
    print("  Procesos:")
    print("  +-------+----------------+-----------+")
    print("  | PID   | Tiempo Llegada | Duración  |")
    print("  +-------+----------------+-----------+")
    for p in procesos:
        print(f"  | {p.pid:<5} | {p.tiempo_llegada:^14} | {p.duracion:^9} |")
    print("  +-------+----------------+-----------+")

# Función para imprimir la tabla de métricas
def print_metrics_table(metrics):
    print("  Métricas de rendimiento:")
    print("  +-----------+------------+------------+------------+")
    print("  | Algoritmo | T_promedio | E_promedio | P_promedio |")
    print("  +-----------+------------+------------+------------+")
    for alg, (T, E, P) in metrics.items():
        print(f"  | {alg:<9} | {T:^10.1f} | {E:^10.1f} | {P:^10.2f} |")
    print("  +-----------+------------+------------+------------+")

# Función para calcular las métricas promedio
def calcular_metricas(procesos):
    total_retorno = sum(p.tiempo_retorno for p in procesos)
    total_espera = sum(p.tiempo_espera for p in procesos)
    total_penalizacion = sum(p.tiempo_retorno / p.duracion for p in procesos)
    n = len(procesos)
    promedio_retorno = total_retorno / n
    promedio_espera = total_espera / n
    promedio_penalizacion = total_penalizacion / n
    return promedio_retorno, promedio_espera, promedio_penalizacion

# Función principal para ejecutar las simulaciones
def main():
    num_rondas = 5
    num_procesos = 5

    # Abrir archivo CSV para escribir los resultados
    with open('resultados_planificacion.csv', 'w', newline='') as csvfile:
        fieldnames = ['Ronda', 'Algoritmo', 'Procesos', 'Esquema', 'T_promedio', 'E_promedio', 'P_promedio']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for ronda in range(1, num_rondas + 1):
            print(f"\n{'='*60}")
            print(f" Ronda {ronda}")
            print(f"{'='*60}")
            # Generar procesos aleatorios
            procesos = generar_procesos(num_procesos)
            # Mostrar información de los procesos
            print_process_table(procesos)
            # Convertir la información de los procesos para el CSV
            detalles_procesos = ", ".join([f"{p.pid}({p.tiempo_llegada},{p.duracion})" for p in procesos])
            # Crear copias de los procesos para cada algoritmo
            procesos_algoritmos = {
                'FCFS': [Proceso(p.pid, p.tiempo_llegada, p.duracion) for p in procesos],
                'RR1': [Proceso(p.pid, p.tiempo_llegada, p.duracion) for p in procesos],
                'RR4': [Proceso(p.pid, p.tiempo_llegada, p.duracion) for p in procesos],
                'SPN': [Proceso(p.pid, p.tiempo_llegada, p.duracion) for p in procesos],
                'FB': [Proceso(p.pid, p.tiempo_llegada, p.duracion) for p in procesos],
                'SRR': [Proceso(p.pid, p.tiempo_llegada, p.duracion) for p in procesos],
            }
            # Diccionarios para almacenar métricas y esquemas
            metrics = {}
            esquemas = {}
            # Ejecutar cada algoritmo
            for alg in ['FCFS', 'RR1', 'RR4', 'SPN', 'FB', 'SRR']:
                if alg == 'FCFS':
                    esquema = fcfs(procesos_algoritmos[alg])
                elif alg == 'RR1':
                    esquema = round_robin(procesos_algoritmos[alg], quantum=1)
                elif alg == 'RR4':
                    esquema = round_robin(procesos_algoritmos[alg], quantum=4)
                elif alg == 'SPN':
                    esquema = spn(procesos_algoritmos[alg])
                elif alg == 'FB':
                    esquema = feedback(procesos_algoritmos[alg])
                elif alg == 'SRR':
                    esquema = srr(procesos_algoritmos[alg], quantum=1)
                promedio_retorno, promedio_espera, promedio_penalizacion = calcular_metricas(procesos_algoritmos[alg])
                metrics[alg] = (promedio_retorno, promedio_espera, promedio_penalizacion)
                esquemas[alg] = esquema
                # Escribir en el CSV
                writer.writerow({
                    'Ronda': ronda,
                    'Algoritmo': alg,
                    'Procesos': detalles_procesos,
                    'Esquema': esquema,
                    'T_promedio': f"{promedio_retorno:.2f}",
                    'E_promedio': f"{promedio_espera:.2f}",
                    'P_promedio': f"{promedio_penalizacion:.2f}"
                })
            # Agregar una fila vacía y repetir los encabezados
            writer.writerow({})
            writer.writerow(dict(zip(fieldnames, fieldnames)))
            # Imprimir métricas en formato de tabla
            print_metrics_table(metrics)
            # Mostrar esquemas de ejecución
            print("\n  Esquema de ejecución:")
            for alg in ['FCFS', 'RR1', 'RR4', 'SPN', 'FB', 'SRR']:
                print(f"  {alg:<5}: {esquemas[alg]}")
            print()

    print("Los resultados se han guardado en 'resultados_planificacion.csv'.")

if __name__ == "__main__":
    main()
