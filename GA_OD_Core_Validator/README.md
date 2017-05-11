# GA_OD_Core Validator
Se trata de un validador para la API [GA_OD_Core](https://github.com/aragonopendata/GA_OD_Core)

Ese script se hará valer de la API [GA_OD_Core](https://github.com/aragonopendata/GA_OD_Core) para descargase una muestra de todas las Vistas en formato .csv

Para ello usará la URL que nos devuelve todas las Vistas. (http://opendata.aragon.es/GA_OD_Core/views)

Y una por una irá descargando en formato csv, tantos registros como se indique en conf.URL_PARAMS.

El script creará un fichero (conf.FILE_ERRORS) con los errores obtenidos.

Creará una carpeta en el caso de que no exista, a nivel de donde estén los ficheros python con nombre similar a este *files2017-05-11 12:36:31.537557_PRO*, donde guardará los ficheros generados.

Para ejecutarlo, nos situaremos en la carpeta y ejecutamos:
```sh
$ python main.py
```
Se compone de 2 ficheros:

`main.py`
Es el fichero principal con la lógica

`conf.py`
Fichero con configuraciones, se describen a continuación las más susceptibles a ser modificadas:
```python
ENTORNO
```
Puede ser PRE o PRO, para apuntar al entorno de PREPRODUCCIÓN o PRODUCCIÓN.
```python
NUM_ROWS
```
Número de registros que descargará de cada tabla.
```python
DIRECTORY_DOWNLOAD
```
Nombre de la carpeta que creará en la ejecución de la app, que contendrá los ficheros csv descargados y el informe con los errores.
```python
FILE_ERRORS
```
Nombre del fichero con el informe de los errores y éxitos.
```python
ERRORS
ERRORS2
ERRORS3
```
Hay contempladas 3 respuestas de la API que sería consideradas error.