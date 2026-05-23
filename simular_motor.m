% --- PARÁMETROS NOMINALES DE UN MOTOR DC DE POTENCIA ---
R = 1.12;      % Resistencia eléctrica de armadura (Ohms)
L = 0.045;     % Inductancia de armadura (Henrios)
J = 0.022;     % Momento de inercia del rotor (kg·m^2)
B = 0.0015;    % Coeficiente de fricción mecánica (N·m·s/rad)
Kt = 0.48;     % Constante de torque electromecánico (N·m/A)
Ke = 0.48;     % Constante de fuerza contraelectromotriz (V·s/rad)
dt = 0.08;     % Resolución temporal

% Estados iniciales en reposo total
ia = 0.0; 
w = 0.0;

% --- ACTUALIZACIÓN DE CARPETA DE TRABAJO ---
cd('C:\Users\Hp\Documents\Inversi-n-de-Giro-Autom-tica-Maniobra-de-Potencia');

if exist('entrada.txt', 'file'), delete('entrada.txt'); end
if exist('salida.txt', 'file'), delete('salida.txt'); end

fprintf('Actuador Electromecánico de Potencia inicializado en la nueva ruta. Esperando comandos de Python...\n');

while true
    fid_in = fopen('entrada.txt', 'r');
    if fid_in ~= -1
        linea = fgetl(fid_in);
        fclose(fid_in);
        
        if ischar(linea)
            datos = sscanf(linea, '%f %f');
            
            if length(datos) >= 2
                Va = datos(1); % Voltaje enviado por el PID
                Tl = datos(2); % Perturbación de torque externo
                
                delete('entrada.txt'); % Handshake de liberación
                
                % RESOLUCIÓN POR MÉTODO DE INTEGRACIÓN NUMÉRICA DE EULER
                % Ecuación 1: di_a/dt (Malla eléctrica)
                dia = (Va - R * ia - Ke * w) / L;
                ia = ia + dia * dt;
                
                % Ecuación 2: dw/dt (Dinámica de rotación del rotor)
                dw = (Kt * ia - B * w - Tl) / J;
                w = w + dw * dt;
                
                % RETORNO DE VARIABLES DE ESTADO CONTINUAS
                fid_out = fopen('salida.txt', 'w');
                if fid_out ~= -1
                    fprintf(fid_out, '%.4f %.4f\n', w, ia);
                    fclose(fid_out);
                end
            end
        end
    end
    pause(0.005);
end