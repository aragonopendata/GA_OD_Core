activate_this = '/data/apps/ckan/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/data/apps/GA_OD_Core')

#from run import app as application

#For debbugging ONLY
from werkzeug.debug import DebuggedApplication
from run import app as application
application = DebuggedApplication(application, evalex=True)
