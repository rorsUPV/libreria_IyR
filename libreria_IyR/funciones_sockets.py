# funciones_sockets.py

import ipaddress
import threading
import time

try:
    from socket import *
except (ImportError, RuntimeError):
    print("\n[AVISO IyR]: No se pudo importtar la clase socket.\n")

################## DECLARACION VARIABLES GLOBALES #####################

sockets_locales = {}  # diccionario donde almacenar los sockets locales
_tiempo_vencimiento = 0.0 # Variable global para el temporizador

################## FUNCIONES MANEJO HILOS y TEMPORIZADORES #####################

def lanzaHilo(nombre_funcion):
    hilo = threading.Thread(target=nombre_funcion)
    hilo.start()


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
    
################## FUNCIONES MANEJO IPs #####################
    
def resolverIPporDominio(Dominio):
    try:
        ip_Dominio = socket.gethostbyname(Dominio)
        return (True,ip_Dominio)
    except socket.error:
        return (False, '')

def obtener_IP_Local():
    try:
        ip_local = socket.gethostbyname(socket.gethostname())
        return (True,ip_local)
    except socket.error:
        return (False, 'localhost')

################## FUNCIONES MANEJO cadenas bytes #####################
    
def encode(texto):
    return texto.encode()

def decode(cadena):
    return cadena.decode()

################## FUNCIONES MANEJO UDP #####################
    
def crear_socket_udp(ip=None, puerto=None, bloqueante=True):
    """
    Crea un socket UDP.
    - ip/puerto: Si se pasan, actúa como servidor haciendo bind(). Si no, como cliente.
    - bloqueante: True (por defecto) para modo bloqueante, False para modo no bloqueante.
    """
    # 1. Crear el socket UDP base
    socketUDP = socket(AF_INET, SOCK_DGRAM)
    # 2. Configurar el bloqueo según el parámetro
    socketUDP.setblocking(bloqueante)
    # Mensaje informativo del modo de operación
    modo = "BLOQUEANTE" if bloqueante else "NO BLOQUEANTE"    
    # 3. Decidir comportamiento (Servidor vs Cliente)
    if ip is not None and puerto is not None:
        socketUDP.bind((ip, puerto))
    parametros = socketUDP.getsockname()
    ip = parametros[0]
    puerto = parametros[1]
    sockets_locales[puerto] = socketUDP
    print('Creado socket UDP '+modo+' en '+ip+':'+str(puerto))
    return (ip, puerto)

def verificar_recepcion_udp(puerto):
    """
    Retorna False si no hay datos en el búfer de red.
    Retorna True inmediatamente en cuanto llega un datagrama.
    """
    try:
        # Intenta leer del socket inmediatamente
        datos, direccion = sockets_locales[puerto].recvfrom(1024)
        ultimo_mensaje = datos.decode()
        return (True, datos, direccion)  # Se recibió un datagrama con éxito
    except BlockingIOError:
        # Excepción que lanza Python cuando el socket está vacío en modo no bloqueante
        return (False, '', '')
 
def obtener_parametros_socket(puerto):
    parametros = sockets_locales[puerto].getsockname()
    return parametros
    
def sendto(puerto, mensaje, socket_destino):
    sockets_locales[puerto].sendto(mensaje, socket_destino)

def receivefrom(puerto, long_buffer):
    return sockets_locales[puerto].recvfrom(long_buffer)

def close(puerto):
    sockets_locales[puerto].close()

################## FUNCIONES MANEJO TCP #####################
    
def crear_socket_acogida(parametros_socket_servidor, max_conexiones):
    socket_servidorTCP = socket(AF_INET, SOCK_STREAM)
    socket_servidorTCP.bind((parametros_socket_servidor))
    socket_servidorTCP.listen(max_conexiones)
    ip_acogida = parametros_socket_servidor[0]
    puerto_acogida = parametros_socket_servidor[1]
    socket_acogida = (ip_acogida, puerto_acogida)
    sockets_locales[puerto_acogida] = socket_servidorTCP
    return socket_acogida

def aceptar_conexiones(socket_acogida):
    ip_acogida = socket_acogida[0]
    puerto_acogida = socket_acogida[1]
    socket_conectado_lado_servidor, direccion_cliente = sockets_locales[puerto_acogida].accept()
    ip_cliente = direccion_cliente[0]
    puerto_cliente = direccion_cliente[1]
    ip_servidor, puerto_servicio = socket_conectado_lado_servidor.getsockname()
    sockets_locales[puerto_servicio] = socket_conectado_lado_servidor
    conexion = (ip_servidor, puerto_servicio, ip_cliente, puerto_cliente)
    return conexion

def conectar_socket_cliente(parametros_socket_servidor):
    socket_conectado_lado_cliente = socket(AF_INET, SOCK_STREAM)
    socket_conectado_lado_cliente.connect(parametros_socket_servidor)
    ip_cliente, puerto_cliente = socket_conectado_lado_cliente.getsockname()
    sockets_locales[puerto_cliente] = socket_conectado_lado_cliente
    ip_servidor, puerto_servidor = socket_conectado_lado_cliente.getpeername()
    conexion = (ip_cliente, puerto_cliente, ip_servidor, puerto_servidor)
    return conexion
    
def send(conexion, mensaje):
    puerto_socket = conexion[1]
    sockets_locales[puerto_socket].send(mensaje)

def recv(conexion, long_buffer):
    puerto_socket = conexion[1]
    return sockets_locales[puerto_socket].recv(long_buffer)
