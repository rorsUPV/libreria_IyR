"""
iyr_SENSE_HAT.py
Módulo Wrapper Procedural para Raspberry Pi Sense HAT (I&R) con Modo Simulado Interactivo.
Proporciona funciones no orientadas a objetos con el prefijo iyr_ para eliminar
completamente las llamadas a objetos y el uso del operador punto (.).

Cuando no se dispone de hardware real ni emulador gráfico (fake == True):
- Las funciones de entrada (sensores, IMU, joystick) solicitan valores al usuario de forma interactiva por consola.
- Las funciones de salida estática (LED matrix) muestran visualmente la cuadrícula 8x8 con colores en consola.
- Las funciones de salida dinámica (show_message, show_letter) muestran una explicación detallada del comportamiento del hardware.

Versión para integrar en las bibliotecas IyR:
- Añade la función de inicialización iyr_inicia_sense_hat() para la inicialización

"""

import time
# Inicialización segura y multiplataforma del SenseHAT
fake = False 
_sense = None

def iyr_inicia_sense_hat():
    # Inicialización segura y multiplataforma del SenseHAT

    global fake  
    global _sense 

    try:
        from sense_hat import SenseHat
        _sense = SenseHat()
    except Exception:    
        try:
            from sense_emu import SenseHat
            _sense = SenseHat()
        except Exception:
            print("[iyr_SENSE_HAT] No se han encontrado sense_hat ni sense_emu.\n Empleando version simulada interactiva.\n")
            fake = True 


# ==============================================================================
# ESTRUCTURAS Y ESTADO VIRTUAL PARA MODO SIMULADO
# ==============================================================================
class VirtualStickEvent:
    def __init__(self, action="pressed", direction="middle"):
        self.action = action
        self.direction = direction
        self.timestamp = time.time()

    def __repr__(self):
        return f"InputEvent(action='{self.action}', direction='{self.direction}')"

# Estado interno de la matriz 8x8 (64 tuplas/listas RGB)
_virtual_matrix = [[0, 0, 0] for _ in range(64)]
_virtual_rotation = 0
_virtual_low_light = False
_virtual_imu_config = {"compass": True, "gyro": True, "accel": True}

# Mapeo de caracteres para letras comunes en 8x8
_LETTER_BITMAPS = {
    'U': [
        (1,1), (1,2), (1,3), (1,4), (1,5),
        (6,1), (6,2), (6,3), (6,4), (6,5),
        (2,6), (3,6), (4,6), (5,6)
    ],
    'D': [
        (2,1), (2,2), (2,3), (2,4), (2,5), (2,6),
        (3,1), (4,1), (5,2), (5,3), (5,4), (5,5), (4,6), (3,6)
    ],
    'L': [
        (2,1), (2,2), (2,3), (2,4), (2,5), (2,6),
        (3,6), (4,6), (5,6)
    ],
    'R': [
        (2,1), (2,2), (2,3), (2,4), (2,5), (2,6),
        (3,1), (4,1), (5,2), (4,3), (3,3),
        (4,4), (5,5), (5,6)
    ],
    'M': [
        (1,1), (1,2), (1,3), (1,4), (1,5), (1,6),
        (6,1), (6,2), (6,3), (6,4), (6,5), (6,6),
        (2,2), (3,3), (4,3), (5,2)
    ],
    '?': [
        (2,1), (3,1), (4,1), (5,2), (4,3), (3,4), (3,6)
    ]
}


