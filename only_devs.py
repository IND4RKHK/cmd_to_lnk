import base64

json_lines = {

    "normal": 0,
    "minimal": 1,

    "normal-icon": 2,
    "minimal-icon" :3

}

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
        
        print(f"[ALERT] LNK file switched to {my_lnk_edit.upper()} =>> [OK]")

        my_lnk = json_lines[my_lnk_edit]
        my_new_lnk = input(f"{my_lnk_edit}_new_file_path >> ")

        break

except Exception as err:
    print(f"[ERROR] {err}")
    exit(0)

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
        exit(0)

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
        exit(0)

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
        exit(0)

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