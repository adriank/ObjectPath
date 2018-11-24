#!/usr/bin/env python

# This file is part of ObjectPath released under MIT license.
# Copyright (C) 2010-2014 Adrian Kalbarczyk

# Code from http://effbot.org/zone/simple-top-down-parsing.htm was used in this file.
# Licence of the code is public domain.
# Relicenced to AGPL v3 by Adrian Kalbarczyk and:
# - specialized to work with ObjectPath,
# - optimized

import sys

if sys.version_info[0] >= 3:
  from io import StringIO
else:
  from cStringIO import StringIO

from objectpath.core import SELECTOR_OPS, NUM_TYPES

symbol_table = {}
token = nextToken = None
# TODO optimization ('-',1) -> -1
# TODO optimization operators should be numbers

TRUE = ["true", "t"]
FALSE = ["false", "f"]
NONE = ["none", "null", "n", "nil"]

class symbol_base(object):
  id = None
  value = None
  fst = snd = third = None

  def nud(self):
    raise SyntaxError("Syntax error (%r)." % self.id)

  def led(self):
    raise SyntaxError("Unknown operator (%r)." % self.id)

  def getTree(self):
    if self.id == "(name)":
      val = self.value.lower()
      if val in TRUE:
        return True
      elif val in FALSE:
        return False
      elif val in NONE:
        return None
      return (self.id[1:-1], self.value)
    elif self.id == "(number)":
      return self.value
    elif self.id == "(literal)":
      fstLetter = self.value[0]
      if fstLetter in ["'", "\""]:
        return self.value[1:-1]
      # elif fstLetter.isdigit():
      # 	try:
      # 		return int(self.value)
      # 	except:
      # 		return float(self.value)
      else:
        if self.value == "True":
          return True
        elif self.value == "False":
          return False
        elif self.value == "None":
          return None
    ret = [self.id]
    ret_append = ret.append
    L = (dict, tuple, list)
    for i in filter(None, [self.fst, self.snd, self.third]):
      if type(i) is str:
        ret_append(i)
      elif type(i) in L:
        t = []
        t_append = t.append
        if self.id == "{":
          ret = {}
          for j in list(self.fst.items()):
            ret[j[0].getTree()] = j[1].getTree()
          return ret
        for j in i:
          try:
            t_append(j.getTree())
          except Exception:
            t_append(j)
        if self.id in ("[", ".", ".."):
          ret.append(t)
        else:
          ret.extend(t)
        # ret_append(t)
        # return (self.id,ret[1:])
      else:
        if type(self.fst.value) in NUM_TYPES and self.snd is None:
          if self.id == "-":
            return -self.fst.value
          if self.id == "+":
            return self.fst.value
        ret_append(i.getTree())
    if self.id == "{":
      return {}
    # if self.id == "[" and self.fst == []:
    # 	return []
    if self.id == "(":
      # this will produce ("fn","fnName",arg1,arg2,...argN)
      # try:
      return tuple(["fn", ret[1][1]] + ret[2:])
    # except:
    # 	pass
    return tuple(ret)

  def __repr__(self):
    if self.id == "(name)" or self.id == "(literal)":
      return "(%s:%s)" % (self.id[1:-1], self.value)
    out = [self.id, self.fst, self.snd, self.third]
    # out=list(map(str, filter(None, out)))
    return "(" + " ".join(out) + ")"

def symbol(ID, bp=0):
  try:
    s = symbol_table[ID]
  except KeyError:

    class s(symbol_base):
      pass

    s.__name__ = "symbol-" + ID  # for debugging
    s.id = ID
    s.value = None
    s.lbp = bp
    symbol_table[ID] = s
  else:
    s.lbp = max(bp, s.lbp)
  return s

# helpers

def infix(ID, bp):
  def led(self, left):
    self.fst = left
    self.snd = expression(bp)
    return self

  symbol(ID, bp).led = led

def infix_r(ID, bp):
  def led(self, left):
    self.fst = left
    self.snd = expression(bp - 1)
    return self

  symbol(ID, bp).led = led

