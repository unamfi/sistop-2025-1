import random
import numpy as np

maxLlegada = 10
maxT = 10
listaProcesos = []
stringProcesos = ''
matrizFCFS = np.array([['Proceso', 't', 'nt', 'E', 'T', 'P'],
                       ['A', 0, 0, 0, 0, 0], ['B', 0, 0, 0, 0, 0],
                       ['C', 0, 0, 0, 0, 0], ['D', 0, 0, 0, 0, 0],
                       ['E', 0, 0, 0, 0, 0]])
matrizRR1 = np.array([['Proceso', 't', 'nt', 'E', 'T', 'P'],
                      ['A', 0, 0, 0, 0, 0], ['B', 0, 0, 0, 0, 0],
                      ['C', 0, 0, 0, 0, 0], ['D', 0, 0, 0, 0, 0],
                      ['E', 0, 0, 0, 0, 0]])
matrizRR4 = np.array([['Proceso', 't', 'nt', 'E', 'T', 'P'],
                      ['A', 0, 0, 0, 0, 0], ['B', 0, 0, 0, 0, 0],
                      ['C', 0, 0, 0, 0, 0], ['D', 0, 0, 0, 0, 0],
                      ['E', 0, 0, 0, 0, 0]])
matrizSPN = np.array([['Proceso', 't', 'nt', 'E', 'T', 'P'],
                      ['A', 0, 0, 0, 0, 0], ['B', 0, 0, 0, 0, 0],
                      ['C', 0, 0, 0, 0, 0], ['D', 0, 0, 0, 0, 0],
                      ['E', 0, 0, 0, 0, 0]])

maxLlegadaA = 1
maxLlegadaB = random.randint(maxLlegadaA, maxT)
maxLlegadaC = random.randint(maxLlegadaB, maxT)
maxLlegadaD = random.randint(maxLlegadaC, maxT)
maxLlegadaE = random.randint(maxLlegadaD, maxT)

procesos = {
    'A': (maxLlegadaA, random.randint(1, maxT)),
    'B': (maxLlegadaB, random.randint(1, maxT)),
    'C': (maxLlegadaC, random.randint(1, maxT)),
    'D': (maxLlegadaD, random.randint(1, maxT)),
    'E': (maxLlegadaE, random.randint(1, maxT))
}

tiempoMaxTot = procesos['A'][1] + procesos['B'][1] + procesos['C'][
    1] + procesos['D'][1] + procesos['E'][1]

print("Proceso (Llegada, Duración)")
for key, value in procesos.items():
  print(key, value)

for key in procesos.keys():
  cont = procesos[key][1]
  while cont > 0:
    listaProcesos.append(key)
    cont = cont - 1

stringProcesos = ''.join(listaProcesos)

