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
	parser.add_argument('-o', '--file', dest='file', help='File containing JSON document.')
	parser.add_argument('-u', '--URL', dest='URL', help='URL containing JSON document.')
	parser.add_argument('-xml', dest='xml', help='Expect XML input.',action='store_true')
	parser.add_argument('-d', '--debug', dest='debug', help='Debbuging on/off.', action='store_true')

	args = parser.parse_args()
	a={}
	if args.debug:
		a["debug"]=True
	File=args.file or len(sys.argv) is 2 and sys.argv[1]
	if args.xml:
		from utils.xmlextras import xml2tree
	if File:
		tree=Tree(json.load(open(File,"r")),a)
		print "JSON document loaded from", File
	elif args.URL:
		from urllib2 import urlopen
		if args.xml:
			tree=Tree(json.loads(json.dumps(xml2tree(args.URL))),a)
			#print json.dumps(xml2tree(args.URL))
		else:
			tree=Tree(json.load(urlopen(args.URL)),a)
			print type(json.load(urlopen(args.URL)))
	else:
		print "JSON document source not specified. Creating ObjectPath interpreter for empty object {}."
		tree=Tree({},a)
	try:
		while True:
			try:
				#if fakeEnv.doDebug:
				#	print tree.tree
				r=tree.execute(raw_input(">>> "))
				if type(r) in (generator,chain):
					#if debug:
					#	print "returning",type(r).__name__
					print json.dumps(list(r))
				else:
					print json.dumps(r)
			except Exception,e:
				print e
	except KeyboardInterrupt:
		pass
	#new line at the end forces command prompt to apear at left
	print
