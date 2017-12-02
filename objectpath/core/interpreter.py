#!/usr/bin/env python

# This file is part of ObjectPath released under AGPL v3 license.
# Copyright (C) 2010-2014 Adrian Kalbarczyk

import sys
import re
from .parser import parse
from .lexer import Lexer, Functions, OP_TOKENS, FN_TOKENS
from objectpath.core import *
import objectpath.utils.colorify as color  # pylint: disable=W0614
from objectpath.utils import flatten, filter_dict, timeutils, skip
from objectpath.utils.json_ext import py2JSON
from objectpath.core import ITER_TYPES, generator, chain
from objectpath.utils.debugger import Debugger


EXPR_CACHE = {}

# setting external modules to 0, thus enabling lazy loading. 0 ensures that Pythonic types are never matched.
# this way is efficient because if statement is fast and once loaded these variables are pointing to libraries.
ObjectId = generateID = calendar = escape = escapeDict = unescape = unescapeDict = 0
TYPES = [str, int, float, bool, generator, chain]
try:
    TYPES += [long]
except NameError:
    pass


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
        self.functions = Functions(self.exe, self.D)
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
            if fnName in FN_TOKENS.keys():
                return self.functions[fnName](*args)
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
