# funciones_hat.py

################### VARIABLES GLOBALES ####################################

_hat = None
_modo_real = False

################### PUESTA EN MARCHA ####################################

def activar_SenseHat():
    try:
        # IMPORTANTE: Importamos el módulo completo aquí dentro
        import sense_hat
        _hat = sense_hat.SenseHat()
        _modo_real = True
    except (ImportError, RuntimeError):
        _hat = None
        _modo_real = False
        return("\n[AVISO IyR]: Modo simulación activado (No se detectó el módulo Sense HAT).\n")

################### FUNCIONES SALIDA DIGITAL ####################################

def iyr_set_rotation(angulo):
    if _modo_real and _hat:
        _hat.set_rotation(angulo)
    else:
        return("[PANTALLA LED SIMULADA]: Rotacion de "+str(angulo)+" Grados")

def iyr_set_pixels(lista):
    if _modo_real and _hat:
        _hat.set_pixels(lista)
    else:
        return("[PANTALLA LED SIMULADA]: recibida lista de pixels")

def iyr_get_pixels():
    if _modo_real and _hat:
        return _hat.get_pixels()
    else:
        return("[PANTALLA LED SIMULADA]: retorna la lista de pixels")

def iyr_set_pixel(c_X, c_Y, color):
    if _modo_real and _hat:
        _hat.set_pixel(c_X, c_Y, color)
    else:
        return("[PANTALLA LED SIMULADA]: colocado el pixel: ("+str(c_X)+','+str(c_Y)+') al color: '+color)

def iyr_get_pixel(c_X, c_Y):
    if _modo_real and _hat:
        return _hat.get_pixel(c_X, c_Y)
    else:
        return("[PANTALLA LED SIMULADA]: retrna el color del pixel: ("+str(c_X)+','+str(c_Y)+')')

def iyr_clear(r, g, b):
    if _modo_real and _hat:
        _hat.clear(r, g, b)
    else:
        return(f"[FONDO SIMULADO]: Color R={r}, G={g}, B={b}")

def iyr_show_message(texto):
    if _modo_real and _hat:
        _hat.show_message(texto)
    else:
        return(f"[PANTALLA LED SIMULADA]: {texto}")

def iyr_show_letter(letra, clor_L, color_F):
    if _modo_real and _hat:
        _hat.show_letter(letra, clor_L, color_F)
    else:
        return(f"[PANTALLA LED SIMULADA]: {letra}")
        
################### FUNCIONES ENTRADA DIGITAL ####################################
        
def iyr_get_events():
    if _modo_real and _hat:
        return _hat.get_events()
    else:
        return("[PANTALLA LED SIMULADA]: retorna el evento sucedido")

def iyr_wait_for_event(buffer):
    if _modo_real and _hat:
        return _hat.wait_for_event(buffer)
    else:
        return("[PANTALLA LED SIMULADA]: retorna el evento sucedido")
        

################### FUNCIONES SALIDA ANALOGICA ####################################
        
################### FUNCIONES ENTRADA ANALOGICA ###################################

def iyr_get_pressure():
    if _modo_real and _hat:
        return _hat.get_pressure()
    else:
        return("[PANTALLA LED SIMULADA]: retorna la presión")
        
def iyr_get_humidity():
    if _modo_real and _hat:
        return _hat.get_humidity()
    else:
        return("[PANTALLA LED SIMULADA]: retorna la humedad relativa")
        
def iyr_get_temperature():
    if _modo_real and _hat:
        return _hat.get_humidity()
    else:
        return("[PANTALLA LED SIMULADA]: retorna la temperatura")

def iyr_set_imu_config(compass, gyro, accel ):
    if _modo_real and _hat:
        _hat.set_imu_config(compass, gyro, accel )
    else:
        return("[PANTALLA LED SIMULADA]: activa la configuracion del imu")

def iyr_get_orientation_degrees():
    if _modo_real and _hat:
        return _hat.get_orientation_degrees()
    else:
        return("[PANTALLA LED SIMULADA]: retorna la orientación")

def iyr_get_compass():
    if _modo_real and _hat:
        return _hat.get_compass()
    else:
        return ("[PANTALLA LED SIMULADA]: retorna los grados de desviación Norte")

