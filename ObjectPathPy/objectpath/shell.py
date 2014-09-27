#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import readline

from objectpath import *
from objectpath.utils.colorify import *
from objectpath.utils import json_compat as json

LAST_LIST=None

def printJSON(o, length=5,depth=5):
	spaces=2

	def plus():
		currDepth[0]+=1

	def minus():
		currDepth[0]-=1

	def out(s):
		try:
			s=str(s)
		except:
			pass
		if not ret:
			ret.append(s)
		elif ret[-1][-1]=="\n":
			ret.append(currDepth[0]*spaces*" "+s)
		else:
			ret.append(s)

	def rec(o):
		if type(o) in ITER_TYPES:
			if length is not -1 and type(o) is pymongo.cursor.Cursor:
				x=list(o[0:length+1])
				#o.close()
				o=x
			else:
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
				#if len(o)<=length and type(o[0:length][-1]) is dict:
				#	plus()
				if length is not -1 and len(o)>length:
					out("... ("+str(len(o)-length)+" more items)\n")
				else:
					ret.pop()
					if len(o) > 1:
						#minus()
						out("\n")
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
				if len(keys) > 1:
					plus()
					out("\n")
				for k in o.keys():
					out(string('"'+str(k)+'"')+": ")
					rec(o[k])
					#if type(o[k]) is list:
					#	plus()
					out(",\n")
				ret.pop()
				if len(keys) > 1:
					minus()
					out("\n")
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

def main():
	parser=argparse.ArgumentParser(description='Command line options')
	#parser.add_argument('-o', '--file', dest='file', help='File containing JSON document.')
	parser.add_argument('-u', '--url', dest='URL', help='URL containing JSON document.')
	parser.add_argument('-xml', dest='xml', help='[EXPERIMENTAL] Expect XML input.',action='store_true')
	parser.add_argument('-d', '--debug', dest='debug', help='Debbuging on/off.', action='store_true')
	parser.add_argument('-e', '--expr', dest='expr', help='Expression/query to execute on file, print on stdout and exit.')
	parser.add_argument('file', metavar='FILE', nargs="?", help='File name')

	args = parser.parse_args()
	a={}
	expr=args.expr

	if not expr: print(bold("ObjectPath interactive shell")+"\n"+bold("ctrl+c")+" to exit, documentation at "+const("http://adriank.github.io/ObjectPath")+".\n")

	if args.debug:
		a["debug"]=True
	File=args.file
	if args.xml:
		from utils.xmlextras import xml2tree
	src=False
	if args.URL:
		if sys.version >= '3':
			from urllib.request import Request,build_opener
		else:
			from urllib2 import Request,build_opener
		request=Request(args.URL)
		opener = build_opener()
		request.add_header('User-Agent', 'ObjectPath/1.0 +http://objectpath.org/')
		src=opener.open(request)
	elif File:
		src=open(File,"r")
	if not src:
		if not expr:print ("JSON document source not specified. Working with an empty object {}.")
		tree=Tree({},a)
	else:
		if not expr: sys.stdout.write("Loading JSON document from "+str(args.URL or File)+"...")
		sys.stdout.flush()
		if args.xml:
			tree=Tree(json.loads(json.dumps(xml2tree(src))),a)
		else:
			tree=Tree(json.load(src),a)
		if not expr: print(" "+bold("done")+".")

	if expr:
		print(json.dumps(tree.execute(expr)))
		exit()

	try:
		while True:
				limitResult=5
			#try:
				if sys.version >= '3':
					r=input(">>> ")
				else:
					r=raw_input(">>> ")

				if r.startswith("all"):
					limitResult=-1
					r=tree.execute(r[3:].strip())
				else:
					r=tree.execute(r)
				#python 3 raises error here - unicode is not a proper type there
				try:
					if type(r) is unicode:
						r=r.encode("utf8")
				except NameError:
					pass
				print(printJSON(r,length=limitResult))
			#except Exception as e:
				#print(e)
	except KeyboardInterrupt:
		pass
	#new line at the end forces command prompt to apear at left
	print(bold("\nbye!"))
