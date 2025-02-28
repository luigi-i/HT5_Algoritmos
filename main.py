import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Configuración inicial
RANDOM_SEED = 42
RAM_CAPACITY = 100
CPU_INSTRUCTIONS_PER_TICK = 3
INTERVAL = 10  # Intervalo de llegada de procesos (distribución exponencial)
process_counts = [25, 50, 100, 150, 200]

random.seed(RANDOM_SEED)

avg_times = []
std_times = []

class Process:
    def __init__(self, env, name, ram, cpu):
        self.env = env
        self.name = name
        self.ram = ram
        self.cpu = cpu
        self.memory_needed = random.randint(1, 10)  # Memoria requerida (1-10)
        self.instructions = random.randint(1, 10)    # Instrucciones totales (1-10)
        self.start_time = env.now
        self.action = env.process(self.run())

    def run(self):
        # Estado NEW: Solicitar memoria RAM
        yield self.ram.get(self.memory_needed)
        
        # Estado READY y RUNNING
        while self.instructions > 0:
            with self.cpu.request() as req:
                yield req
                # Estado RUNNING: Ejecutar 3 instrucciones por unidad de tiempo
                yield self.env.timeout(1)
                self.instructions = max(0, self.instructions - CPU_INSTRUCTIONS_PER_TICK)
                
                if self.instructions > 0:
                    # Decidir próximo estado después de RUNNING (probabilidad 1/21 para WAITING, 20/21 para READY)
                    next_state = random.randint(1, 21)  # Generar número entre 1 y 21
                    if next_state == 1:  # WAITING (1/21 probabilidad, I/O)
                        yield self.env.timeout(1)  # Simular tiempo de I/O
                    # Si no es 1 (20/21 probabilidad), vuelve implícitamente a READY (espera por CPU)

        # Estado TERMINATED: Liberar memoria
        total_time = self.env.now - self.start_time
        yield self.ram.put(self.memory_needed)
        process_times.append(total_time)

def process_generator(env, num_processes, ram, cpu):
    for i in range(num_processes):
        Process(env, f"Process {i}", ram, cpu)
        yield env.timeout(random.expovariate(1.0 / INTERVAL))

# Ejecutar simulación para cada cantidad de procesos
for num_processes in process_counts:
    process_times = []
    env = simpy.Environment()
    ram = simpy.Container(env, init=RAM_CAPACITY, capacity=RAM_CAPACITY)
    cpu = simpy.Resource(env, capacity=1)
    
    env.process(process_generator(env, num_processes, ram, cpu))
    env.run()
    
    avg_time = np.mean(process_times)
    std_time = np.std(process_times)
    avg_times.append(avg_time)
    std_times.append(std_time)
    
    print(f"\nResults for {num_processes} processes:")
    print(f"Average time: {avg_time:.2f}")
    print(f"Standard deviation: {std_time:.2f}")

# Generar la gráfica
plt.figure(figsize=(10, 6))
plt.errorbar(process_counts, avg_times, yerr=std_times, fmt='o-', capsize=5, label='Average Time', color='blue')
plt.xlabel('Number of Processes')
plt.ylabel('Average Time in System (units)')
plt.title('Average Process Time vs Number of Processes')
plt.grid(True)
plt.legend()
plt.savefig('process_time_vs_number.png')
plt.show()
