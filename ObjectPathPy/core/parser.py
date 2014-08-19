#!/usr/bin/env python

# code from http://effbot.org/zone/simple-top-down-parsing.htm
# licence of original code was public domain
# relicenced to AGPL v3 by Adrian Kalbarczyk and:
# - specialized to work with ObjectPath,
# - optimized
from cStringIO import StringIO
from core import *

symbol_table={}

#TODO optimization ('-',1) -> -1
#TODO optimization operators should be numbers

TRUE=["true","t"]
FALSE=["false","f"]
NONE=["none","null","n","nil"]

class symbol_base(object):
	id=None
	value=None
	fst=snd=third=None

	def nud(self):
		raise SyntaxError("Syntax error (%r)." % self.id)

	def led(self, left):
		raise SyntaxError("Unknown operator (%r)." % self.id)

	def getTree(self):
		if self.id == "(name)":
			val=self.value.lower()
			if val in TRUE:
				return True
			elif val in FALSE:
				return False
			elif val in NONE:
				return None
			return (self.id[1:-1], self.value)
		elif self.id == "(literal)":
			fstLetter=self.value[0]
			if fstLetter in ["'","\""]:
				return self.value[1:-1]
			elif fstLetter.isdigit():
				try:
					return int(self.value)
				except:
					return float(self.value)
			else:
				if self.value=="True":
					return True
				elif self.value=="False":
					return False
				elif self.value=="None":
					return None
		ret=[self.id]
		ret_append=ret.append
		L=(dict,tuple,list)
		for i in filter(None, [self.fst, self.snd, self.third]):
			if type(i) is str:
				ret_append(i)
			elif type(i) in L:
				t=[]
				t_append=t.append
				if self.id is "{":
					ret={}
					for j in self.fst.iteritems():
						ret[j[0].getTree()]=j[1].getTree()
					return ret
				for j in i:
					try:
						t_append(j.getTree())
					except:
						t_append(j)
				#TODO check if this is ever used?
				if self.id is "[":
					return t
				else:
					ret.extend(t)
				#ret_append(t)
				#return (self.id,ret[1:])
			else:
				ret_append(i.getTree())
		if self.id is "(":
			#this will produce ("fn","fnName",arg1,arg2,...argN)
			return tuple(["fn",ret[1][1]]+ret[2:])
		return tuple(ret)

	def __repr__(self):
		if self.id == "(name)" or self.id == "(literal)":
			return "(%s %s)" % (self.id[1:-1], self.value)
		out=[self.id, self.fst, self.snd, self.third]
		out=map(str, filter(None, out))
		return "(" + " ".join(out) + ")"

def symbol(id, bp=0):
	try:
		s=symbol_table[id]
	except KeyError:
		class s(symbol_base):
			pass
		s.__name__="symbol-" + id # for debugging
		s.id=id
		s.value=None
		s.lbp=bp
		symbol_table[id]=s
	else:
		s.lbp=max(bp, s.lbp)
	return s

# helpers

def infix(id, bp):
	def led(self, left):
		self.fst=left
		self.snd=expression(bp)
		return self
	symbol(id, bp).led=led

def infix_r(id, bp):
	def led(self, left):
		self.fst=left
		self.snd=expression(bp-1)
		return self
	symbol(id, bp).led=led

def prefix(id, bp):
	def nud(self):
		self.fst=expression(bp)
		return self
	symbol(id).nud=nud

def advance(id=None):
	global token
	if id and token.id != id:
		raise SyntaxError("Expected %r, got %s"%(id,token.id))
	token=next()

def method(s):
	# decorator
	assert issubclass(s, symbol_base)
	def bind(fn):
		setattr(s, fn.__name__, fn)
	return bind

infix_r("or", 30); infix_r("and", 40); prefix("not", 50)
infix("in", 60); infix("not", 60) # not in
infix("is", 60);
infix("<", 60); infix("<=", 60)
infix(">", 60); infix(">=", 60)
#infix("	", 60); infix("!=", 60); infix("==", 60)
#infix("|", 70); infix("^", 80); infix("&", 90)
#infix("<<", 100); infix(">>", 100)
infix("+", 110); infix("-", 110)
infix("*", 120); infix("/", 120); infix("//", 120)
infix("%", 120)
prefix("-", 130); prefix("+", 130); #prefix("~", 130)
#infix_r("**", 140)
symbol(".", 150); symbol("[", 150); symbol("(", 150)
# additional behaviour
symbol("(name)").nud=lambda self: self
symbol("(literal)").nud=lambda self: self
symbol("(end)")
symbol(")")

