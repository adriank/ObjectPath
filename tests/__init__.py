#!/usr/bin/env python
# -*- coding: utf-8 -*-
#unit tests for ACR functions

from .test_ObjectPath import op_test
from .test_utils import utils_test

import unittest

def doTests():
	print ('Started ObjectPath Python implementation testing.\n')
	#print ('utils/interpreter.py')
	unittest.TextTestRunner(verbosity = 2).run(op_test)
	unittest.TextTestRunner(verbosity = 2).run(utils_test)
