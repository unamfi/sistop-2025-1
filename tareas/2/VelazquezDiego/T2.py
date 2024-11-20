from fpdf import FPDF
import matplotlib.pyplot as plt
import random
from collections import deque

# Generar los procesos aleatorios con tiempos de llegada y duración
def generar_procesos(num_procesos):
    procesos = []
    for i in range(num_procesos):
        tiempo_llegada = random.randint(0, 10)
        tiempo_duracion = random.randint(1, 5)
        procesos.append((chr(65 + i), tiempo_llegada, tiempo_duracion))  # (Nombre, Llegada, Duración)
    return sorted(procesos, key=lambda x: x[1])

# Cálculo de tiempo de retorno, espera y penalización
def calcular_metricas(procesos, ejecucion):
    tiempo_total = 0
    tiempo_retorno = []
    tiempo_espera = []
    
    tiempo_actual = 0
    for p in ejecucion:
        proceso = next((proc for proc in procesos if proc[0] == p), None)
        tiempo_inicio = max(tiempo_actual, proceso[1])
        tiempo_final = tiempo_inicio + proceso[2]
        
        tiempo_retorno.append(tiempo_final - proceso[1])
        tiempo_espera.append(tiempo_inicio - proceso[1])
        tiempo_total += proceso[2]
        tiempo_actual = tiempo_final

    T = sum(tiempo_retorno) / len(procesos)
    E = sum(tiempo_espera) / len(procesos)
    P = T / sum([proc[2] for proc in procesos])

    return T, E, P

# FCFS
def fcfs(procesos):
    ejecucion = []
    tiempo_actual = 0
    for p in procesos:
        if tiempo_actual < p[1]:
            tiempo_actual = p[1]
        ejecucion.extend([p[0]] * p[2])
        tiempo_actual += p[2]
    return ejecucion

# Round Robin con un quantum
def round_robin(procesos, quantum):
    ejecucion = []
    cola = deque(procesos)
    tiempo_actual = 0
    while cola:
        p = cola.popleft()
        tiempo_llegada, tiempo_duracion = p[1], p[2]
        if tiempo_actual < tiempo_llegada:
            tiempo_actual = tiempo_llegada
        tiempo_de_ejecucion = min(quantum, tiempo_duracion)
        ejecucion.extend([p[0]] * tiempo_de_ejecucion)
        tiempo_actual += tiempo_de_ejecucion
        if tiempo_duracion > quantum:
            cola.append((p[0], tiempo_actual, tiempo_duracion - quantum))
    return ejecucion

# SPN
def spn(procesos):
    ejecucion = []
    tiempo_actual = 0
    cola = []
    procesos_restantes = list(procesos)
    while procesos_restantes or cola:
        while procesos_restantes and procesos_restantes[0][1] <= tiempo_actual:
            cola.append(procesos_restantes.pop(0))
        if cola:
            cola.sort(key=lambda x: x[2])  # Ordena por tiempo de duración
            proceso = cola.pop(0)
            ejecucion.extend([proceso[0]] * proceso[2])
            tiempo_actual += proceso[2]
        else:
            tiempo_actual += 1
    return ejecucion

# Almacenamiento de resultados
def comparar_planificadores():
    num_procesos = 5
    rondas = 5
    resultados_globales = []

    for i in range(rondas):
        print(f"- Ronda {i+1}")
        procesos = generar_procesos(num_procesos)
        print("  Procesos:\n", [(p[0], f"llegada={p[1]}", f"duración={p[2]}") for p in procesos])
        
        resultados_ronda = {"Ronda": i + 1, "Procesos": procesos, "Resultados": {}}
        
        # FCFS
        ejecucion_fcfs = fcfs(procesos)
        T, E, P = calcular_metricas(procesos, ejecucion_fcfs)
        resultados_ronda["Resultados"]["FCFS"] = (T, E, P, ''.join(ejecucion_fcfs))
        
        # Round Robin con quantum = 1
        ejecucion_rr1 = round_robin(procesos, 1)
        T, E, P = calcular_metricas(procesos, ejecucion_rr1)
        resultados_ronda["Resultados"]["RR1"] = (T, E, P, ''.join(ejecucion_rr1))
        
        # Round Robin con quantum = 4
        ejecucion_rr4 = round_robin(procesos, 4)
        T, E, P = calcular_metricas(procesos, ejecucion_rr4)
        resultados_ronda["Resultados"]["RR4"] = (T, E, P, ''.join(ejecucion_rr4))
        
        # SPN
        ejecucion_spn = spn(procesos)
        T, E, P = calcular_metricas(procesos, ejecucion_spn)
        resultados_ronda["Resultados"]["SPN"] = (T, E, P, ''.join(ejecucion_spn))
        
        # Imprimir resultados
        for planificador, (T, E, P, ejecucion) in resultados_ronda["Resultados"].items():
            print(f"  {planificador}: T={T:.2f}, E={E:.2f}, P={P:.2f}")
            print(f"  {ejecucion}")

        resultados_globales.append(resultados_ronda)

    return resultados_globales


