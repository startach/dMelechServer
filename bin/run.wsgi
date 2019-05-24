#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/srv/dMelechServer/webapp')

from RestApi import app as application
