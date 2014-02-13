#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.interpreter import *
import argparse
import readline,sys
from types import GeneratorType as generator
from itertools import chain
from utils import json_compat as json

print """ObjectPath interactive shell
	ctrl+c to exit.
"""
if __name__=="__main__":
	parser=argparse.ArgumentParser(description='Command line options')
	parser.add_argument('-o', '--objectFile', dest='object', help='File containing JSON object.')
	parser.add_argument('-d', '--debug', dest='debug', help='Debbuging on/off.', action='store_true')
	#parser.set_defaults(port = 9999, host='', appsDir=os.path.join(os.path.expanduser('~'),"projects"), appDir='', ACRconf='')
	args = parser.parse_args()
	a={}
	if args.debug:
		a["debug"]=True
	JSONfile=args.object or len(sys.argv) is 2 and sys.argv[1]
	if JSONfile:
		tree=Tree(json.load(open(JSONfile,"r")),a)
		print "JSON file loaded from", JSONfile
	else:
		print "JSON file not specified. Creating ObjectPath interpreter for empty object ({})."
		tree=Tree({},a)
	try:
		while True:
			#try:
				#if fakeEnv.doDebug:
				#	print tree.tree
				r=tree.execute(raw_input(">>> "))
				if type(r) in (generator,chain):
					#if debug:
					#	print "returning",type(r).__name__
					print json.dumps(list(r))
				else:
					print json.dumps(r)
			#except Exception,e:
				#print e
	except KeyboardInterrupt:
		pass
	#new line at the end forces command prompt to apear at left
	print
