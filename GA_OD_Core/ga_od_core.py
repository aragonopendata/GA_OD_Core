# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26

@author: Miquel Quetglas
@author: AMS
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
#from flask import request
from flask import make_response
from flask import jsonify
import dicttoxml
dicttoxml.set_debug(False)
import sustCaracter as sustCaracter
import logging

from flask import request

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    
#Creation of the log file with personalized format.
logging.basicConfig(filename=configuracion.CUSTOM_LOG,
                    level=logging.ERROR,
                    datefmt='%a, %d %b %Y %H:%M:%S',                    
                    format='%(asctime)s: %(filename)s: %(lineno)s %(levelname)s: %(message)s')


#DEBUG = If is True will write logs with the deb() function
DEBUG = configuracion.DEBUG_VAR

def deb(msg):
    """
    If DEBUG is True, will write in log file.
    """
    if DEBUG is True:
        logging.info(" "+  msg)


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
    #cursor.execute("SELECT ID_VISTA,NOMBRE FROM " + configuracion.OPEN_VIEWS + " ORDER BY ID_VISTA")
    if user == 'admin' or user is None:
        sentencia = "SELECT id_vista, nombre FROM opendata.opendata_v_vistas order by id_vista"
    else:
        sentencia = "SELECT * FROM opendata.opendata_v_listadoVistas where usuario='" + user + "' order by id_vista"
    cursor.execute(sentencia)
    rows = cursor.fetchall()
    resultado = []    


    for row in rows:
        resultado.append(row)    
   
    cursor.close()
             
    #resultados = jsonify(results = resultado)
    #Esto FUNCIONA!
    #resultados = json.dumps(resultado, ensure_ascii=False,sort_keys=True,indent=4)
    resultados = json.dumps(resultado,ensure_ascii=False,indent=4)
    
    #resultados = str(resultado)
    #resultados = Response(json.dumps(resultado),  mimetype='application/json')
    #Return  results in JSON format indented.
    return resultados  

def show_columns(view_id):
    """
    Show Columns
    Args:    
        view_id(Integer): ID of the View to query
    Returns:
        resultados(Array): Array with information about the columns and data types
    """
    
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
            deb("<Seleccionamos vista: " + i[0])
            nombre_vista = i[0]
            tipo_vista = i[1]
            resultado.append(i)
        
        cursor.close()    
        
        #Query to the View according to environment
        db = conexiones.conexion(tipo_vista).cadena  
        deb("--------------------")
        deb("CADENA DE CONEXION: " + str(db))
        deb("--------------------")
 
        #Obtain the type of Database (oracle, mysql, postge o sqlserver) according to environment
        tipo = conexiones.conexion(tipo_vista).tipo
        deb("TIPO DE BASE DE DATOS: " + str(tipo))
        
        cursor = db.cursor()
        
        #Query according the type of Database
        if tipo == 'oracle':
            cursor.execute("select COLUMN_NAME,DATA_TYPE from ALL_TAB_COLUMNS where TABLE_NAME = UPPER('" + nombre_vista + "')")
        elif tipo == 'postgre':
            cursor.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_name   = '"+ nombre_vista+"'")
        elif tipo == 'sqlserver':
            cursor.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_name   = '"+ nombre_vista+"'")
        elif tipo == 'mysql' and view_id == 104:
            '''
            Hack for database name problem in list of our views.
            '''
            cursor.execute("SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'open_poligonos'")       
        elif tipo == 'mysql' and not view_id == 104:
            cursor.execute("SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"+ nombre_vista+"'")
        else:
            deb("UNKNOWN TYPE OF DATABSE !!!!!")
        
        
        rows = cursor.fetchall()
        deb("--------------------")
        resultado = []
        
        #Insert results in a ( { key : value } ) dictionary
        columns = [column[0] for column in cursor.description]
        for row in rows:
            resultado.append(dict(zip(columns, row)))
            
        cursor.close()    

        #resultados = jsonify(results = resultado)
        resultados = json.dumps(resultado, ensure_ascii=False,sort_keys=True,indent=4)
        #resultados = Response(json.dumps(resultado),  mimetype='application/json') 
        #resultados = str(resultado)    
        return resultados
    except Exception,e:
        #logging.error(e)
        pass 

    

