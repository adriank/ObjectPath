#!/usr/bin/env python

# This file is part of ObjectPath released under AGPL v3 license.
# Copyright (C) 2010-2014 Adrian Kalbarczyk

import sys
import re
from .parser import parse
from objectpath.core import *
import objectpath.utils.colorify as color  # pylint: disable=W0614
from objectpath.utils import flatten, filter_dict, timeutils, skip
from objectpath.utils.json_ext import py2JSON
from objectpath.core import ITER_TYPES, generator, chain
from objectpath.utils.debugger import Debugger

EPSILON = 0.0000000000000001  # this is used in float comparison
EXPR_CACHE = {}

# setting external modules to 0, thus enabling lazy loading. 0 ensures that Pythonic types are never matched.
# this way is efficient because if statement is fast and once loaded these variables are pointing to libraries.
ObjectId = generateID = calendar = escape = escapeDict = unescape = unescapeDict = 0
TYPES = [str, int, float, bool, generator, chain]
try:
    TYPES += [long]
except NameError:
    pass

OP_TOKENS = {
    "or": "o_or",
    "and": "o_and",
    "not": "o_not",
    "in": "o_in",
    "not in": "o_not_in",
    "is": "o_is_not_is",
    "is not": "o_is_not_is",

    "re": "o_re",
    "matches": "o_matches",

    "+": "o_plus",
    "-": "o_minus",
    "*": "o_star",
    "/": "o_slash",
    # "|": "o_vbar",
    # "&": "o_amper",
    "<": "o_less",
    ">": "o_greater",
    # "=": "o_equal",
    # ".": "o_dot",
    "%": "o_percent",
    # "{": "o_brace_left",
    # "}": "o_brace_right",
    # "==": "o_equal_equal",
    # "!=": "o_not_equal",
    "<=": "o_less_equal",
    ">=": "o_greater_equal",
    # "~": "o_tilde",
    # "^": "o_circumflex",
    # "<<": "o_left_shift",
    # ">>": "o_right_shift",
    # "**": "o_double_star",
    # "+=": "o_plus_equal",
    # "-=": "o_minus_equal",
    # "*=": "o_star_equal",
    # "/=": "o_slash_equal",
    # "%=": "o_percent_equal",
    # "&=": "o_amper_equal",
    # "|=": "o_vbar_equal",
    # "^=": "o_circumflex_equal",
    # "<<=": "o_left_shift_equal",
    # ">>=": "o_right_shift_equal",
    # "**=": "o_double_star_equal",
    # "//": "o_double_slash",
    # "//=": "o_double_slash_equal",
    # "@": "o_at",
    # "@=": "o_at_equal"
}


