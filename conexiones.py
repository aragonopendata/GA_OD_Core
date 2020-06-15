# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26

@author: Miquel Quetglas
@author: AMS
@version: 1.2 (20/10/2016)
"""
import conf as configuracion
import os
os.environ["NLS_LANG"] = "SPANISH_SPAIN.AL32UTF8"
import cx_Oracle
import psycopg2
import pymssql
# import MySQLdb
import pymysql
pymysql.install_as_MySQLdb()


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
        devolver = ConexionDB(pymssql.connect(host='xxx', user='xxx', password='xxx', database='xxx', charset='cp1251'),"sqlserver")
    elif (ubicacion.lower() == 'app5'):
        devolver = ConexionDB(pymysql.connect(host='xxx',port=xxx, user='xxx', passwd='0p3n-DATA',db='xxx',charset='utf8', init_command='SET NAMES UTF8'),"mysql")
    elif ubicacion.lower() == 'app6':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.AST_USR + "/" + configuracion.AST_PASS + "@" + configuracion.ORACLE_IAA_VIEJAS),"oracle")
    elif ubicacion.lower() == 'app7':
        devolver = ConexionDB('','google_analytics')
    elif ubicacion.lower() == 'app8':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.AST_USR + "/" + configuracion.AST_PASS + "@" + configuracion.AST_TURISMO),"oracle")
    elif ubicacion.lower() == 'app9':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.CRA_USR + "/" + configuracion.CRA_PASS + "@" + configuracion.CRA_CONEXION),"oracle")  
    elif ubicacion.lower() == 'app10':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.OPENDATA_USR + "/" + configuracion.OPENDATA_USR + "@" + configuracion.ORACLE_IAA),"oracle")
    elif ubicacion.lower() == 'app11':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.OPENDATA_USR + "/" + configuracion.OPENDATA_USR + "@" + configuracion.TRANSPORTE_CONEXION),"oracle")
    elif ubicacion.lower() == 'app12':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.ORACLE_DESFOR_USR + "/" + configuracion.ORACLE_DESFOR_PASS + "@" + configuracion.ORACLE_DESFOR_CONEXION),"oracle")
    elif ubicacion.lower() == 'app13':
         devolver = ConexionDB(psycopg2.connect(configuracion.IGEAR_CONEXION_BD),"postgre")
    elif ubicacion.lower() == 'app14':
         devolver = ConexionDB(cx_Oracle.connect(configuracion.OPENDATA_USR + "/" + configuracion.OPENDATA_USR + "@" + configuracion.ENERGIA), "oracle")
    elif ubicacion.lower() == 'app15':
        devolver = ConexionDB(cx_Oracle.connect(configuracion.OPENDATA_USR + "/" + configuracion.OPENDATA_PASS_PRO + "@" + configuracion.ORACLE_ADMIN_ELECTRONICA_CONEXION),"oracle")
    elif ubicacion.lower() == 'app16':
         devolver = ConexionDB(psycopg2.connect(configuracion.DOMINIOS_POSTGRE_CONEXION_BD),"postgre")        
    elif ubicacion.lower() == 'app17':
         devolver = ConexionDB(psycopg2.connect(configuracion.PRESUPUESTOS_POSTGRE_CONEXION_BD),"postgre")
    elif ubicacion.lower() == 'app18':
         devolver = ConexionDB(cx_Oracle.connect(configuracion.OPENDATA_USR + "/" + configuracion.OPENDATA_PASS + "@" + configuracion.BIBLIOTECAS_BD),"oracle")
    elif ubicacion.lower() == 'app19':
         devolver = ConexionDB(psycopg2.connect(configuracion.SALUD_CONEXION_BD),"postgre")
    else:
        print ('There is no connection to: ' + ubicacion)
        return None;
    return devolver
