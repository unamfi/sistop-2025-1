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

def reset_procesos():
    datos = [
        ['A', 3, 0],
        ['B', 5, 1],
        ['C', 2, 3],
        ['D', 5, 9],
        ['E', 5, 12]
    ]
    return {proc[0]: Proceso(proc[0], proc[1], proc[2]).datos for proc in datos}

def tiempoTotal(carga):
    return sum(proceso[1] for proceso in carga.values())

def FCFS(carga: Dict):
    resultados = {"T": 0, "E": 0, "P": 0}
    cola = []
    grafica = ""
    t_total = tiempoTotal(carga)
    
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
        else:
            t_total += 1
        
        for key, value in list(carga.items()):
            if value[0] == (tik + 1):
                cola.append(key)
                carga[key][2] = carga[key][1]
        
        tik += 1
    
    for tiempos in carga.values():
        resultados["T"] += tiempos[5]
        resultados["E"] += tiempos[6]
        resultados["P"] += tiempos[7]
    
    resultados['T'] /= len(carga)
    resultados['E'] /= len(carga)
    resultados['P'] /= len(carga)
    
    print(f"FCFS: T = {resultados['T']:0.2f}, E = {resultados['E']:0.2f}, P = {resultados['P']:0.2f}")
    print(grafica)

def RR(carga: Dict, quantum: int = 1):
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

def SPN(carga: Dict):
    resultados = {"T": 0, "E": 0, "P": 0}
    cola = []
    grafica = ""
    t_total = tiempoTotal(carga)
    
    for key, value in list(carga.items()):
        if value[0] == 0:
            cola.append(key)
            carga[key][2] = carga[key][1]
    
    if cola:
        cola.sort(key=lambda x: carga[x][1])
    
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
                
                for key, value in list(carga.items()):
                    if value[0] == (tik + 1):
                        cola.append(key)
                        carga[key][2] = carga[key][1]
                
                cola.sort(key=lambda x: carga[x][1])
            else:
                for key, value in list(carga.items()):
                    if value[0] == (tik + 1):
                        cola.append(key)
                        carga[key][2] = carga[key][1]
                
                procesos_esperando = cola[1:]
                procesos_esperando.sort(key=lambda x: carga[x][1])
                cola[1:] = procesos_esperando
        else:
            t_total += 1
        
        tik += 1
    
    for tiempos in carga.values():
        resultados["T"] += tiempos[5]
        resultados["E"] += tiempos[6]
        resultados["P"] += tiempos[7]
    
    resultados['T'] /= len(carga)
    resultados['E'] /= len(carga)
    resultados['P'] /= len(carga)
    
    print(f"SPN: T = {resultados['T']:0.2f}, E = {resultados['E']:0.2f}, P = {resultados['P']:0.2f}")
    print(grafica)

def main():
    procesos = reset_procesos()
    print("Realizando FCFS: ")
    FCFS(procesos.copy())
    
    print("\nRealizando RR: ")
    RR(procesos.copy())
    
    print("\nRealizando SPN: ")
    SPN(procesos.copy())

if __name__ == "__main__":
    main()