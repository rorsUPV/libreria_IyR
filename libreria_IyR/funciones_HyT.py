# funciones_HyT.py

import threading
import time
from datetime import datetime

################## DECLARACION VARIABLES GLOBALES #####################

_tiempo_vencimiento = 0.0 # Variable global para el temporizador

################## FUNCIONES MANEJO HILOS  #####################

def lanzaHilo(nombre_funcion):
    hilo = threading.Thread(target=nombre_funcion)
    hilo.start()

################## FUNCIONES MANEJO TEMPORIZADORES #####################
    
def arrancar_TimeOut(segundos):
    """Registra el momento exacto del futuro en el que vencerá el tiempo."""
    global _tiempo_vencimiento
    tiempo_actual = time.time()  # Segundos actuales desde 1970 [1]
    _tiempo_vencimiento = tiempo_actual + segundos
    print(f"[Timer] Arrancado por {segundos} segundos.")

def TimeOut_vencido():
    """Retorna True si el tiempo actual ya superó el vencimiento, False si no."""
    global _tiempo_vencimiento
    tiempo_actual = time.time()
    if tiempo_actual >= _tiempo_vencimiento:
        return True
    else:
        return False

def sleep(tiempo):
    time.sleep(tiempo)

################## FUNCIONES MANEJO FECHA Y HORA #####################

def fecha():
    ahora = datetime.now()
    anyo = ahora.year
    mes = ahora.month
    dia = ahora.day
    fecha = (dia, mes, anyo)
    return fecha

def hora():
    ahora = datetime.now()
    hora = ahora.hour
    minutos = ahora.minute
    segundos = ahora.second
    tiempo = (hora, minutos, segundos)
    return tiempo
