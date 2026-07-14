# Librería IyR
Esta librería contiene las funciones para las prácticas de la asignatrua I&R.

## Instalación
Para instalarla, abre la terminal y escribe:
pip install git+https://github.com/rorsUPV/libreria_IyR.git'

## Funciones para el manejo de SenseHat

## Funciones para el manejo de hilos
lanzaHilo(nombre_funcion)
parámetros: nombre_funcion - función que contiene el código que queremos que se ejcute dentro del hilo
retorna: nada

## Funciones para el manejo de los sockets

gethostbyname(host : String) : String
parametros: host - un String con un dominio del que se desea conocer la IP
retorna: un String correspondiente a la IP de ese dominio o un String indicando que no se ha podido resolver ese dominio

crearsocketUDP(socket_local : Tupla)
parametros: socket_local - una Tupla formada por dos elementos: una IP y un puerto al que se enlazará el socket
retorna: nada (aunque se crea el socket para su uso posterior)

sendto(mensaje : vector de bytes, socket_destino: Tupla)
parámetros:
   - mensaje - es el vector de bytes donde está la información a transmitir
   - socket_destino  es un Tupla formada por dos elementos: una IP y un puerto al que se enviará el mensaje
retorna: nada

receivefrom(long_buffer : int)
parámetros: long_buffer es un entero que fija el tamaño del buffer de recepción
retorna:
    - mensaje - que es un vector de bytes que contiene la información recibida
    - socket_origen -  que es una Tupla formada por dos elementos correspondientes a la IP y al puerto origen

