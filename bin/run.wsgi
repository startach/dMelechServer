#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
# sys.path.insert(0,"/var/www/minyaneto/")
sys.path.insert(0, '/var/www/dmelech')


#from main import app as application
from RestApi import app as application