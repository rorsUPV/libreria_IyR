# test.py

from libreria_IyR import *

#################### PROGRAMA DE TEST #######################
# simplemente vamos a probar que la funcion sleep() funciona
print('Comienza el test. Mira a ver que pasa')
arrancar_TimeOut(0.001)
parar = False
while not parar:
    if not TimeOut_vencido():
        print('tic tac')
    else:
        parar = True
print('\nsi ves esto al cabo de unos tics es que tiens instalada correctamente la libreria')