def FCFS(procesos):
  indice = 1
  for key in procesos.keys():
    matrizFCFS[indice][1] = procesos[key][1]
    matrizFCFS[indice][2] = procesos[key][0]
    indice = indice + 1
  contTick = 0

  while contTick < tiempoMaxTot:
    if (int(matrizFCFS[1][1]) > 0 and contTick == int(matrizFCFS[1][2])):
      matrizFCFS[1][1] = int(matrizFCFS[1][1]) - 1
      matrizFCFS[1][2] = int(matrizFCFS[1][2]) + 1
    elif (int(matrizFCFS[2][1]) > 0 and contTick == int(matrizFCFS[2][2])):
      matrizFCFS[2][1] = int(matrizFCFS[2][1]) - 1
      matrizFCFS[2][2] = int(matrizFCFS[2][2]) + 1
    elif (int(matrizFCFS[3][1]) > 0 and contTick == int(matrizFCFS[3][2])):
      matrizFCFS[3][1] = int(matrizFCFS[3][1]) - 1
      matrizFCFS[3][2] = int(matrizFCFS[3][2]) + 1
    elif (int(matrizFCFS[4][1]) > 0 and contTick == int(matrizFCFS[4][2])):
      matrizFCFS[4][1] = int(matrizFCFS[4][1]) - 1
      matrizFCFS[4][2] = int(matrizFCFS[4][2]) + 1
    elif (int(matrizFCFS[5][1]) > 0 and contTick == int(matrizFCFS[5][2])):
      matrizFCFS[5][1] = int(matrizFCFS[5][1]) - 1
      matrizFCFS[5][2] = int(matrizFCFS[5][2]) + 1

    if (int(matrizFCFS[1][2]) == contTick and int(matrizFCFS[1][1]) > 0):
      matrizFCFS[1][2] = int(matrizFCFS[1][2]) + 1
    if (int(matrizFCFS[2][2]) == contTick and int(matrizFCFS[2][1]) > 0):
      matrizFCFS[2][2] = int(matrizFCFS[2][2]) + 1
    if (int(matrizFCFS[3][2]) == contTick and int(matrizFCFS[3][1]) > 0):
      matrizFCFS[3][2] = int(matrizFCFS[3][2]) + 1
    if (int(matrizFCFS[4][2]) == contTick and int(matrizFCFS[4][1]) > 0):
      matrizFCFS[4][2] = int(matrizFCFS[4][2]) + 1
    if (int(matrizFCFS[5][2]) == contTick and int(matrizFCFS[5][1]) > 0):
      matrizFCFS[5][2] = int(matrizFCFS[5][2]) + 1
    contTick = contTick + 1
  i = 1
  for key in procesos.keys():
    matrizFCFS[i][4] = int(matrizFCFS[i][2]) - procesos[key][0]
    i = i + 1
  j = 1
  for key in procesos.keys():
    matrizFCFS[j][3] = int(matrizFCFS[j][4]) - procesos[key][1]
    j = j + 1
  k = 1
  for key in procesos.keys():
    matrizFCFS[k][5] = int(matrizFCFS[k][4]) / procesos[key][1]
    k = k + 1


quantum = 1


