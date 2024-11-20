from Promedio import promedios

def fb(procesos):
    cola1 = []
    cola2 = []
    cola3 = []
    A= []

    esquema_visual = " "

    for proceso in procesos:

        A.append(proceso.t_requerido)

    t_final = 0

    while any(proceso.t_requerido > 0 for proceso in procesos):

        for proceso in procesos:

            if proceso.t_llegada <= t_final:

                cola1.append(proceso)

        for _ in range (3):

            for proceso in cola1:

                quantum = 3

                while(quantum != 0 and proceso.t_requerido != 0):

                    quantum -=1
                    proceso.t_requerido -=1
                    t_final +=1
                    esquema_visual = esquema_visual + proceso.name

                    if proceso.t_requerido == 0:
                        proceso.T = t_final - proceso.t_llegada
                        cola1.remove(proceso)

        aux = cola1
        cola1 = cola2
        cola2 = cola3
        cola3 = aux

        t_final +=1

    for i in range(len(procesos)):

        procesos[i].t_requerido = A[i]

        procesos[i].E = procesos[i].T - procesos[i].t_requerido

        procesos[i].P = procesos[i].T / procesos[i].t_requerido

    return promedios(procesos),esquema_visual