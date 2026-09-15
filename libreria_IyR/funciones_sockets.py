# funciones_sockets.py

import ipaddress
import threading
import time
import socket
import urllib.request
import ssl

################## DECLARACION VARIABLES GLOBALES #####################

sockets_locales = {}  # diccionario donde almacenar los sockets locales
    
################## FUNCIONES MANEJO IPs #####################
    
def resolverIPporDominio(Dominio):
    try:
        ip_Dominio = socket.gethostbyname(Dominio)
        return (True,ip_Dominio)
    except socket.error:
        return (False, '')

def obtener_IP_Local():
    # Creamos un socket UDP temporal
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No necesita conectarse realmente, solo simula una salida hacia internet
        # para que el sistema operativo le asigne la IP de la interfaz de red activa
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        ip_publica = (True, ip)
    except Exception:
        # Si no hay internet en absoluto, recurrimos al localhost
        ip = '127.0.0.1'
        ip_publica = (False, ip)
    finally:
        s.close()
    return ip_publica

def obtener_IP_Publica():
    try:
        contexto_seguro = ssl._create_unverified_context()
        # Intentamos conectar con ipify que es muy estable
        with urllib.request.urlopen('https://api.ipify.org', context=contexto_seguro, timeout=5) as respuesta:
            ip = respuesta.read().decode('utf-8').strip()
            return (True, ip)
    except Exception as e:
        # Aquí capturamos el error real y devolvemos qué lo causó
        return (False, '')


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
    
def iyr_sendto(puerto, mensaje, socket_destino):
    sockets_locales[puerto].sendto(mensaje, socket_destino)

def iyr_receivefrom(puerto, long_buffer):
    return sockets_locales[puerto].recvfrom(long_buffer)

def iyr_close(puerto):
    sockets_locales[puerto].close()

################## FUNCIONES MANEJO TCP #####################
    
def crear_socket_acogida(parametros_socket_servidor, max_conexiones):
    socket_servidorTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    socket_conectado_lado_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_conectado_lado_cliente.connect(parametros_socket_servidor)
    ip_cliente, puerto_cliente = socket_conectado_lado_cliente.getsockname()
    sockets_locales[puerto_cliente] = socket_conectado_lado_cliente
    ip_servidor, puerto_servidor = socket_conectado_lado_cliente.getpeername()
    conexion = (ip_cliente, puerto_cliente, ip_servidor, puerto_servidor)
    return conexion
    
def iyr_send(conexion, mensaje):
    puerto_socket = conexion[1]
    sockets_locales[puerto_socket].send(mensaje)

def iyr_recv(conexion, long_buffer):
    puerto_socket = conexion[1]
    return sockets_locales[puerto_socket].recv(long_buffer)
