#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of ObjectPath released under MIT license.
# Copyright (C) 2010-2014 Adrian Kalbarczyk

from types import GeneratorType as generator
from itertools import chain

SELECTOR_OPS = [
  "is", ">", "<", "is not", ">=", "<=", "in", "not in", ":", "and", "or", "fn"
]
# it must be list because of further concatenations
NUM_TYPES = [int, float]

try:
  NUM_TYPES += [long]
except NameError:
  pass

STR_TYPES = [str]

try:
  STR_TYPES += [unicode]
except NameError:
  pass

ITER_TYPES = [list, generator, chain]

try:
  ITER_TYPES += [map, filter]
except NameError:
  pass

class ProgrammingError(Exception):
  pass

class ExecutionError(Exception):
  pass

PY_TYPES_MAP = {
  "int": "number",
  "float": "number",
  "str": "string",
  "dict": "object",
  "list": "array"
}