def prefix(ID, bp):
  def nud(self):
    self.fst = expression(bp)
    return self

  symbol(ID).nud = nud

def advance(ID=None):
  global token
  if ID and token.id != ID:
    raise SyntaxError("Expected %r, got %s" % (ID, token.id))
  token = nextToken()

def method(s):
  # decorator
  assert issubclass(s, symbol_base)

  def bind(fn):
    setattr(s, fn.__name__, fn)

  return bind

infix_r("or", 30)
infix_r("and", 40)
prefix("not", 50)
infix("in", 60)
infix("not", 60)  # not in
infix("is", 60)
infix("matches", 60)
infix("<", 60)
infix("<=", 60)
infix(">", 60)
infix(">=", 60)
# infix("	", 60); infix("!=", 60); infix("==", 60)
# infix("&", 90)
# infix("<<", 100); infix(">>", 100)
infix("+", 110)
infix("-", 110)
infix("*", 120)
infix("/", 120)
infix("//", 120)
infix("%", 120)
prefix("-", 130)
prefix("+", 130)
#prefix("~", 130)
# infix_r("**", 140)
symbol(".", 150)
symbol("[", 150)
symbol("{", 150)
symbol("(", 150)
# additional behavior
symbol("(name)").nud = lambda self: self
symbol("(literal)").nud = lambda self: self
symbol("(number)").nud = lambda self: self
symbol("(end)")
symbol(")")

# REGEX
infix("|", 0)
infix("^", 0)
infix("?", 0)
infix("\\", 0)

symbol("@")

@method(symbol("@"))
def nud(self):  # pylint: disable=E0102
  self.id = "(current)"
  return self

symbol("!")

@method(symbol("!"))
def nud(self):  # pylint: disable=E0102
  self.id = "(node)"
  return self

# RegEx
@method(symbol("/"))
def nud(self):  # pylint: disable=E0102
  self.id = "re"
  regex = []
  if token.id != "/":
    self_fst_append = regex.append
    while 1:
      if token.id == "/":
        break
      if token.id in ["(name)", "(number)"]:
        self_fst_append(str(token.value))
      else:
        self_fst_append(token.id)
      advance()
  self.fst = "".join(regex).replace("\\", "\\\\")
  advance("/")
  return self

@method(symbol("("))
def nud(self):  # pylint: disable=E0102,W0613
  expr = expression()
  advance(")")
  return expr

symbol(",")

@method(symbol("."))
def led(self, left):  # pylint: disable=E0102
  attr = False
  if token.id == ".":
    self.id = ".."
    advance()
  if token.id == "@":
    attr = True
    advance()
  if token.id == "(":
    advance()
    self.fst = left
    self.snd = []
    if token.id != ")":
      self_snd_append = self.snd.append
      while 1:
        self_snd_append(expression())
        if token.id != ",":
          break
        advance(",")
    advance(")")
    return self
  if token.id not in ["(name)", "*", "(literal)", "("]:
    raise SyntaxError("Expected an attribute name.")
  self.fst = left
  if attr:
    token.value = "@" + token.value
  self.snd = token
  advance()
  return self

# handling namespaces; e.g $.a.b.c or $ss.a.b.c
# default storage is the request namespace
symbol("$")

@method(symbol("$"))
def nud(self):  # pylint: disable=E0102
  global token  # pylint: disable=W0602
  self.id = "(root)"
  if token.id == ".":
    self.fst = "rs"
  else:
    self.fst = token.value
    advance()
  return self

symbol("]")

@method(symbol("["))
def led(self, left):  # pylint: disable=E0102
  self.fst = left
  self.snd = expression()
  advance("]")
  return self

symbol(",")

# this is for built-in functions
@method(symbol("("))
def led(self, left):  # pylint: disable=E0102
  # self.id="fn"
  self.fst = left
  self.snd = []
  if token.id != ")":
    self_snd_append = self.snd.append
    while 1:
      self_snd_append(expression())
      if token.id != ",":
        break
      advance(",")
  advance(")")
  return self

