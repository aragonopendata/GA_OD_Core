# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26

@author: Miquel Quetglas
@author: AMS
@version: 1.2 (20/10/2016)
"""
import conf as configuracion
import sys
sys.path.insert(0, configuracion.APP_PATH)
import conexiones
import json
import sys
import os
os.environ["NLS_LANG"] = "SPANISH_SPAIN.AL32UTF8"
import cgi
import flask
from flask import make_response
from flask import jsonify
import dicttoxml
dicttoxml.set_debug(False)
import logging
import logging.handlers
from flask import request
# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    
#Added for google analytics
import argparse

from googleapiclient.discovery import build

import httplib2
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials
#from oauth2client.contrib.appengine import OAuth2Decorator
from oauth2client import file
from oauth2client import tools
import urllib
import urllib.parse as urlparse
# from importlib import reload
import cx_Oracle

#Added to remove all views unused in GA_OD_Core (Logical deletion)
from disabledViewsList import *

#LOG_DEBUG = If is True will write logs with the deb() function
LOG_DEBUG = configuracion.DEBUG_VAR

FORMAT='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
my_logger=logging.getLogger("MyLogger")
if LOG_DEBUG is True:
    my_logger.setLevel(logging.DEBUG)
else:
    my_logger.setLevel(logging.ERROR)
fh=logging.handlers.RotatingFileHandler(configuracion.CUSTOM_LOG, maxBytes=5000000, backupCount=5)
if LOG_DEBUG is True:
    fh.setLevel(logging.DEBUG)
else:
    fh.setLevel(logging.ERROR)
fh.setFormatter(logging.Formatter(FORMAT))
my_logger.addHandler(fh)
dicttoxml.set_debug(False)

# reload(sys)
# sys.setdefaultencoding('utf-8')

#Array that contains the list of views that want to be removed from the result so that they are not displayed
disabled_views_id = views_id_list

def deb(msg):
    """
    If LOG_DEBUG is True, will write in log file.
    """
    if LOG_DEBUG is True:
        my_logger.info(msg)
        #print msg



def views(user):
    """
    Views
        Args:
           user(String): user logged in Opendata Portal (CKAN).
        Returns: 
            resultados(Array): Array with all available views returned in indented JSON
    """
    db = conexiones.conexion(configuracion.VIEWS_DB).cadena
    cursor = db.cursor()
    try:
        if user == 'admin' or user is None:
            sentencia = "SELECT id_vista, nombre FROM opendata.opendata_v_vistas order by id_vista"
        else:
            sentencia = "SELECT * FROM opendata.opendata_v_listadoVistas where usuario='" + user + "' order by id_vista"
        cursor.execute(sentencia)
        rows = cursor.fetchall()  
    except Exception as e:
        my_logger.error(e)
        return json.dumps([" Something went wrong. please try again or contact your administrator"], ensure_ascii=False,sort_keys=True,indent=4)
    
    #It checks if any view id exists in the result array, in which case it eliminates it
    for view in disabled_views_id:
        for row in rows:
            if view in row:
                rows.remove(row)

    cursor.close()
    resultados = json.dumps(rows,ensure_ascii=False,sort_keys=True,indent=4)
    return resultados

def show_columns(view_id):
    """
    Show Columns
    Args:    
        view_id(Integer): ID of the View to query
    Returns:
        resultados(Array): Array with information about the columns and data types
    """
    #It checks if the inserted id is in the list of views that should not be displayed
    if int(float(view_id)) not in disabled_views_id:
        try:    
            #Connect to the database according to environment
            db = conexiones.conexion(configuracion.VIEWS_DB).cadena
            cursor = db.cursor()
            cursor.execute("SELECT SUBSTR(NOMBREREAL,INSTR(NOMBREREAL,'.',-1)+1),BASEDATOS from " + configuracion.OPEN_VIEWS + " WHERE ID_VISTA = '"+ str(view_id) + "'")
            rows = cursor.fetchall()
            resultado = []
            
            #Keep Fields 'NOMBRE'(from ';' to the end) and field 'BASEDEDATOS'  
            for i in rows:
                deb("--------------------")        
                deb("*********************PID: " + str(os.getpid()))  
                deb("<Seleccionamos vista: " + i[0])
                nombre_vista = i[0]
                tipo_vista = i[1]
                resultado.append(i)

            cursor.close()    
            #Query to the View according to environment
            try:
                db = conexiones.conexion(tipo_vista).cadena  
                deb("--------------------")
                deb("CADENA DE CONEXION: " + str(db))
                deb("--------------------")
            except Exception as e:
                my_logger.error("View " + str(view_id) + " does not exist - e: " + str(e))
                return json.dumps(["View " + str(view_id) + " does not exist"], ensure_ascii=False,sort_keys=True,indent=4)

            #Obtain the type of Database (oracle, mysql, postge o sqlserver) according to environment
            tipo = conexiones.conexion(tipo_vista).tipo
            deb("TIPO DE BASE DE DATOS: " + str(tipo))

            table = devuelve_rows(view_id,None,None,1,1)
            rows = table[0]
            col = table[1]

            if len(rows) > 0 and len(col) > 0:
                #If the View is google_analytics type we store name and dataType to match views database
                if tipo == 'google_analytics':
                    resultado = []
                    
                    for n in range(len(col)):
                        resultado.append(dict(columnName=str(col[n]['name']),dataType=str(col[n]['dataType'])))
                else:
                    cursor = db.cursor()
                    try:

                        #Query according the type of Database
                        if tipo == 'oracle':
                            my_logger.error("select COLUMN_NAME,DATA_TYPE from ALL_TAB_COLUMNS where TABLE_NAME = UPPER('" + nombre_vista + "')")
                            cursor.execute("select COLUMN_NAME,DATA_TYPE from ALL_TAB_COLUMNS where TABLE_NAME = UPPER('" + nombre_vista + "')")
                        elif tipo == 'postgre':
                            cursor.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_name   = '"+ nombre_vista+"'")
                        elif tipo == 'sqlserver':
                            cursor.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_name   = '"+ nombre_vista+"'")
                            #En PRE la vista es 104, anteriormente era 126
                        elif tipo == 'mysql' and view_id == '104':
                            '''
                            Hack for database name problem in list of our views.
                            '''
                            cursor.execute("SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'open_poligonos'")       
                        elif tipo == 'mysql' and not view_id == '126':
                            cursor.execute("SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"+ nombre_vista+"'")
                        else:
                            deb("UNKNOWN TYPE OF DATABSE !!!!!")
                    except Exception as e:
                        my_logger.error(e)
                        return json.dumps([" Something went wrong. please try again or contact your administrator"], ensure_ascii=False,sort_keys=True,indent=4)
                    
                    rows = cursor.fetchall()
                    resultado = []
                    
                    #Insert results in a ( { key : value } ) dictionary
                    columns = [column[0] for column in cursor.description]
                    for row in rows:
                        resultado.append(dict(zip(columns, row)))
                    cursor.close() 

                resultados = json.dumps(resultado, ensure_ascii=False,sort_keys=True,indent=4) 
                return resultados
            else:
                return json.dumps([col[0]], ensure_ascii=False,sort_keys=True,indent=4)
        except Exception as e:
            my_logger.error(e)
            return json.dumps([" Something went wrong. please try again or contact your administrator"], ensure_ascii=False,sort_keys=True,indent=4)
    else:
        return json.dumps(["View " + str(view_id) + " does not exist"], ensure_ascii=False,sort_keys=True,indent=4)

def devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize):
    """
    Devuelve Rows
    Args:    
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        resultados(Array): Array with records requested in the query
        columns(Array): Array with the name of the Fields
    """
    try:          
        #my_logger.error('prueba0')
        deb("*********************PID: " + str(os.getpid()))  
        deb("*********************view_id: " + str(view_id))
        deb("*********************select_sql: " + str(select_sql))
        deb("*********************filter_sql: " + str(filter_sql))
        deb("*********************_page: " + str(_page))
        deb("*********************_pageSize: " + str(_pageSize))
        
        #Query to the View according to environment
        db_v = conexiones.conexion(configuracion.VIEWS_DB).cadena
        #my_logger.error('prueba1')
        cursor_v = db_v.cursor()
        cursor_v.execute("SELECT NOMBREREAL,BASEDATOS from " + configuracion.OPEN_VIEWS + " WHERE ID_VISTA = '"+ str(view_id) + "'")    
        rows = cursor_v.fetchall()
        #my_logger.error('prueba2')
        #Keep Fields 'NOMBRE' and 'BASEDEDATOS'  
        for i in rows:
            deb("--------------------")  
            deb("Seleccionamos vista: " + i[0])
            nombre_vista = i[0]
            tipo_vista = i[1]
            #my_logger.error('Nombre de vista: ' + str(nombre_vista))
            #my_logger.error('Tipo de vista: ' + str(tipo_vista))
        cursor_v.close()
        #my_logger.error('prueba3')
        try:
            deb("**tipo_vista: " + str(tipo_vista))
            db = conexiones.conexion(tipo_vista).cadena

            deb("--------------------")
            deb("CADENA DE CONEXION: " + str(db))
            deb("--------------------")
            #my_logger.error('prueba4')
            #Obtain the type of Database (oracle, mysql, postge o sqlserver) according to environment    
            tipo = conexiones.conexion(tipo_vista).tipo
            deb("1-TIPO DE BASE DE DATOS: " + str(tipo))
        except Exception as e:
            my_logger.error("View " + str(view_id) + " does not exist - e: " + str(e))
            return json.dumps(["View " + str(view_id) + " does not exist"], ensure_ascii=False,sort_keys=True,indent=4)
        #my_logger.error('prueba4.5')
        if _page == '' or _page is None:
            _page = 1
        if _pageSize == '' or _pageSize is None:
            _pageSize = 999999

        #my_logger.error('prueba4.6')
        if tipo == 'google_analytics':
            url = nombre_vista.replace("'","")
            parsed = urlparse.urlparse(url)
            profile = str(urlparse.parse_qs(parsed.query)['profile'][0])
            start_date = str(urlparse.parse_qs(parsed.query)['start_date'][0])
            end_date = str(urlparse.parse_qs(parsed.query)['end_date'][0])
            metrics = str(urlparse.parse_qs(parsed.query)['metrics'][0])    
            try:
                dimensions = str(urlparse.parse_qs(parsed.query)['dimensions'][0])
            except Exception as e:
                dimensions = None
    
            try:
                filters = str(urlparse.parse_qs(parsed.query)['filters'][0])
            except Exception as e:
                filters = None
            
            try:
                include_empty_rows = str(urlparse.parse_qs(parsed.query)['include_empty_rows'][0])
            except Exception as e:
                include_empty_rows = None
            
            try:
                max_results = str(urlparse.parse_qs(parsed.query)['max_results'][0])
            except Exception as e:
                max_results = None

            try:
                output = str(urlparse.parse_qs(parsed.query)['output'][0])
            except Exception as e:
                output = None

            try:
                samplingLevel = str(urlparse.parse_qs(parsed.query)['samplingLevel'][0])
            except Exception as e:
                samplingLevel = None

            try:
                segment = str(urlparse.parse_qs(parsed.query)['segment'][0])
            except Exception as e:
                segment = None

            try:
                sort = str(urlparse.parse_qs(parsed.query)['sort'][0])
            except Exception as e:
                sort = None

            try:
                start_index = str(urlparse.parse_qs(parsed.query)['start_index'][0])
            except Exception as e:
                start_index = None
            
            try:
                fields = str(urlparse.parse_qs(parsed.query)['fields'][0])
            except Exception as e:
                fields = None
            
            rowToStart = (int(_page) * int(_pageSize)) - int(_pageSize) + 1
            rowToEnd = int(_pageSize)
            rowToStart = str(rowToStart)
            rowToEnd = str(rowToEnd)

            if max_results is None or max_results == '' or max_results == '100000':
                max_results  = rowToEnd
            if start_index is None or start_index == '': 
                start_index= rowToStart		
            response = google_analytics(profile,start_date,end_date,metrics,dimensions,filters,include_empty_rows,max_results,output,samplingLevel,segment,sort,start_index,fields)  
            columns = []
            resultados = json.loads(response)

            for n in range(len(resultados['columnHeaders'])):
                columns.append(resultados['columnHeaders'][n])
            resultados = resultados['rows']
        else:
            #my_logger.error('prueba4.7')
            #If NOT GOOGLE ANALYTICS VIEW
            cursor = db.cursor()
            #select_sql = ' * '
            #If GET[select_sql] is empty select all (*)
            if select_sql is None:
                select_sql = ' * '
            else:
                #my_logger.error('prueba4.8')
                columnasArr = []
                
                columnas = json.loads(show_columns(view_id))
                for x in range (len(columnas)):
                    if tipo == 'postgre' or tipo == 'sqlserver':
                        deb("col " + str(x) + " es: " + str(columnas[x]['column_name']))
                        columnasArr.append(columnas[x]['column_name'])
                    else:
                        deb("col " + str(x) + " es: " + str(columnas[x]['COLUMN_NAME']))
                        columnasArr.append(columnas[x]['COLUMN_NAME'])
                deb("columnasArr es: " + str(columnasArr))
                select_sqlArr = select_sql.split(',')
                deb("select_sqlArr es: " + str(select_sqlArr))
                for word in select_sqlArr: 
                    if word not in columnasArr and word != '*':
                        return [],[str(word) + " is not a valid column"]
            #my_logger.error('prueba4.9')
            #Hack for fix a wrong name in database       
            if nombre_vista == 'BD_WEBIAF':
                nombre_vista = 'open_poligonos'

            rowToStart = str((int(_page) * int(_pageSize)) - int(_pageSize))
            rowToEnd = str(_pageSize)

            if tipo == 'oracle':
                #my_logger.error('prueba5.1')
                rowToEnd = str(int(_page) * int(_pageSize))
                if filter_sql is None or filter_sql == '':
                    if nombre_vista == 'pac1.opendata_solicitudes':
                        sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT "+ str(select_sql) +" FROM " + str(nombre_vista) + " WHERE CCOSEC != '2004') a  where ROWNUM <="+rowToEnd+" ) where rnum  > "+rowToStart+""
                    else:    
                        sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT "+ str(select_sql) +" FROM " + str(nombre_vista) + " ) a  where ROWNUM <="+rowToEnd+" ) where rnum  > "+rowToStart+""
                else:
                    sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT "+ str(select_sql) +" FROM " + str(nombre_vista) + " WHERE " + str(filter_sql).replace("\"","\'") +") a where ROWNUM <= "+rowToEnd+" ) where rnum  >= "+rowToStart+""
            elif tipo == 'sqlserver':
                rowToEnd = str(int(_page) * int(_pageSize) -1)
                filter_sql_added = ' rnum BETWEEN '+rowToStart+' AND ' +rowToEnd
                if filter_sql is None or filter_sql == '':
                    sentencia = "select "+ str(select_sql) +" from (SELECT *,ROW_NUMBER() OVER(ORDER BY (SELECT 0)) rnum FROM "+ str(nombre_vista) +") t WHERE " + str(filter_sql_added)
                else:
                    sentencia = "select "+ str(select_sql) +" from (SELECT *,ROW_NUMBER() OVER(ORDER BY (SELECT 0)) rnum FROM "+ str(nombre_vista) +") t WHERE " + str(filter_sql) + " AND " + str(filter_sql_added) 
            else:
                if tipo == 'postgre':
                    filter_sql_added = ' LIMIT '+rowToEnd+' OFFSET ' +rowToStart
                elif tipo == 'mysql':
                    filter_sql_added = ' LIMIT '+rowToStart+','+rowToEnd
                else:
                    filter_sql_added = ''
                if filter_sql is not None and filter_sql != '':
                    filter_sql = " WHERE " + filter_sql
                sentencia = "select " + str(select_sql) + " from " + str(nombre_vista)
                sentencia = str(sentencia) +  " " + str(filter_sql).replace("\"","\'") + " " + filter_sql_added
            
            if view_id == '265':
                sentencia = """ select  *  from "V_Dominio" """
                sentencia = str(sentencia) +  " " + str(filter_sql).replace("\"","\'") + " " + filter_sql_added
            elif view_id == '72':
                if filter_sql is not None and filter_sql != '':
                    sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT SIGNATURA, ACTIVIDAD_SIGLA, ACTIVIDAD_PROVINCIA, EXPEDIENTE_EJERCICIO, EXPEDIENTE_NUMERO, TITULARIDAD, TIPO_EMPRESA, NOMBRE_COMERCIAL, CIF_EMPRESA, NOMBRE_EMPRESA, DIRECCION_ESTABLECIMIENTO, PROVINCIA_ESTABLECIMIENTO, MUNICIPIO_ESTABLECIMIENTO, LOCALIDAD_ESTABLECIMIENTO, CODIGO_POSTAL_ESTABLECIMIENTO, TELEFONO_ESTABLECIMIENTO, FAX_ESTABLECIMIENTO, E_MAIL, DIRECCION_WEB, FECHA_SOLICITUD, FECHA_AUTORIZACION, ESTADO, FECHA_ULTIMA_INSPECCION, FECHA_BAJA, FECHA_ULT_ACTUAL_MODIF, NUMERO_MONITORES, NUMERO_GUIAS, FECHA_DESDE_TEMP_ALTA , FECHA_HASTA_TEMP_ALTA, FECHA_DESDE_TEMP_MEDIA, FECHA_HASTA_TEMP_MEDIA, FECHA_DESDE_TEMP_BAJA, FECHA_HASTA_TEMP_BAJA, OBSERVACIONES_TEMPORADA, ABIERTO_TODO_ANO, ABIERTO_NAVIDAD, ABIERTO_SEMANA_SANTA, ABIERTO_FIESTAS_LOCALES, VIGENCIA_SEGURO_RC_HASTA, NOMBRE_COMARCA, NACIONALIDAD  FROM " + str(nombre_vista) + " WHERE " + str(filter_sql).replace("\"","\'") + "  ) a  where ROWNUM <="+rowToEnd+" ) where rnum  > "+rowToStart+""
                else:
                    sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT SIGNATURA, ACTIVIDAD_SIGLA, ACTIVIDAD_PROVINCIA, EXPEDIENTE_EJERCICIO, EXPEDIENTE_NUMERO, TITULARIDAD, TIPO_EMPRESA, NOMBRE_COMERCIAL, CIF_EMPRESA, NOMBRE_EMPRESA, DIRECCION_ESTABLECIMIENTO, PROVINCIA_ESTABLECIMIENTO, MUNICIPIO_ESTABLECIMIENTO, LOCALIDAD_ESTABLECIMIENTO, CODIGO_POSTAL_ESTABLECIMIENTO, TELEFONO_ESTABLECIMIENTO, FAX_ESTABLECIMIENTO, E_MAIL, DIRECCION_WEB, FECHA_SOLICITUD, FECHA_AUTORIZACION, ESTADO, FECHA_ULTIMA_INSPECCION, FECHA_BAJA, FECHA_ULT_ACTUAL_MODIF, NUMERO_MONITORES, NUMERO_GUIAS, FECHA_DESDE_TEMP_ALTA , FECHA_HASTA_TEMP_ALTA, FECHA_DESDE_TEMP_MEDIA, FECHA_HASTA_TEMP_MEDIA, FECHA_DESDE_TEMP_BAJA, FECHA_HASTA_TEMP_BAJA, OBSERVACIONES_TEMPORADA, ABIERTO_TODO_ANO, ABIERTO_NAVIDAD, ABIERTO_SEMANA_SANTA, ABIERTO_FIESTAS_LOCALES, VIGENCIA_SEGURO_RC_HASTA, NOMBRE_COMARCA, NACIONALIDAD  FROM " + str(nombre_vista) + " ) a  where ROWNUM <="+rowToEnd+" ) where rnum  > "+rowToStart+""
            elif view_id == '279':
                sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT ID_FICHERO, VERSION, FECHA_PUBLICACION, DESCRIPCION FROM " + str(nombre_vista) + " ) a  where ROWNUM <="+rowToEnd+" ) where rnum  > "+rowToStart+""
            elif view_id == '282':
                if filter_sql is not None and filter_sql != '':
                    filter_sql = " AND " + filter_sql
                    sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT * FROM " + str(nombre_vista) + " WHERE BICOBI NOT IN ('MSHUE','MSCABR','MSZAR') " + str(filter_sql).replace("\"","\'") + " ) a  where ROWNUM <="+rowToEnd+" ) where rnum  > "+rowToStart+""
                else:
                    sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT * FROM " + str(nombre_vista) + " WHERE BICOBI NOT IN ('MSHUE','MSCABR','MSZAR') ) a  where ROWNUM <="+rowToEnd+" ) where rnum  > "+rowToStart+""
            elif view_id == '283':
                if filter_sql is not None and filter_sql != '':
                    filter_sql = " AND " + filter_sql
                    sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT * FROM " + str(nombre_vista) + " WHERE SUCOBI NOT IN ('MSHUE','MSCABR','MSZAR') " + str(filter_sql).replace("\"","\'") + " ) a  where ROWNUM <="+rowToEnd+" ) where rnum  > "+rowToStart+""
                else:
                    sentencia = "select * from ( select a.*, ROWNUM rnum from  ( SELECT * FROM " + str(nombre_vista) + " WHERE SUCOBI NOT IN ('MSHUE','MSCABR','MSZAR') ) a  where ROWNUM <="+rowToEnd+" ) where rnum  > "+rowToStart+""
            deb("sentencia: " + str(sentencia))
            #my_logger.error('prueba5.2')
            if filter_sql is not None or filter_sql != '':
                wordArr = ["count","lol","select","drop","union","password","admin","exec","declare","begin","BENCHMARK","encode"]
                for word in wordArr:    
                    if word in str(filter_sql).lower(): 
                        return [],[str(word) + " is not a valid expresion"]

            try:
                #my_logger.error('prueba5.3')
                #my_logger.error('Sentencia ->' + str(sentencia))
                cursor.execute(sentencia)         
            except Exception as e:
                my_logger.error(e)
                return [],["Something is wrong with the query, please check the params"]
            #Hack to manage LOB items in ORACLE
            #if nombre_vista == 'OPENDATA.OPACARA_ITEM_BIS':
            #    try:
            #        rows = []
            #        for row in cursor:
            #            r = []
            #            for col in row:
            #                if isinstance(col, cx_Oracle.LOB):
            #                    r.append(str(col))
            #                else:
            #                    r.append(col)
            #            rows.append(r)
            #    except Exception as e:
            #        my_logger.error(e)
            if nombre_vista == 'TURISMO.V_TUR_OD_TURISMO_ACTIVO' and filter_sql is None and _page == 1 and _pageSize == 999999:
                try:
                    for row in cursor:
                        r = []
                        for col in row:
                            try: 
                                #deb("col.read- " + str(col.read())) 
                                r.append(col.read())
                            except: 
                                #deb("col- " + str(col))
                                r.append(col)
                        rows.append(r)
                except Exception as e:
                    my_logger.error(e)
            else:
                rows = cursor.fetchall()
            #rows = cursor.fetchall()
            #my_logger.error('prueba5.6')
            resultados = rows
            #my_logger.error('RESULTADOS -> ' + str(resultados))
            #Hack to replace characters that cause errors in sqlserverDB
            if tipo == 'sqlserver':
                resultados = []
                r = []
                for r in rows:
                    longitud = len(r)
                    arrayTupla = []
                    for i in range(longitud):
                        try:
                            arrayTupla.append(r[i])
                            #arrayTupla.append(sustCaracter.sustitucionCaracterAlt(r[i]))
                        except Exception as e: 
                            arrayTupla.append(r[i])
                            deb("Exception encoding sqlserver")
                            #deb("sustitucionCaracterAlt fails in : " + str(e))
                    resultados.append(arrayTupla)
            #my_logger.error('prueba5.7')
            columns = [column[0] for column in cursor.description]
            #my_logger.error('prueba5.8')
        return resultados,columns
    except Exception as e:
        my_logger.error(e)
        return [],["Something went wrong. please try again or contact your administrator"]

def preview(view_id,select_sql,filter_sql,_page,_pageSize):
    """
    Preview
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        resultados(Array): Array with records requested in the query. Allways is like SELECT {select_sql} from {nombre_vista} where {filter_sql}
    """
    #It checks if the inserted id is in the list of views that should not be displayed
    if int(float(view_id)) not in disabled_views_id:
        try:
            try:
                #Query to the View according to environment
                deb("--------------------")
                db_v = conexiones.conexion(configuracion.VIEWS_DB).cadena
                deb("--------------------")
                cursor_v = db_v.cursor()
                cursor_v.execute("SELECT NOMBREREAL,BASEDATOS from " + configuracion.OPEN_VIEWS + " WHERE ID_VISTA = '"+ str(view_id) + "'")    
                rows = cursor_v.fetchall()
                
                for i in rows:
                    deb("--------------------")  
                    deb("Seleccionamos vista: " + i[0])
                    nombre_vista = i[0]
                    tipo_vista = i[1]
                cursor_v.close()    
            
                #Obtain the type of Database (oracle, mysql, postge o sqlserver) according to environment    
                tipo = conexiones.conexion(tipo_vista).tipo    
            except Exception as e:
                my_logger.error("View " + str(view_id) + " does not exist" + str(e))
                return json.dumps(["View " + str(view_id) + " does not exist"], ensure_ascii=False,sort_keys=True,indent=4)

            #Limit the amount of records we will return , because without are many fails get 500
            num_reg = configuracion.NUM_REGISTROS
            deb("-->  tipo_vista es: " + str(tipo))  
        
            deb("-->  filter_sql es: " + str(filter_sql))
        
            #Obtain registers and columns        
            table = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)
            rows = table[0]
            col = table[1]

            #deb("-->>>>> Rows: " + str(rows))
            #deb("-->>>>> Columns: " + str(col))
            if len(rows) > 0 and len(col) > 0:
                if tipo == 'google_analytics':
                    columns = []
                    for n in range(len(col)):
                        columns.append(col[n]['name'])
                else:
                    columns = col

                resultado = []
                resultado.append(columns)

                for row in rows:
                    resultado.append(row)

                #This way format to use on opendata.aragon.es      
                d_string = json.dumps(resultado,default=date_handler,ensure_ascii=False,sort_keys=True,indent=4)
                return d_string
            else:
                return json.dumps([col[0]], ensure_ascii=False,sort_keys=True,indent=4)
        except Exception as e: 
            my_logger.error(e)
            return json.dumps([" Something went wrong. please try again or contact your administrator"], ensure_ascii=False,sort_keys=True,indent=4)
    else:
        return json.dumps(["View " + str(view_id) + " does not exist"], ensure_ascii=False,sort_keys=True,indent=4)

def download(view_id,select_sql,filter_sql,formato,_page,_pageSize):
    """
    Download
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
        formato(String): String with the format of the document to download, can be JSON, CSV or XML
    Returns:
        {nombre}.{formato} (File): A file with the format requested
    """ 
    #It checks if the inserted id is in the list of views that should not be displayed
    if int(float(view_id)) not in disabled_views_id:
        try:
            db_v = conexiones.conexion(configuracion.VIEWS_DB).cadena
            cursor_v = db_v.cursor()
            cursor_v.execute("SELECT NOMBREREAL,BASEDATOS from " + configuracion.OPEN_VIEWS + " WHERE ID_VISTA = '"+ str(view_id) + "'")    
            rows = cursor_v.fetchall()
            
            for i in rows:
                deb("--------------------")  
                deb("Seleccionamos vista: " + i[0])
                nombre_vista = i[0]
                tipo_vista = i[1]
            cursor_v.close()

            #Obtain the type of Database (oracle, mysql, postge o sqlserver) according to environment   
            tipo = conexiones.conexion(tipo_vista).tipo
        except Exception as e:
                my_logger.error("View " + str(view_id) + " does not exist - e:" + str(e))
                return json.dumps(["View " + str(view_id) + " does not exist"], ensure_ascii=False,sort_keys=True,indent=4)

        #Differentiate format
        if formato.upper() == "JSON":
            resultado = []    
            resultado = create_JSON_array(view_id,select_sql,filter_sql,tipo,_page,_pageSize)  
        elif formato.upper() == 'XML':
            obj = create_XML_array(view_id,select_sql,filter_sql,tipo,_page,_pageSize)
            resultado = dicttoxml.dicttoxml(obj,attr_type=False)
        elif formato.upper() == 'CSV':
            resultado = ""
            resultado = create_CSV(view_id,select_sql,filter_sql,tipo,_page,_pageSize)      
        else:
            resultado = "Must enter the parameter <b>format</b>. (XML, JSON o CSV)"
        return resultado
    else:
        
        #Differentiate format
        if formato.upper() == "JSON":
            resultado = []
            resultado =  json.dumps(["View " + str(view_id) + " does not exist"], ensure_ascii=False,sort_keys=True,indent=4)
        elif formato.upper() == 'XML':
            obj = []
            obj.append(dict(zip(['ERROR'], ["View " + str(view_id) + " does not exist"])))
            resultado = dicttoxml.dicttoxml(obj,attr_type=False)
        elif formato.upper() == 'CSV':
            resultado = ""
            resultado = "View " + str(view_id) + " does not exist"
        else:
            resultado = "Must enter the parameter <b>format</b>. (XML, JSON o CSV)"
        return resultado



def create_JSON_array(view_id,select_sql,filter_sql,tipo,_page,_pageSize):
    """
    Create JSON Array
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve .
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        reultados(Array):Array in JSON format
    """            
    resultado = []

    table = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)
    rows = table[0]
    col = table[1]

    if len(rows) > 0 and len(col) > 0:
        if tipo == 'google_analytics':
            col = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)[1]
            columns = []
            for n in range(len(col)):
                columns.append(col[n]['name'])
        else:
            columns = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)[1]
        resultado.append(columns)
        for row in rows:
            resultado.append(row)
        d_string = json.dumps(resultado, default=date_handler, ensure_ascii=False,sort_keys=True,indent=4)    
        return d_string
    else:
        return json.dumps([col[0]], ensure_ascii=False,sort_keys=True,indent=4)


def create_XML_array(view_id,select_sql,filter_sql,tipo,_page,_pageSize):
    """
    Create XML Array
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve .
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        reultados(Dictionary): Array in dictionary format.
    """            
    resultado = []

    table = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)
    rows = table[0]
    col = table[1]

    if len(rows) > 0 and len(col) > 0:
        if tipo == 'google_analytics':
            col = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)[1]
            columns = []
            for n in range(len(col)):
                columns.append(col[n]['name'])
        else:
            columns = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)[1]
        for row in rows:
            resultado.append(dict(zip(columns, row)))
        return resultado
    else:
        resultado.append(dict(zip(['ERROR'], [col[0]])))
        return resultado


def create_CSV(view_id,select_sql,filter_sql,tipo,_page,_pageSize):
    """
    Create CSV
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        reultados(String): String in csv format.
    """    
    table = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)
    rows = table[0]
    col = table[1]

    if len(rows) > 0 and len(col) > 0:
        if tipo == 'google_analytics':
            col = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)[1]
            columns = []
            for n in range(len(col)):
                columns.append(col[n]['name'])
        else:
            columns = devuelve_rows(view_id,select_sql,filter_sql,_page,_pageSize)[1]

        #Creating csv with ';' as separator
        out = ""
        for row in columns:
            out += '\"' + row + '\";'
            #out = out + '\";'
        out += '\n'
        for row in rows:
            for column in row:
                out += '\"' + str(column) + '\";'
                #out += '\";'
            out += '\n'
        #Different way in sqlserver
        if view_id=='103':
            deb('VISTA 103')
            return out
        else:
            return out.encode('utf-8')
    else:
        out = col[0]
        return out.encode('utf-8')


def get_view_id(resource_id):
    """
    Gets the Id of the View (VISTA) in opendata_v_resourceVista table knowing the Id of the resource (ID_RESOURCEVISTA)
    """
    db_v = conexiones.conexion(configuracion.VIEWS_DB).cadena
    cursor_v = db_v.cursor()
    cursor_v.execute("SELECT VISTA from opendata_v_resourceVista WHERE ID_RESOURCEVISTA = "+ str(resource_id))   
    rows = cursor_v.fetchall()
    for i in rows:
        view_id = i[0]
    cursor_v.close()
    return view_id    
 

def date_handler(obj):
    """
    For date format in json.dumps()
    """    
    return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)


def google_analytics(profile,start_date,end_date,metrics,dimensions,filters,include_empty_rows,max_results,output,samplingLevel,segment,sort,start_index,fields):
    """Returns a query to google analytics API.
    https://developers.google.com/apis-explorer/#p/analytics/v3/
    Using:
    https://developers.google.com/apis-explorer/#p/analytics/v3/analytics.data.ga.get
     Args:
        start_date(String): Requests can specify a start date formatted as YYYY-MM-DD, or as a relative date (e.g., today, yesterday, or 7daysAgo). The default value is 7daysAgo. (string)
        end_date(String): Requests can specify a start date formatted as YYYY-MM-DD, or as a relative date (e.g., today, yesterday, or 7daysAgo). The default value is 7daysAgo. (string)
        metrics(String): A comma-separated list of Analytics metrics. E.g., 'ga:sessions,ga:pageviews'. At least one metric must be specified. (string)
        dimensions(String):A comma-separated list of Analytics dimensions. E.g., 'ga:browser,ga:city'.
        filters(String):A comma-separated list of dimension or metric filters to be applied to Analytics data. 
        include-empty-rows(Boolean):The response will include empty rows if this parameter is set to true, the default is true 
        max-results(Integer):The maximum number of entries to include in this feed. 
        output(String):The selected format for the response. Default format is JSON. 
        samplingLevel(String):The desired sampling level. 
        segment(String):An Analytics segment to be applied to data. 
        sort(String):A comma-separated list of dimensions or metrics that determine the sort order for Analytics data. 
        start-index(integer, 1+):An index of the first entity to retrieve. Use this parameter as a pagination mechanism along with the max-results parameter. 
        fields:Selector specifying which fields to include in a partial response.
    Returns:
        reultados(Dictionary): Array in dictionary format.
    """            
    # Use the Analytics Service Object to query the Core Reporting API
    service_account_email = configuracion.SERVICE_ACCOUNT_EMAIL
    
    #key_file_location = 'client_secrets.p12'
    key_file_location = configuracion.APP_PATH + '/client_secrets.p12'

    # Define the auth scopes to request.
    scope = ['https://www.googleapis.com/auth/analytics.readonly']
    service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)

    resultado = service.data().ga().get(
        ids='ga:' + profile,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
        dimensions=dimensions,
        filters=filters,
        include_empty_rows=include_empty_rows,
        max_results=max_results,
        output=output,
        samplingLevel=samplingLevel,
        segment=segment,
        sort=sort,
        start_index=start_index,
        fields=fields
        ).execute()
    #Return  results in JSON format indented.
    return json.dumps(resultado,ensure_ascii=False,sort_keys=True,indent=1) 


def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
  """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

  Returns:
    A service that is connected to the specified API.
  """

  #with open(key_file_location, 'rb') as f:
  #  key = f.read()
  #  f.close()

  credentials = ServiceAccountCredentials.from_p12_keyfile(service_account_email, key_file_location, scopes=scope)
  #creds = ServiceAccountCredentials.from_p12_keyfile('foo@bar.com', '/path/to/keyfile.p12')

  http = credentials.authorize(httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http, cache_discovery=False)
  return service
