import random
import pandas as pd
from tabulate import tabulate

def generaProceso(no_procesos=5, max_arrival=10, max_duration=10):
    """
    Genera un conjunto de procesos con tiempos de llegada y duración aleatorios.
    
    Parámetros:
    - no_procesos: Número de procesos a generar
    - max_arrival: Tiempo máximo de llegada
    - max_duration: Duración máxima del proceso
    
    Retorna una lista de procesos ordenados por tiempo de llegada
    """
    procesos = []
    for i in range(no_procesos):
        # Generar tiempo de llegada y duración aleatorios
        arrival_time = random.randint(0, max_arrival)
        duration = random.randint(1, max_duration)
        # Crear proceso con nombre (letra), tiempo de llegada y duración
        procesos.append((chr(65 + i), arrival_time, duration))
    procesos.sort(key=lambda x: x[1])  # Ordenar por tiempo de llegada
    return procesos

def fcfs(procesos):
    """
    Algoritmo de Planificación First-Come, First-Served (FCFS)
    Los procesos se ejecutan en orden de llegada
    
    Parámetros:
    - procesos: Lista de procesos a ejecutar
    
    Retorna el cronograma de ejecución y tiempos de finalización
    """
    if not procesos:
        return [], {}
    
    schedule = []
    current_time = 0
    compl_times = {}
    
    for process in procesos:
        # Agregar tiempo ocioso si hay espacio entre procesos
        while current_time < process[1]:
            schedule.append("_")
            current_time += 1
            
        # Ejecutar el proceso completamente
        for _ in range(process[2]):
            schedule.append(process[0])
            current_time += 1
        compl_times[process[0]] = current_time
    
    return schedule, compl_times

def rr(procesos, quantum):
    """
    Algoritmo de Planificación Round Robin (RR)
    Los procesos se ejecutan en turnos de tiempo fijo (quantum)
    
    Parámetros:
    - procesos: Lista de procesos a ejecutar
    - quantum: Tiempo de ejecución por turno
    
    Retorna el cronograma de ejecución y tiempos de finalización
    """
    if not procesos:
        return [], {}
    
    schedule = []
    time = 0
    compl_times = {}
    remaining_times = {p[0]: p[2] for p in procesos}  # Tiempo restante de cada proceso
    ready_queue = []  # Cola de procesos listos
    process_arrived = {p[0]: False for p in procesos}  # Rastrear procesos que han llegado
    
    while len(compl_times) < len(procesos):
        # Verificar nuevos procesos que llegan
        for process in procesos:
            if process[1] <= time and not process_arrived[process[0]]:
                ready_queue.append(process[0])
                process_arrived[process[0]] = True
        
        if ready_queue:
            current = ready_queue.pop(0)
            # Ejecutar por quantum o tiempo restante
            execution_time = min(quantum, remaining_times[current])
            for _ in range(execution_time):
                schedule.append(current)
                time += 1
                remaining_times[current] -= 1
                
                # Verificar nuevos procesos durante la ejecución
                for process in procesos:
                    if process[1] <= time and not process_arrived[process[0]]:
                        ready_queue.append(process[0])
                        process_arrived[process[0]] = True
            
            if remaining_times[current] > 0:
                ready_queue.append(current)
            else:
                compl_times[current] = time
        else:
            schedule.append("_")
            time += 1
    
    return schedule, compl_times

