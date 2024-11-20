def promedios(procesos):

    T_total = 0
    E_Total = 0
    P_Total = 0

    for proceso in procesos:

        T_total = T_total + proceso.T

        E_Total = E_Total + proceso.E

        P_Total = P_Total + proceso.P
    
    resultados = []

    resultados.append(T_total/len(procesos))
    resultados.append(E_Total/len(procesos))
    resultados.append(P_Total/len(procesos))

    return resultados