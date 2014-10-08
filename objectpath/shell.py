#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of ObjectPath released under AGPL v3 license.
# Copyright (C) 2010-2014 Adrian Kalbarczyk

import argparse
import sys
import readline
# this is to prevent various tools from deleting import readline
___x=readline.__doc__

from objectpath import Tree
from objectpath.utils.colorify import * # pylint: disable=W0614
from objectpath.utils import json_compat as json
from objectpath.utils.json_compat import printJSON

def main():
	parser=argparse.ArgumentParser(description='Command line options')
	parser.add_argument('-u', '--url', dest='URL', help='URL containing JSON document.')
	#parser.add_argument('-xml', dest='xml', help='[EXPERIMENTAL] Expect XML input.',action='store_true')
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
	#if args.xml:
	#	from utils.xmlextras import xml2tree
	src=False
	if args.URL:
		if sys.version_info.major >= 3:
			from urllib.request import Request,build_opener # pylint: disable=E0611
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
		#if args.xml:
		#	tree=Tree(json.loads(json.dumps(xml2tree(src))),a)
		#else:
		tree=Tree(json.load(src),a)
		if not expr: print(" "+bold("done")+".")

	if expr:
		print(json.dumps(tree.execute(expr)))
		exit()

	try:
		while True:
			try:
				if sys.version_info.major >= 3:
						r=tree.execute(input(">>> "))
				else:
						r=tree.execute(raw_input(">>> "))
				# python 3 raises error here - unicode is not a proper type there
				try:
					if type(r) is unicode:
						r=r.encode("utf8")
				except NameError:
					pass
				print(printJSON(r))
			except Exception as e:
				print(e)
	except KeyboardInterrupt:
		pass
	# new line at the end forces command prompt to apear at left
	print(bold("\nbye!"))

if __name__ == "__main__":
	main()