def spn(procesos):
    """
    Algoritmo de Planificación Shortest Process Next (SPN)
    Selecciona y ejecuta el proceso más corto disponible
    
    Parámetros:
    - procesos: Lista de procesos a ejecutar
    
    Retorna el cronograma de ejecución y tiempos de finalización
    """
    if not procesos:
        return [], {}
    
    schedule = []
    time = 0
    compl_times = {}
    ready_queue = []
    process_arrived = {p[0]: False for p in procesos}
    
    while len(compl_times) < len(procesos):
        # Verificar nuevos procesos que llegan
        for process in procesos:
            if process[1] <= time and not process_arrived[process[0]]:
                ready_queue.append(process)
                process_arrived[process[0]] = True
        
        if ready_queue:
            # Seleccionar el proceso más corto
            next_process = min(ready_queue, key=lambda x: x[2])
            ready_queue.remove(next_process)
            
            # Ejecutar el proceso completo
            for _ in range(next_process[2]):
                schedule.append(next_process[0])
                time += 1
                # Verificar nuevos procesos durante la ejecución
                for process in procesos:
                    if process[1] <= time and not process_arrived[process[0]]:
                        ready_queue.append(process)
                        process_arrived[process[0]] = True
            
            compl_times[next_process[0]] = time
        else:
            schedule.append("_")
            time += 1
    
    return schedule, compl_times

def fb(procesos, num_queues=4):
    """
    Algoritmo de Planificación Feedback (FB)
    Usa múltiples colas con diferentes prioridades
    
    Parámetros:
    - procesos: Lista de procesos a ejecutar
    - num_queues: Número de colas de prioridad
    
    Retorna el cronograma de ejecución y tiempos de finalización
    """
    if not procesos:
        return [], {}
    
    schedule = []
    time = 0
    compl_times = {}
    queues = [[] for _ in range(num_queues)]  # Múltiples colas con diferentes prioridades
    process_queue_level = {p[0]: 0 for p in procesos}  # Rastrear nivel de cola de cada proceso
    remaining_times = {p[0]: p[2] for p in procesos}
    process_arrived = {p[0]: False for p in procesos}
    
    while len(compl_times) < len(procesos):
        # Verificar nuevos procesos que llegan
        for process in procesos:
            if process[1] <= time and not process_arrived[process[0]]:
                queues[0].append(process[0])  # Nuevos procesos comienzan en cola de mayor prioridad
                process_arrived[process[0]] = True
        
        # Encontrar la cola no vacía de mayor prioridad
        current_process = None
        current_queue = -1
        for i, queue in enumerate(queues):
            if queue:
                current_process = queue.pop(0)
                current_queue = i
                break
        
        if current_process:
            # Ejecutar proceso por 2^nivel_de_cola unidades de tiempo
            quantum = 2 ** current_queue
            execution_time = min(quantum, remaining_times[current_process])
            
            for _ in range(execution_time):
                schedule.append(current_process)
                time += 1
                remaining_times[current_process] -= 1
                
                # Verificar nuevos procesos durante la ejecución
                for process in procesos:
                    if process[1] <= time and not process_arrived[process[0]]:
                        queues[0].append(process[0])
                        process_arrived[process[0]] = True
            
            if remaining_times[current_process] > 0:
                # Mover a cola de menor prioridad si no ha terminado
                next_queue = min(current_queue + 1, num_queues - 1)
                queues[next_queue].append(current_process)
                process_queue_level[current_process] = next_queue
            else:
                compl_times[current_process] = time
        else:
            schedule.append("_")
            time += 1
    
    return schedule, compl_times

def calculate_metrics(procesos, compl_times):
    """
    Calcula métricas de rendimiento de los algoritmos de planificación
    
    Métricas:
    - T: Tiempo de retorno promedio
    - E: Tiempo de espera promedio
    - P: Penalización promedio
    """
    if not procesos or not compl_times:
        return {"T": 0, "E": 0, "P": 0}
    
    turnarounds = []
    waiting_times = []
    penalties = []
    
    for process in procesos:
        completion = compl_times[process[0]]
        turnaround = completion - process[1]  # Tiempo de retorno
        waiting = turnaround - process[2]  # Tiempo de espera
        
        turnarounds.append(turnaround)
        waiting_times.append(waiting)
        penalties.append(turnaround / process[2])  # Penalización
    
    return {
        "T": sum(turnarounds) / len(turnarounds),  # Tiempo de retorno promedio
        "E": sum(waiting_times) / len(waiting_times),  # Tiempo de espera promedio
        "P": sum(penalties) / len(penalties),  # Penalización promedio
    }

