# -*- coding: utf-8 -*-
"""
@author: Miquel Quetglas
@author: AMS
@version: 1.0 (04/01/2017)
@description: Ese script se hará valer de la API GA_OD_Core para descargase todas las Vistas en formato .csv
Para ello usará la URL que nos devuelve todas las Vistas. (http://opendata.aragon.es/GA_OD_Core/views)
Y una por una irá descargando en formato csv, tantos registros como se indique en conf.URL_PARAMS.
El script creará un fichero (conf.) con los errores obtenidos.
"""

import conf as conf
import sys
import requests
import os
import json


def download_file(url,id_view):
	local_filename = (url.split('?')[1]).split('&')[0] + '.csv'
	# NOTE the stream=True parameter
	r = requests.get(url, stream=True)
	if conf.ERRORS in r.text or conf.ERRORS2 in r.text or conf.ERRORS3 in r.text:
		print 'La VISTA ' + str(id_view) + ' FALLA'
		errors.append(id_view)
	with open(conf.DIRECTORY_DOWNLOAD + local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
				#f.flush()
	return local_filename


def create_id_list():
	r = requests.get(conf.URL + conf.URL_VIEWS)
	json_data = json.loads(r.text)
	num_list = []
	for x in json_data:
		num_list.append(x[0])
	return num_list


if __name__ == '__main__':
	global errors
	errors = []
	if not os.path.exists(conf.DIRECTORY_DOWNLOAD):
		os.makedirs(conf.DIRECTORY_DOWNLOAD)
	file_errors = open(conf.DIRECTORY_DOWNLOAD + conf.FILE_ERRORS,'w')
	
	for x in create_id_list():
		print '... DeScArGaNdO vista ' + str(x) + ' ...'
		download_file(conf.URL + conf.URL_DOWNLOAD + str(x) + conf.URL_PARAMS,x)

	for t in errors:
		file_errors.write('VISTA ' + str(t) + ' FALLA - ' + conf.URL + conf.URL_DOWNLOAD + str(t) + conf.URL_PARAMS + '\n')
		print 'VISTA ' + str(t) + ' FALLA - ' + conf.URL + conf.URL_DOWNLOAD + str(t) + conf.URL_PARAMS