symbol(":")
symbol("=")

# constants

def constant(ID):
  @method(symbol(ID))
  def nud(self):  # pylint: disable=W0612
    self.id = "(literal)"
    self.value = ID
    return self

constant("None")
constant("True")
constant("False")

# multitoken operators

@method(symbol("not"))
def led(self, left):  # pylint: disable=E0102
  if token.id != "in":
    raise SyntaxError("Invalid syntax")
  advance()
  self.id = "not in"
  self.fst = left
  self.snd = expression(60)
  return self

@method(symbol("is"))
def led(self, left):  # pylint: disable=E0102
  if token.id == "not":
    advance()
    self.id = "is not"
  self.fst = left
  self.snd = expression(60)
  return self

symbol("]")

@method(symbol("["))
def nud(self):  # pylint: disable=E0102
  self.fst = []
  if token.id != "]":
    while 1:
      if token.id == "]":
        break
      self.fst.append(expression())
      if token.id not in SELECTOR_OPS + [","]:
        break
      advance(",")
  advance("]")
  return self

symbol("}")

@method(symbol("{"))
def nud(self):  # pylint: disable=E0102
  self.fst = {}
  if token.id != "}":
    while 1:
      if token.id == "}":
        break
      key = expression()
      advance(":")
      self.fst[key] = expression()
      if token.id != ",":
        break
      advance(",")
  advance("}")
  return self

import tokenize as tokenizer
type_map = {
    tokenizer.NUMBER: "(number)",
    tokenizer.STRING: "(literal)",
    tokenizer.OP: "(operator)",
    tokenizer.NAME: "(name)",
    tokenizer.ERRORTOKEN:
    "(operator)"  #'$' is recognized in python tokenizer as error token!
}

# python tokenizer
def tokenize_python(program):
  if sys.version_info[0] < 3:
    tokens = tokenizer.generate_tokens(StringIO(program).next)
  else:
    tokens = tokenizer.generate_tokens(StringIO(program).__next__)
  for t in tokens:
    # print type_map[t[0]], t[1]
    try:
      # change this to output python values in correct type
      yield type_map[t[0]], t[1]
    except KeyError:
      if t[0] in [tokenizer.NL, tokenizer.COMMENT, tokenizer.NEWLINE]:
        continue
      if t[0] == tokenizer.ENDMARKER:
        break
      else:
        raise SyntaxError("Syntax error")
  yield "(end)", "(end)"

def tokenize(program):
  if isinstance(program, list):
    source = program
  else:
    source = tokenize_python(program)
  for ID, value in source:
    if ID == "(literal)":
      symbol = symbol_table[ID]
      s = symbol()
      s.value = value
    elif ID == "(number)":
      symbol = symbol_table[ID]
      s = symbol()
      try:
        s.value = int(value)
      except Exception:
        s.value = float(value)
    elif value == " ":
      continue
    else:
      # name or operator
      symbol = symbol_table.get(value)
      if symbol:
        s = symbol()
      elif ID == "(name)":
        symbol = symbol_table[ID]
        s = symbol()
        s.value = value
      else:
        raise SyntaxError("Unknown operator '%s', '%s'" % (ID, value))
    yield s

# parser engine
def expression(rbp=0):
  global token
  t = token
  token = nextToken()
  left = t.nud()
  while rbp < token.lbp:
    t = token
    token = nextToken()
    left = t.led(left)
  return left

def parse(expr, D=False):
  if sys.version_info[0] < 3 and type(expr) is unicode:
    expr = expr.encode("utf8")
  if type(expr) is not str:
    return expr
  expr = expr.strip()
  global token, nextToken
  if sys.version_info[0] >= 3:
    nextToken = tokenize(expr).__next__
  else:
    nextToken = tokenize(expr).next
  token = nextToken()
  r = expression().getTree()
  if D:
    print("PARSE STAGE")
    print(r)
  return r