def _get_color_info(r, g, b):
    """
    Determina la letra representativa y el nombre del color según valores RGB.
    Letras estándar:
      . = Apagado
      R = Rojo
      G = Verde
      B = Azul
      W = Blanco
      Y = Amarillo
      C = Cyan
      M = Magenta
      O = Naranja
      K = Gris
      X = Color personalizado
    """
    if r == 0 and g == 0 and b == 0:
        return ".", "Apagado (0,0,0)"
    
    # Escala de grises / blancos
    if r == g == b:
        if r >= 180:
            return "W", f"Blanco ({r},{g},{b})"
        elif r > 0:
            return "K", f"Gris ({r},{g},{b})"
    
    # Colores secundarios y compuestos
    if r > 180 and g > 180 and b < 80:
        return "Y", f"Amarillo ({r},{g},{b})"
    if r > 180 and b > 180 and g < 80:
        return "M", f"Magenta ({r},{g},{b})"
    if g > 180 and b > 180 and r < 80:
        return "C", f"Cyan ({r},{g},{b})"
    if r > 180 and 80 <= g <= 160 and b < 60:
        return "O", f"Naranja ({r},{g},{b})"
    
    # Colores primarios dominantes
    if r > g and r > b:
        return "R", f"Rojo ({r},{g},{b})"
    if g > r and g > b:
        return "G", f"Verde ({r},{g},{b})"
    if b > r and b > g:
        return "B", f"Azul ({r},{g},{b})"
    
    return "X", f"Color ({r},{g},{b})"


def _rgb_to_ansi(r, g, b):
    """Devuelve la letra del color formateada con códigos ANSI TrueColor o texto plano centrada en 3 caracteres."""
    char, _ = _get_color_info(r, g, b)
    if r == 0 and g == 0 and b == 0:
        return "\033[90m . \033[0m"  # Punto gris oscuro para apagado
    return f"\033[38;2;{r};{g};{b}m {char} \033[0m"


def _render_matrix():
    """Muestra en consola la matriz 8x8 con letras y colores en modo simulado."""
    print("\n" + "=" * 48)
    print(f"  [MATRIZ LED SENSE HAT 8x8] (Rotacion: {_virtual_rotation} deg)")
    print("=" * 48)
    print("     0  1  2  3  4  5  6  7   (X)")
    print("  +--------------------------+")
    
    active_colors = {}
    for y in range(8):
        row_str = f"{y} |"
        for x in range(8):
            # Aplicar rotacion a las coordenadas
            rx, ry = x, y
            if _virtual_rotation == 90:
                rx, ry = y, 7 - x
            elif _virtual_rotation == 180:
                rx, ry = 7 - x, 7 - y
            elif _virtual_rotation == 270:
                rx, ry = 7 - y, x

            pixel = _virtual_matrix[ry * 8 + rx]
            r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
            
            char, desc = _get_color_info(r, g, b)
            if char != ".":
                active_colors[char] = (r, g, b, desc)
                
            row_str += _rgb_to_ansi(r, g, b)
        row_str += " |"
        print(row_str)
    print("  +--------------------------+")
    
    # Leyenda dinámica de los colores presentes en la matriz
    legend_items = [". = Apagado"]
    for char, (r, g, b, desc) in sorted(active_colors.items()):
        colored_char = f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        legend_items.append(f"{colored_char} = {desc}")
    
    print("  Leyenda: " + " | ".join(legend_items))
    print("=" * 48 + "\n")


def _prompt_float(prompt_text, default_val):
    """Solicita un valor float interactivo con fallback por defecto."""
    try:
        user_input = input(f"{prompt_text} [Por defecto {default_val}]: ").strip()
        if not user_input:
            return float(default_val)
        return float(user_input)
    except (EOFError, ValueError):
        return float(default_val)


def _prompt_int(prompt_text, default_val):
    """Solicita un valor entero interactivo con fallback por defecto."""
    try:
        user_input = input(f"{prompt_text} [Por defecto {default_val}]: ").strip()
        if not user_input:
            return int(default_val)
        return int(user_input)
    except (EOFError, ValueError):
        return int(default_val)


# ==============================================================================
# WRAPPERS DE TIEMPO Y SISTEMA (Sin uso de operador punto)
# ==============================================================================
# Se supone ya definida en la librería principal
def iyr_sleep(seconds):
    #Pausa la ejecucion del programa durante N segundos.
    return time.sleep(seconds)


def iyr_time():
    """Devuelve la marca de tiempo actual en segundos."""
    return time.time()


