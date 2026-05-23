% --- PARÁMETROS NOMINALES DE UN MOTOR DC DE POTENCIA ---
R = 1.12;      
L = 0.045;     
J = 0.022;     
B = 0.0015;    
Kt = 0.48;     
Ke = 0.48;     
dt = 0.005;    % REDUCCIÓN SÍNCRONA DEL PASO TEMPORAL MATEMÁTICO

ia = 0.0; 
w = 0.0;

cd('C:\Users\Hp\Documents\proyecto_inversion_giro');

if exist('entrada.txt', 'file'), delete('entrada.txt'); end
if exist('salida.txt', 'file'), delete('salida.txt'); end

fprintf('Actuador Electromecánico Estabilizado. Esperando comandos...\n');

while true
    fid_in = fopen('entrada.txt', 'r');
    if fid_in ~= -1
        linea = fgetl(fid_in);
        fclose(fid_in);
        
        if ischar(linea)
            datos = sscanf(linea, '%f %f');
            
            if length(datos) >= 2
                Va = datos(1); 
                Tl = datos(2); 
                
                delete('entrada.txt'); 
                
                % RESOLUCIÓN POR MÉTODO DE EULER DE ALTA PRECISIÓN
                dia = (Va - R * ia - Ke * w) / L;
                ia = ia + dia * dt;
                
                dw = (Kt * ia - B * w - Tl) / J;
                w = w + dw * dt;
                
                fid_out = fopen('salida.txt', 'w');
                if fid_out ~= -1
                    fprintf(fid_out, '%.4f %.4f\n', w, ia);
                    fclose(fid_out);
                end
            end
        end
    end
    pause(0.001); % Sincronización acelerada
end