class Lexer(Debugger):

    def __init__(self, run, debug=False):
        if debug:
            super(Lexer, self).__init__()
        self._debug = debug
        self.run = run

    def o_error(self, *args):
        self.debug("%s not exists", args[0])

    def o_or(self, *args, **kwargs):
        if self._debug:
            self.debug("%s or %s", args[1], args[2])
        return self.run(args[1]) or self.run(args[2])

    def o_and(self, *args, **kwargs):
        if self._debug:
            self.debug("%s and %s", args[1], args[2])
        return self.run(args[1]) and self.run(args[2])

    def o_not(self, *args, **kwargs):
        fst = self.run(args[1])
        if self._debug:
            self.debug("doing not '%s'", fst)
        return not fst

    def o_in(self, *args, **kwargs):
        fst = self.run(args[1])
        snd = self.run(args[2])
        if self._debug:
            self.debug("doing '%s' in '%s'", args[1], args[2])
        if type(fst) in ITER_TYPES and type(snd) in ITER_TYPES:
            return any(x in max(fst, snd, key=len) for x in min(fst, snd, key=len))
        return self.run(args[1]) in self.run(args[2])
    
    def o_not_in(self, *args, **kwargs):
        fst = self.run(args[1])
        snd = self.run(args[2])
        if self._debug:
            self.debug("doing '%s' not in '%s'", args[1], args[2])
        if type(fst) in ITER_TYPES and type(snd) in ITER_TYPES:
            return not any(x in max(fst, snd, key=len) for x in min(fst, snd, key=len))
        return self.run(args[1]) not in self.run(args[2])

    def o_is_not_is(self, *args, **kwargs):
        if self._debug:
            self.debug("found operator '%s'", op)
        # try:
        op = args[0]
        fst = self.run(args[1])
        # except Exception as e:
        #     if D: self.debug("NOT ERROR! Can't execute args[1] '%s', error: '%s'. Falling back to orginal value.",args[1],str(e))
        #     fst=args[1]
        # try:
        snd = self.run(args[2])
        # except Exception as e:
        #     if D: self.debug("NOT ERROR! Can't execute args[2] '%s', error: '%s'. Falling back to orginal value.",args[2],str(e))
        #     snd=args[2]
        if op == "is" and fst == snd:
            return True
        # this doesn't work for 3 is not '3'
        # if op == "is not" and fst != snd:
        #     return True
        typefst = type(fst)
        typesnd = type(snd)
        if self._debug:
            self.debug("type fst: '%s', type snd: '%s'", typefst, typesnd)
        if typefst in STR_TYPES:
            if self._debug:
                self.info("doing string comparison '\"%s\" is \"%s\"'", fst, snd)
            result = fst == str(snd)
        elif typefst is float:
            if self._debug:
                self.info("doing float comparison '%s is %s'", fst, snd)
            result = abs(fst - float(snd)) < EPSILON
        elif typefst is int:
            if self._debug:
                self.info("doing integer comparison '%s is %s'", fst, snd)
            result = fst == int(snd)
        elif typefst is list and typesnd is list:
            if self._debug:
                self.info("doing array comparison '%s' is '%s'", fst, snd)
            result = fst == snd
        elif typefst is dict and typesnd is dict:
            if self._debug:
                self.info("doing object comparison '%s' is '%s'", fst, snd)
            result = fst == snd
        # else:
        #     try:
        #         global ObjectId
        #         if not ObjectId:
        #             from bson.objectid import ObjectId
        #         if typefst is ObjectId or typesnd is ObjectId:
        #             if D: self.info("doing MongoDB objectID comparison '%s' is '%s'",fst,snd)
        #             ret=str(fst)==str(snd)
        #         else:
        #             if D: self.info("doing standard comparison '%s' is '%s'",fst,snd)
        #             ret=fst is snd
        #     except Exception:
        #         pass
        if op == "is not":
            if self._debug:
                self.info("'is not' found. Returning %s", not result)
            return not result
        else:
            if self._debug:
                self.info("returning '%s' is '%s'='%s'", fst, snd, result)
            return result

    def o_plus(self, *args, **kwargs):
        if len(args) > 2:
            fst = self.run(args[1])
            snd = self.run(args[2])
            if None in (fst, snd):
                return fst or snd
            typefst = type(fst)
            typesnd = type(snd)
            if typefst is dict:
                try:
                    fst.update(snd)
                except Exception:
                    if type(snd) is not dict:
                        raise ProgrammingError("Can't add value of type %s to %s" % (
                            color.bold(PY_TYPES_MAP.get(type(snd).__name__, type(snd).__name__)),
                            color.bold("object")))
                return fst
            if typefst is list and typesnd is list:
                if self._debug:
                    self.debug("both sides are lists, returning '%s'", fst + snd)
                return fst + snd
            if typefst in ITER_TYPES or typesnd in ITER_TYPES:
                if typefst not in ITER_TYPES:
                    fst = [fst]
                elif typesnd not in ITER_TYPES:
                    snd = [snd]
                if self._debug:
                    self.debug("at least one side is generator and other is iterable, returning chain")
                return chain(fst, snd)
            if typefst in NUM_TYPES:
                try:
                    return fst + snd
                except Exception:
                    return fst + float(snd)
            if typefst in STR_TYPES or typesnd in STR_TYPES:
                if self._debug:
                    self.info("doing string comparison '%s' is '%s'", fst, snd)
                if sys.version_info[0] < 3:
                    if typefst is unicode:
                        fst = fst.encode("utf-8")
                    if typesnd is unicode:
                        snd = snd.encode("utf-8")
                return str(fst) + str(snd)
            try:
                timeType = timeutils.datetime.time
                if typefst is timeType and typesnd is timeType:
                    return timeutils.addTimes(fst, snd)
            except Exception:
                pass
            if self._debug:
                self.debug("standard addition, returning '%s'", fst + snd)
            return fst + snd
        else:
            return self.run(args[1])
        
    def o_minus(self, *args, **kwargs):
        if len(args) > 2:
            fst = self.run(args[1])
            snd = self.run(args[2])
            try:
                return fst - snd
            except Exception:
                typefst = type(fst)
                typesnd = type(snd)
                timeType = timeutils.datetime.time
                if typefst is timeType and typesnd is timeType:
                    return timeutils.subTimes(fst, snd)
        else:
            return - self.run(args[1])
        
    def o_star(self, *args, **kwargs):
        return self.run(args[1]) * self.run(args[2])

    def o_percent(self, *args, **kwargs):
        return self.run(args[1]) % self.run(args[2])

    def o_slash(self, *args, **kwargs):
        return self.run(args[1]) / float(self.run(args[2]))

    def o_greater(self, *args, **kwargs):
        if self._debug:
            self.debug("%s > %s, %s", args[1], args[2], args[1] > args[2])
        return self.run(args[1]) > self.run(args[2])

    def o_less(self, *args, **kwargs):
        return self.run(args[1]) < self.run(args[2])

    def o_greater_equal(self, *args, **kwargs):
        return self.run(args[1]) >= self.run(args[2])

    def o_less_equal(self, *args, **kwargs):
        return self.run(args[1]) <= self.run(args[2])

    def o_re(self, *args, **kwargs):
        return re.compile(self.run(args[1]))

    def o_matches(self, *args, **kwargs):
        return not not re.match(self.run(args[1]), self.run(args[2]))

    def __getitem__(self, item):
        return getattr(self, OP_TOKENS[item], self.o_error)