# ==============================================================================
# WRAPPERS DE LA PANTALLA LED 8x8
# ==============================================================================
def iyr_rotation():
    global fake
    global _sense
    
    """Devuelve la rotacion actual de la pantalla LED."""
    if fake:  
        print(f"[SenseHAT - Salida] iyr_rotation() -> Rotacion actual: {_virtual_rotation} deg")
        return _virtual_rotation
    else:
        return _sense.rotation


def iyr_set_rotation(r, redraw=True):
    """Establece la rotacion de la pantalla (0, 90, 180, 270)."""
    global _virtual_rotation    
    global fake  
    global _sense 
    if fake:
        if r in (0, 90, 180, 270):
            _virtual_rotation = r
            print(f"[SenseHAT - Salida] iyr_set_rotation({r}) -> Rotacion actualizada a {r} deg")
            if redraw:
                _render_matrix()
        else:
            print(f"[SenseHAT - Advertencia] Rotacion {r} no valida. Debe ser 0, 90, 180 o 270.")
        return
    else:
        return _sense.set_rotation(r, redraw=redraw)


def iyr_flip_h(redraw=True):
    """Invierte horizontalmente la matriz de LEDs."""
    global _virtual_matrix
    global fake  
    global _sense 
    if fake:
        print("[SenseHAT - Salida] iyr_flip_h() -> Matriz invertida horizontalmente")
        for y in range(8):
            row = _virtual_matrix[y * 8 : (y + 1) * 8]
            _virtual_matrix[y * 8 : (y + 1) * 8] = row[::-1]
        if redraw:
            _render_matrix()
        return _virtual_matrix
    else:
        return _sense.flip_h(redraw=redraw)


def iyr_flip_v(redraw=True):
    """Invierte verticalmente la matriz de LEDs."""
    global _virtual_matrix
    global fake  
    global _sense 
    if fake:
        print("[SenseHAT - Salida] iyr_flip_v() -> Matriz invertida verticalmente")
        new_matrix = []
        for y in range(7, -1, -1):
            new_matrix.extend(_virtual_matrix[y * 8 : (y + 1) * 8])
        _virtual_matrix = new_matrix
        if redraw:
            _render_matrix()
        return _virtual_matrix
    else:
        return _sense.flip_v(redraw=redraw)


def iyr_set_pixels(pixel_list):
    """Establece la matriz completa de 64 pixeles y la renderiza."""
    global _virtual_matrix
    global fake  
    global _sense 
    if fake:
        if len(pixel_list) == 64:
            _virtual_matrix = [list(p) for p in pixel_list]
            print("[SenseHAT - Salida Estatica] iyr_set_pixels() -> Matriz actualizada con 64 pixeles:")
            _render_matrix()
        else:
            print(f"[SenseHAT - Error] iyr_set_pixels requiere 64 pixeles, recibidos: {len(pixel_list)}")
        return
    else:
        return _sense.set_pixels(pixel_list)


def iyr_get_pixels():
    """Devuelve la lista actual de 64 pixeles."""
    global fake  
    global _sense 
    if fake:
        return [list(p) for p in _virtual_matrix]
    else:
        return _sense.get_pixels()


def iyr_set_pixel(x, y, *args):
    """
    Establece el color de un pixel individual (x, y).
    Admite: iyr_set_pixel(x, y, r, g, b) o iyr_set_pixel(x, y, (r, g, b)) o iyr_set_pixel(x, y, [r, g, b]).
    """
    global fake  
    global _sense 
    global _virtual_matrix
    if fake:
        if len(args) == 1:
            color = list(args[0])
        elif len(args) == 3:
            color = [args[0], args[1], args[2]]
        else:
            color = [255, 255, 255]

        if 0 <= x < 8 and 0 <= y < 8:
            _virtual_matrix[y * 8 + x] = color
            print(f"[SenseHAT - Salida Estatica] iyr_set_pixel(x={x}, y={y}, color={color})")
            _render_matrix()
        else:
            print(f"[SenseHAT - Advertencia] Coordenadas fuera de rango (0-7): x={x}, y={y}")
        return
    else:
        return _sense.set_pixel(x, y, *args)


