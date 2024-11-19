import random
from typing import List, Dict

class Proceso:
    def __init__(self, nombre: str, duracion: int, start_time: int) -> None:
        self.datos = [
            start_time,   # tiempo_llegada
            duracion,     # t (tiempo de ejecución)
            duracion,     # tiempo_restante
            0,            # inicio
            0,            # fin
            0,            # T (tiempo total)
            0,            # E (tiempo de espera)
            0             # P (proporción de penalización)
        ]
        self.nombre = nombre

def tiempoTotal(carga):
    return sum(proceso[1] for proceso in carga.values())

def FCFS(carga: Dict):
    resultados = {"T": 0, "E": 0, "P": 0}  # Diccionario para almacenar resultados promedio.
    cola = []  # Cola de procesos listos para ejecutar.
    grafica = ""  # Representación gráfica de la ejecución.
    t_total = tiempoTotal(carga)  # Tiempo total basado en los tiempos de ejecución.

    for key, value in list(carga.items()):
        if value[0] == 0:  # Si el proceso llega al tiempo 0, se agrega a la cola.
            cola.append(key)
            carga[key][2] = carga[key][1]  # Actualiza el tiempo restante.

    tik = 0  # Reloj del sistema.
    while tik < t_total:
        if cola:  # Si hay procesos en cola.
            carga[cola[0]][2] -= 1  # Reduce el tiempo restante del proceso en ejecución.
            grafica += cola[0]  # Agrega el proceso actual al gráfico.

            if carga[cola[0]][2] == 0:  # Si el proceso termina.
                carga[cola[0]][4] = tik + 1  # Tiempo de finalización.
                carga[cola[0]][5] = carga[cola[0]][4] - carga[cola[0]][0]  # Tiempo total (T).
                carga[cola[0]][6] = carga[cola[0]][5] - carga[cola[0]][1]  # Tiempo de espera (E).
                carga[cola[0]][7] = carga[cola[0]][5] / carga[cola[0]][1]  # Proporción de penalización (P).
                cola.pop(0)  # Elimina el proceso de la cola.
        else:
            t_total += 1  # Aumenta el tiempo total si no hay procesos listos.

        # Agregar procesos que lleguen al instante actual.
        for key, value in list(carga.items()):
            if value[0] == (tik + 1):
                cola.append(key)
                carga[key][2] = carga[key][1]

        tik += 1  # Incrementa el reloj.

    # Calcula promedios para T, E y P.
    for tiempos in carga.values():
        resultados["T"] += tiempos[5]
        resultados["E"] += tiempos[6]
        resultados["P"] += tiempos[7]

    resultados['T'] /= len(carga)
    resultados['E'] /= len(carga)
    resultados['P'] /= len(carga)

    print(f"FCFS: T = {resultados['T']:0.2f}, E = {resultados['E']:0.2f}, P = {resultados['P']:0.2f}")
    print(grafica)  # Imprime la representación gráfica.

def RR(carga: Dict, quantum: int = 1): #Implementación similar a FCFS pero con manejo de quantum.
    resultados = {"T": 0, "E": 0, "P": 0}
    cola = []
    grafica = ""
    t_total = tiempoTotal(carga)
    conta_tik = 0
    
    for key, value in list(carga.items()):
        if value[0] == 0:
            cola.append(key)
            carga[key][2] = carga[key][1]
    
    tik = 0
    while tik < t_total:
        if cola:
            carga[cola[0]][2] -= 1
            grafica += cola[0]
            
            if carga[cola[0]][2] == 0:
                carga[cola[0]][4] = tik + 1
                carga[cola[0]][5] = carga[cola[0]][4] - carga[cola[0]][0]
                carga[cola[0]][6] = carga[cola[0]][5] - carga[cola[0]][1]
                carga[cola[0]][7] = carga[cola[0]][5] / carga[cola[0]][1]
                cola.pop(0)
                conta_tik = 0
            else:
                conta_tik += 1
        else:
            t_total += 1
        
        for key, value in list(carga.items()):
            if value[0] == (tik + 1):
                cola.append(key)
                carga[key][2] = carga[key][1]
        
        if conta_tik == quantum:
            cola.append(cola.pop(0))
            conta_tik = 0
        
        tik += 1
    
    for tiempos in carga.values():
        resultados["T"] += tiempos[5]
        resultados["E"] += tiempos[6]
        resultados["P"] += tiempos[7]
    
    resultados['T'] /= len(carga)
    resultados['E'] /= len(carga)
    resultados['P'] /= len(carga)
    
    print(f"RR: T = {resultados['T']:0.2f}, E = {resultados['E']:0.2f}, P = {resultados['P']:0.2f}")
    print(grafica)

