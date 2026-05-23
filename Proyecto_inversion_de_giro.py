import time
import os
import matplotlib.pyplot as plt

# --- NUEVA RUTA PARA EL PROYECTO DE INVERSIÓN DE GIRO ---
ruta_compartida = r"C:\Users\Hp\Documents\proyecto_inversion_giro"

# Crear la carpeta automáticamente si no existe
if not os.path.exists(ruta_compartida):
    os.makedirs(ruta_compartida)
os.chdir(ruta_compartida)

# --- CONFIGURACIÓN DE LA SIMULACIÓN ---
pasos = 250  
dt = 0.08  # Paso del tiempo para capturar transitorios eléctricos rápidos
set_point = 100.0  # Velocidad objetivo inicial (Giro Horario)

# Sintonización PID robusta para inversión de marcha eléc-mecánica
Kp, Ki, Kd = 1.2, 0.4, 0.02
integral, error_anterior = 0.0, 0.0

w_actual = 0.0
ia_actual = 0.0
voltaje_va = 0.0
t_carga = 0.0

# Historiales para los 6 gráficos del reporte
historial_tiempo = []
historial_w = []
historial_setpoint = []
historial_ia = []
historial_va = []
historial_error = []
historial_tcarga = []

# Limpieza inicial de archivos
for f in ['entrada.txt', 'salida.txt']:
    if os.path.exists(f):
        try: os.remove(f)
        except: pass

print("==================================================================")
print("  CO-SIMULACIÓN: INVERSIÓN DE GIRO AUTOMÁTICA EN LAZO CERRADO   ")
print("==================================================================")

for step in range(pasos):
    tiempo = step * dt
    
    # CRITERIO DE INVERSIÓN AUTOMÁTICA DE GIRO (A los 10 segundos de operación)
    if tiempo >= 10.0:
        set_point = -100.0  # Inversión de marcha (Giro Antihorario)
    
    # PERTURBACIÓN EXTRA: Torque de carga de frenado en el segundo 16
    if tiempo >= 16.0:
        t_carga = 3.5  # Torque resistente en Newtons-metro
    else:
        t_carga = 0.0

    # 1. CONTROLADOR PID
    error = set_point - w_actual
    integral += error * dt
    derivada = (error - error_anterior) / dt
    
    # Voltaje comandado de armadura (Inversión Automática) con límite de fuente industrial
    voltaje_va = (Kp * error) + (Ki * integral) + (Kd * derivada)
    voltaje_va = max(-28.0, min(voltaje_va, 28.0))  # Límite físico +/- 28V
    error_anterior = error

    # Guardar historiales
    historial_tiempo.append(tiempo)
    historial_w.append(w_actual)
    historial_setpoint.append(set_point)
    historial_ia.append(ia_actual)
    historial_va.append(voltaje_va)
    historial_error.append(error)
    historial_tcarga.append(t_carga)

    # 2. COMUNICACIÓN: ENVIAR COMANDOS A MATLAB
    with open('entrada.txt', 'w') as f:
        f.write(f"{voltaje_va:.4f} {t_carga:.4f}\n")
    
    # 3. ESPERAR PLANTA EN MATLAB
    while not os.path.exists('salida.txt'):
        time.sleep(0.005)

    # 4. CAPTURAR RESPUESTA ELECTROMECÁNICA
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
            time.sleep(0.005)

    try: os.remove('salida.txt')
    except: pass

print("\n¡Co-simulación de potencia completada! Generando panel analítico...")

# --- MACRO-PANEL DE MONITOREO DE POTENCIA INDUSTRIAL (3x2 GRID) ---
plt.figure(figsize=(14, 10))

# G1: Velocidad Angular Real vs Consigna de Inversión
plt.subplot(3, 2, 1)
plt.plot(historial_tiempo, historial_setpoint, 'r--', label='Referencia de Giro')
plt.plot(historial_tiempo, historial_w, 'b-', linewidth=2, label='Velocidad del Motor (w)')
plt.axvline(x=10.0, color='gray', linestyle=':', label='Orden de Inversión')
plt.ylabel('Velocidad (rad/s)')
plt.title('Dinámica del Rotor: Perfil de Velocidad Angular', fontsize=11, fontweight='bold')
plt.legend(loc='lower left')
plt.grid(True)

# G2: Corriente de Armadura (Transitorios Dinámicos Severos)
plt.subplot(3, 2, 2)
plt.plot(historial_tiempo, historial_ia, 'g-', linewidth=2, label='Corriente de Armadura (Ia)')
plt.axvline(x=10.0, color='gray', linestyle=':')
plt.ylabel('Corriente (A)')
plt.title('Monitoreo de Potencia: Corriente de Armadura', fontsize=11, fontweight='bold')
plt.legend(loc='upper right')
plt.grid(True)

# G3: Tensión de Control Aplicada (Acción de Maniobra)
plt.subplot(3, 2, 3)
plt.plot(historial_tiempo, historial_va, 'm-', linewidth=2, label='Voltaje de Armadura (Va)')
plt.axvline(x=10.0, color='gray', linestyle=':')
plt.ylabel('Voltaje (V)')
plt.title('Acción de Control: Señal Eléctrica de Entrada', fontsize=11, fontweight='bold')
plt.legend(loc='lower left')
plt.grid(True)

# G4: Error del Seguimiento de Perfil
plt.subplot(3, 2, 4)
plt.plot(historial_tiempo, historial_error, 'c-', linewidth=2, label='Error (SP - w)')
plt.ylabel('Error (rad/s)')
plt.title('Magnitud de Desviación Cinemática (Error)', fontsize=11, fontweight='bold')
plt.legend(loc='upper right')
plt.grid(True)

# G5: Estado de la Perturbación Mecánica (Torque de Carga)
plt.subplot(3, 2, 5)
plt.fill_between(historial_tiempo, historial_tcarga, color='orange', alpha=0.3, label='Carga Mecánica Externa (TL)')
plt.xlabel('Tiempo (segundos)')
plt.ylabel('Torque (N·m)')
plt.title('Perfil de Perturbación: Torque de Carga Asignado', fontsize=11, fontweight='bold')
plt.legend(loc='upper left')
plt.grid(True)

# G6: Plano de Fase Electromecánico (Corriente vs Velocidad)
plt.subplot(3, 2, 6)
plt.plot(historial_ia, historial_w, 'k-', linewidth=1.5, label='Evolución Electromecánica')
plt.xlabel('Corriente de Armadura Ia (A)')
plt.ylabel('Velocidad Angular w (rad/s)')
plt.title('Plano de Fase: Espacio de Estados Electromecánicos', fontsize=11, fontweight='bold')
plt.legend(loc='lower right')
plt.grid(True)

plt.tight_layout()
plt.show()