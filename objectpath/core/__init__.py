#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of ObjectPath released under AGPL v3 license.
# Copyright (C) 2010-2014 Adrian Kalbarczyk

from objectpath.utils import iterators

SELECTOR_OPS=["is",">","<","is not",">=","<=","in","not in",":","and","or","fn"]
# it must be list because of further concatenations
NUM_TYPES=[int,float]
try:
	NUM_TYPES+=[long]
except NameError:
	pass
STR_TYPES=[str]
try:
	STR_TYPES+=[unicode]
except NameError:
	pass
ITER_TYPES=iterators

class ProgrammingError(Exception):
	pass

class ExecutionError(Exception):
	pass

PY_TYPES_MAP={
	"int":"number",
	"str":"string",
	"float":"number",
	"dict":"object",
	"list":"array"
}
