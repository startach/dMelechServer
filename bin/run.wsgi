#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/srv/src/dMelechServer/webapp')

from RestApi import app as application
