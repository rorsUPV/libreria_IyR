# FICHERO: funciones_basicas.py

################### TRATAMIENTO DE CADENAS ####################################

def split(cadena, separador):
    return cadena.split(separador)

def strip(cadena):
    return cadena.strip()

def lower(cadena):
    return cadena.lower()

def upper(cadena):
    return cadena.upper()

def isdigit(cadena):
    return cadena.isdigit()

def es_numerico(cadena):
    try:
        float(cadena)
        return True
    except ValueError:
        return False

################### TRATAMIENTO DE TUPLAS ####################################

################### TRATAMIENTO DE LISTAS ####################################
def append(lista, elemento):
    lista.append(elemento)
  
def insert(lista, posicion, elemento):
    lista.insert(posicion, elemento)

def remove(lista, elemento):
    lista.remove(elemento)

# funciones para el tratamiento de Diccionarios
def keys(diccionario):
    return diccionario.keys()

def values(diccionario):
    return diccionario.values()

def pop(diccionario, clave):
    return diccionario.pop(clave)

################### TRATAMIENTO DE TEMPORIZADORES ####################################

def retardo(tiempo):
    time.sleep(tiempo)

################### VARIABLES ALEATORIAS ####################################
import random

def randint(a, b):
    return random.randint(a, b)
    