def devuelve_rows(view_id,select_sql,filter_sql):
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
        deb("*********************view_id: " + str(view_id))
        deb("*********************select_sql: " + str(select_sql))
        deb("*********************filter_sql: " + str(filter_sql))
        
        #Query to the View according to environment
        db_v = conexiones.conexion(configuracion.VIEWS_DB).cadena
        cursor_v = db_v.cursor()
        cursor_v.execute("SELECT NOMBREREAL,BASEDATOS from " + configuracion.OPEN_VIEWS + " WHERE ID_VISTA = '"+ str(view_id) + "'")    
        rows = cursor_v.fetchall()
        
        #Keep Fields 'NOMBRE' and 'BASEDEDATOS'  
        for i in rows:
            deb("--------------------")  
            deb("Seleccionamos vista: " + i[0])
            nombre_vista = i[0]
            tipo_vista = i[1]
        cursor_v.close()    
        
        
         
        db = conexiones.conexion(tipo_vista).cadena
        deb("--------------------")
        deb("CADENA DE CONEXION: " + str(db))
        
        deb("--------------------")
       
        #Obtenemos el tipo de base de datos que es (oracle, mysql, postge o sqlserver) según el campo 'BASEDATOS'        
        tipo = conexiones.conexion(tipo_vista).tipo
        deb("TIPO DE BASE DE DATOS: " + str(tipo))
        
        cursor = db.cursor()
        
        #Si GET[select_sql] es vacío recuperamos todo (*)
        if select_sql is None:
            select_sql = '*'
    
        #TODO: Esta hardcodedado en package.py como vista a la que consultar.        
        if nombre_vista == 'BD_WEBIAF':
            nombre_vista = 'open_poligonos'
        sentencia = "select " + str(select_sql) + " from " + str(nombre_vista)
        
        #Si GET[filter_sql es vacío no aplicamos filtros a la consulta]
        if filter_sql is None:
            filter_sql = "" 
        else:
            sentencia = str(sentencia) +  " " + str(filter_sql).replace("\"","\'")
            #sentencia = str(sentencia) +  " " + str(filter_sql)
        deb("sentencia: " + str(sentencia))
        
        cursor.execute(sentencia)
        rows = cursor.fetchall()
        resultados = rows
        
        #HAck para sustituir carácteres que causan error.         
        if tipo == 'mysql' or tipo == 'sqlserver':
            resultados = []
            r = []
            for r in rows:
                longitud = len(r)
                arrayTupla = []
                for i in range(longitud):
                    try:                
                        arrayTupla.append(sustCaracter.sustitucionCaracter(r[i]))
                        #arrayTupla.append(r[i].encode('latin1').decode('utf8'))
                    except Exception,e: 
                        arrayTupla.append(r[i])
                resultados.append(arrayTupla)
       

        columns = [column[0] for column in cursor.description]
        deb("devuelve_rows--------------------")
        
        return resultados,columns
    except Exception,e:
        #logging.error(e)
        pass        

        


    
