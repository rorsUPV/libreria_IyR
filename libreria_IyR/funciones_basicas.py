# FICHERO: funciones_basicas.py

################### TRATAMIENTO DE CADENAS ####################################

def iyr_split(cadena, separador):
    return cadena.split(separador)

def iyr_strip(cadena):
    return cadena.strip()

def iyr_lower(cadena):
    return cadena.lower()

def iyr_upper(cadena):
    return cadena.upper()

def iyr_isdigit(cadena):
    return cadena.isdigit()

def iyr_es_numerico(cadena):
    try:
        float(cadena)
        return True
    except ValueError:
        return False

################### TRATAMIENTO DE TUPLAS ####################################

################### TRATAMIENTO DE LISTAS ####################################
def iyr_append(lista, elemento):
    lista.append(elemento)
  
def iyr_insert(lista, posicion, elemento):
    lista.insert(posicion, elemento)

def iyr_remove(lista, elemento):
    lista.remove(elemento)

# funciones para el tratamiento de Diccionarios
def iyr_keys(diccionario):
    return diccionario.keys()

def iyr_values(diccionario):
    return diccionario.values()

def iyr_pop(diccionario, clave):
    return diccionario.pop(clave)

################### TRATAMIENTO DE TEMPORIZADORES ####################################

def retardo(tiempo):
    time.sleep(tiempo)

################### VARIABLES ALEATORIAS ####################################
import random

def iyr_randint(a, b):
    return random.randint(a, b)
    