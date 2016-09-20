# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26

@author: Miquel Quetglas
@author: AMS
@version: 1.1 (25/05/2016)
"""
import conf as configuracion
import os
os.environ["NLS_LANG"] = "SPANISH_SPAIN.AL32UTF8"
import cx_Oracle
import psycopg2
import pymssql
import MySQLdb


class ConexionDB:
    """Class to create connections to database"""
    def __init__(self,cadena,tipo):          
        self.cadena = cadena
        self.tipo = tipo
   
def conexion(ubicacion):
    """
    conexion
    Args:
        ubicacion(String): String with the name to database 
    Returns:
        devolver(Obj): Object with the conexion to database
    """
    if ubicacion.lower() == 'pre-opendata-oracle':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.OPENDATA_USR + "/" + configuracion.OPENDATA_PASS + "@" + configuracion.OPENDATA_CONEXION_BD_PRE),"oracle")
    elif ubicacion.lower() == 'pro-opendata-oracle':
       devolver = ConexionDB(cx_Oracle.connect(configuracion.OPENDATA_USR + "/" + configuracion.OPENDATA_PASS + "@" + configuracion.OPENDATA_CONEXION_BD),"oracle")
    elif ubicacion.lower() == 'des-opendata-oracle':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.OPENDATA_USR + "/" + configuracion.OPENDATA_PASS + "@" + configuracion.OPENDATA_CONEXION_BD_DES),"oracle")
    elif ubicacion.lower() == 'app1':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.AST_USR + "/" + configuracion.AST_PASS + "@" + configuracion.AST1_CONEXION_BD),"oracle")
    elif ubicacion.lower() == 'app2':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.AST_USR + "/" + configuracion.AST_PASS + "@" + configuracion.AST2_CONEXION_BD),"oracle") 
    elif ubicacion.lower() == 'app3':
         devolver = ConexionDB(psycopg2.connect(configuracion.AST3_CONEXION_BD),"postgre")
    elif ubicacion.lower() == 'opendata-postgre':
        devolver= ConexionDB(psycopg2.connect(configuracion.OPENDATA_POSTGRE_CONEXION_BD),"postgre")
    elif (ubicacion.lower() == 'app4'):
        devolver = ConexionDB(pymssql.connect(host='xxx', user='xxx', password='xxx', database='xxx'),"sqlserver")
    elif (ubicacion.lower() == 'app5'):
        #devolver = ConexionDB(MySQLdb.connect(host='xxx',port=xxx, user='xxx', passwd='xxx',db='xxx'),"mysql")
        devolver = ConexionDB(MySQLdb.connect(host='xxx',port=xxx, user='xxx', passwd='xxx',db='xxx'),"mysql")
    elif ubicacion.lower() == 'app6':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.AST_USR + "/" + configuracion.AST_PASS + "@" + configuracion.AST5_CONEXION_BD),"oracle")
    elif ubicacion.lower() == 'app7':
        devolver = ConexionDB('','google_analytics')
    elif ubicacion.lower() == 'app8':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.AST_USR + "/" + configuracion.AST_PASS + "@" + configuracion.AST_TURISMO),"oracle")
    elif ubicacion.lower() == 'app9':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.CRA_USR + "/" + configuracion.CRA_PASS + "@" + configuracion.CRA_CONEXION),"oracle")  
    else:
        print 'There is no connection to: ' + ubicacion
        return None;
    return devolver