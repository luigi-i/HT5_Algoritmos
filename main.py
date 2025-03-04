import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Configuración inicial
semilla = 524
RAM = 200
ticks = 6
capacidad = 10 # Intervalo de llegada de procesos (distribución exponencial)
nProcesos = [25, 50, 100, 150, 200]

random.seed(semilla)

avg_times = []
std_times = []

class Process:
    def __init__(self, env, name, ram, cpu):
        self.env = env
        self.name = name
        self.ram = ram
        self.cpu = cpu
        self.memoriaRequerida = random.randint(1, 10)  # Memoria requerida aleatoria
        self.instructions = random.randint(1, 10)    # Instrucciones totales aleatorias
        self.start_time = env.now
        self.action = env.process(self.run())

    def run(self):
        # NEW
        yield self.ram.get(self.memoriaRequerida)
        
        # ready y running
        while self.instructions > 0:
            with self.cpu.request() as req:
                yield req
                # Running
                yield self.env.timeout(1)
                self.instructions = max(0, self.instructions - ticks)
                
                if self.instructions > 0:
                    # Decidir próximo estado 
                    next_state = random.randint(1, 2)  # Generar número entre 1 y 2
                    if next_state == 1:  # waiting 1/2 (I/O)
                        yield self.env.timeout(1)  # Simular tiempo de I/O

        # Terminated, borra la memoria del proceso
        total_time = self.env.now - self.start_time
        yield self.ram.put(self.memoriaRequerida)
        tDeProcesado.append(total_time)

def process_generator(env, num_processes, ram, cpu):
    for i in range(num_processes):
        Process(env, f"Process {i}", ram, cpu)
        yield env.timeout(random.expovariate(1.0 / capacidad))


# Ejecutar simulación para cada cantidad de procesos
for num_procesos in nProcesos:
    tDeProcesado = []
    env = simpy.Environment()
    ram = simpy.Container(env, init=RAM, capacity=RAM)
    cpu = simpy.Resource(env, capacity=1)
    
    env.process(process_generator(env, num_procesos, ram, cpu))
    env.run()
    
    avg_time = np.sum(tDeProcesado) / 100  # Ambos divididos por 100 para que
    std_time = np.std(tDeProcesado) / 100  # Se lea mejor
    avg_times.append(avg_time)
    std_times.append(std_time)
    
    #resultados
    print(f"\nResultados para: {num_procesos} processes:")
    print(f"Tiempo promedio: {avg_time:.2f}")
    print(f"Desviacion estandar: {std_time:.2f}")
    print(f"RAM disponible: {RAM}")
    print(f"Procesos por ciclo: {ticks}")

# gráfica
plt.figure(figsize=(10, 6))
plt.errorbar(nProcesos, avg_times, yerr=std_times, fmt='o-', capsize=5, label='Average Time', color='blue')
plt.xlabel('Numero de Procesos')
plt.ylabel('Tiempo requerido en unidades del sistema / 100')
plt.suptitle("Tiempo promedio / Numero de procesos")
plt.title("Intervalo de procesos: 10, RAM = 100, Procesos por ciclo = 6")
plt.grid(True)
plt.legend()
plt.savefig('process_time_vs_number.png')
plt.show()
