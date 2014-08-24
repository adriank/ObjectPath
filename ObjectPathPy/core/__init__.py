#!/usr/bin/env python
# -*- coding: utf-8 -*-
from utils import iterators

SELECTOR_OPS=["is",">","<","is not",">=","<=","in","not in",":","and","or"]
#it must be list because of further concatenations
NUM_TYPES=[int,float,long]
STR_TYPES=[str,unicode]
ITER_TYPES=iterators

class ProgrammingError(Exception):
	pass

PY_TYPES_MAP={
	"int":"number",
	"float":"number",
	"dict":"object",
	"list":"array"
}
