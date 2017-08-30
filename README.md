# GA_OD_Core API


GA_OD_Core se trata de un API creada con la finalidad de poder obtener datos de determinadas conjuntos de datos servidos actualmente a través del portal Aragón Open Data (http://opendata.aragon.es) en formatos json, xml y csv
Con esta API pretendemos dar la oportunidad a desarrolladores y usuarios de consultar estos datos de forma que estén actualizados y preparados para ser usados en otras aplicaciones o servicios mediante la arquitectura REST.

Se encuentra alojada en:
http://opendata.aragon.es/GA_OD_Core/

Se puede acceder a su manual gráfico a través de la siguiente URL:
http://opendata.aragon.es/GA_OD_Core/ui/


## Operaciones

#### Views
###### Visualiza todas las vistas disponibles en base de datos.
http://<i></i>opendata.aragon.es/GA_OD_Core/views

#### Show Columns
###### Visualiza  las columnas de una tabla
http://<i></i>opendata.aragon.es/GA_OD_Core/show_columns?view_id={view_id}

#### Preview
###### Visualiza una consulta contra una de las vistas disponibles.
http://<i></i>opendata.aragon.es/GA_OD_Core/preview?view_id={view_id}&select_sql={select_sql}&filter_sql={filter_sql}

#### Download
###### Descarga un fichero en formato XML, JSON o CSV.
http://<i></i>opendata.aragon.es/GA_OD_Core/download?view_id={view_id}&select_sql={select_sql}&filter_sql={filter_sql}&formato={formato}



## Instalación
Para desplegar GA_OD_Core en nuestra máquina tenemos que seguir los siguientes puntos:
- Descargar y extraer la carpeta GA_OD_Core en nuestro servidor virtual (xammp, wamp, etc.) o el directorio por defecto del Apache de la máquina.

- Instalar python2.7 y los módulos necesarios (ver  Dependencias)

- Creamos nuestra Tabla / Vista en donde listaremos las Vistas que tenemos disponibles para consultar. (Si tenemos la información sobre la conectividad a la tabla no será necesario realizar modificaciones.)

- Modificamos los siguientes ficheros 

    - `conf.py`
    Añadimos los credenciales de nuestra base de datos y las cadenas de conexión que     vayamos a utilizar.
    Importante cambiar las variables APP_PATH y CUSTOM_LOG por la ruta a nuestro     directorio.
    Importante también la variable OPEN_VIEWS, la cual hace referencia al nombre de la tabla o vista que hemos creado en el punto 3.

    - `conexiones.py`
    Añadimos los Objetos de tipo ConexionDB con los credenciales, cadena de conexión y     tipo de Base de Datos todo esto, relacionándolo con el campo BASEDATOS de la Vista     previamente creada en el punto 3. (Si tenemos la información de conectividad a las     Bases de Datos no será necesario modificar nada)

- Situados dentro de la carpeta ejecutar por consola 
    ```
    python run.py
    ```
    Podemos modificar el fichero run.py, para cambiar el puerto en el que hacer correr la API, de lo contrario lo hará en el 50050.

- Abrimos el navegador la siguiente ruta: http://localhost:50050/ y vemos que funciona correctamente si nos muestra “index page”
Será posible realizar consultas ya sirviéndonos de las URL listadas en el punto 4 de este documento.

- Para hacer uso del manual gráfico, se ha incluido en la carpeta todo lo necesario.
Para el funcionamiento del manual gráfico será necesario modificar los siguientes * ficheros:
     - `swagger/index.html`
    	Poner la url hasta nuestro archivo swagger.json
	```
	var url = "http://localhost/GA_OD_Core/swagger/swagger.json";
	```
	
    -  `swagger/swagger.json`
    	Poner el host y el path para acceder por URL a la interfaz gráfica del Swagger.
    	
        ```
        host: "localhost:50050",
        "basePath": "/"
        ```
- A través de http://localhost/GA_OD_Core/swagger/ veremos el manual, que podemos modificar desde /swagger/swagger.json

- (Opcional) El API contiene un .wsgi, con el que podemos arrancar el python run.py automáticamente, añadiendo a nuestro httpd.conf lo siguiente:
   ```sh
   #GA_OD_Core - Deploy as a daemon
   WSGIScriptAlias /GA_OD_Core {nuestra_ruta}/GA_OD_Core/run.wsgi
   WSGIDaemonProcess ga_od_core display-name=ga_od_core
   WSGIProcessGroup ga_od_core
   #GA_OD_Core API
   Alias /GA_OD_Core/ui {nuestra_ruta}/GA_OD_Core/swagger
   ```
#
#
#


---
#

### v1.1:
- Añadida funcionalidad para consultar Vistas de tipo google_analytics
- Modificados los logs sean rotativos y con máximo de 5MB de tamaño de archivo
- Con esta versión PRO escribira logs pero no dará información por pantalla
- Condicionar según variable ENTORNO en fichero de configuración alguna conexión a base de datos para simplificar el despliegue en diferentes entornos
- Traducción de algunos comentarios que quedaban en castellano
- Limpieza de líneas comentadas en código

---
#

### v1.2:
- Añadidos 2 campos, _page y _pageSize para paginar las consultas en los métodos 'preview' y 'download', _pageSize limita el número de registros que devuelve la consulta y _page el número de página devuelto.
- Añadidos control de errores para evitar errores 500.
- Mejora de algunos logs para dar mas información en caso de que se produzca un error.
- Mejora en la creación de ficheros CSV.
- Corregidos problemas causados por la codificación de caráteres en alguna tabla.

---
#

### v1.2.1:
- Añadida aplicación independiente "GA_OD_Core Validator" para validar las URLs de la API
- Añadidos logs relacionados con conexión a Base de datos.

---
#

### v1.2.2:
- Tipo de dato de _page corregido.