def RR1(procesos, quantum, matrizRR1):
  a = 0
  b = 0
  c = 0
  d = 0
  e = 0

  resultado = []
  indice = 1
  for key in procesos.keys():
    matrizRR1[indice][1] = procesos[key][1]
    matrizRR1[indice][2] = procesos[key][0]
    indice = indice + 1
  colaProcesos = []
  prioridad = '0'
  contTick = 0
  while contTick <= tiempoMaxTot + 2:

    try:
      prioridad = colaProcesos.pop(0)
    except:
      prioridad = 'X'
    if (prioridad == 'A'):
      matrizRR1[1][4] = contTick
      resultado.append('A')
    elif (prioridad == 'B'):
      matrizRR1[2][4] = contTick
      resultado.append('B')
    elif (prioridad == 'C'):
      matrizRR1[3][4] = contTick
      resultado.append('C')
    elif (prioridad == 'D'):
      matrizRR1[4][4] = contTick
      resultado.append('D')
    elif (prioridad == 'E'):
      matrizRR1[5][4] = contTick
      resultado.append('E')
    temp = contTick + 1
    if (int(matrizRR1[1][2]) == temp and a == 0 and int(matrizRR1[1][1]) > 0):
      a = 1
      b = 0
      c = 0
      d = 0
      e = 0
      for ja in range(0, quantum):
        if (int(matrizRR1[1][1]) > 0):
          colaProcesos.append('A')
          matrizRR1[1][1] = int(matrizRR1[1][1]) - 1
          matrizRR1[1][2] = int(matrizRR1[1][2]) + 1

    if (int(matrizRR1[2][2]) == temp and b == 0 and int(matrizRR1[2][1]) > 0):
      a = 0
      b = 1
      c = 0
      d = 0
      e = 0
      for ja in range(0, quantum):
        if (int(matrizRR1[2][1]) > 0):
          colaProcesos.append('B')
          matrizRR1[2][1] = int(matrizRR1[2][1]) - 1
          matrizRR1[2][2] = int(matrizRR1[2][2]) + 1
    if (int(matrizRR1[3][2]) == temp and c == 0 and int(matrizRR1[3][1]) > 0):
      a = 0
      b = 0
      c = 1
      d = 0
      e = 0
      for ja in range(0, quantum):
        if (int(matrizRR1[3][1]) > 0):
          colaProcesos.append('C')
          matrizRR1[3][1] = int(matrizRR1[3][1]) - 1
          matrizRR1[3][2] = int(matrizRR1[3][2]) + 1
    if (int(matrizRR1[4][2]) == temp and d == 0 and int(matrizRR1[4][1]) > 0):
      a = 0
      b = 0
      c = 0
      d = 1
      e = 0
      for ja in range(0, quantum):
        if (int(matrizRR1[4][1]) > 0):
          colaProcesos.append('D')
          matrizRR1[4][1] = int(matrizRR1[4][1]) - 1
          matrizRR1[4][2] = int(matrizRR1[4][2]) + 1

    if (int(matrizRR1[5][2]) == temp and e == 0 and int(matrizRR1[5][1]) > 0):
      a = 0
      b = 0
      c = 0
      d = 0
      e = 1
      for ja in range(0, quantum):
        if (int(matrizRR1[5][1]) > 0):
          colaProcesos.append('E')
          matrizRR1[5][1] = int(matrizRR1[5][1]) - 1
          matrizRR1[5][2] = int(matrizRR1[5][2]) + 1

    i = 1
    for key in procesos.keys():
      temp = contTick + 1
      if (int(matrizRR1[i][2]) == temp):
        for j in range(1, quantum + 1):
          if (int(matrizRR1[i][1]) > 0):
            if (key == 'A'):
              a = 1
              b = 0
              c = 0
              d = 0
              e = 0
            if (key == 'B'):
              a = 0
              b = 1
              c = 0
              d = 0
              e = 0
            if (key == 'C'):
              a = 0
              b = 0
              c = 1
              d = 0
              e = 0
            if (key == 'D'):
              a = 0
              b = 0
              c = 0
              d = 1
              e = 0
            if (key == 'E'):
              a = 0
              b = 0
              c = 0
              d = 0
              e = 1
            colaProcesos.append(key)
            matrizRR1[i][1] = int(matrizRR1[i][1]) - 1
            matrizRR1[i][2] = int(matrizRR1[i][2]) + 1
      i = i + 1

    contTick = contTick + 1
  m = 1
  for key in procesos.keys():
    matrizRR1[m][1] = int(matrizRR1[m][4]) - procesos[key][0]
    m = m + 1  

  k = 1
  for key in procesos.keys():
    matrizRR1[k][3] = int(matrizRR1[k][1]) - procesos[key][1]
    k = k + 1
  n = 1
  for key in procesos.keys():
    matrizRR1[n][5] = int(matrizRR1[n][1]) / procesos[key][1]
    n = n + 1
  stringProcesosRR1 = ''.join(resultado)
  return stringProcesosRR1

def SPN(procesos):

  indice = 1
  for key in procesos.keys():
    matrizSPN[indice][1] = procesos[key][1]
    matrizSPN[indice][2] = procesos[key][0]
    indice = indice + 1

  contTick = 1
  procesoMasCorto = 'A'
  resultado = []
  while contTick <= tiempoMaxTot + 2:
    i = 1
    for key in procesos.keys():
      if (procesoMasCorto == key and int(matrizSPN[i][1]) > 0):
        matrizSPN[i][1] = int(matrizSPN[i][1]) - 1
        matrizSPN[i][2] = int(matrizSPN[i][2]) + 1
        resultado.append(procesoMasCorto)
        if (int(matrizSPN[i][1]) == 0):
          procesoMasCorto = 'X'
      i += 1
    j = 1
    for key in procesos.keys():
      if (int(matrizSPN[j][2]) == contTick and int(matrizSPN[j][1]) > 0):
        matrizSPN[j][2] = int(matrizSPN[j][2]) + 1
      j += 1


    if (procesoMasCorto == 'X'):
      k = 1
      siguienteValor = ''
      proxProcesos = []
      for key in procesos.keys():
        if (contTick + 1 == int(matrizSPN[k][2]) and int(matrizSPN[k][1]) > 0):
          proxProcesos.append(int(matrizSPN[k][1]))
        k += 1
      proxProcesos = sorted(proxProcesos)

      try:
        siguienteValor = proxProcesos.pop(0)
      except:
        print()
      n = 1
      for key in procesos.keys():
        if (siguienteValor == int(matrizSPN[n][1]) and int(matrizSPN[n][2]) == contTick + 1):
          procesoMasCorto = matrizSPN[n][0]
        n += 1

    contTick += 1
  T = 1
  for key in procesos.keys():
    matrizSPN[T][4] = int(matrizSPN[T][2]) - procesos[key][0]
    T = T + 1
  E = 1
  for key in procesos.keys():
    matrizSPN[E][3] = int(matrizSPN[E][2]) - procesos[key][1]
    matrizSPN[E][3] = int(matrizSPN[E][3]) - procesos[key][0]
    E = E + 1
  P = 1
  for key in procesos.keys():
    matrizSPN[P][5] = int(matrizSPN[P][4]) / procesos[key][1]
    P = P + 1

  stringProcesosSPN = ''.join(resultado)
  return stringProcesosSPN