def preview(view_id,select_sql,filter_sql):
    """
    Preview
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        resultados(Array): Array with records requested in the query. Allways is like SELECT {select_sql} from {nombre_vista} where {filter_sql}
    """    
   

    
    try:
           #Conectamos con la base de datos según el entorno
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
        
        #Obtenemos el tipo de base de datos que es (oracle, mysql, postge o sqlserver) según el campo 'BASEDATOS'    
        tipo = conexiones.conexion(tipo_vista).tipo    
       
        
        
        #La cantidad de registros que vamos a devolver, ya que sin son muchos da error 500
        num_reg = configuracion.NUM_REGISTROS
        deb("-->  tipo_vista es: " + str(tipo))  
       
        #Para el PREVIEW si devolvemos cierta cantidad de registros da un 500        
        if filter_sql == None or filter_sql is None:
            if tipo == 'oracle':
                filter_sql = " WHERE ROWNUM< " + str(num_reg)
            elif tipo == 'sqlserver':
                filter_sql = ""
            elif tipo == 'postgre' or tipo == 'mysql':
                filter_sql = " LIMIT " + str(num_reg)
        else:
            if tipo == 'oracle':
                filter_sql = " WHERE " + str(filter_sql) + " AND ROWNUM< " + str(num_reg)
            elif tipo == 'sqlserver':
                filter_sql = " WHERE " + str(filter_sql)
            elif tipo == 'postgre' or tipo == 'mysql':
                filter_sql = " WHERE " + str(filter_sql) + " LIMIT " + str(num_reg)          
            
            
        deb("-->  filter_sql es: " + str(filter_sql))
       
        #Obtenemos registros y columnas        
        rows = devuelve_rows(view_id,select_sql,filter_sql)[0]
        columns = devuelve_rows(view_id,select_sql,filter_sql)[1]
        
        resultado = []
        resultado.append(columns)
        for row in rows:
            resultado.append(row)
            #[M] Esto solo si queremos formatearlo como un diccionario            
            #resultado.append(dict(zip(columns, row)))
        
        #file = open("{path/to/our/aplication/}GA_OD_Core/newfile.txt", "w")   
        #file.write(str(resultado))
        #file.close()
        #[M] Así de esta forma lo devuelve igual que en opendata        
        d_string = json.dumps(resultado,default=date_handler,ensure_ascii=False,sort_keys=True,indent=4)
        
        
        #d_string = json.dumps(resultado, default=date_handler, ensure_ascii=False,sort_keys=True,indent=4)
        #d_string is a string object
     
        #[M] Para evitar errores de codificación
        #d_unicode = d_string.decode('unicode-escape')
        #d_unicode is a unicode object
        
        #[M] Para evitar errores de codificación
        #d_unicode = d_unicode.encode('utf-8').strip()
        
        return d_string
        #return unicode
        #return resultado
        #return jsonify(results = resultado)
        #return Response(json.dumps(resultado),  mimetype='application/json')
        
    except Exception,e: 
        #logging.error(e)
        pass

                 
def download(view_id,select_sql,filter_sql,formato):
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
    
    if filter_sql != None or filter_sql is not None:
        filter_sql = " WHERE " + str(filter_sql)
    #Diferenciamos el formato
    if formato.upper() == "JSON":
        resultado = []    
        resultado = create_JSON_array(view_id,select_sql,filter_sql)  
    elif formato.upper() == 'XML':
        obj = create_XML_array(view_id,select_sql,filter_sql)
        resultado = dicttoxml.dicttoxml(obj,attr_type=False)
    elif formato.upper() == 'CSV':
        resultado = ""
        resultado = create_CSV(view_id,select_sql,filter_sql)      
    else:
        resultado = "Debe introducir el parámetro <b>format</b>. (XML, JSON o CSV)"
    return resultado    


def create_JSON_array(view_id,select_sql,filter_sql):
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
    rows = devuelve_rows(view_id,select_sql,filter_sql)[0]
    columns = devuelve_rows(view_id,select_sql,filter_sql)[1]
    resultado.append(columns)
    for row in rows:
        resultado.append(row)
    d_string = json.dumps(resultado, default=date_handler, ensure_ascii=False,sort_keys=True,indent=4)    
    #d_string = json.dumps(resultado,default=date_handler)
    return d_string

def create_XML_array(view_id,select_sql,filter_sql):
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
    rows = devuelve_rows(view_id,select_sql,filter_sql)[0]
    columns = devuelve_rows(view_id,select_sql,filter_sql)[1]
    for row in rows:
        resultado.append(dict(zip(columns, row)))
    #res = json.dumps(resultado)
    return resultado

def create_CSV(view_id,select_sql,filter_sql):
    """
    Create CSV
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        reultados(String): String in csv format.
    """    
    rows = devuelve_rows(view_id,select_sql,filter_sql)[0]
    columns = devuelve_rows(view_id,select_sql,filter_sql)[1]
    
    #CSV creando el archivo en el servidor, es otra forma de hacerlo
    '''    
    with open("tmp/" + str(random.random()) + " _out.csv", "wb") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(columns) # write headers
        csv_writer.writerows(rows)
    '''
    
    #CSV creado de forma manual, con ";" como separador
    out = ""
    for row in columns:
        out = out + str(row)
        out = out + ";"
    out = out + '\n'
    for row in rows:
        for column in row:
            out = out + str(column)
            out = out + ";"
        out = out + '\n'

    return str(out)


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
    Se usa para el formato de fechas en json.dumps()
    For date format in json.dumps()
    """    
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj