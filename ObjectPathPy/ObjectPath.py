#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.interpreter import *
import argparse
import sys
import readline
# from types import GeneratorType as generator
# from itertools import chain
from utils import json_compat as json

print """ObjectPath interactive shell
	ctrl+c to exit.
"""

def printJSON(o):
	depth=5
	length=3
	def plus():
		currDepth[0]+=1

	def minus():
		currDepth[0]-=1

	def rec(o):
		plus()
		if type(o) is list:
			if currDepth[0]>depth: return ["<array of "+str(len(o))+" items>"]
			l=[]
			for i in o[0:length]:
				l.append(rec(i))
				minus()
			if len(o)>length:
				l.append("<"+str(len(o)-length)+"more items>")
			return l
		if type(o) is dict:
			if currDepth[0]>depth: return {}
			r={}
			for k in o.keys():
				r[k]=rec(o[k])
				minus()
			return r
		else:
			minus()
			return o

	currDepth=[0]
	r=rec(o)
	currDepth[0]=0
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
	File=args.file or sys.argv[-1]
	if args.xml:
		from utils.xmlextras import xml2tree
	src=False
	if args.URL:
		from urllib2 import Request,build_opener
		request=Request(args.URL)
		opener = build_opener()
		request.add_header('User-Agent', 'ObjectPath/1.0 +http://objectpath.org/')
		src=opener.open(request)
	elif File:
		src=open(File,"r")
	if not src:
		print "JSON document source not specified. Creating ObjectPath interpreter for empty object {}."
		tree=Tree({},a)
	else:
		sys.stdout.write("Loading JSON document from "+str(args.URL or File)+"...")
		sys.stdout.flush()
		if args.xml:
			tree=Tree(json.loads(json.dumps(xml2tree(src))),a)
		else:
			tree=Tree(json.load(src),a)
		print(" done.")
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
