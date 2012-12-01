#!/usr/bin/env python
# -*- coding: utf-8 -*-
#unit tests for ACR functions

from test_ObjectPath import utils_interpreter

import unittest

def doTests():
	print 'Started ObjectPath Python implementation testing.\n'
	print '\nutils/interpreter.py'
	unittest.TextTestRunner(verbosity = 2).run(utils_interpreter)
