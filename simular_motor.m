% --- PARÁMETROS NOMINALES DE UN MOTOR DC DE POTENCIA ---
R = 1.12;      % Resistencia eléctrica de armadura (Ohms)
L = 0.045;     % Inductancia de armadura (Henrios)
J = 0.022;     % Momento de inercia del rotor (kg·m^2)
B = 0.0015;    % Coeficiente de fricción mecánica (N·m·s/rad)
Kt = 0.48;     % Constante de torque electromecánico (N·m/A)
Ke = 0.48;     % Constante de fuerza contraelectromotriz (V·s/rad)
dt = 0.005;    % Sincronización estricta del paso del resolvedor discreto

% Estados iniciales
ia = 0.0; 
w = 0.0;

% --- REDIRECCIONAMIENTO FÍSICO DE LA CARPETA ---
cd('C:\Users\Hp\Documents\Inversi-n-de-Giro-Autom-tica-Maniobra-de-Potencia');

if exist('entrada.txt', 'file'), delete('entrada.txt'); end
if exist('salida.txt', 'file'), delete('salida.txt'); end

fprintf('Actuador Electromecánico listo en la nueva ruta. Esperando señales de Python...\n');

while true
    fid_in = fopen('entrada.txt', 'r');
    if fid_in ~= -1
        linea = fgetl(fid_in);
        fclose(fid_in);
        
        if ischar(linea)
            datos = sscanf(linea, '%f %f');
            
            if length(datos) >= 2
                Va = datos(1); % Tensión enviada por el PID
                Tl = datos(2); % Torque de la perturbación
                
                delete('entrada.txt'); % Handshake de liberación
                
                % RESOLUCIÓN POR MÉTODO DE EULER DE ALTA PRECISIÓN (PREVIENE INESTABILIDAD)
                % Ecuación de corriente: di_a/dt
                dia = (Va - R * ia - Ke * w) / L;
                ia = ia + dia * dt;
                
                % Ecuación de velocidad rotacional: dw/dt
                dw = (Kt * ia - B * w - Tl) / J;
                w = w + dw * dt;
                
                % DEVOLUCIÓN DE VARIABLES DINÁMICAS SINCRO-TEMPORALES
                fid_out = fopen('salida.txt', 'w');
                if fid_out ~= -1
                    fprintf(fid_out, '%.4f %.4f\n', w, ia);
                    fclose(fid_out);
                end
            end
        end
    end
    pause(0.001); % Pausa mínima para no congestionar ciclos de CPU
end