def iyr_get_pixel(x, y):
    """Obtiene el color del pixel en (x, y)."""
    global fake  
    global _sense 
    if fake:
        if 0 <= x < 8 and 0 <= y < 8:
            return _virtual_matrix[y * 8 + x]
        return [0, 0, 0]
    else:
        return _sense.get_pixel(x, y)


def iyr_load_image(file_path, redraw=True):
    """Carga una imagen de 8x8 en la matriz."""
    global fake  
    global _sense 
    global _virtual_matrix
    if fake:
        print(f"[SenseHAT - Salida Dinamica/Imagen] iyr_load_image('{file_path}')")
        print("-> En hardware real, se decodifica el archivo de imagen de 8x8 pixeles y se carga en los LEDs.")
        if redraw:
            _render_matrix()
        return _virtual_matrix
    else:
        return _sense.load_image(file_path, redraw=redraw)


def iyr_clear(*args):
    """
    Limpia la matriz LED con un color (por defecto apagado: 0, 0, 0).
    Admite: iyr_clear(), iyr_clear(r, g, b), iyr_clear((r, g, b)), iyr_clear([r, g, b]).
    """
    global _virtual_matrix
    global fake
    global _sense
    
    if fake:
        color = [0, 0, 0]
        if len(args) == 1:
            color = list(args[0])
        elif len(args) == 3:
            color = [args[0], args[1], args[2]]

        _virtual_matrix = [list(color) for _ in range(64)]
        print(f"[SenseHAT - Salida Estatica] iyr_clear(color={color}) -> Matriz LED limpiada.")
        _render_matrix()
        return
    else:
        return _sense.clear(*args)


def iyr_show_message(text_string, scroll_speed=0.1, text_colour=[255, 255, 255], back_colour=[0, 0, 0]):
    """Muestra una explicacion de la salida dinamica de texto deslizante en los LEDs."""
    global fake  
    global _sense 
    if fake:
        print("\n" + "=" * 65)
        print("  [SenseHAT - SALIDA DINAMICA: MENSAJE DESLIZANTE / SCROLL]")
        print("=" * 65)
        print(f"  * Texto a mostrar      : \"{text_string}\"")
        print(f"  * Color del texto (RGB): {text_colour}")
        print(f"  * Color de fondo (RGB) : {back_colour}")
        print(f"  * Velocidad de scroll  : {scroll_speed} s/caracter")
        print("-" * 65)
        print("  Explicacion:")
        print("  En la Sense HAT real, la pantalla LED 8x8 muestra el mensaje")
        print("  desplazando los caracteres suavemente de derecha a izquierda.")
        print(f"  Duracion estimada del desplazamiento: ~{round(len(str(text_string)) * 8 * scroll_speed, 2)} segundos.")
        print("=" * 65 + "\n")
        return
    else:
        return _sense.show_message(text_string, scroll_speed=scroll_speed, text_colour=text_colour, back_colour=back_colour)


def iyr_show_letter(s, text_colour=[255, 255, 255], back_colour=[0, 0, 0]):
    """Muestra una letra o caracter en la matriz LED."""
    global fake  
    global _sense 
    global _virtual_matrix
    if fake:
        char = str(s)[0] if len(str(s)) > 0 else ' '
        print("\n" + "=" * 65)
        print(f"  [SenseHAT - SALIDA ESTATICA / CARACTER: '{char}']")
        print("=" * 65)
        print(f"  * Caracter             : '{char}'")
        print(f"  * Color de letra (RGB) : {text_colour}")
        print(f"  * Color de fondo (RGB) : {back_colour}")
        print("-" * 65)
        print(f"  En la Sense HAT real, se renderiza la fuente tipografica del")
        print(f"  caracter '{char}' fija sobre la matriz de 8x8 LEDs.")

        # Si tenemos bitmap de la letra, actualizamos y mostramos la matriz
        _virtual_matrix = [list(back_colour) for _ in range(64)]
        if char.upper() in _LETTER_BITMAPS:
            for (lx, ly) in _LETTER_BITMAPS[char.upper()]:
                _virtual_matrix[ly * 8 + lx] = list(text_colour)
        _render_matrix()
        return
    else:
        return _sense.show_letter(s, text_colour=text_colour, back_colour=back_colour)


