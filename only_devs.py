with open("modular_lnk.b64", "r", encoding="utf-8") as read_:

    # Leemos todas las líneas del archivo
    file_all = read_.readlines()

    # Posibles firmas que representan el inicio del payload (comillas de apertura en base64)
    bytes_prev_pos = ["ACAAIgAg", "ACIAIA"]
    
    # Fragmentos que forman parte del bloque de padding en base64 (varias formas de '====')
    sing_ = ["AD0", "APQ", "A9"]

    # Lista temporal para almacenar las posiciones donde aparece cada fragmento en el texto
    to_num = []
    
    sum = 0

    # Obtenemos la posición de aparición de cada fragmento en el texto base64
    for ele in sing_:
        to_num.append(file_all[0].index(ele))
    
    # Determinamos cuál aparece primero (el de menor índice)
    trunc_ = min(to_num)

    # Extraemos 8 caracteres desde la posición del fragmento más cercano al inicio
    target_ = file_all[0][trunc_:trunc_+8]

    # Contamos cuántas veces se repite esa secuencia completa
    count_target = file_all[0].count(target_)
    
    # Dividimos el texto en dos partes, antes y después del bloque de padding repetido
    two_list_b64 = file_all[0].split(target_ * count_target)

    # Obtenemos los últimos 19 caracteres antes del bloque de padding (zona de apertura del payload)
    bytes_prev = two_list_b64[0][-19:]

    # Buscamos cuál de las firmas conocidas está presente en esa zona
    for elem in bytes_prev_pos:
        if elem in bytes_prev:
            bytes_prev = elem
            break
    
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
    
    # Ordenamos los fragmentos según su posición
    previus_order_chain.sort()
    str_previus = ""

    # Unimos los fragmentos en una sola cadena
    for elem in previus_order_chain:
        str_previus = str_previus + elem[0]

    # Mostramos los resultados del análisis
    print(f"""
Inicio de carga de payload: {bytes_prev}
Cadena de bytes vacíos: {target_} x {count_target}
Previa final de carga: {str_previus}
Final de carga de payload: {bytes_next}
""")
   
    # Contamos cuántas veces aparece cada tipo de fragmento
    for elem in sing_:
        print(file_all[0].count(elem), elem)
        sum = sum + file_all[0].count(elem)
    
    print("Total de caracteres permitidos en UTF-8: ", sum)

    # Reconstruimos el payload para su verificación o análisis
    total_str = bytes_prev + target_ * count_target + str_previus + bytes_next
    print(total_str)

    # Verificamos si el payload reconstruido existe en el texto base64
    if total_str in file_all[0]:
        print("[INFO] Formato correcto =>> [OK]")