class Tree(Debugger):
    _REGISTERED_FUNCTIONS = {}

    @classmethod
    def register_function(cls, name, func):
        """
        This method is used to add custom functions not catered for by default
        :param str name: The name by which the function will be referred to in the expression
        :param callable func: The function
        :return:
        """
        cls._REGISTERED_FUNCTIONS[name] = func

    def __init__(self, obj, cfg=None):
        if not cfg:
            cfg = {}
        self.D = cfg.get("debug", False)
        self._data = None

        self.data = obj
        self.object_getter = None
        self.set_object_getter(cfg.get("object_getter", None))
        self.lexer = Lexer(self.exe, self.D)
        self.current = self.node = None
        if self.D:
            super(Tree, self).__init__()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if isinstance(value, (list, generator, chain, dict)):
            self._data = value

    def set_object_getter(self, value):
        if callable(value):
            self.object_getter = value
        else:
            self.object_getter = self.default_getter

    def default_getter(self, o, attr):
        try:
            return o.__getattribute__(attr)
        except AttributeError:
            if self.D:
                self.end(color.op(".") + " returning '%s'", color.bold(o))
            return o

    def compile(self, expr):
        if expr in EXPR_CACHE:
            return EXPR_CACHE[expr]
        ret = EXPR_CACHE[expr] = parse(expr, self.D)
        return ret

    def exeSelector(self, fst, selector):
        selector0 = selector[0]
        selector1 = selector[1]
        selector2 = selector[2]
        for i in fst:
            if self.D:
                self.debug("setting self.current to %s", color.bold(i))
                self.debug("%s %s %s %s", selector0, selector1, selector2, i)
            self.current = i
            if selector0 == "fn":
                yield self.exe(selector)
            # elif type(selector1) in STR_TYPES and False:
            #     if D: self.debug("found string %s", type(i))
            #     try:
            #         if exe((selector0,i[selector1],selector2)):
            #             yield i
            #             if D: self.debug("appended")
            #         if D: self.debug("discarded")
            #     except Exception as e:
            #         if D: self.debug("discarded, Exception: %s",color.bold(e))
            else:
                try:
                    # TODO optimize an event when @ is not used. self.exe(selector1) can be cached
                    if self.exe((selector0, self.exe(selector1), self.exe(selector2))):
                        yield i
                        if self.D:
                            self.debug("appended")
                    if self.D:
                        self.debug("discarded")
                except Exception:
                    if self.D:
                        self.debug("discarded")

    # TODO change to yield?
    def exe(self, node):
        """
            node[0] - operator name
            node[1:] - params
        """
        types = [str, timeutils.datetime.time, timeutils.datetime.date, timeutils.datetime.datetime]
        try:
            types += [unicode]
        except:
            pass
        if self.D:
            self.start("executing node '%s'", node)
        type_node = type(node)
        if node is None or type_node in TYPES:
            return node
        elif type_node in types:
            return node
        elif type_node is list:
            return (self.exe(n) for n in node)
        elif type_node is dict:
            ret = {}
            for i in node.items():
                ret[self.exe(i[0])] = self.exe(i[1])
            return ret
        op = node[0]
        if op in OP_TOKENS.keys():
            return self.lexer[op](*node)
        elif op == "(root)":  # this is $
            return self.data
        # elif op=="(node)":# this is !
        #     if D: self.debug("returning node %s",self.node)
        #     return self.node
        elif op == "(current)":  # this is @
            if self.D:
                self.debug("returning current node %s", self.current)
            return self.current
        elif op == "name":
            return node[1]
        elif op == ".":
            fst = node[1]
            if type(fst) is tuple:
                fst = self.exe(fst)
            typefst = type(fst)
            if self.D:
                self.debug(color.op(".") + " left is '%s'", fst)
            # try:
            if node[2][0] == "*":
                if self.D:
                    self.end(color.op(".") + " returning '%s'", typefst in ITER_TYPES and fst or [fst])
                return fst  # typefst in ITER_TYPES and fst or [fst]
            # except:
            #     pass
            snd = self.exe(node[2])
            if self.D:
                self.debug(color.op(".") + " right is '%s'", snd)
            if typefst in ITER_TYPES:
                if self.D:
                    self.debug(color.op(".") + " filtering %s by %s", color.bold(fst), color.bold(snd))
                if type(snd) in ITER_TYPES:
                    return filter_dict(fst, list(snd))
                else:
                    # if D: self.debug(list(fst))
                    return (e[snd] for e in fst if type(e) is dict and snd in e)
            try:
                if self.D:
                    self.end(color.op(".") + " returning '%s'", fst.get(snd))
                return fst.get(snd)
            except Exception:
                if isinstance(fst, object):
                    return self.object_getter(fst, snd)
                if self.D:
                    self.end(color.op(".") + " returning '%s'", color.bold(fst))
                return fst
        elif op == "..":
            fst = flatten(self.exe(node[1]))
            if node[2][0] == "*":
                if self.D:
                    self.debug(color.op("..") + " returning '%s'", color.bold(fst))
                return fst
            # reduce objects to selected attributes
            snd = self.exe(node[2])
            if self.D:
                self.debug(color.op("..") + " finding all %s in %s", color.bold(snd), color.bold(fst))
            if type(snd) in ITER_TYPES:
                ret = filter_dict(fst, list(snd))
                if self.D:
                    self.debug(color.op("..") + " returning %s", color.bold(ret))
                return ret
            else:
                ret = chain(*(type(x) in ITER_TYPES and x or [x] for x in (e[snd] for e in fst if snd in e)))
                # print list(chain(*(type(x) in ITER_TYPES and x or [x] for x in (e[snd] for e in fst if snd in e))))
                if self.D:
                    self.debug(color.op("..") + " returning %s", color.bold(ret))
                return ret
        elif op == "[":
            len_node = len(node)
            # TODO move it to tree generation phase
            if len_node is 1:  # empty list
                if self.D:
                    self.debug("returning an empty list")
                return []
            if len_node is 2:  # list - preserved to catch possible event of leaving it as '[' operator
                if self.D:
                    self.debug("doing list mapping")
                return [self.exe(x) for x in node[1]]
            if len_node is 3:  # selector used []
                fst = self.exe(node[1])
                # check against None
                if not fst:
                    return fst
                selector = node[2]
                if self.D:
                    self.debug("found '%s' selector. executing on %s", color.bold(selector), color.bold(fst))
                selectorIsTuple = type(selector) is tuple

                if selectorIsTuple and selector[0] is "[":
                    nodeList = []
                    nodeList_append = nodeList.append
                    for i in fst:
                        if self.D:
                            self.debug("setting self.current to %s", color.bold(i))
                        self.current = i
                        nodeList_append(self.exe((selector[0], self.exe(selector[1]), self.exe(selector[2]))))
                    if self.D:
                        self.debug("returning %s objects: %s", color.bold(len(nodeList)), color.bold(nodeList))
                    return nodeList

                if selectorIsTuple and selector[0] == "(current)":
                    if self.D:
                        self.warning(color.bold("$.*[@]") + " is eqivalent to " + color.bold("$.*") + "!")
                    return fst

                if selectorIsTuple and selector[0] in SELECTOR_OPS:
                    if self.D:
                        self.debug("found %s operator in selector, %s", color.bold(selector[0]),
                                     color.bold(selector))
                    if type(fst) is dict:
                        fst = [fst]
                    # TODO move it to tree building phase
                    if type(selector[1]) is tuple and selector[1][0] == "name":
                        selector = (selector[0], selector[1][1], selector[2])
                    # if D and nodeList: self.debug("returning '%s' objects: '%s'", color.bold(len(nodeList)), color.bold(nodeList))
                    return self.exeSelector(fst, selector)
                self.current = fst
                snd = self.exe(node[2])
                typefst = type(fst)
                if typefst in [tuple] + ITER_TYPES + STR_TYPES:
                    typesnd = type(snd)
                    # nodes[N]
                    if typesnd in NUM_TYPES or typesnd is str and snd.isdigit():
                        n = int(snd)
                        if self.D:
                            self.info("getting %sth element from '%s'", color.bold(n), color.bold(fst))
                        if typefst in (generator, chain):
                            if n > 0:
                                return skip(fst, n)
                            elif n == 0:
                                return next(fst)
                            else:
                                fst = list(fst)
                        else:
                            try:
                                return fst[n]
                            except (IndexError, TypeError):
                                return None
                    # $.*['string']==$.string
                    if type(snd) in STR_TYPES:
                        return self.exe((".", fst, snd))
                    else:
                        # $.*[@.string] - bad syntax, but allowed
                        return snd
                else:
                    try:
                        if self.D:
                            self.debug("returning %s", color.bold(fst[snd]))
                        return fst[snd]
                    except KeyError:
                        # CHECK - is it ok to do that or should it be ProgrammingError?
                        if self.D:
                            self.debug("returning an empty list")
                        return []
            raise ProgrammingError("Wrong usage of " + color.bold("[") + " operator")
        elif op == "fn":
            # Built-in functions
            fnName = node[1]
            args = None
            try:
                args = [self.exe(x) for x in node[2:]]
            except IndexError:
                if self.D:
                    self.debug("NOT ERROR: can't map '%s' with '%s'", node[2:], self.exe)
            # arithmetic
            if fnName == "sum":
                args = args[0]
                if type(args) in NUM_TYPES:
                    return args
                return sum((x for x in args if type(x) in NUM_TYPES))
            elif fnName == "max":
                args = args[0]
                if type(args) in NUM_TYPES:
                    return args
                return max((x for x in args if type(x) in NUM_TYPES))
            elif fnName == "min":
                args = args[0]
                if type(args) in NUM_TYPES:
                    return args
                return min((x for x in args if type(x) in NUM_TYPES))
            elif fnName == "avg":
                args = args[0]
                if type(args) in NUM_TYPES:
                    return args
                if type(args) not in ITER_TYPES:
                    raise Exception("Argument for avg() is not an array")
                else:
                    args = list(args)
                try:
                    return sum(args) / float(len(args))
                except TypeError:
                    args = [x for x in args if type(x) in NUM_TYPES]
                    self.warning("Some items in array were ommited")
                    return sum(args) / float(len(args))
            elif fnName == "round":
                return round(*args)
            # casting
            elif fnName == "int":
                return int(args[0])
            elif fnName == "float":
                return float(args[0])
            elif fnName == "str":
                return str(py2JSON(args[0]))
            elif fnName in ("list", "array"):
                try:
                    a = args[0]
                except IndexError:
                    return []
                targs = type(a)
                if targs is timeutils.datetime.datetime:
                    return timeutils.date2list(a) + timeutils.time2list(a)
                if targs is timeutils.datetime.date:
                    return timeutils.date2list(a)
                if targs is timeutils.datetime.time:
                    return timeutils.time2list(a)
                return list(a)
            # string
            elif fnName == "upper":
                return args[0].upper()
            elif fnName == "lower":
                return args[0].lower()
            elif fnName == "capitalize":
                return args[0].capitalize()
            elif fnName == "title":
                return args[0].title()
            elif fnName == "split":
                return args[0].split(*args[1:])
            elif fnName == "slice":
                if args and type(args[1]) not in ITER_TYPES:
                    raise ExecutionError(
                        "Wrong usage of slice(STRING, ARRAY). Second argument is not an array but %s." % color.bold(
                            type(args[1]).__name__))
                try:
                    pos = list(args[1])
                    if type(pos[0]) in ITER_TYPES:
                        if self.D:
                            self.debug("run slice() for a list of slicers")
                        return (args[0][x[0]:x[1]] for x in pos)
                    return args[0][pos[0]:pos[1]]
                except IndexError:
                    if len(args) != 2:
                        raise ProgrammingError(
                            "Wrong usage of slice(STRING, ARRAY). Provided %s argument, should be exactly 2." % len(
                                args))
            elif fnName == "escape":
                global escape, escapeDict
                if not escape:
                    from objectpath.utils import escape, escapeDict
                return escape(args[0], escapeDict)
            elif fnName == "unescape":
                global unescape, unescapeDict
                if not unescape:
                    from objectpath.utils import unescape, unescapeDict
                return unescape(args[0], unescapeDict)
            elif fnName == "replace":
                if sys.version_info[0] < 3 and type(args[0]) is unicode:
                    args[0] = args[0].encode("utf8")
                return str.replace(args[0], args[1], args[2])
            # TODO this should be supported by /regex/
            # elif fnName=="REsub":
            #     return re.sub(args[1],args[2],args[0])
            elif fnName == "sort":
                if len(args) > 1:
                    key = args[1]
                    a = {"key": lambda x: x.get(key, 0)}
                else:
                    a = {}
                args = args[0]
                if self.D:
                    self.debug("doing sort on '%s'", args)
                try:
                    return sorted(args, **a)
                except TypeError:
                    return args
            elif fnName == "reverse":
                args = args[0]
                try:
                    args.reverse()
                    return args
                except TypeError:
                    return args
            elif fnName == "map":
                return map(lambda x: self.exe(("fn", args[0], x)), args[1])
            elif fnName in ("count", "len"):
                args = args[0]
                if args in (True, False, None):
                    return args
                if type(args) in ITER_TYPES:
                    return len(list(args))
                return len(args)
            elif fnName == "join":
                try:
                    joiner = args[1]
                except Exception:
                    joiner = ""
                try:
                    return joiner.join(args[0])
                except TypeError:
                    try:
                        return joiner.join(map(str, args[0]))
                    except Exception:
                        return args[0]
            # time
            elif fnName in ("now", "age", "time", "date", "dateTime"):
                if fnName == "now":
                    return timeutils.now()
                if fnName == "date":
                    return timeutils.date(args)
                if fnName == "time":
                    return timeutils.time(args)
                if fnName == "dateTime":
                    return timeutils.dateTime(args)
                # TODO move lang to localize() entirely!
                if fnName == "age":
                    a = {}
                    if len(args) > 1:
                        a["reference"] = args[1]
                    if len(args) > 2:
                        a["lang"] = args[2]
                    return list(timeutils.age(args[0], **a))
            elif fnName == "toMillis":
                args = args[0]
                if args.utcoffset() is not None:
                    args = args - args.utcoffset()  # pylint: disable=E1103
                global calendar
                if not calendar:
                    import calendar
                return int(calendar.timegm(args.timetuple()) * 1000 + args.microsecond / 1000)
            elif fnName == "localize":
                if type(args[0]) is timeutils.datetime.datetime:
                    return timeutils.UTC2local(*args)
            # polygons
            elif fnName == "area":
                def segments(p):
                    p = list(map(lambda x: x[0:2], p))
                    return zip(p, p[1:] + [p[0]])

                return 0.5 * abs(sum(x0 * y1 - x1 * y0
                                     for ((x0, y0), (x1, y1)) in segments(args[0])))
            # misc
            elif fnName == "keys":
                try:
                    return list(args[0].keys())
                except AttributeError:
                    raise ExecutionError(
                        "Argument is not " + color.bold("object") + " but %s in keys()" % color.bold(
                            type(args[0]).__name__))
            elif fnName == "type":
                ret = type(args[0])
                if ret in ITER_TYPES:
                    return "array"
                if ret is dict:
                    return "object"
                return ret.__name__
            elif fnName in self._REGISTERED_FUNCTIONS:
                return self._REGISTERED_FUNCTIONS[fnName](*args)
            else:
                raise ProgrammingError("Function " + color.bold(fnName) + " does not exist.")
        else:
            return node

    def execute(self, expr):
        if self.D:
            self.start("Tree.execute")
        # D = self.D
        if type(expr) in STR_TYPES:
            tree = self.compile(expr)
        elif type(expr) not in (tuple, list, dict):
            return expr
        ret = self.exe(tree)
        if self.D:
            self.end("Tree.execute with: '%s'", ret)
        return ret

    def __str__(self):
        return "TreeObject()"

    def __repr__(self):
        return self.__str__()
