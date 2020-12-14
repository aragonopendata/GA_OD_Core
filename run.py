# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26

@author: Miquel Quetglas
@author: AMS
@version: 1.2 (20/10/2016)
"""
from flask import Flask
import ga_od_core
from flask import request
import conf as configuracion
# import connexion

from urllib.parse import quote
import flask
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
from flask import make_response

app = Flask(__name__)


#For debbugging ONLY if True
if configuracion.ENTORNO == 'PRO':
    app.debug = False
else:
    app.debug = True

from werkzeug.debug import DebuggedApplication
application = DebuggedApplication(app, evalex=configuracion.DEBUG_VAR)

class MetaSingleton(type):
    instance = None
    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(MetaSingleton, cls).__call__(*args, **kw)
        return cls.instance

class PoolManager(object):
    __metaclass__ = MetaSingleton


    def __init__(self):
        self.pool = None

    def create_pool(self, count=4):
        self.pool = multiprocessing.Pool(processes=count)

    def use_worker(self, func, params, tout=1): 
        result = self.pool.apply_async(func, params)    
        return result.get(timeout=tout)           

    def map_workers(self, func, params):
        return self.pool.map(func, params)

    def get_pool(self):
        return self.pool

    
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
        responseJson = ga_od_core.show_columns(view_id)
        res = make_response(responseJson)
        if 'wrong' in responseJson:
            res = flask.Response("Error", 201)
            
        res.headers['Access-Control-Allow-Headers'] = "*"        
        res.headers['Access-Control-Allow-Origin'] = "*"        
        res.headers['Access-Control-Allow-Methods'] = "GET"
        res.headers['Content-Type'] = 'application/json; charset=UTF-8'
    return res 

    
@app.route('/preview', methods=['GET', 'POST'])
def run_preview():
        
    view_id = request.args.get("view_id")
    _pageSize = request.args.get("_pageSize")
    _page = request.args.get("_page")
    if view_id is None:
        res = flask.Response("<b> view_id</b> is required.")
    elif view_id=="0" or not view_id.isdigit():
        res = flask.Response("<b> view_id</b> must be a number")
    #elif _pageSize is None:
        #res = flask.Response("<b> _pageSize</b> is required.")
    #elif _page is None:
        #res = flask.Response("<b> _page</b> is required.")
    else:      
        select_sql = request.args.get("select_sql")
        filter_sql = request.args.get("filter_sql")
        res = make_response(ga_od_core.preview(view_id,select_sql,filter_sql,_page,_pageSize))
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
    _pageSize = request.args.get("_pageSize")
    _page = request.args.get("_page")
    name = request.args.get("nameRes")
    filename = ""
    if name is None:
        filename = filename + "view_id_" + str(view_id)
    #if select_sql is not None:
    #    filename = filename + "_" + str(select_sql)
    #if filter_sql is not None:
    #    filename = filename + "_" + str(filter_sql)

    if name is not None:
        filename = name
    if view_id is None:
        res = flask.Response("<b> view_id</b> is required.")
    elif view_id=="0" or not view_id.isdigit():
        res = flask.Response("<b> view_id</b> must be a number")
    elif formato is None or (formato.upper() not in ['CSV','JSON','XML']):
        res = flask.Response("<b> formato</b> must be CSV,JSON or XML")
    #elif _pageSize is None:
        #res = flask.Response("<b> _pageSize</b> is required.")
    #elif _page is None:
        #res = flask.Response("<b> _page</b> is required.")
    else:
	#udata = filename.decode("utf-8")
	#filename = udata.encode("ascii","ignore") 
        resultado =  ga_od_core.download(view_id,select_sql,filter_sql,formato,_page,_pageSize);
        res = make_response(resultado)
        res.headers['Access-Control-Allow-Headers'] = "*"        
        res.headers['Access-Control-Allow-Origin'] = "*"        
        res.headers['Access-Control-Allow-Methods'] = "GET"
        if formato.upper() == "JSON":
            res.headers['Content-Type'] = 'application/json'
            filename = filename + ".json"
            res.headers["Content-Disposition"] = "attachment;filename={ascii_filename};" \
            "filename*=UTF-8''{utf_filename}".format(
                ascii_filename=quote(filename),
                utf_filename=quote(filename)
            )
        elif formato.upper() == 'XML':
            res.headers['Content-Type'] = 'text/xml,application/xml'
            filename = filename + ".xml"
            res.headers["Content-Disposition"] = "attachment;filename={ascii_filename};" \
            "filename*=UTF-8''{utf_filename}".format(
                ascii_filename=quote(filename),
                utf_filename=quote(filename)
            )
        elif formato.upper() == 'CSV':
            res.headers['Content-Type'] = 'text/csv'
            filename = filename + ".csv"
            res.headers["Content-Disposition"] = "attachment;filename={ascii_filename};" \
            "filename*=UTF-8''{utf_filename}".format(
                ascii_filename=quote(filename),
                utf_filename=quote(filename)
            )
        else:
            res = flask.Response(resultado)
    return res


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=50058, debug=configuracion.DEBUG_VAR)