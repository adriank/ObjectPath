#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Asyncode Runtime - XML framework allowing developing internet
# applications without using programming languages.
# Copyright (C) 2008-2010  Adrian Kalbarczyk

# This program is free software: you can redistribute it and/or modify
# it under the terms of the version 3 of GNU General Public License as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#TODO; remove tpath
#@marcin: functions docstrings

from xml.sax import make_parser, handler
from xml.sax.saxutils import escape, unescape
#from ACR.errors import Error
import re
from datetime import datetime, date, time
from types import GeneratorType as generator
from itertools import chain

#DONTDO do not change that to tuple
iterators=[list,generator,chain]

RE_ATTR=re.compile("'([^']+)': '?([^',]*)'?,*")
unescapeDict={"&apos;":"'","&quot;":"\""}
escapeDict={"'":"&apos;","\"":"&quot;"}

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

class ObjectTree(tuple):
	def __init__(self,seq):
		tuple.__init__(seq)

	def get(self,path,default=None):
		return tpath(self,path,default)

#TO-C
def escapeQuotes(s):
	"""
	Escapes characters '<', '>', '\'', '"', '&' to HTML entities.
	input: string
	returns: string with escaped characters
	"""
	return escape(unescape(s,unescapeDict),escapeDict)

def unescapeQuotes(s):
	"""
	Unescapes HTML entities to '<', '>', '\'', '"', '&'
	input: string
	returns: string with escaped characters
	"""
	return unescape(s,unescapeDict)

#def serialize(value,doEscape=False):
#	typev=type(value)
#	if typev is str:
#		sI=value
#		return sI
#	elif typev is datetime:
#		return value.strftime("%A, %d %B %Y, %X")
#	else:
#		return str(value)

def tree2xml(root,esc=False):
	"""
	Converts dict/list or tuple tree to a xml. Dict/list and tuple trees cannot be mixed at this time.
	input: (dict|list|tuple) a tree root/a fragment (list of dicts)
	returns: an xml fragment
	"""
	def tuplerec(node):
		if type(node) is not tuple:
			node=py2JSON(node)
		if type(node) is str:
			if esc:
				node=escapeQuotes(node)
			if not node.strip():
				tab.append(" ")
			else:
				tab.append(node)
			return
		tab.append("<"+node[0])
		if node[1]:
			for i in node[1].iteritems():
				tab.append(" %s=\"%s\""%(i[0],escapeQuotes(i[1])))
		if node[2]:
			tab.append(">")
			for i in node[2]:
				tuplerec(i)
			tab.append("</"+node[0]+">")
		else:
			tab.append("/>")

	def rec(node,name=None):
		attrs={}
		#if type(node) is chain:
		#	print list(node)
		#	print
		nodetype=type(node)
		if nodetype is dict:
			tag="object"
			for i in node.keys():
				if i[0]=='@':
					attrs[i[1:]]=escapeQuotes(str(node.pop(i)))
		elif nodetype in iterators:
			tag="list"
		else:
			if nodetype in (datetime,date,time):
				d={
					"type":nodetype.__name__
				}
				try:
					dt={
						"year":node.year,
						"month":node.month>9 and node.month or '0'+str(node.month),
						"day":node.day>9 and node.day or '0'+str(node.day)
					}
					d.update(dt)
				except: pass
				try:
					d["hour"]=node.hour
					d["minute"]=node.minute>9 and node.minute or '0'+str(node.minute)
					d["second"]=node.second>9 and node.second or '0'+str(node.second)
					d["ms"]=node.microsecond
				except: pass
				#maybe it can be done more efficently with datetime fmt functions
				tab.append("<"+name+" "+" ".join(map(lambda i: i[0]+"=\""+str(i[1])+"\"",d.iteritems()))+"/>")
				return
			if nodetype not in (str,unicode):
				node=py2JSON(node)
			if esc:
				node=escapeQuotes(node)
			if name:
				tab.append('<%s>%s</%s>'%(name,node,name))
			else:
				tab.append(node)
			return
		if name:
			attrs["name"]=name
		tab.append("<"+tag)
		if attrs and len(attrs)>0:
			for i in attrs.iteritems():
				tab.append(" %s=\"%s\""%(i[0],escapeQuotes(i[1])))
		nodes=[]
		if not node:
			tab.append("/>")
		else:
			tab.append(">")
			if type(node) is dict:
				for i in node.iteritems():
					rec(i[1],i[0])
			if type(node) in iterators:
				for i in node:
					if type(i) in [dict]+iterators:
						rec(i)
					else:
						try:
							i=py2JSON(i)
						except:
							i=i.encode("utf8")
						if esc:
							i=escapeQuotes(i)
						tab.append("<item>%s</item>"%i)
			tab.append("</"+tag+">")

	#if D: log.info("Generating XML")
	if type(root) is dict:
		tab=["<list>"]
		#this is an exception. We want to have <object/>'s with name in root subnodes.
		for i in root.iteritems():
			if type(i[1]) in (str,unicode):
				tab.append('<object name="%s">%s</object>'%i)
			else:
				rec(i[1],i[0])
		tab.append("</list>")
	elif type(root) is list:
		tab=[]
		rec(root)
	elif type(root) is tuple:
		tab=[]
		tuplerec(root)
	else:
		tab=[root]
	#XXX delete it!!!
	for i in range(len(tab)):
		if type(tab[i]) is unicode:
			tab[i]=tab[i].encode("utf-8")
	ret="".join(tab)
	if type(ret) is unicode:
		ret=ret.encode("utf-8")
	return ret