def SPN(carga: Dict): # Similar a FCFS, pero organiza la cola según el tiempo restante.
    resultados = {"T": 0, "E": 0, "P": 0}
    cola = []
    grafica = ""
    t_total = tiempoTotal(carga) + max(proceso[0] for proceso in carga.values())  # Considera los tiempos de llegada

    tik = 0
    while tik < t_total:
        # Agregar procesos a la cola si han llegado
        for key, value in list(carga.items()):
            if value[0] == tik:
                cola.append(key)
                carga[key][2] = value[1]  # Actualizar tiempo restante

        # Ordenar la cola por tiempo restante (Shortest Process Next)
        if cola:
            cola.sort(key=lambda x: carga[x][2])

            # Ejecutar el primer proceso en la cola
            carga[cola[0]][2] -= 1  # Disminuir tiempo restante
            grafica += cola[0]

            # Verificar si el proceso ha terminado
            if carga[cola[0]][2] == 0:
                carga[cola[0]][4] = tik + 1  # Tiempo de fin
                carga[cola[0]][5] = carga[cola[0]][4] - carga[cola[0]][0]  # Tiempo total
                carga[cola[0]][6] = carga[cola[0]][5] - carga[cola[0]][1]  # Tiempo de espera
                carga[cola[0]][7] = carga[cola[0]][5] / carga[cola[0]][1]  # Proporción de penalización
                cola.pop(0)
        else:
            pass

        tik += 1

    # Calcular resultados promedio
    for tiempos in carga.values():
        resultados["T"] += tiempos[5]
        resultados["E"] += tiempos[6]
        resultados["P"] += tiempos[7]

    resultados['T'] /= len(carga)
    resultados['E'] /= len(carga)
    resultados['P'] /= len(carga)

    print(f"SPN: T = {resultados['T']:0.2f}, E = {resultados['E']:0.2f}, P = {resultados['P']:0.2f}")
    print(grafica)


def generar_procesos_aleatorios(num_procesos: int = 5) -> Dict[str, List[int]]:
    """Genera una carga de procesos aleatorios"""
    procesos = {}
    for i in range(num_procesos):
        nombre = chr(65 + i)  # Nombres A, B, C, etc.
        duracion = random.randint(1, 10)  # Duración aleatoria entre 1 y 10
        start_time = random.randint(0, 15)  # Tiempo de llegada aleatorio entre 0 y 15
        procesos[nombre] = Proceso(nombre, duracion, start_time).datos
    return procesos

def main():
    for ejecucion in range(1, 6):  # 5 ejecuciones
        procesos = generar_procesos_aleatorios()
        print(f"\n--- Ejecución {ejecucion} ---\n")
        print("Datos generados: ")
        for nombre, datos in procesos.items():
            print(f"{nombre}: Llegada={datos[0]}, Duración={datos[1]}")
        # Calcular e imprimir el tiempo total
        t_total = tiempoTotal(procesos)
        print(f"\nTiempo total: {t_total}")


        print("\n")
        FCFS(procesos.copy())
        
        print("\n")
        RR(procesos.copy())
        
        print("\n")
        SPN(procesos.copy())

if __name__ == "__main__":
    main()