def iyr_gamma():
    """Devuelve la tabla gamma actual."""
    global fake  
    global _sense 
    if fake:
        print("[SenseHAT] iyr_gamma() -> Retornando tabla gamma estandar de 32 niveles")
        return list(range(32))
    else:
        return _sense.gamma


def iyr_gamma_reset():
    """Restablece la tabla gamma a los valores predeterminados."""
    global fake  
    global _sense 
    if fake:
        print("[SenseHAT] iyr_gamma_reset() -> Tabla gamma restablecida a valores por defecto")
        return
    else:
        return _sense.gamma_reset()


def iyr_low_light():
    """Devuelve el estado del modo de baja luminosidad."""
    global fake  
    global _sense 
    if fake:
        return _virtual_low_light
    else:
        return getattr(_sense, 'low_light', False)


def iyr_set_low_light(value):
    """Activa o desactiva el modo de baja luminosidad."""
    global fake  
    global _sense 
    global _virtual_low_light
    if fake:
        _virtual_low_light = bool(value)
        print(f"[SenseHAT - Salida] Modo baja luminosidad (low_light) establecido en: {_virtual_low_light}")
        return
    else:
        setattr(_sense, 'low_light', value)


def iyr_get_low_light():
    """Devuelve el estado del modo de baja luminosidad."""
    global fake  
    global _sense 
    return iyr_low_light()


# ==============================================================================
# WRAPPERS DE SENSORES AMBIENTALES
# ==============================================================================
def iyr_get_humidity(*args, **kwargs):
    """Obtiene la humedad relativa (0 - 100%)."""
    global fake  
    global _sense 
    if fake:
        val = _prompt_float("[SenseHAT Entrada - Sensor Humedad] Introduce porcentaje de humedad (0-100%)", 45.0)
        print(f"-> Humedad leida: {val:.1f} %")
        return val
    else:
        return _sense.get_humidity(*args, **kwargs)


def iyr_get_temperature_from_humidity(*args, **kwargs):
    """Obtiene la temperatura en oC a partir del sensor de humedad."""
    global fake  
    global _sense 
    if fake:
        val = _prompt_float("[SenseHAT Entrada - Sensor Temperatura (HTS221)] Introduce temperatura en oC", 21.5)
        print(f"-> Temperatura (humedad) leida: {val:.1f} oC")
        return val
    else:
        return _sense.get_temperature_from_humidity(*args, **kwargs)


def iyr_get_temperature_from_pressure(*args, **kwargs):
    """Obtiene la temperatura en oC a partir del sensor de presion."""
    global fake  
    global _sense 
    if fake:
        val = _prompt_float("[SenseHAT Entrada - Sensor Temperatura (LPS25H)] Introduce temperatura en oC", 21.5)
        print(f"-> Temperatura (presion) leida: {val:.1f} oC")
        return val
    else:
        return _sense.get_temperature_from_pressure(*args, **kwargs)


def iyr_get_temperature(*args, **kwargs):
    """Obtiene la temperatura ambiente actual en oC."""
    global fake  
    global _sense 
    if fake:
        val = _prompt_float("[SenseHAT Entrada - Sensor Temperatura] Introduce temperatura en oC", 22.0)
        print(f"-> Temperatura leida: {val:.1f} oC")
        return val
    else:
        return _sense.get_temperature(*args, **kwargs)