def create_results_table(round_num, procesos, results):
    """
    Crea tablas formateadas con los resultados de la simulación
    
    Parámetros:
    - round_num: Número de ronda de simulación
    - procesos: Lista de procesos generados
    - results: Resultados de los algoritmos de planificación
    
    Retorna tablas con información de procesos y resultados de algoritmos
    """
    # Crear DataFrame con la información de los procesos
    process_info = pd.DataFrame([
        {
            'Proceso': p[0],
            'Llegada': p[1],
            'Duración': p[2]
        } for p in procesos
    ])
    
    # Crear DataFrame con los resultados de los algoritmos
    metrics_data = []
    for algo_name, (schedule, metrics) in results.items():
        metrics_data.append({
            'Algoritmo': algo_name,
            'T (Tiempo promedio)': f"{metrics['T']:.1f}",
            'E (Tiempo espera)': f"{metrics['E']:.1f}",
            'P (Penalización)': f"{metrics['P']:.2f}",
            'Cronograma': ''.join(schedule)
        })
    
    results_df = pd.DataFrame(metrics_data)
    
    return process_info, results_df

def run():
    """
    Función principal que ejecuta la simulación de algoritmos de planificación
    
    Ejecuta 5 rondas de simulación, generando procesos aleatorios y 
    aplicando diferentes algoritmos de planificación
    """
    for round_num in range(1, 6):  # 5 rondas
        print(f"\n{'='*20} Ronda {round_num} {'='*20}")
        procesos = generaProceso(no_procesos=5, max_arrival=12, max_duration=7)
        
        # Ejecutar todos los algoritmos y calcular métricas
        fcfs_schedule, fcfs_completion = fcfs(procesos)
        rr1_schedule, rr1_completion = rr(procesos, 1)
        rr4_schedule, rr4_completion = rr(procesos, 4)
        spn_schedule, spn_completion = spn(procesos)
        fb_schedule, fb_completion = fb(procesos)

        results = {
            'FCFS': (fcfs_schedule, calculate_metrics(procesos, fcfs_completion)),
            'RR1': (rr1_schedule, calculate_metrics(procesos, rr1_completion)),
            'RR4': (rr4_schedule, calculate_metrics(procesos, rr4_completion)),
            'SPN': (spn_schedule, calculate_metrics(procesos, spn_completion)),
            'FB': (fb_schedule, calculate_metrics(procesos, fb_completion))
        }
        
        # Crear tablas de resultados
        process_info, results_df = create_results_table(round_num, procesos, results)
        
        # Mostrar información de procesos
        print("\nProcesos generados:")
        print(tabulate(process_info, headers='keys', tablefmt='grid', showindex=False))
        
        # Mostrar métricas y cronogramas
        print("\nResultados de los algoritmos:")
        pd.set_option('display.max_colwidth', None)  # Para mostrar cronogramas completos
        print(tabulate(results_df, headers='keys', tablefmt='grid', showindex=False))
        
        # Calcular y mostrar estadísticas comparativas
        metrics_only = results_df[['T (Tiempo promedio)', 'E (Tiempo espera)', 'P (Penalización)']]
        metrics_only = metrics_only.apply(pd.to_numeric)  # Convertir a números para calcular promedio
        
        comparative_stats = pd.DataFrame({
            'T promedio': [metrics_only['T (Tiempo promedio)'].mean()],
            'E promedio': [metrics_only['E (Tiempo espera)'].mean()],
            'P promedio': [metrics_only['P (Penalización)'].mean()]
        })
        
        print("\nEstadísticas comparativas:")
        print(tabulate(comparative_stats, headers='keys', tablefmt='grid', showindex=False))

if __name__ == "__main__":
    # Configurar pandas para mejor visualización
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    # Ejecutar simulaciones
    run()