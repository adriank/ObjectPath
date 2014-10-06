#!/usr/bin/env python

try:
	import json
except ImportError:
	try:
		import simplejson as json
	except ImportError:
		raise Exception("JSONNotFound")

load=json.load
def loads(s,object_hook=None):
	if s.find("u'")!=-1:
		s=s.replace("u'","'")
	s=s.replace("'",'"')
	try:
		return json.loads(s,object_hook=object_hook)
	except ValueError as e:
		raise Exception(str(e)+" "+s)

def dumps(s,default=None):
	return json.dumps(s,default=default, indent=2, separators=(',',':'))
dump=json.dump