#TODO whitespaces checkup and W3C spec verification of whitespace handling in XML and (X)HTML.
class Reader(handler.ContentHandler):
	def __init__(self,newlines,preserveCase=True):
		self.root=None
		self.newlines=newlines
		self.path=[]
		self.preserveCase=preserveCase

	def startElement(self, name, a):
		attrs=None
		if len(a)>0:
			attrs={}
			for i in a.keys():
				attrs[str(i)]=a[i].strip().encode("utf-8")
		if not self.preserveCase:
			name=name.lower()
		if not len(self.path):
			self.root=ObjectTree([name,attrs,[]])
			self.path.append(self.root)
		else:
			l=self.path[-1]
			l[2].append((name,attrs,[]))
			self.path.append(l[2][-1])

	def characters(self,data):
		l=len(data.strip())
		if l>0:
			self.path[-1][2].append(data.encode("utf-8").replace("\t",""))
		elif self.newlines and len(data)==1 and data[0]=="\n":
			self.path[-1][2].append("\n")
		#TODO make it work with ANY whitespaces in XML files
		elif len(data)==1 and data[0] not in ["\t","\n"]:
			self.path[-1][2].append(" ")
		elif " " in data:
			self.path[-1][2].append(" ")

	def endElement(self,x):
		subelems=[]
		lines=[]
		elem=self.path[-1][2]
		for i in elem:
			if type(i) is tuple:
				if len(lines):
					subelems.append("".join(lines))
					lines=[]
				subelems.append(i)
			elif type(i) is str:
				lines.append(i)
		if len(lines):
			subelems.append("".join(lines))
		elem[0:len(elem)]=subelems
		self.path.pop()

def xml2tree(xmlfile,newlines=False,preserveCase=True):
	"""
	Parses xml resource to xml tree.
	input:
		- xmlfile - xml file or url resource
		- newlines - preserve newlines?
		- preserveCase - if true all tags will be lowercased
	returns: xml tree
	"""
	parser=make_parser(['prixx'])
	r=Reader(newlines,preserveCase)
	parser.setContentHandler(r)
	parser.parse(xmlfile)
	return r.root

def tpath(root,path, default=None):
	t=path.split("/")
	try:
		t.pop(0)
		ret=root
		if t:
			for i in t:
				if type(ret) is list:
					ret=ret[0]
				splitter=i.find("[")
				_filter=None
				if splitter>0:
					_filter=i[splitter+1:-1].strip()
					i=i[0:splitter]
				if i=="*":
					ret=ret[2]
				if i=="text()":
					ret=list(filter(lambda x: type(x[0]) is str,ret[2]))
				else:
					tags=i.split("|")
					ret=list(filter(lambda x: x[0] in tags, ret[2]))
				if _filter:
					if _filter.isdigit():
						ret=ret[int(filter)]
					elif _filter[0] is "@":
						t=_filter[1:].split("=")
						if len(t)>1:
							ret=list(filter(lambda x: x[1].get(attr,"ERROR")==t[1],ret))[0]
						else:
							if t[0]=="*":
								return ret[0][1]
							return ret[0][1][t[0]]
	except (AttributeError, KeyError, TypeError,IndexError),e:
		return default
	return ret

def NS2Tuple(s,delimiter=":"):
	"""
	Splits tag to namespace and name.
	input: tag name in format "ns:name"
	returns: tuple (namespace, name)
	"""
	try:
		ns,action=s.split(delimiter,1)
	except:
		ns,action=(None,s)
	return (ns,action)
