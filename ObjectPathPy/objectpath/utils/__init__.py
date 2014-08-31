#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,time,random,base64,re
from datetime import datetime, timedelta
from types import GeneratorType as generator
from itertools import chain

iterators=[list,generator,chain]
try:
	iterators+=[map]
except:
	pass
#if hasattr(random, 'SystemRandom'):
#	randrange=random.SystemRandom().randrange
#else:
#	randrange=random.randrange

#RE_PATH=re.compile("{\$([^}]+)}") # {$ foobar}
#RE_PATH_split=re.compile("{\$[^}]+}") # {$ foobar}

from itertools import islice

# islice=islice is an optimization
def skip(iterable, n, islice=islice):
	try:
		return next(islice(iterable, n, None))
	except StopIteration:
		raise IndexError("generator index out of range")

def py2JSON(o):
	if o is True:
		return 'true'
	if o is False:
		return 'false'
	if o is None:
		return 'null'
	#TODO - check if that is correct
	if type(o) is tuple:
		return list(o)
	elif type(o) in iterators+[list,str]:
		return o
	try:
		return str(o)
	except UnicodeEncodeError:
		return o.encode("utf8")
	except:
		return o

def str2obj(s):
	"""
		Converts string to an object.
		input: string
		returns: object which was converted or the same string's object representation as in input
	"""
	r=s.strip().lower()
	if r in ("true","t","y","yes"):
		return True
	elif r in ("false","f","no"):
		return False
	elif r in ("none","nil","null"):
		return None
	return s