class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Comparación de Planificadores de Procesos en Sistemas Operativos", 0, 1, "C")
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(4)
    
    def chapter_body(self, body):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_table(self, headers, data):
        self.set_font("Arial", "B", 10)
        col_width = 190 / len(headers)  # Ajusta el ancho de columnas dinámicamente
        for header in headers:
            self.cell(col_width, 10, header, 1, 0, "C")
        self.ln()
        self.set_font("Arial", "", 10)
        for row in data:
            for item in row:
                self.cell(col_width, 10, str(item), 1, 0, "C")
            self.ln()
        self.ln(5)




# Crear el PDF basado en los resultados
def generar_pdf(resultados_globales):
    pdf = PDF()
    pdf.add_page()

    # Introducción
    pdf.chapter_title("Introducción")
    pdf.chapter_body("Este documento compara varios algoritmos de planificación de procesos...")

    # Resultados por ronda
    pdf.chapter_title("Resultados de Simulaciones")
    headers = ["Planificador", "T (Retorno)", "E (Espera)", "P (Penalización)"]

    for ronda in resultados_globales:
        pdf.chapter_body(f"Ronda {ronda['Ronda']}:")
        pdf.chapter_body("Procesos: " + ', '.join([f"{p[0]}(llegada={p[1]}, duración={p[2]})" for p in ronda["Procesos"]]))

        data = [
            [planificador, f"{T:.2f}", f"{E:.2f}", f"{P:.2f}"]
            for planificador, (T, E, P, _) in ronda["Resultados"].items()
        ]
        pdf.add_table(headers, data)

    # Graficar comparaciones
    generar_grafico(resultados_globales)
    pdf.chapter_title("Gráficos Comparativos")
    pdf.image("grafico_retornos.png", x=10, y=None, w=180)

    pdf.output("comparacion_planificadores.pdf")
    print("\nEl PDF 'comparacion_planificadores.pdf' se generó correctamente.\n")
    print("\nAhí puedes verificar la información estructurada y la gráfica de \nlos datos reales generados (tiempos de retorno) con las tendencias \nentre los planificadores.\n")




# Generar gráfico basado en resultados globales
def generar_grafico(resultados_globales):
    rondas = [ronda["Ronda"] for ronda in resultados_globales]
    fcfs_T = [ronda["Resultados"]["FCFS"][0] for ronda in resultados_globales]
    rr1_T = [ronda["Resultados"]["RR1"][0] for ronda in resultados_globales]
    rr4_T = [ronda["Resultados"]["RR4"][0] for ronda in resultados_globales]
    spn_T = [ronda["Resultados"]["SPN"][0] for ronda in resultados_globales]

    plt.plot(rondas, fcfs_T, label="FCFS")
    plt.plot(rondas, rr1_T, label="RR1")
    plt.plot(rondas, rr4_T, label="RR4")
    plt.plot(rondas, spn_T, label="SPN")
    plt.legend()
    plt.title("Comparación de Tiempo de Retorno")
    plt.xlabel("Rondas")
    plt.ylabel("T (Retorno)")
    plt.savefig("grafico_retornos.png")
    plt.close()


if __name__ == "__main__":
    resultados_globales = comparar_planificadores()
    generar_pdf(resultados_globales)
