# -*- coding: utf-8 -*-
"""
@author: Miquel Quetglas
@author: AMS
@version: 1.0 (04/01/2017)
"""
import datetime
#ENTORNO can be PRE or PRO
ENTORNO='PRE'
if ENTORNO=='PRE':
	URL='http://preopendata.aragon.es/GA_OD_Core/'
elif ENTORNO=='PRO':
	URL='http://opendata.aragon.es/GA_OD_Core/'
URL_DOWNLOAD='download?view_id='
URL_VIEWS= 'views'
NUM_ROWS=100
URL_PARAMS='&formato=csv&_pageSize='+str(NUM_ROWS)+'&_page=1'
DIRECTORY_DOWNLOAD='files' +str(datetime.datetime.now()) + '_' + ENTORNO +'/'
FILE_ERRORS='errors.txt'
ERRORS='does not exist'
ERRORS2= 'Something is wrong'
ERRORS3= 'Something went wrong'
