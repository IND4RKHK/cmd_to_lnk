## 📄 Documentación Técnica — `lnkforge.py`

### 📌 Descripción General
Este script permite generar archivos `.lnk` (accesos directos de Windows) que contienen comandos embebidos de PowerShell. El payload se codifica en Base64 utilizando UTF-16BE, respetando los límites de tamaño del archivo `.lnk` generado, e insertándolo en un archivo base modificado (`modular_lnk.txt`). Se soporta un modo "minimal" para que la consola se ejecute minimizada.

---

### ⚙️ Requisitos Previos

- Python 3.x
- Archivo `modular_lnk.txt` con accesos directos codificados en Base64, en dos líneas:
  - Línea 0: LNK normal (ventana visible)
  - Línea 1: LNK minimal (ventana minimizada)

---

### 🔧 Variables Principales

| Variable | Tipo | Descripción |
|---------|------|-------------|
| `b64_extra_bytes` | `str` | Cadena de relleno en Base64 que se reemplaza por el código embebido. Aumenta el espacio en memoria del `.lnk`. |
| `max_bytes` | `int` | Límite en bytes del código embebido, basado en la longitud de `b64_extra_bytes`. |
| `buffer_` | `str` | Acumulador de comandos ingresados por el usuario. |
| `minimal_` | `bool` | Flag que define si el `.lnk` se debe ejecutar en modo minimizado. |
| `json_lines` | `dict` | Diccionario que mapea el modo de ejecución (`normal`, `minimal`) a líneas del archivo base. |

---

### 🧠 Lógica Interna

#### 1. **Ingreso de Comandos**

- El script entra en un bucle interactivo (`while True`) donde el usuario escribe comandos.
- Si se ingresa `minimal`, se activa la ejecución minimizada.
- Los comandos se concatenan en `buffer_` y se valida que su codificación en Base64 no exceda `max_bytes`.

#### 2. **Validación de Tamaño**

- Se utiliza la función `check_len_or_save()` para:
  - Obtener la longitud del comando en Base64 (`check_ = True`)
  - Codificar el payload final (`check_ = False`)

#### 3. **Construcción del LNK**

- Se abre `modular_lnk.txt`, se selecciona la línea adecuada (`normal` o `minimal`).
- Se reemplaza `b64_extra_bytes` por el contenido codificado (`code_`).
- Se ajustan los caracteres de padding (`=`) para cumplir con la codificación Base64 válida.
- Finalmente, se guarda el resultado como `command_py.lnk`.

---

### 🧪 Ejemplo de Uso

```bash
$ python cmd_to_lnk.py
:: LNKFORGE :: =>> [INFO]
:: Todo lo que escribas a continuacion quedara guardado como acceso directo ::
...

cmd_lnk_executor >> systeminfo
cmd_lnk_executor >> ipconfig
cmd_lnk_executor >> minimal
cmd_lnk_executor >> whoami
cmd_lnk_executor >> exit
```

> Resultado: Se guarda un `.lnk` llamado `command_py.lnk` que ejecuta `systeminfo; ipconfig; whoami;` con la ventana de PowerShell minimizada.

---

### ⚠️ Consideraciones de Seguridad

- Este script puede ser utilizado con fines ofensivos (ej. persistencia en sistemas Windows), por lo que se recomienda su uso en entornos controlados y con fines educativos o de auditoría (hacking ético).
- Los `.lnk` generados están “corrompidos” en estructura pero siguen siendo funcionales.

---

### 🧼 Tips adicionales

- Se recomienda limpiar el Base64 del `.lnk` de saltos de línea antes de usarlo como plantilla (`https://pinetools.com/es/eliminar-saltos-linea`).
- Puedes experimentar con cadenas más largas reemplazando `b64_extra_bytes` para expandir el tamaño del payload permitido.
