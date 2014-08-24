#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.interpreter import *
import argparse
import sys
import readline
from utils.colorify import *
# from types import GeneratorType as generator
# from itertools import chain
from utils import json_compat as json

print """ObjectPath interactive shell
	ctrl+c to exit.
"""

def printJSON(o):
	depth=5
	length=2
	spaces=2

	def plus():
		currDepth[0]+=1

	def minus():
		currDepth[0]-=1

	def out(s):
		s=str(s)
		if not ret:
			ret.append(s)
		elif ret[-1][-1]=="\n":
			ret.append(currDepth[0]*spaces*" "+s)
		else:
			ret.append(s)

	def rec(o):
		if type(o) in ITER_TYPES:
			o=list(o)
			if currDepth[0]>=depth:
				out("<array of "+str(len(o))+" items>\n")
			out("[")
			if len(o) > 0:
				if len(o) > 1:
					out("\n")
					plus()
				for i in o[0:length]:
					rec(i)
					out(",\n")
				if o and not len(o)>length and type(o[0:length][-1]) is dict:
					plus()
				if len(o)>length:
					out("... ("+str(len(o)-length)+" more items)\n")
				else:
					ret.pop()
					if len(o) > 1:
						out("\n")
						minus()
				if len(o) > 1:
					minus()
			out("]")
			#return l

		if type(o) is dict:
			if currDepth[0]>depth:
				out("...\n")
			r={}
			keys=o.keys()
			out("{")
			if len(keys) > 0:
				plus()
				if len(keys) > 1:
					out("\n")
				for k in o.keys():
					out(string('"'+k+'"')+" = ")
					rec(o[k])
					#if type(o[k]) is list:
					#	plus()
					out(",\n")
				if len(keys) == 1:
					ret.pop()
					#out("}")
				else:
					ret.pop()
					out("\n")
					minus()
			out("}")
		else:
			if type(o) in [int,float]:
				out(const(o))
			elif o in [None, False, True]:
				out(const(py2JSON(o)))
			elif type(o) in STR_TYPES:
				out(string('"'+o+'"'))

	currDepth=[0]
	ret=[]
	rec(o)
	currDepth[0]=0
	return "".join(ret)

if __name__=="__main__":
	#print bold(printJSON({}))
	#print printJSON([None, False, True,'',"",2,2.0,{}])
	#exit()
	parser=argparse.ArgumentParser(description='Command line options')
	#parser.add_argument('-o', '--file', dest='file', help='File containing JSON document.')
	parser.add_argument('-u', '--url', dest='URL', help='URL containing JSON document.')
	parser.add_argument('-xml', dest='xml', help='[EXPERIMENTAL] Expect XML input.',action='store_true')
	parser.add_argument('-d', '--debug', dest='debug', help='Debbuging on/off.', action='store_true')
	parser.add_argument('file', metavar='FILE', nargs="?", help='File name')

	args = parser.parse_args()
	a={}
	if args.debug:
		a["debug"]=True
	File=args.file
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
		print "JSON document source not specified. Working with an empty object {}."
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
				print printJSON(r)
				#print json.dumps(r)
			except Exception,e:
				print e
	except KeyboardInterrupt:
		pass
	#new line at the end forces command prompt to apear at left
	print
