activate_this = '/usr/lib/ckan/default/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/var/www/wolfcms/GA_OD_Core')

#from run import app as application

#For debbugging ONLY
from werkzeug.debug import DebuggedApplication
from run import app as application
application = DebuggedApplication(application, evalex=True)