symbol("@")
@method(symbol("@"))
def nud(self):
	self.id="(current)"
	return self

symbol("!")
@method(symbol("!"))
def nud(self):
	self.id="(node)"
	return self

@method(symbol("("))
def nud(self):
	expr=expression()
	advance(")")
	return expr

@method(symbol("."))
def led(self, left):
	attr=False
	if token.id is ".":
		self.id=".."
		advance()
	if token.id is "@":
		attr=True
		advance()
	if token.id not in ["(name)","*" ]:
		raise SyntaxError("Expected an attribute name.")
	self.fst=left
	if attr:
		token.value="@"+token.value
	self.snd=token
	advance()
	return self

#handling namespaces; e.g $.a.b.c or $ss.a.b.c
#default storage is the request namespace
symbol("$")
@method(symbol("$"))
def nud(self):
	global token
	self.id="(root)"
	if token.id is ".":
		self.fst="rs"
	else:
		self.fst=token.value
		advance()
	return self

symbol("]")

@method(symbol("["))
def led(self, left):
	self.fst=left
	self.snd=expression()
	advance("]")
	return self

symbol(",")

#this is for built-in functions
@method(symbol("("))
def led(self, left):
	#self.id="fn"
	self.fst=left
	self.snd=[]
	if token.id is not ")":
		self_snd_append=self.snd.append
		while 1:
			self_snd_append(expression())
			if token.id is not ",":
				break
			advance(",")
	advance(")")
	return self

symbol(":")
symbol("=")

# constants

def constant(id):
	@method(symbol(id))
	def nud(self):
		self.id="(literal)"
		self.value=id
		return self

constant("None")
constant("True")
constant("False")

#multitoken operators

@method(symbol("not"))
def led(self, left):
	if token.id != "in":
		raise SyntaxError("Invalid syntax")
	advance()
	self.id="not in"
	self.fst=left
	self.snd=expression(60)
	return self

@method(symbol("is"))
def led(self, left):
	if token.id == "not":
		advance()
		self.id="is not"
	self.fst=left
	self.snd=expression(60)
	return self

symbol("]")

@method(symbol("["))
def nud(self):
	self.fst=[]
	if token.id is not "]":
		while 1:
			if token.id is "]":
				break
			self.fst.append(expression())
			if token.id not in SELECTOR_OPS+[","]:
				break
			advance(",")
	advance("]")
	return self

symbol("}")

@method(symbol("{"))
def nud(self):
	self.fst={}
	if token.id is not "}":
		while 1:
			if token.id is "}":
				break
			key=expression()
			advance(":")
			self.fst[key]=expression()
			if token.id is not ",":
				break
			advance(",")
	advance("}")
	return self

import tokenize as tokenizer
type_map={
	tokenizer.NUMBER:"(literal)",
	tokenizer.STRING:"(literal)",
	tokenizer.OP:"(operator)",
	tokenizer.NAME:"(name)",
	tokenizer.ERRORTOKEN:"(operator)" #'$' is recognized in python tokenizer as error token!
}

# python tokenizer
def tokenize_python(program):
	if type(program) is unicode:
		program = program.encode('utf8')
	for t in tokenizer.generate_tokens(StringIO(program).next):
		try:
			#change this to output python values in correct type
			yield type_map[t[0]], t[1]
		except KeyError:
			if t[0] in [tokenizer.NL, tokenizer.COMMENT]:
				continue
			if t[0] == tokenizer.ENDMARKER:
				break
			else:
				raise SyntaxError("Syntax error")
	yield "(end)", "(end)"

def tokenize(program):
	if isinstance(program, list):
		source=program
	else:
		source=tokenize_python(program)
	for id, value in source:
		if id=="(literal)":
			symbol=symbol_table[id]
			s=symbol()
			s.value=value
		elif value is " ":
			continue
		else:
			# name or operator
			symbol=symbol_table.get(value)
			if symbol:
				s=symbol()
			#elif id==" ":
			elif id=="(name)":
				symbol=symbol_table[id]
				s=symbol()
				s.value=value
			else:
				raise SyntaxError("Unknown operator '%s', '%s'" % (id,value))
		yield s

# parser engine
def expression(rbp=0):
	global token
	t=token
	token=next()
	left=t.nud()
	while rbp < token.lbp:
		t=token
		token=next()
		left=t.led(left)
	return left

def parse(expr):
	if type(expr) not in STR_TYPES:
		return expr
	expr=expr.strip()
	if not len(expr):
		return Tree(True)
	global token, next
	next=tokenize(expr).next
	token=next()
	return expression().getTree()
