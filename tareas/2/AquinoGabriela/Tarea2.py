import random

def metodo_spn(lista):
    lista.sort(key=lambda proceso: proceso[2])
    tiempo_retorno, tiempo_espera, penalizacion = calcular_estadisticas(lista)
    promedio_t = sum(tiempo_retorno) / len(tiempo_retorno)
    promedio_e = sum(tiempo_espera) / len(tiempo_espera)
    promedio_p = sum(penalizacion) / len(penalizacion)
    resultado = ''.join([proceso[0] for proceso in lista])
    mostrar_estadisticas(promedio_t, promedio_e, promedio_p, 'SPN')
    print(resultado)
rondas_totales = random.randint(1, 5)
def calcular_estadisticas(lista):
    n = len(lista)
    duracion = [lista[i][2] for i in range(n)]
    tiempo_finalizacion = [0] * n
    tiempo_retorno = [0] * n
    tiempo_espera = [0] * n
    penalizacion = [0] * n
    for i in range(n):
        if i == 0:
            tiempo_finalizacion[i] = lista[i][2]
        else:
            tiempo_finalizacion[i] = max(lista[i][1], tiempo_finalizacion[i - 1]) + lista[i][2]
        tiempo_retorno[i] = tiempo_finalizacion[i] - lista[i][1]
        tiempo_espera[i] = tiempo_retorno[i] - lista[i][2]
        penalizacion[i] = tiempo_retorno[i] / lista[i][2]
    return tiempo_retorno, tiempo_espera, penalizacion
def mostrar_estadisticas(promedio_t, promedio_e, promedio_p, nombre_metodo):
    print(f'{nombre_metodo}: T = {promedio_t:.2f}\tE = {promedio_e:.2f}\tP = {promedio_p:.2f}')
def generar_procesos(cantidad_procesos=5):
    nombres = ['A', 'B', 'C', 'D', 'E']
    tiempo_llegada = 0
    lista_procesos = []
    for indice in range(cantidad_procesos):
        proceso = nombres[indice]
        duracion = random.randint(1, 5)
        lista_procesos.append([proceso, tiempo_llegada, duracion])
        tiempo_llegada += random.randint(0, duracion - 1)
    return lista_procesos
def metodo_fcfs(lista):
    tiempo_retorno, tiempo_espera, penalizacion = calcular_estadisticas(lista)
    promedio_t = sum(tiempo_retorno) / len(tiempo_retorno)
    promedio_e = sum(tiempo_espera) / len(tiempo_espera)
    promedio_p = sum(penalizacion) / len(penalizacion)
    mostrar_estadisticas(promedio_t, promedio_e, promedio_p, 'FCFS')
def metodo_rr1(lista):
    n = len(lista)
    tiempos_restantes = [lista[i][2] for i in range(n)]
    tiempo_retorno, tiempo_espera, penalizacion = calcular_estadisticas(lista)
    resultado = ''
    tiempo_actual = 0
    while any(t > 0 for t in tiempos_restantes):
        for i in range(n):
            if tiempos_restantes[i] >= 1 and tiempo_actual >= lista[i][1]:
                resultado += lista[i][0]
                tiempos_restantes[i] -= 1
                tiempo_actual += 1
    promedio_t = sum(tiempo_retorno) / len(tiempo_retorno)
    promedio_e = sum(tiempo_espera) / len(tiempo_espera)
    promedio_p = sum(penalizacion) / len(penalizacion)
    mostrar_estadisticas(promedio_t, promedio_e, promedio_p, 'RR1')
    print(resultado)
def metodo_rr4(lista):
    n = len(lista)
    tiempos_restantes = [lista[i][2] for i in range(n)]
    tiempo_retorno, tiempo_espera, penalizacion = calcular_estadisticas(lista)
    resultado = ''
    tiempo_actual = 0
    while any(t > 0 for t in tiempos_restantes):
        for i in range(n):
            if tiempos_restantes[i] >= 4 and tiempo_actual >= lista[i][1]:
                resultado += lista[i][0] * 4
                tiempo_actual += 4
                tiempos_restantes[i] -= 4
            elif 0 < tiempos_restantes[i] < 4 and tiempo_actual >= lista[i][1]:
                resultado += lista[i][0] * tiempos_restantes[i]
                tiempo_actual += tiempos_restantes[i]
                tiempos_restantes[i] = 0
    promedio_t = sum(tiempo_retorno) / len(tiempo_retorno)
    promedio_e = sum(tiempo_espera) / len(tiempo_espera)
    promedio_p = sum(penalizacion) / len(penalizacion)
    mostrar_estadisticas(promedio_t, promedio_e, promedio_p, 'RR4')
    print(resultado)
def presentacion():
    print("Facultad de ingenieria\nGabriela Aquino Lozada")

presentacion()
for ronda in range(rondas_totales):
    procesos = generar_procesos()
    print(f'\nRonda Número: {ronda + 1}')
    print(f'Lista de Procesos: {procesos}')
    metodo_fcfs(procesos)
    metodo_rr1(procesos)
    metodo_rr4(procesos)
    metodo_spn(procesos)

