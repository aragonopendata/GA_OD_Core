# -*- coding: utf-8 -*-
#Sustitucion de Caracteres
#Funcion que utilizaremos para realizar un replace de los caracteres no admitidos.
def sustitucionCaracterAlt(cadena):
    cadena = cadena.decode('unicode_escape').encode('utf-8')
    return cadena
#Sustitucion de Caracteres