def iyr_get_pressure(*args, **kwargs):
    """Obtiene la presion barometrica actual en milibares/hPa."""
    global fake  
    global _sense 
    if fake:
        val = _prompt_float("[SenseHAT Entrada - Sensor Presion] Introduce presion en mbar/hPa", 1013.25)
        print(f"-> Presion leida: {val:.1f} mbar")
        return val
    else:
        return _sense.get_pressure(*args, **kwargs)


# ==============================================================================
# WRAPPERS DE SENSORES DE MOVIMIENTO E INERCIA (IMU)
# ==============================================================================
def iyr_set_imu_config(compass_enabled, gyro_enabled, accel_enabled):
    """Habilita o deshabilita los sensores de la IMU."""
    global fake  
    global _sense 
    global _virtual_imu_config
    if fake:
        _virtual_imu_config = {
            "compass": bool(compass_enabled),
            "gyro": bool(gyro_enabled),
            "accel": bool(accel_enabled)
        }
        print(f"[SenseHAT IMU] Configuracion IMU actualizada -> Brujula: {compass_enabled}, Giroscopio: {gyro_enabled}, Acelerometro: {accel_enabled}")
        return
    else:
        return _sense.set_imu_config(compass_enabled, gyro_enabled, accel_enabled)


def iyr_get_orientation_degrees(*args, **kwargs):
    """Obtiene la orientacion (pitch, roll, yaw) en grados (0 - 360)."""
    global fake  
    global _sense 
    if fake:
        print("\n[SenseHAT Entrada - IMU Orientacion (Grados)]")
        try:
            raw = input("Introduce pitch, roll, yaw separados por comas [Por defecto: 0.0, 0.0, 0.0]: ").strip()
            if raw:
                parts = [float(x.strip()) for x in raw.split(",")]
                pitch = parts[0] if len(parts) > 0 else 0.0
                roll = parts[1] if len(parts) > 1 else 0.0
                yaw = parts[2] if len(parts) > 2 else 0.0
            else:
                pitch, roll, yaw = 0.0, 0.0, 0.0
        except (EOFError, Exception):
            pitch, roll, yaw = 0.0, 0.0, 0.0

        res = {"pitch": pitch, "roll": roll, "yaw": yaw}
        print(f"-> Orientacion: Elevacion(pitch)={pitch:.2f} deg, Alabeo(roll)={roll:.2f} deg, Rumbo(yaw)={yaw:.2f} deg")
        return res
    else:
        return _sense.get_orientation_degrees(*args, **kwargs)


def iyr_get_orientation(*args, **kwargs):
    """Alias de get_orientation_degrees."""
    return iyr_get_orientation_degrees(*args, **kwargs)


def iyr_get_compass(*args, **kwargs):
    """Obtiene la direccion de la brujula en grados respecto al norte magnetico."""
    global fake  
    global _sense 
    if fake:
        val = _prompt_float("[SenseHAT Entrada - Brujula] Introduce angulo de brujula en grados (0-360 deg)", 0.0)
        print(f"-> Brujula: {val:.2f} deg")
        return val
    else:
        return _sense.get_compass(*args, **kwargs)


def iyr_get_compass_raw(*args, **kwargs):
    """Obtiene los valores brutos del magnetometro (ejes x, y, z en microteslas)."""
    global fake  
    global _sense 
    if fake:
        print("\n[SenseHAT Entrada - Magnetometro Raw (uT)]")
        try:
            raw = input("Introduce x, y, z separados por comas [Por defecto: 0.0, 0.0, 0.0]: ").strip()
            if raw:
                parts = [float(p.strip()) for p in raw.split(",")]
                x = parts[0] if len(parts) > 0 else 0.0
                y = parts[1] if len(parts) > 1 else 0.0
                z = parts[2] if len(parts) > 2 else 0.0
            else:
                x, y, z = 0.0, 0.0, 0.0
        except (EOFError, Exception):
            x, y, z = 0.0, 0.0, 0.0
        return {"x": x, "y": y, "z": z}
    else:
        return _sense.get_compass_raw(*args, **kwargs)


