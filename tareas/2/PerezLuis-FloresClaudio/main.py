import random
from typing import List, Dict
from copy import deepcopy

class Proceso:
    def __init__(self, nombre: str, duracion: int, start_time: int, prioridad: int) -> None:
        self.datos = [
            start_time,   # tiempo_llegada
            duracion,     # t (tiempo de ejecución)
            duracion,     # tiempo_restante
            0,            # inicio
            0,            # fin
            0,            # T (tiempo total)
            0,            # E (tiempo de espera)
            0,            # P (proporción de penalización)
            prioridad,            # prioridad (para cola multiple)
            3,            # numero de ejecuciones (para cola multiple)
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

    clock = 0  # Reloj del sistema.
    while clock < t_total:
        if cola:  # Si hay procesos en cola.
            carga[cola[0]][2] -= 1  # Reduce el tiempo restante del proceso en ejecución.
            grafica += cola[0]  # Agrega el proceso actual al gráfico.

            if carga[cola[0]][2] == 0:  # Si el proceso termina.
                carga[cola[0]][4] = clock + 1  # Tiempo de finalización.
                carga[cola[0]][5] = carga[cola[0]][4] - carga[cola[0]][0]  # Tiempo total (T).
                carga[cola[0]][6] = carga[cola[0]][5] - carga[cola[0]][1]  # Tiempo de espera (E).
                carga[cola[0]][7] = carga[cola[0]][5] / carga[cola[0]][1]  # Proporción de penalización (P).
                cola.pop(0)  # Elimina el proceso de la cola.
        else:
            grafica += "□"
            t_total += 1  # Aumenta el tiempo total si no hay procesos listos.

        # Agregar procesos que lleguen al instante actual.
        for key, value in list(carga.items()):
            if value[0] == (clock + 1):
                cola.append(key)
                carga[key][2] = carga[key][1]

        clock += 1  # Incrementa el reloj.

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
    conta_clock = 0
    
    for key, value in list(carga.items()):
        if value[0] == 0:
            cola.append(key)
            carga[key][2] = carga[key][1]
    
    clock = 0
    while clock < t_total:
        if cola:
            carga[cola[0]][2] -= 1
            grafica += cola[0]
            
            if carga[cola[0]][2] == 0:
                carga[cola[0]][4] = clock + 1
                carga[cola[0]][5] = carga[cola[0]][4] - carga[cola[0]][0]
                carga[cola[0]][6] = carga[cola[0]][5] - carga[cola[0]][1]
                carga[cola[0]][7] = carga[cola[0]][5] / carga[cola[0]][1]
                cola.pop(0)
                conta_clock = 0
            else:
                conta_clock += 1
        else:
            t_total += 1
        
        for key, value in list(carga.items()):
            if value[0] == (clock + 1):
                cola.append(key)
                carga[key][2] = carga[key][1]
        
        if conta_clock == quantum:
            cola.append(cola.pop(0))
            conta_clock = 0
        
        clock += 1
    
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

    clock = 0
    while clock < t_total:
        # Agregar procesos a la cola si han llegado
        for key, value in list(carga.items()):
            if value[0] == clock:
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
                carga[cola[0]][4] = clock + 1  # Tiempo de fin
                carga[cola[0]][5] = carga[cola[0]][4] - carga[cola[0]][0]  # Tiempo total
                carga[cola[0]][6] = carga[cola[0]][5] - carga[cola[0]][1]  # Tiempo de espera
                carga[cola[0]][7] = carga[cola[0]][5] / carga[cola[0]][1]  # Proporción de penalización
                cola.pop(0)
        else:
            pass

        clock += 1

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

def FB(carga: Dict):
    resultados = {"T": 0, "E": 0, "P": 0}
    #Colas para prioridad 0 = max prioridad, 4 = min prioridad
    colas = [[],
            [],
            [],
            [],
            []
            ]
    grafica = ""
    t_total = tiempoTotal(carga) + max(proceso[0] for proceso in carga.values())  # Considera los tiempos de llegada
    
    clock = 0
    while clock<t_total:
        #Carga los procesos conforme llegan
        for key, values in list(carga.items()):
            if values[0] == clock:
                colas[values[8]].append(key)

        #Recorre las colas de mayor a menor prioridad
        for q in colas:
            #Si hay elementos en la cola q
            if q:
                carga[q[0]][2]-=1
                carga[q[0]][9]-=1 #Numero de veces que se ha ejecutado con esta prioridad

                grafica+= q[0] #Representacion grafica de la actividad
                if (carga[q[0]][2]==0):
                    carga[q[0]][4] = clock + 1  # Tiempo de fin
                    carga[q[0]][5] = carga[q[0]][4] - carga[q[0]][0]  # Tiempo total
                    carga[q[0]][6] = carga[q[0]][5] - carga[q[0]][1]  # Tiempo de espera
                    carga[q[0]][7] = carga[q[0]][5] / carga[q[0]][1]  # Proporción de penalización
                    q.pop(0) #Termina el proceso
                elif carga[q[0]][9] == 0 and carga[q[0]][8]<4:
                    carga[q[0]][8]+=1 #Reduccion de prioridad
                    carga[q[0]][9]=3  #Reinicio del contador
                    colas[ carga[q[0]][8] ].append(q.pop(0)) #Se mete a la cola inferior

                #Break para asegurar que solo se ejecute un proceso por tick
                break
        #print(clock,"/",t_total)
        clock += 1
    
    # Calcular resultados promedio
    for tiempos in carga.values():
        resultados["T"] += tiempos[5]
        resultados["E"] += tiempos[6]
        resultados["P"] += tiempos[7]

    resultados['T'] /= len(carga)
    resultados['E'] /= len(carga)
    resultados['P'] /= len(carga)

    print(f"FB: T = {resultados['T']:0.2f}, E = {resultados['E']:0.2f}, P = {resultados['P']:0.2f}")
    print(grafica)

def generar_procesos_aleatorios(num_procesos: int = 5) -> Dict[str, List[int]]:
    """Genera una carga de procesos aleatorios"""
    procesos = {}
    for i in range(num_procesos):
        nombre = chr(65 + i)  # Nombres A, B, C, etc.
        duracion = random.randint(1, 10)  # Duración aleatoria entre 1 y 10
        start_time = random.randint(0, 15)  # Tiempo de llegada aleatorio entre 0 y 15
        prioridad = random.randint(0,4)     #Prioridad del proceso para FB 0=max 4=min
        procesos[nombre] = Proceso(nombre, duracion, start_time, prioridad).datos
    return procesos

def main():
    for ejecucion in range(1, 6):  # 5 ejecuciones
        procesos = generar_procesos_aleatorios()
        print(f"\n--- Ejecución {ejecucion} ---\n")
        print("Datos generados: ")
        for nombre, datos in procesos.items():
            print(f"{nombre}: Llegada={datos[0]}, Duración={datos[1]}, Prioridad={datos[8]}")
        # Calcular e imprimir el tiempo total
        t_total = tiempoTotal(procesos)
        print(f"\nTiempo total: {t_total}")


        print("\n")
        FCFS(deepcopy(procesos))
        
        print("\n")
        RR(deepcopy(procesos))
        
        print("\n")
        SPN(deepcopy(procesos))
        
        #procesos = generar_procesos_aleatorios()
        print("\n")
        FB(deepcopy(procesos))

if __name__ == "__main__":
    main()
