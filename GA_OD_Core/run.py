# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26

@author: Miquel Quetglas
@author: AMS
@version: 1.1 (25/05/2016)
"""
from flask import Flask
import ga_od_core
from flask import request
import conf as configuracion
import connexion
import flask
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import make_response
app = Flask(__name__)

#For debbugging ONLY if True
if configuracion.ENTORNO == 'PRO':
    app.debug = False
else:
    app.debug = True

from werkzeug.debug import DebuggedApplication
application = DebuggedApplication(app, evalex=configuracion.DEBUG_VAR)

    
@app.route('/')
def index():
    return 'Index Page'
    

@app.route('/hello')
def hello():
    res = flask.Response("Hello! Welcome to GA_OD_Core API")
    res.headers['Access-Control-Allow-Headers'] = "*"        
    res.headers['Access-Control-Allow-Origin'] = "*"        
    res.headers['Access-Control-Allow-Methods'] = "GET"
    
    return res
    
@app.route('/views', methods=['GET', 'POST'])
def run_views():
    user = request.args.get("user")
    res = make_response(ga_od_core.views(user))    
    res.headers['Access-Control-Allow-Headers'] = "*"        
    res.headers['Access-Control-Allow-Origin'] = "*"        
    res.headers['Access-Control-Allow-Methods'] = "GET"
    res.headers['Content-Type'] = 'application/json; charset=UTF-8'
    return res
    
@app.route('/show_columns', methods=['GET', 'POST'])
def run_show_columns():
    view_id = request.args.get("view_id")
    if view_id is None:
        res = flask.Response("<b> view_id</b> is required.")
    elif view_id=="0" or not view_id.isdigit():
        res = flask.Response("<b> view_id</b> must be a number")
    else:      
        res = make_response(ga_od_core.show_columns(view_id))
        res.headers['Access-Control-Allow-Headers'] = "*"        
        res.headers['Access-Control-Allow-Origin'] = "*"        
        res.headers['Access-Control-Allow-Methods'] = "GET"
        res.headers['Content-Type'] = 'application/json; charset=UTF-8'
    return res 

    
@app.route('/preview', methods=['GET', 'POST'])
def run_preview():
        
    view_id = request.args.get("view_id")
    if view_id is None:
        res = flask.Response("<b> view_id</b> is required.")
    elif view_id=="0" or not view_id.isdigit():
        res = flask.Response("<b> view_id</b> must be a number")
    else:      
        select_sql = request.args.get("select_sql")
        filter_sql = request.args.get("filter_sql")
        res = make_response(ga_od_core.preview(view_id,select_sql,filter_sql))
        res.headers['Access-Control-Allow-Headers'] = "*"        
        res.headers['Access-Control-Allow-Origin'] = "*"        
        res.headers['Access-Control-Allow-Methods'] = "GET"
        res.headers['Content-Type'] = 'application/json; charset=UTF-8'
    return res   
    
@app.route('/download', methods=['GET', 'POST'])
def run_download():
    view_id = request.args.get("view_id")
    select_sql = request.args.get("select_sql")
    filter_sql = request.args.get("filter_sql")    
    formato = request.args.get("formato")
    
    filename = str(view_id)
    if select_sql is not None:
        filename = filename + "_" + str(select_sql)
    if filter_sql is not None:
        filename = filename + "_" + str(filter_sql)
    if view_id is None:
        res = flask.Response("<b> view_id</b> is required.")
    elif view_id=="0" or not view_id.isdigit():
        res = flask.Response("<b> view_id</b> must be a number")
    elif formato is None or (formato.upper() not in ['CSV','JSON','XML']):
        res = flask.Response("<b> formato</b> must be CSV,JSON or XML")
    else:
        resultado =  ga_od_core.download(view_id,select_sql,filter_sql,formato);
        res = make_response(resultado)
        res.headers['Access-Control-Allow-Headers'] = "*"        
        res.headers['Access-Control-Allow-Origin'] = "*"        
        res.headers['Access-Control-Allow-Methods'] = "GET"
        if formato.upper() == "JSON":
            res.headers['Content-Type'] = 'application/json'
            res.headers['Content-Disposition'] = "attachment;filename=\"" + filename + "\""+".json"
        elif formato.upper() == 'XML':
            res.headers['Content-Type'] = 'text/xml,application/xml'
            res.headers['Content-Disposition'] = "attachment;filename=\"" + filename + "\""+".xml"
        elif formato.upper() == 'CSV':
            res.headers['Content-Type'] = 'text/csv'
            res.headers['Content-Disposition'] = "attachment;filename=\"" + filename + "\""+".csv"
        else:
            res = flask.Response(resultado)
    return res


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=50050, debug=configuracion.DEBUG_VAR)     