def iyr_get_gyroscope(*args, **kwargs):
    """Obtiene la orientacion estimada por el giroscopio (pitch, roll, yaw en grados)."""
    global fake  
    global _sense 
    if fake:
        return iyr_get_orientation_degrees(*args, **kwargs)
    else:
        return _sense.get_gyroscope(*args, **kwargs)


def iyr_get_gyroscope_raw(*args, **kwargs):
    """Obtiene los valores brutos del giroscopio (ejes x, y, z en radianes/s)."""
    global fake  
    global _sense 
    if fake:
        print("\n[SenseHAT Entrada - Giroscopio Raw (rad/s)]")
        try:
            raw = input("Introduce x, y, z separados por comas [Por defecto: 0.0, 0.0, 0.0]: ").strip()
            if raw:
                parts = [float(p.strip()) for p in raw.split(",")]
                x = parts[0] if len(parts) > 0 else 0.0
                y = parts[1] if len(parts) > 1 else 0.0
                z = parts[2] if len(parts) > 2 else 0.0
            else:
                x, y, z = 0.0, 0.0, 0.0
        except (EOFError, Exception):
            x, y, z = 0.0, 0.0, 0.0
        return {"x": x, "y": y, "z": z}
    else:
        return _sense.get_gyroscope_raw(*args, **kwargs)


def iyr_get_accelerometer(*args, **kwargs):
    """Obtiene la orientacion estimada por el acelerometro (pitch, roll, yaw en grados)."""
    global fake  
    global _sense 
    if fake:
        return iyr_get_orientation_degrees(*args, **kwargs)
    else:
        return _sense.get_accelerometer(*args, **kwargs)


def iyr_get_accelerometer_raw(*args, **kwargs):
    """Obtiene los valores brutos del acelerometro (ejes x, y, z en Gs)."""
    global fake  
    global _sense 
    if fake:
        print("\n[SenseHAT Entrada - Acelerometro Raw (G)]")
        try:
            raw = input("Introduce x, y, z separados por comas [Por defecto: 0.0, 0.0, 1.0]: ").strip()
            if raw:
                parts = [float(p.strip()) for p in raw.split(",")]
                x = parts[0] if len(parts) > 0 else 0.0
                y = parts[1] if len(parts) > 1 else 0.0
                z = parts[2] if len(parts) > 2 else 1.0
            else:
                x, y, z = 0.0, 0.0, 1.0
        except (EOFError, Exception):
            x, y, z = 0.0, 0.0, 1.0
        return {"x": x, "y": y, "z": z}
    else:
        return _sense.get_accelerometer_raw(*args, **kwargs)


# ==============================================================================
# WRAPPERS DEL JOYSTICK
# ==============================================================================
def iyr_get_stick_events():
    """
    Devuelve la lista de eventos pendientes del joystick.
    En modo simulado pregunta si se desea introducir un movimiento de joystick.
    """
    global fake  
    global _sense 
    if fake:
        try:
            print("\n[SenseHAT Entrada - Joystick]")
            print("  Opciones rapidas:")
            print("    u: up (arriba)    | d: down (abajo) | l: left (izquierda)")
            print("    r: right (derecha)| m: middle (pulsacion central)")
            print("    (o presiona Intro directamente para no enviar ningun movimiento)")
            user_input = input("  Introduce direccion o evento: ").strip().lower()

            if not user_input:
                return []

            shortcuts = {
                'u': ('pressed', 'up'),
                'd': ('pressed', 'down'),
                'l': ('pressed', 'left'),
                'r': ('pressed', 'right'),
                'm': ('pressed', 'middle'),
                'up': ('pressed', 'up'),
                'down': ('pressed', 'down'),
                'left': ('pressed', 'left'),
                'right': ('pressed', 'right'),
                'middle': ('pressed', 'middle'),
            }

            parts = user_input.split()
            if len(parts) == 1:
                action, direction = shortcuts.get(parts[0], ('pressed', parts[0]))
            elif len(parts) >= 2:
                if parts[0] in ('pressed', 'released', 'held'):
                    action, direction = parts[0], parts[1]
                else:
                    direction, action = parts[0], parts[1]
            else:
                action, direction = 'pressed', 'middle'

            event = VirtualStickEvent(action=action, direction=direction)
            print(f"-> Evento simulado generado: {event}")
            return [event]
        except (EOFError, KeyboardInterrupt):
            return []
    else:
        if hasattr(_sense, 'stick') and hasattr(_sense.stick, 'get_events'):
            return _sense.stick.get_events()
        return []


