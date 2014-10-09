#!/usr/bin/env python
# -*- coding: utf-8 -*-

from types import GeneratorType as generator
from itertools import chain

iterators=[list,generator,chain]
try:
	iterators+=[map, filter]
except NameError:
	pass

from itertools import islice
from xml.sax.saxutils import escape, unescape

escape=escape
unescape=unescape
unescapeDict={"&apos;":"'","&quot;":"\""}
escapeDict={"'":"&apos;","\"":"&quot;"}

# islice=islice is an optimization
def skip(iterable, n, islice=islice):
	try:
		return next(islice(iterable, n, None))
	except StopIteration:
		return None
		#raise IndexError("generator index out of range")

def filter_dict(iterable, keys):
	"""
	filters keys of each element of iterable
	"""
	if type(keys) is not list:
		keys=[keys]
	for i in iterable:
		try:
			d={}
			for a in keys:
				d[a]=i[a]
			yield d
		except Exception:
			pass

def flatten(fragment,skip=False):
	def rec(frg):
		typefrg=type(frg)
		if typefrg in (list,generator,chain):
			for i in frg:
				for j in rec(i):
					yield j
		elif typefrg is dict:
			yield frg
			for i in frg.items():
				for j in rec(i[1]):
					yield j

	g=rec(fragment)
	if skip:
		for i in xrange(skip):
			g.next()
	for i in g:
		yield i

def py2JSON(o):
	if o is True:
		return 'true'
	if o is False:
		return 'false'
	if o is None:
		return 'null'
	# TODO - check if that is correct
	if type(o) is tuple:
		return list(o)
	elif type(o) in iterators+[list,str]:
		return o
	try:
		return str(o)
	except UnicodeEncodeError:
		return o.encode("utf8")
	except Exception:
		return o
