# funciones_servidor

from wsgiref.simple_server import make_server
import socket

################### FUNCION BASICA SERVIDOR ####################################

def runServidor(IP_Servidor, Puerto_Servidor, application):
    srv = make_server(IP_Servidor, Puerto_Servidor, application)
    srv.serve_forever()