def iyr_get_event_action(event):
    """Devuelve la accion del evento (ej. 'pressed', 'released', 'held')."""
    return getattr(event, 'action', str(event))


def iyr_get_event_direction(event):
    """Devuelve la direccion del evento (ej. 'up', 'down', 'left', 'right', 'middle')."""
    return getattr(event, 'direction', str(event))


# ==============================================================================
# GETTERS INDIVIDUALES PARA EVITAR USO DE DICCIONARIOS Y METODOS DE OBJETO
# ==============================================================================
def iyr_get_pitch():
    orient = iyr_get_orientation_degrees()
    return orient.get('pitch', 0) if isinstance(orient, dict) else 0


def iyr_get_roll():
    orient = iyr_get_orientation_degrees()
    return orient.get('roll', 0) if isinstance(orient, dict) else 0


def iyr_get_yaw():
    orient = iyr_get_orientation_degrees()
    return orient.get('yaw', 0) if isinstance(orient, dict) else 0


def iyr_get_accel_pitch():
    acc = iyr_get_accelerometer()
    return acc.get('pitch', 0) if isinstance(acc, dict) else 0


def iyr_get_accel_roll():
    acc = iyr_get_accelerometer()
    return acc.get('roll', 0) if isinstance(acc, dict) else 0


def iyr_get_accel_yaw():
    acc = iyr_get_accelerometer()
    return acc.get('yaw', 0) if isinstance(acc, dict) else 0


def iyr_get_gyro_pitch():
    gyro = iyr_get_gyroscope()
    return gyro.get('pitch', 0) if isinstance(gyro, dict) else 0


def iyr_get_gyro_roll():
    gyro = iyr_get_gyroscope()
    return gyro.get('roll', 0) if isinstance(gyro, dict) else 0


def iyr_get_gyro_yaw():
    gyro = iyr_get_gyroscope()
    return gyro.get('yaw', 0) if isinstance(gyro, dict) else 0


def iyr_get_accel_x():
    accel = iyr_get_accelerometer_raw()
    return accel.get('x', 0) if isinstance(accel, dict) else 0


def iyr_get_accel_y():
    accel = iyr_get_accelerometer_raw()
    return accel.get('y', 0) if isinstance(accel, dict) else 0


def iyr_get_accel_z():
    accel = iyr_get_accelerometer_raw()
    return accel.get('z', 0) if isinstance(accel, dict) else 0


def iyr_get_gyro_x():
    gyro = iyr_get_gyroscope_raw()
    return gyro.get('x', 0) if isinstance(gyro, dict) else 0


def iyr_get_gyro_y():
    gyro = iyr_get_gyroscope_raw()
    return gyro.get('y', 0) if isinstance(gyro, dict) else 0


def iyr_get_gyro_z():
    gyro = iyr_get_gyroscope_raw()
    return gyro.get('z', 0) if isinstance(gyro, dict) else 0


def iyr_get_compass_x():
    comp = iyr_get_compass_raw()
    return comp.get('x', 0) if isinstance(comp, dict) else 0


def iyr_get_compass_y():
    comp = iyr_get_compass_raw()
    return comp.get('y', 0) if isinstance(comp, dict) else 0


def iyr_get_compass_z():
    comp = iyr_get_compass_raw()
    return comp.get('z', 0) if isinstance(comp, dict) else 0
