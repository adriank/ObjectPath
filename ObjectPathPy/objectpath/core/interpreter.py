#!/usr/bin/env python

# !!!NOT THREAD SAFE!!!
#TODO thread safety!
import sys
import re
from .parser import parse
from objectpath.core import *
from objectpath.utils.colorify import *
from objectpath.utils import dicttree,timeutils,py2JSON
from objectpath.utils import iterators, generator, chain, skip
from objectpath.utils.debugger import Debugger

EPSILON=0.0000000000000001 #this is used in float comparison
EXPR_CACHE={}

#setting external modules to 0, thus enabling lazy loading. 0 ensures that Pythonic types are never matched.
#this way is efficient because if statement is fast and once loaded these variables are pointing to libraries.
ObjectId=generateID=calendar=escape=escapeDict=unescape=unescapeDict=0

class Tree(Debugger):
	def __init__(self,obj,cfg={}):
		self.D=cfg.get("debug",False)
		self.setData(obj)
		self.current=self.node=None
		try:
			if self.D:
				super(Tree, self).__init__()
		except (KeyError, TypeError):
			pass

	def setData(self,obj):
		if type(obj) in iterators+[dict]:
			self.data=obj

	def compile(self,expr):
		if expr in EXPR_CACHE:
			return EXPR_CACHE[expr]
		ret=EXPR_CACHE[expr]=parse(expr,self.D)
		return ret

	def execute(self,expr):
		D=self.D
		if D: self.start("Tree.execute")
		TYPES=[str,int,float,bool,generator,chain]
		try:
			TYPES+=[long]
		except:
			pass
		#TODO change to yield?
		def exe(node):
			"""
				node[0] - operator name
				node[1:] - params
			"""
			if D: self.start("executing node '%s'", node)
			type_node=type(node)
			if node is None or type_node in TYPES:
				return node
			elif type_node is list:
				return list(map(exe,node))
			elif type_node is dict:
				ret={}
				for i in node.items():
					ret[exe(i[0])]=exe(i[1])
				return ret
			op=node[0]
			if op=="or":
				if D: self.debug("%s or %s", node[1],node[2])
				return exe(node[1]) or exe(node[2])
			elif op=="and":
				if D: self.debug("%s and %s", node[1],node[2])
				return exe(node[1]) and exe(node[2])
			elif op=="+":
				if len(node)>2:
					fst=exe(node[1])
					snd=exe(node[2])
					if fst is None:
						return snd
					if snd is None:
						return fst
					typefst=type(fst)
					typesnd=type(snd)
					if typefst is dict:
						try:
							fst.update(snd)
						except:
							if type(snd) is not dict:
								raise ProgrammingError("Can't add value of type %s to %s" % (bold(PY_TYPES_MAP.get(type(snd).__name__,type(snd).__name__)), bold("object")))
						return fst
					if typefst is list and typesnd is list:
						if D: self.debug("both sides are lists, returning '%s'",fst+snd)
						return fst+snd
					if typefst in ITER_TYPES or typesnd in ITER_TYPES:
						if typefst not in ITER_TYPES:
							fst=[fst]
						elif typesnd not in ITER_TYPES:
							snd=[snd]
						if D: self.debug("at least one side is generator and other is iterable, returning chain")
						return chain(fst,snd)
					if typefst in (int,float):
						try:
							return fst+snd
						except:
							return fst+float(snd)
					if typefst in STR_TYPES or typesnd in STR_TYPES:
						if D: self.info("doing string comparison '%s' is '%s'",fst,snd)
						if sys.version < "3":
							if typefst is unicode:
								fst=fst.encode("utf-8")
							if typesnd is unicode:
								snd=snd.encode("utf-8")
						return str(fst)+str(snd)
					try:
						timeType=timeutils.datetime.time
						if typefst is timeType and typesnd is timeType:
							return timeutils.addTimes(fst,snd)
					except:
						pass
					if D: self.debug("standard addition, returning '%s'",fst+snd)
					return fst + snd
				else:
					return exe(node[1])
			elif op=="-":
				#TODO move -N to tree builder!
				if len(node)>2:
					fst=exe(node[1])
					snd=exe(node[2])
					try:
						return fst-snd
					except:
						typefst=type(fst)
						typesnd=type(snd)
						timeType=timeutils.datetime.time
						if typefst is timeType and typesnd is timeType:
							return timeutils.subTimes(fst,snd)
				else:
					return - exe(node[1])
			elif op=="*":
				return exe(node[1]) * exe(node[2])
			elif op=="%":
				return exe(node[1]) % exe(node[2])
			elif op=="/":
				#print(node[1])
				#print(exe(node[1]))
				return exe(node[1]) / float(exe(node[2]))
			elif op==">":
				if D: self.debug("%s > %s", node[1],node[2])
				return exe(node[1]) > exe(node[2])
			elif op=="<":
				return exe(node[1]) < exe(node[2])
			elif op==">=":
				return exe(node[1]) >= exe(node[2])
			elif op=="<=":
				return exe(node[1]) <= exe(node[2])
			#TODO this algorithm produces 3 for 1<2<3 and should be true
			#elif op in "<=>=":
			#	fst=exe(node[1])
			#	snd=exe(node[2])
			#	if op==">":
			#		return fst > snd and snd or False
			#	elif op=="<":
			#		return fst < snd and snd or False
			#	elif op==">=":
			#		return fst >= snd and snd or False
			#	elif op=="<=":
			#		return fst <= snd and snd or False
			elif op=="not":
				fst=exe(node[1])
				if D: self.debug("doing not '%s'",fst)
				return not fst
			elif op=="in":
				fst=exe(node[1])
				snd=exe(node[2])
				if D: self.debug("doing '%s' in '%s'",node[1],node[2])
				if type(fst) in ITER_TYPES and type(snd) in ITER_TYPES:
					return any(x in max(fst,snd,key=len) for x in min(fst,snd,key=len))
				return exe(node[1]) in exe(node[2])
			elif op=="not in":
				fst=exe(node[1])
				snd=exe(node[2])
				if D: self.debug("doing '%s' not in '%s'",node[1],node[2])
				if type(fst) in ITER_TYPES and type(snd) in ITER_TYPES:
					return not any(x in max(fst,snd,key=len) for x in min(fst,snd,key=len))
				return exe(node[1]) not in exe(node[2])
			elif op in ("is","is not"):
				if D: self.debug("found operator '%s'",op)
				try:
					fst=exe(node[1])
				except Exception as e:
					if D: self.debug("NOT ERROR! Can't execute node[1] '%s', error: '%s'. Falling back to orginal value.",node[1],str(e))
					fst=node[1]
				try:
					snd=exe(node[2])
				except Exception as e:
					if D: self.debug("NOT ERROR! Can't execute node[2] '%s', error: '%s'. Falling back to orginal value.",node[2],str(e))
					snd=node[2]
				if op is "is" and fst == snd:
					return True
				if op is "is not" and fst != snd:
					return True
				typefst=type(fst)
				typesnd=type(snd)
				if D: self.debug("type fst: '%s', type snd: '%s'",typefst,typesnd)
				if typefst in STR_TYPES:
					if D: self.info("doing string comparison '\"%s\" is \"%s\"'",fst,snd)
					ret=fst==str(snd)
				elif typefst is float:
					if D: self.info("doing float comparison '%s is %s'",fst,snd)
					ret=abs(fst-float(snd))<EPSILON
				elif typefst is int:
					if D: self.info("doing integer comparison '%s is %s'",fst,snd)
					ret=fst==int(snd)
				elif typefst is list and typesnd is list:
					if D: self.info("doing array comparison '%s' is '%s'",fst,snd)
					ret=fst==snd
				elif typefst is dict and typesnd is dict:
					if D: self.info("doing object comparison '%s' is '%s'",fst,snd)
					ret=fst==snd
				else:
					try:
						global ObjectId
						if not ObjectId:
							from bson.objectid import ObjectId
						if typefst is ObjectId or typesnd is ObjectId:
							if D: self.info("doing MongoDB objectID comparison '%s' is '%s'",fst,snd)
							ret=str(fst)==str(snd)
						else:
							if D: self.info("doing standard comparison '%s' is '%s'",fst,snd)
							ret=fst is snd
					except:
						pass
				if op=="is not":
					if D: self.info("'is not' found. Returning %s",not ret)
					return not ret
				else:
					if D: self.info("returning '%s' is '%s'='%s'",fst,snd,ret)
					return ret
			elif op=="(literal)":
				fstLetter=node[1][0]
				if fstLetter is "'":
					return node[1][1:-1]
				elif fstLetter.isdigit:
					return int(node[1])
			elif op=="(root)":# this is $
				return self.data
			elif op=="(node)":# this is !
				if D: self.debug("returning node %s",self.node)
				return self.node
			elif op=="(current)":# this is @
				if D: self.debug("returning current node %s",self.current)
				return self.current
			elif op=="name":
				return node[1]
			elif op==".":
				fst=node[1]
				if type(fst) is tuple:
					fst=exe(fst)
				typefst=type(fst)
				if D: self.debug("left is '%s'",fst)
				if node[2][0] == "*":
					if D: self.end("returning '%s'",typefst in ITER_TYPES and fst or [fst])
					return typefst in ITER_TYPES and fst or [fst]
				snd=exe(node[2])
				if D: self.debug("right is '%s'",snd)
				if typefst in ITER_TYPES:
					ret=[]
					ret_append=ret.append
					for i in fst:
						try:
							ret_append(i[snd])
						except:
							pass
					if D: self.end(". returning '%s'",ret)
					return ret
				try:
					if D: self.end(". returning '%s'",fst.get(snd))
					return fst.get(snd)
				except:
					if isinstance(fst,object):
						try:
							return fst.__getattribute__(snd)
						except:
							pass
					if D: self.end(". returning '%s'",fst)
					return fst
			elif op=="..":
				fst=dicttree.flatten(exe(node[1]))
				if node[2][0]=="*":
					if D: self.debug("returning '%s'",fst)
					return fst
				ret=[]
				snd=exe(node[2])
				for i in fst:
					try:
						ret.append(i[snd])
					except:
						pass
				if D: self.debug("returning '%s'",ret)
				return len(ret) is 1 and ret[0] or ret
			#TODO move it to tree generation phase
			elif op=="{":
				return {}
			elif op=="[":
				len_node=len(node)
				#TODO move it to tree generation phase
				if len_node is 1: # empty list
					if D: self.debug("returning an empty list")
					return []
				if len_node is 2: # list - preserved to catch possible event of leaving it as '[' operator
					#TODO yielding is not possible here
					#if type(node[1]) in (generator,chain):
					#	for i in node[1]:
					#		yield exe(i)
					if D: self.debug("doing list mapping")
					return list(map(exe,node[1]))
				if len_node is 3: # selector used []
					fst=exe(node[1])
					# check against None
					if not fst:
						return fst
					selector=node[2]
					if D: self.debug("found '%s' selector for '%s'",selector,fst)

					if type(selector) is tuple and selector[0] is "[":
						nodeList=[]
						nodeList_append=nodeList.append
						for i in fst:
							if D: self.debug("setting self.current to '%s'",i)
							self.current=i
							nodeList_append(exe((selector[0],exe(selector[1]),exe(selector[2]))))
						if D: self.debug("returning '%s' objects: '%s'",len(nodeList),nodeList)
						return nodeList

					#if type(selector) is tuple and selector[0]=="fn":
					#	for i in fst:

					if type(selector) is tuple and selector[0] == "(current)":
						if D: self.warning(bold("$.*[@]")+" is eqivalent to "+bold("$.*")+"!")
						return fst

					if type(selector) is tuple and selector[0] in SELECTOR_OPS:
						if D: self.debug("found '%s' operator in selector",selector[0])
						nodeList=[]
						nodeList_append=nodeList.append
						if type(fst) is dict:
							fst=[fst]
						for i in fst:
							if D: self.debug("setting self.current to '%s'",i)
							self.current=i
							#TODO move it to tree building phase
							if type(selector[1]) is tuple and selector[1][0]=="name":
								selector=(selector[0],selector[1][1],selector[2])
							if selector[0]=="fn":
								print self.current
								nodeList_append(exe(selector))
							elif type(selector[1]) in STR_TYPES:
								try:
									if exe((selector[0],i[selector[1]],selector[2])):
										nodeList_append(i)
										if D: self.debug("appended")
									if D: self.debug("discarded")
								except Exception as e:
									if D: self.debug("discarded, Exception: %s",e)
							else:
								try:
									#TODO optimize an event when @ is not used. exe(selector[1]) can be cached
									if exe((selector[0],exe(selector[1]),exe(selector[2]))):
										nodeList_append(i)
										if D: self.debug("appended")
									if D: self.debug("discarded")
								except:
									if D: self.debug("discarded")
						if D: self.debug("returning '%s' objects: '%s'",len(nodeList),nodeList)
						return nodeList
					snd=exe(node[2])
					typefst=type(fst)
					if typefst in [tuple]+ITER_TYPES+STR_TYPES:
						typesnd=type(snd)
						# nodes[N]
						if typesnd in NUM_TYPES or typesnd is str and snd.isdigit():
							n=int(snd)
							if D: self.debug("getting %sth element from '%s'",n,snd)
							if typefst in (generator,chain):
								if n>0:
									return skip(fst,n)
								elif n==0:
									return list(next(fst))[0]
								else:
									fst=list(fst)
							else:
								try:
									return fst[n]
								except:
									return None
						# $.*['string']==$.string
						return exe((".",fst,snd))
					else:
						try:
							if D: self.debug("returning '%s'",fst[snd])
							return fst[snd]
						except:
							#CHECK - is it ok to do that or should it be ProgrammingError?
							if D: self.debug("returning an empty list")
							return []
				raise ProgrammingError("Wrong usage of the '[' operator")
			elif op=="fn":
				""" Built-in functions """
				fnName=node[1]
				args=None
				try:
					args=list(map(exe,node[2:]))
				except IndexError as e:
					if D: self.debug("NOT ERROR: can't map '%s' with '%s'",node[2:],exe)
				#arithmetic
				if fnName=="sum":
					args=args[0]
					if type(args) in NUM_TYPES:
						return args
					return sum(map(lambda x:type(x) in NUM_TYPES and x or exe(x), args))
				elif fnName=="max":
					args=args[0]
					if type(args) in NUM_TYPES:
						return args
					return max(map(lambda x:type(x) in NUM_TYPES and x or exe(x), args))
				elif fnName=="min":
					args=args[0]
					if type(args) in NUM_TYPES:
						return args
					return min(map(lambda x:type(x) in NUM_TYPES and x or exe(x), args))
				elif fnName=="avg":
					args=args[0]
					if type(args) in NUM_TYPES:
						return args
					if type(args) not in ITER_TYPES:
						raise Exception("Argument for avg() is not iterable")
					try:
						return sum(args)/float(len(args))
					except TypeError:
						args=filter(lambda x: type(x) in NUM_TYPES, args)
						self.warning("Some items in array were ommited")
						return sum(args)/float(len(args))
				elif fnName=="round":
					return round(*args)
				#casting
				elif fnName=="int":
					return int(args[0])
				elif fnName=="float":
					return float(args[0])
				elif fnName=="str":
					return str(py2JSON(args[0]))
				elif fnName in ("list","array"):
					try:
						a=args[0]
					except:
						return []
					targs=type(a)
					if targs is timeutils.datetime.datetime:
						return timeutils.date2list(a)+timeutils.time2list(a)
					if targs is timeutils.datetime.date:
						return timeutils.date2list(a)
					if targs is timeutils.datetime.time:
						return timeutils.time2list(a)
					return list(a)
				#string
				elif fnName=="escape":
					global escape,escapeDict
					if not escape:
						from objectpath.utils.xmlextras import escape, escapeDict
					return escape(args[0],escapeDict)
				elif fnName=="upper":
					return args[0].upper()
				elif fnName=="lower":
					return args[0].lower()
				elif fnName=="capitalize":
					return args[0].capitalize()
				elif fnName=="title":
					return args[0].title()
				elif fnName=="split":
					return args[0].split(*args[1:])
				elif fnName=="unescape":
					global unescape,unescapeDict
					if not unescape:
						from objectpath.utils.xmlextras import unescape, unescapeDict
					return unescape(args[0],unescapeDict)
				elif fnName=="replace":
					if sys.version < "3" and type(args[0]) is unicode:
						args[0]=args[0].encode("utf8")
					return str.replace(args[0],args[1],args[2])
				elif fnName=="REsub":
					return re.sub(args[1],args[2],args[0])
				#array
				elif fnName=="sort":
					if D: self.debug("doing sort on '%s'",args)
					if not args:
						return args
					if type(args) in (generator,chain):
						args=list(args)
					if len(args)>1:
						key=args[1]
						a={"key":lambda x: x.get(key)}
						args=args[0]
					else:
						a={}
						args=args[0]
					if type(args) is not list:
						return args
					args.sort(**a)
					return args
				elif fnName=="reverse":
					args=args[0]
					if type(args) in (generator,chain):
						args=list(args)
					args.reverse()
					return args
				elif fnName in ("count","len"):
					args=args[0]
					if args in (True,False,None):
						return args
					if type(args) in ITER_TYPES:
						return len(list(args))
					return len(args)
				elif fnName=="join":
					try:
						joiner=args[1]
					except:
						joiner=""
					try:
						return joiner.join(args[0])
					except:
						try:
							return joiner.join(map(str,args[0]))
						except:
							return args[0]
				#time
				elif fnName in ("now","age","time","date","dateTime"):
					if fnName=="now":
						return timeutils.now()
					if fnName=="date":
						return timeutils.date(args)
					if fnName=="time":
						return timeutils.time(args)
					if fnName=="dateTime":
						return timeutils.dateTime(args)
					if fnName=="age":
						return timeutils.age(args[0],len(args)>1 and args[1] or "en")
				elif fnName=="toMillis":
					args=args[0]
					if args.utcoffset() is not None:
						args=args-args.utcoffset()
					global calendar
					if not calendar:
						import calendar
					return int(calendar.timegm(args.timetuple()) * 1000 + args.microsnd / 1000)
				elif fnName=="localize":
					if type(args[0]) is timeutils.datetime.datetime:
						return timeutils.UTC2local(*args)
				#polygons
				elif fnName=="area":
					def segments(p):
						p=list(map(lambda x: x[0:2],p))
						return zip(p, p[1:] + [p[0]])
					return 0.5 * abs(sum(x0*y1 - x1*y0
						for ((x0, y0), (x1, y1)) in segments(args[0])))
				#misc
				elif fnName=="keys":
					try:
						return args[0].keys()
					except AttributeError as e:
						raise Exception("Argument is not "+bold("object")+" but %s in keys()"%bold(type(args[0]).__name__))
				elif fnName=="type":
					ret=type(args[0])
					if ret in ITER_TYPES:
						return "array"
					if ret is dict:
						return "object"
					return ret.__name__
				else:
					raise ProgrammingError("Function '"+fnName+"' does not exist.")
			else:
				return node

		D=self.D
		if type(expr) in STR_TYPES:
			tree=self.compile(expr)
		elif type(tree) not in (tuple,list,dict):
			return tree
		ret=exe(tree)
		if D: self.end("Tree.execute with: '%s'", ret)
		return ret

	def __str__(self):
		return "TreeObject()"

	def __repr__(self):
		return self.__str__()