FCFS(procesos)

stringProcesosRR1 = ''
quantum = 1
stringProcesosRR1 = RR1(procesos, quantum, matrizRR1)

stringProcesosRR4 = ''
quantum = 4
stringProcesosRR4 = RR1(procesos, quantum, matrizRR4)

stringProcesosSPN = SPN(procesos)


sumaTFCFS = 0
for i in range(1, 6):
  sumaTFCFS = sumaTFCFS + int(matrizFCFS[i][4])

promTFCFS = sumaTFCFS / 5

sumaEFCFS = 0
for i in range(1, 6):
  sumaEFCFS = sumaEFCFS + int(matrizFCFS[i][3])

promEFCFS = sumaEFCFS / 5

sumaPFCFS = 0
for i in range(1, 6):
  sumaPFCFS = sumaPFCFS + float(matrizFCFS[i][5])

promPFCFS = sumaPFCFS / 5

print("First Come First Served: T=" + str(promTFCFS) + " E=" + str(promEFCFS) + " P=" +
      str(promPFCFS))
print(stringProcesos)

sumaTRR1 = 0
for i in range(1, 6):
  sumaTRR1 = sumaTRR1 + int(matrizRR1[i][1])

promTRR1 = sumaTRR1 / 5

sumaERR1 = 0
for i in range(1, 6):
  sumaERR1 = sumaERR1 + int(matrizRR1[i][3])

promERR1 = sumaERR1 / 5

sumaPRR1 = 0
for i in range(1, 6):
  sumaPRR1 = sumaPRR1 + float(matrizRR1[i][5])

promPRR1 = sumaPRR1 / 5

print("Round Robin Quantum 1: T=" + str(promTRR1) + " E=" + str(promERR1) + " P=" +
      str(promPRR1))
print(stringProcesosRR1)
sumaTRR4 = 0
for i in range(1, 6):
  sumaTRR4 = sumaTRR4 + int(matrizRR4[i][1])

promTRR4 = sumaTRR4 / 5

sumaERR4 = 0
for i in range(1, 6):
  sumaERR4 = sumaERR4 + int(matrizRR4[i][3])

promERR4 = sumaERR4 / 5

sumaPRR4 = 0
for i in range(1, 6):
  sumaPRR4 = sumaPRR4 + float(matrizRR4[i][5])

promPRR4 = sumaPRR4 / 5

print("Round Robin Quantum 4: T=" + str(promTRR4) + " E=" + str(promERR4) + " P=" +
      str(promPRR4))
print(stringProcesosRR4)

sumaTSPN = 0
for i in range(1, 6):
  sumaTSPN = sumaTSPN + int(matrizSPN[i][4])

promTSPN = sumaTSPN / 5

sumaESPN = 0
for i in range(1, 6):
  sumaESPN = sumaESPN + int(matrizSPN[i][3])

promESPN = sumaESPN / 5

sumaPSPN = 0
for i in range(1, 6):
  sumaPSPN = sumaPSPN + float(matrizSPN[i][5])

promPSPN = sumaPSPN / 5

print("Shortest Process Next: T=" + str(promTSPN) + " E=" + str(promESPN) + " P=" +
      str(promPSPN))
print(stringProcesosSPN)