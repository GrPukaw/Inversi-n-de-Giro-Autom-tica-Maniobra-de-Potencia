import time
import os
import matplotlib.pyplot as plt

# --- RUTA ASIGNADA PARA INVERSIÓN DE GIRO ---
ruta_compartida = r"C:\Users\Hp\Documents\Inversi-n-de-Giro-Autom-tica-Maniobra-de-Potencia"
if not os.path.exists(ruta_compartida):
    os.makedirs(ruta_compartida)
os.chdir(ruta_compartida)

# --- CONFIGURACIÓN DE TIEMPO EXTENDIDO Y ALTA RESOLUCIÓN ---
pasos = 3000  # Aumentamos pasos para cubrir 15 segundos
dt = 0.005    
set_point = 100.0  

# NUEVA SINTONIZACIÓN INDUSTRIAL (Elimina el error estacionario y estabiliza)
Kp, Ki, Kd = 0.85, 1.45, 0.005
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
historial_potencia = [] # Nueva variable visual

for f in ['entrada.txt', 'salida.txt']:
    if os.path.exists(f):
        try: os.remove(f)
        except: pass

print("==================================================================")
print("  PROYECTO COMPLETO: INVERSIÓN DE GIRO CON CONVERGENCIA EXACTA   ")
print("==================================================================")

for step in range(pasos):
    tiempo = step * dt
    
    # Evento 1: Inversión de marcha extendida al segundo 5.0
    if tiempo >= 5.0:
        set_point = -100.0  
    
    # Evento 2: Perturbación de carga aplicada al segundo 10.0
    if tiempo >= 10.0:
        t_carga = 3.0  # Incrementamos el torque a 3.0 N·m para mayor impacto visual
    else:
        t_carga = 0.0

    # 1. ALGORITMO DEL CONTROLADOR PID CLÁSICO
    error = set_point - w_actual
    integral += error * dt
    derivada = (error - error_anterior) / dt
    
    voltaje_va = (Kp * error) + (Ki * integral) + (Kd * derivada)
    voltaje_va = max(-24.0, min(voltaje_va, 24.0))  
    error_anterior = error

    # Cálculo de Potencia Eléctrica Activa (P = V * I)
    potencia = voltaje_va * ia_actual

    historial_tiempo.append(tiempo)
    historial_w.append(w_actual)
    historial_setpoint.append(set_point)
    historial_ia.append(ia_actual)
    historial_va.append(voltaje_va)
    historial_error.append(error)
    historial_potencia.append(potencia)

    # 2. ESCRITURA HACIA MATLAB
    with open('entrada.txt', 'w') as f:
        f.write(f"{voltaje_va:.4f} {t_carga:.4f}\n")
    
    # 3. HANDSHAKE
    while not os.path.exists('salida.txt'):
        time.sleep(0.001)

    # 4. LECTURA DE PLANTA
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

print("\n¡Simulación de alta fidelidad completada!")

# --- CONFIGURACIÓN DEL PANEL DE GRÁFICOS OPTIMIZADO ---
plt.figure(figsize=(15, 10))

# G1: Velocidad Angular con seguimiento perfecto
plt.subplot(3, 2, 1)
plt.plot(historial_tiempo, historial_setpoint, 'r--', label='Consigna (SetPoint)')
plt.plot(historial_tiempo, historial_w, 'b-', linewidth=2, label='Velocidad Angular Real (w)')
plt.axvline(x=5.0, color='black', linestyle=':', label='Orden Inversión')
plt.axvline(x=10.0, color='orange', linestyle='--', label='Inyección Carga')
plt.ylabel('Velocidad (rad/s)')
plt.title('Dinámica del Rotor: Perfil de Velocidad Angular ($\omega$)', fontsize=11, fontweight='bold')
plt.legend(loc='lower left')
plt.grid(True)

# G2: Corriente de Armadura con picos reales transitorios
plt.subplot(3, 2, 2)
plt.plot(historial_tiempo, historial_ia, 'g-', linewidth=2, label='Corriente Ia (A)')
plt.axvline(x=5.0, color='black', linestyle=':')
plt.axvline(x=10.0, color='orange', linestyle='--')
plt.ylabel('Corriente (A)')
plt.title('Monitoreo Eléctrico: Corriente de Armadura ($I_a$)', fontsize=11, fontweight='bold')
plt.legend(loc='upper right')
plt.grid(True)

# G3: Voltaje de Control Suave sin Chattering
plt.subplot(3, 2, 3)
plt.plot(historial_tiempo, historial_va, 'm-', linewidth=2, label='Voltaje Va (V)')
plt.ylabel('Voltaje (V)')
plt.title('Acción de Control: Tensión de Entrada Regulada ($V_a$)', fontsize=11, fontweight='bold')
plt.legend(loc='lower left')
plt.grid(True)

# G4: Error del Sistema que converge exactamente a Cero
plt.subplot(3, 2, 4)
plt.plot(historial_tiempo, historial_error, 'c-', linewidth=2, label='Error de Estado')
plt.ylabel('Error (rad/s)')
plt.title('Dinámica del Error: Desviación Cinética Temporal', fontsize=11, fontweight='bold')
plt.legend(loc='upper right')
plt.grid(True)

# G5: NUEVO GRAFICO VISUAL - Consumo Energético Transitorio
plt.subplot(3, 2, 5)
plt.fill_between(historial_tiempo, historial_potencia, color='purple', alpha=0.3, label='Potencia Absorbida/Regenerada')
plt.xlabel('Tiempo (segundos)')
plt.ylabel('Potencia (Watts)')
plt.title('Análisis Energético: Potencia Instantánea en la Maniobra', fontsize=11, fontweight='bold')
plt.legend(loc='upper left')
plt.grid(True)

# G6: Plano de Fase Cerrado Espectacular
plt.subplot(3, 2, 6)
plt.plot(historial_ia, historial_w, 'k-', linewidth=1.5, label='Trayectoria de Estados')
plt.xlabel('Corriente de Armadura Ia (A)')
plt.ylabel('Velocidad Angular w (rad/s)')
plt.title('Plano de Fase: Espacio de Estados Electromecánicos', fontsize=11, fontweight='bold')
plt.legend(loc='lower right')
plt.grid(True)

plt.tight_layout()
plt.show()