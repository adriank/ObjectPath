#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of ObjectPath released under MIT license.
# Copyright (C) 2010-2014 Adrian Kalbarczyk

from itertools import islice
from xml.sax.saxutils import escape, unescape
from objectpath.core import NUM_TYPES, generator, chain, ITER_TYPES

escape = escape
unescape = unescape
unescapeDict = {"&apos;": "'", "&quot;": "\""}
escapeDict = {"'": "&apos;", "\"": "&quot;"}

# islice=islice is an optimization
def skip(iterable, n, islice=islice):
  try:
    return next(islice(iterable, n, None))
  except StopIteration:
    return None
    # raise IndexError("generator index out of range")

def filter_dict(iterable, keys):
  """
	filters keys of each element of iterable
	$.(a,b) returns all objects from array that have at least one of the keys:
	[1,"aa",{"a":2,"c":3},{"c":3},{"a":1,"b":2}].(a,b) -> [{"a":2},{"a":1,"b":2}]
	"""
  if type(keys) is not list:
    keys = [keys]
  for i in iterable:
    try:
      d = {}
      for a in keys:
        try:
          d[a] = i[a]
        except KeyError:
          pass
      if d != {}:
        yield d
    except Exception:
      pass

def flatten(fragment, skip=False):
  def rec(frg):
    typefrg = type(frg)
    if typefrg in ITER_TYPES:
      for i in frg:
        for j in rec(i):
          yield j
    elif typefrg is dict:
      yield frg
      for i in frg.items():
        for j in rec(i[1]):
          yield j

  g = rec(fragment)
  if skip:
    for i in xrange(skip):
      g.next()
  for i in g:
    yield i
