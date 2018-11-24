#!/usr/bin/env python
try:
  import simplejson as json
except ImportError:
  try:
    import json
  except ImportError:
    raise Exception("JSONNotFound")
try:
  import ujson as json_fast
except ImportError:
  json_fast = json

from types import GeneratorType as generator

from objectpath.core import ITER_TYPES, STR_TYPES, NUM_TYPES
from objectpath.utils.colorify import *  # pylint: disable=W0614

load = json_fast.load

def loads(s):
  if s.find("u'") != -1:
    s = s.replace("u'", "'")
  s = s.replace("'", '"')
  try:
    return json_fast.loads(s)  # ,object_hook=object_hook)
  except ValueError as e:
    raise Exception(str(e) + " " + s)

def default(obj):
  if isinstance(obj, generator):
    return list(obj)

def dumps(s, default=default, indent=None):
  return json.dumps(s, default=default, indent=indent, separators=(',', ':'))

dump = json.dump

def py2JSON(o):
  if o is True:
    return 'true'
  if o is False:
    return 'false'
  if o is None:
    return 'null'
  if type(o) in NUM_TYPES:
    return o
  # TODO - check if that is correct
  if type(o) is tuple:
    return list(o)
  elif type(o) in ITER_TYPES + [list, str]:
    return o
  try:
    return str(o)
  except UnicodeEncodeError:
    return o.encode("utf8")
  except Exception:
    return o

LAST_LIST = None

def printJSON(o, length=5, depth=5):
  spaces = 2

  def plus():
    currIndent[0] += 1

  def minus():
    currIndent[0] -= 1

  def out(s):
    try:
      s = str(s)
    except Exception:
      pass
    if not ret:
      ret.append(s)
    elif ret[-1][-1] == "\n":
      ret.append(currIndent[0]*spaces*" " + s)
    else:
      ret.append(s)

  def rec(o):
    if type(o) in ITER_TYPES:
      o = list(o)
      if currDepth[0] >= depth:
        out("<array of " + str(len(o)) + " items>")
        return
      out("[")
      if len(o) > 0:
        if len(o) > 1:
          out("\n")
          plus()
        for i in o[0:length]:
          rec(i)
          out(",\n")
        if length is -1:
          rec(o[-1])
          out(",\n")

        if length is not -1 and len(o) > length:
          out("... (" + str(len(o) - length) + " more items)\n")
        else:
          ret.pop()
          if len(o) > 1:
            out("\n")
        if len(o) > 1:
          minus()
      out("]")

    elif type(o) is dict:
      currDepth[0] += 1
      if currDepth[0] > depth:
        out("{...}")
        return
      keys = o.keys()
      out("{")
      if len(keys) > 0:
        if len(keys) > 1:
          plus()
          out("\n")
        for k in o.keys():
          out(string('"' + str(k) + '"') + ": ")
          rec(o[k])
          out(",\n")
        ret.pop()
        if len(keys) > 1:
          minus()
          out("\n")
      out("}")
    else:
      if type(o) in NUM_TYPES:
        out(const(o))
      elif o in [None, False, True]:
        out(const(py2JSON(o)))
      elif type(o) in STR_TYPES:
        out(string('"' + o + '"'))
      else:
        out(string(o))
    currDepth[0] -= 1

  currIndent = [0]
  currDepth = [0]
  ret = []
  rec(o)
  currIndent[0] = 0
  currDepth[0] = 0
  return "".join(ret)
