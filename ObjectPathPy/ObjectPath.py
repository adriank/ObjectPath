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

def printJSON(o):
	def plus():
		depth[0]=depth[0]+1

	def minus():
		depth[0]=depth[0]-1

	def rec(o):
		plus()
		if type(o) is list:
			if depth[0]>5: return ["<array of "+str(len(o))+" items>"]
			l=[]
			for i in o[0:3]:
				l.append(rec(i))
				minus()
			if len(o)>5:
				l.append("<"+str(len(o)-3)+"more items>")
			return l
		if type(o) is dict:
			if depth[0]>3: return {}
			r={}
			for k in o.keys():
				r[k]=rec(o[k])
				minus()
			return r
		else:
			minus()
			return o

	depth=[0]
	r=rec(o)
	depth[0]=0
	return r

if __name__=="__main__":
	parser=argparse.ArgumentParser(description='Command line options')
	parser.add_argument('-o', '--file', dest='file', help='File containing JSON document.')
	parser.add_argument('-u', '--url', dest='URL', help='URL containing JSON document.')
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
		sys.stdout.write("Loading JSON document from "+File+"...")
		sys.stdout.flush()
		tree=Tree(json.load(open(File,"r")),a)
		print(" done.")
	elif args.URL:
		from urllib2 import urlopen
		if args.xml:
			tree=Tree(json.loads(json.dumps(xml2tree(args.URL))),a)
			#print json.dumps(xml2tree(args.URL))
		else:
			tree=Tree(json.load(urlopen(args.URL)),a)
	else:
		print "JSON document source not specified. Creating ObjectPath interpreter for empty object {}."
		tree=Tree({},a)
	try:
		while True:
			try:
				#if fakeEnv.doDebug:
				#	print tree.tree
				r=tree.execute(raw_input(">>> "))
				print json.dumps(printJSON(r))
				#print json.dumps(r)
			except Exception,e:
				print e
	except KeyboardInterrupt:
		pass
	#new line at the end forces command prompt to apear at left
	print
