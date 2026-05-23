import time
import os
import matplotlib.pyplot as plt

# --- NUEVA RUTA ASIGNADA PARA INVERSIÓN DE GIRO ---
ruta_compartida = r"C:\Users\Hp\Documents\Inversi-n-de-Giro-Autom-tica-Maniobra-de-Potencia"

# Verificación y creación automatizada del directorio de trabajo
if not os.path.exists(ruta_compartida):
    os.makedirs(ruta_compartida)
os.chdir(ruta_compartida)

# --- CONFIGURACIÓN DE ALTA RESOLUCIÓN NUMÉRICA ---
pasos = 1000  # Número de iteraciones
dt = 0.005    # Paso temporal fino (5ms) para asegurar convergencia y estabilidad
set_point = 100.0  

# Sintonización PID suavizada para erradicar el efecto Chattering en el voltaje
Kp, Ki, Kd = 0.25, 0.05, 0.001
integral, error_anterior = 0.0, 0.0

w_actual = 0.0
ia_actual = 0.0
voltaje_va = 0.0
t_carga = 0.0

historial_tiempo = []
historial_w = []
historial_setpoint = []
historial_ia = []
historial_va = []
historial_error = []
historial_tcarga = []

# Limpieza preventiva del canal de archivos compartidos
for f in ['entrada.txt', 'salida.txt']:
    if os.path.exists(f):
        try: os.remove(f)
        except: pass

print("==================================================================")
print("  CO-SIMULACIÓN: INVERSIÓN DE GIRO AUTOMÁTICA EN NUEVO DIRECTORIO ")
print("==================================================================")
print(f"Ruta de operaciones activa: {ruta_compartida}\n")

for step in range(pasos):
    tiempo = step * dt
    
    # Criterio de inversión automática de marcha (A los 2.5 segundos)
    if tiempo >= 2.5:
        set_point = -100.0  
    
    # Perturbación de carga (frenado mecánico) al segundo 4.0
    if tiempo >= 4.0:
        t_carga = 2.0  
    else:
        t_carga = 0.0

    # 1. ALGORITMO DEL CONTROLADOR PID
    error = set_point - w_actual
    integral += error * dt
    derivada = (error - error_anterior) / dt
    
    voltaje_va = (Kp * error) + (Ki * integral) + (Kd * derivada)
    voltaje_va = max(-24.0, min(voltaje_va, 24.0))  # Restricción física a fuente de 24V
    error_anterior = error

    historial_tiempo.append(tiempo)
    historial_w.append(w_actual)
    historial_setpoint.append(set_point)
    historial_ia.append(ia_actual)
    historial_va.append(voltaje_va)
    historial_error.append(error)
    historial_tcarga.append(t_carga)

    # 2. ESCRITURA DE DATOS PARA LA PLANTA EN MATLAB
    with open('entrada.txt', 'w') as f:
        f.write(f"{voltaje_va:.4f} {t_carga:.4f}\n")
    
    # 3. PROTOCOLO HANDSHAKE: ESPERAR SCRIPT DE MATLAB
    while not os.path.exists('salida.txt'):
        time.sleep(0.001)

    # 4. CAPTURA DE RESPUESTA ELECTROMECÁNICA EN LAZO CERRADO
    lectura_exitosa = False
    while not lectura_exitosa:
        try:
            with open('salida.txt', 'r') as f:
                linea = f.read().split()
                if len(linea) >= 2:
                    w_actual = float(linea[0])
                    ia_actual = float(linea[1])
                    lectura_exitosa = True
        except (IOError, ValueError):
            time.sleep(0.001)

    try: os.remove('salida.txt')
    except: pass

print("\n¡Simulación numérica completada! Generando panel analítico estable...")

# --- GRAFICACIÓN SIMULTÁNEA DE VARIABLES (GRID 3x2) ---
plt.figure(figsize=(14, 10))

plt.subplot(3, 2, 1)
plt.plot(historial_tiempo, historial_setpoint, 'r--', label='Referencia de Giro')
plt.plot(historial_tiempo, historial_w, 'b-', linewidth=2, label='Velocidad del Motor (w)')
plt.ylabel('Velocidad (rad/s)')
plt.title('Dinámica del Rotor: Perfil de Velocidad Angular', fontsize=11, fontweight='bold')
plt.legend(loc='lower left')
plt.grid(True)

plt.subplot(3, 2, 2)
plt.plot(historial_tiempo, historial_ia, 'g-', linewidth=2, label='Corriente de Armadura (Ia)')
plt.ylabel('Corriente (A)')
plt.title('Monitoreo de Potencia: Corriente de Armadura', fontsize=11, fontweight='bold')
plt.legend(loc='upper right')
plt.grid(True)

plt.subplot(3, 2, 3)
plt.plot(historial_tiempo, historial_va, 'm-', linewidth=2, label='Voltaje de Armadura (Va)')
plt.ylabel('Voltaje (V)')
plt.title('Acción de Control: Señal Eléctrica de Entrada', fontsize=11, fontweight='bold')
plt.legend(loc='lower left')
plt.grid(True)

plt.subplot(3, 2, 4)
plt.plot(historial_tiempo, historial_error, 'c-', linewidth=2, label='Error (SP - w)')
plt.ylabel('Error (rad/s)')
plt.title('Magnitud de Desviación Cinemática (Error)', fontsize=11, fontweight='bold')
plt.legend(loc='upper right')
plt.grid(True)

plt.subplot(3, 2, 5)
plt.fill_between(historial_tiempo, historial_tcarga, color='orange', alpha=0.3, label='Torque de Carga (TL)')
plt.xlabel('Tiempo (segundos)')
plt.ylabel('Torque (N·m)')
plt.title('Perfil de Perturbación: Torque de Carga Asignado', fontsize=11, fontweight='bold')
plt.legend(loc='upper left')
plt.grid(True)

plt.subplot(3, 2, 6)
plt.plot(historial_ia, historial_w, 'k-', linewidth=1.5, label='Evolución Electromecánica')
plt.xlabel('Corriente de Armadura Ia (A)')
plt.ylabel('Velocidad Angular w (rad/s)')
plt.title('Plano de Fase: Espacio de Estados Electromecánicos', fontsize=11, fontweight='bold')
plt.legend(loc='lower right')
plt.grid(True)

plt.tight_layout()
plt.show()